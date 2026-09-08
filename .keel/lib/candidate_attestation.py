"""Candidate attestations and the existing KEEL Git seal/anchor compatibility boundary."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import git_proof

SCHEMA = "keel.candidate-attestation"
VERSION = 1
CANDIDATE_REF_PREFIX = "refs/keel/candidates/"
ATTESTATION_REF_PREFIX = "refs/keel/attestations/candidates/"
LANDED_REF_PREFIX = "refs/keel/ledger/"


def canonical_digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class CandidateAttestation:
    change_id: str
    work_identity: dict
    candidate_commit: str
    candidate_tree: str
    intent_digest: str
    material_digest: str
    content_digest: str
    evidence_plan_digest: str
    evidence_receipts: tuple[dict, ...]
    policy_runtime_profile_digest: str | None
    changed_paths: tuple[str, ...]
    schema: str = SCHEMA
    version: int = VERSION

    def as_dict(self) -> dict:
        value = dict(self.__dict__)
        value["evidence_receipts"] = list(self.evidence_receipts)
        value["changed_paths"] = list(self.changed_paths)
        return value

    @property
    def digest(self) -> str:
        return canonical_digest(self.as_dict())

    @classmethod
    def from_dict(cls, value: dict) -> "CandidateAttestation":
        if value.get("schema") != SCHEMA or value.get("version") != VERSION:
            raise RuntimeError("unsupported CandidateAttestation schema/version")
        required = ("change_id", "work_identity", "candidate_commit", "candidate_tree", "intent_digest",
                    "material_digest", "content_digest", "evidence_plan_digest", "evidence_receipts", "changed_paths")
        if any(key not in value for key in required):
            raise RuntimeError("CandidateAttestation is incomplete")
        for key in ("candidate_commit", "candidate_tree", "intent_digest", "material_digest", "content_digest", "evidence_plan_digest"):
            raw = value[key]
            expected = {40, 64} if key in {"candidate_commit", "candidate_tree"} else {64}
            if not isinstance(raw, str) or len(raw) not in expected or any(char not in "0123456789abcdef" for char in raw):
                raise RuntimeError(f"CandidateAttestation {key} is invalid")
        receipts = value["evidence_receipts"]
        if not isinstance(receipts, list) or any(set(row) != {"receipt_id", "receipt_digest"} for row in receipts):
            raise RuntimeError("CandidateAttestation evidence_receipts are invalid")
        if any(not isinstance(row["receipt_id"], str) or not row["receipt_id"] or
               not isinstance(row["receipt_digest"], str) or len(row["receipt_digest"]) != 64 for row in receipts):
            raise RuntimeError("CandidateAttestation EvidenceReceipt identity/digest is invalid")
        if not isinstance(value["changed_paths"], list):
            raise RuntimeError("CandidateAttestation changed_paths are invalid")
        for path in value["changed_paths"]:
            git_proof.normalize_repo_path(path)
        return cls(**{**value, "evidence_receipts": tuple(receipts), "changed_paths": tuple(value["changed_paths"])})


def _path(change_id: str, name: str) -> str:
    return f".keel/ledger/{change_id}/{name}"


def _digest_boundary(root: Path, commit: str, change_id: str, paths: list[str], intent_files: tuple[str, ...], boundary: str) -> str:
    names = paths if boundary == "material" else [_path(change_id, name) for name in intent_files]
    return git_proof.digest_entries((boundary, rel if boundary == "material" else Path(rel).name,
                                     git_proof.tree_entry(root, commit, rel)) for rel in sorted(names))


def build(root: Path, change_id: str, commit: str, state: dict, verification: dict,
          intent_files: tuple[str, ...]) -> CandidateAttestation:
    sha = git_proof.resolve_commit(root, commit); paths = sorted(verification["changed_paths"])
    canonical = intent_files == ("intent.json",)
    prefix = "views/" if canonical else ""
    plan = git_proof.show_json(root, sha, _path(change_id, prefix + "evidence-plan.json"))
    receipts_doc = git_proof.show_json(root, sha, _path(change_id, prefix + "evidence-receipts.json"))
    if plan.get("plan_digest") != verification.get("evidence_plan_digest"):
        raise RuntimeError("committed EvidencePlan digest differs from verification")
    intent_value = {name: git_proof.tree_entry(root, sha, _path(change_id, name))[1].decode("utf-8", errors="surrogateescape")
                    for name in intent_files}
    if canonical_digest(intent_value) != verification.get("intent_digest"):
        raise RuntimeError("independent committed intent digest differs from verification")
    for receipt in receipts_doc.get("receipts", []):
        body = {key: value for key, value in receipt.items() if key != "receipt_digest"}
        if canonical_digest(body) != receipt.get("receipt_digest"):
            raise RuntimeError("committed EvidenceReceipt digest is invalid")
    receipts = tuple(sorted(({"receipt_id": row.get("receipt_id") or row.get("verifier", {}).get("id"), "receipt_digest": row.get("receipt_digest")}
                             for row in receipts_doc.get("receipts", [])), key=lambda row: str(row["receipt_id"])))
    if any(not row["receipt_id"] or not row["receipt_digest"] for row in receipts):
        raise RuntimeError("committed EvidenceReceipts lack identity/digest")
    config = git_proof.show_json(root, sha, ".keel/config.json")
    profile = {key: config.get(key) for key in ("schema_version", "verifier_registry") if key in config}
    identity = {"change_id": change_id, "base_commit": state["base_commit"]}
    return CandidateAttestation(change_id, identity, sha, git_proof.commit_tree(root, sha),
        verification["intent_digest"], _digest_boundary(root, sha, change_id, paths, intent_files, "material"),
        verification["content_digest"], plan["plan_digest"], receipts,
        canonical_digest(profile) if profile else None, tuple(paths))


def write_attestation_object(root: Path, attestation: CandidateAttestation, ref: str) -> str:
    payload = (json.dumps(attestation.as_dict(), indent=2, sort_keys=True) + "\n").encode()
    import subprocess
    written = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=root, input=payload, capture_output=True, check=True)
    oid_text = written.stdout.decode().strip()
    old = git_proof.run(root, ["show-ref", "--hash", "--verify", ref], check=False)
    if old.returncode == 0 and old.stdout.strip() != oid_text:
        raise RuntimeError(f"KEEL attestation ref collision: {ref} already points to {old.stdout.strip()}")
    if old.returncode:
        updated = git_proof.run(root, ["update-ref", ref, oid_text, "0" * 40], check=False)
        if updated.returncode: raise RuntimeError(updated.stderr.strip() or "git update-ref attestation failed")
    return oid_text


def read_attestation(root: Path, change_id: str) -> CandidateAttestation:
    ref = ATTESTATION_REF_PREFIX + change_id
    raw = git_proof.run(root, ["cat-file", "blob", ref], check=False, binary=True)
    if raw.returncode: raise RuntimeError(f"candidate attestation missing: {ref}")
    return CandidateAttestation.from_dict(json.loads(raw.stdout.decode()))
