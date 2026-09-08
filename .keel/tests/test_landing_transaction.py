from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import candidate_attestation as ca
import evidence_system
import git_proof
import keel_core as core


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "-c", "user.name=T", "-c", "user.email=t@x", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def repo() -> tuple[Path, str, str, str]:
    directory = Path(tempfile.mkdtemp(prefix="keel-landing-test-"))
    git(directory, "init", "-q")
    git(directory, "config", "user.name", "T")
    git(directory, "config", "user.email", "t@x")
    (directory / "base.txt").write_text("base\n")
    base = commit(directory, "base")
    (directory / "candidate.txt").write_text("candidate\n")
    candidate = commit(directory, "candidate")
    git(directory, "branch", "candidate", candidate)
    git(directory, "checkout", "-q", base)
    (directory / "target.txt").write_text("target\n")
    target = commit(directory, "target")
    git(directory, "branch", "target", target)
    return directory, base, candidate, target


def main() -> None:
    root, base, candidate, target = repo()
    tree, changed = git_proof.synthetic_integration_tree(root, target, candidate, "merge")
    assert git_proof.synthetic_integration_tree(root, target, candidate, "squash")[0] == tree
    assert git_proof.synthetic_integration_tree(root, target, candidate, "rebase")[0] == tree
    assert git_proof.commit_tree(root, target) != tree
    assert changed == ["candidate.txt", "target.txt"]
    landing = ca.LandingAttestation(
        "landing-test", "refs/heads/target", target, "a" * 64, candidate, git_proof.commit_tree(root, candidate),
        tree, "b" * 64, "c" * 64, ({"receipt_id": "r", "receipt_digest": "d" * 64},), "e" * 64,
        "git-merge-tree", "merge")
    assert ca.LandingAttestation.from_dict(json.loads(json.dumps(landing.as_dict()))) == landing
    ca.write_landing_attestation(root, landing)
    core._mark_landing_stale(root, landing, "concurrent target movement")
    assert ca.read_landing_attestation(root, "landing-test").status == "STALE"
    landed = git(root, "commit-tree", tree, "-p", target, "-p", candidate, "-m", "landing")
    verified = core.verify_landing(root, "landing-test", landed, landing)
    assert verified["status"] == "PASS"
    try:
        core.verify_landing(root, "landing-test", candidate, landing)
    except RuntimeError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched landed tree was accepted")
    try:
        git_proof.synthetic_integration_tree(root, target, candidate, "unsupported")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported strategy was accepted")
    conflict = Path(tempfile.mkdtemp(prefix="keel-landing-conflict-"))
    git(conflict, "init", "-q")
    git(conflict, "config", "user.name", "T")
    git(conflict, "config", "user.email", "t@x")
    (conflict / "same.txt").write_text("base\n")
    conflict_base = commit(conflict, "base")
    (conflict / "same.txt").write_text("candidate\n")
    conflict_candidate = commit(conflict, "candidate")
    git(conflict, "checkout", "-q", conflict_base)
    (conflict / "same.txt").write_text("target\n")
    conflict_target = commit(conflict, "target")
    try:
        git_proof.synthetic_integration_tree(conflict, conflict_target, conflict_candidate)
    except RuntimeError as exc:
        assert "conflicts" in str(exc)
    else:
        raise AssertionError("conflicting concurrent changes were accepted")
    verifier = {"id": "v", "version": "1", "provider": "unit_test", "provenance": "fixture", "authority": "TESTED"}
    step = {"verifier_id": "v", "runtime": {"argv": ["true"], "cwd": ".", "timeout_sec": 10}, "establishes": ["ER-1"]}
    candidate_subject = {"kind": "git-worktree", "head_commit": candidate}
    integration_subject = {"kind": "git-integration-tree", "integration_tree": tree}
    receipt = evidence_system.receipt(verifier, step, candidate_subject, "b" * 64, "PASS", [], "s", "e")
    plan = {"errors": [], "steps": [step], "assignments": [{"evidence_requirement_id": "ER-1", "verifier_id": "v"}]}
    requirement = {"id": "ER-1", "minimum_authority": "TESTED"}
    assert evidence_system.evaluate(plan, [receipt], [requirement], integration_subject, "b" * 64)["status"] == "INCONCLUSIVE"
    print("Landing transaction tests PASS")


if __name__ == "__main__":
    main()
