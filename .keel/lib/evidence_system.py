"""Receipt-authoritative verification contracts and deterministic planning.

This module is deliberately pure except for environment fingerprint helpers.  Legacy
evidence graph files are projections built by callers, never inputs to authority.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import PurePosixPath

AUTHORITY = (
    "ASSERTED", "INSPECTED", "TESTED", "RUNTIME_OBSERVED",
    "INDEPENDENTLY_REVIEWED", "FORMALLY_VERIFIED",
)
RESULTS = {"PASS", "FAIL", "INCONCLUSIVE"}
PROVIDERS = {"command", "unit_test", "schema", "browser", "visual", "log_query", "metric_query", "trace_query", "security", "benchmark", "hardware", "human_review", "external_ci", "changed_path", "file_exists"}


def canonical_digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def authority_at_least(actual: str, required: str) -> bool:
    return actual in AUTHORITY and required in AUTHORITY and AUTHORITY.index(actual) >= AUTHORITY.index(required)


def _safe_glob(value: str) -> bool:
    p = PurePosixPath(value.replace("\\", "/"))
    return bool(value) and not p.is_absolute() and ".." not in p.parts


def validate_registry(registry: list[dict]) -> list[str]:
    errors, identities, invocations = [], set(), set()
    if not isinstance(registry, list) or not registry:
        return ["verifier_registry must be a non-empty list"]
    for index, row in enumerate(registry):
        label = f"verifier_registry[{index}]"
        if not isinstance(row, dict): errors.append(f"{label} must be an object"); continue
        identity = row.get("id")
        if not isinstance(identity, str) or not identity.strip(): errors.append(f"{label}.id must be non-empty")
        elif identity in identities: errors.append(f"duplicate verifier identity: {identity}")
        else: identities.add(identity)
        provider = row.get("provider")
        if provider not in PROVIDERS: errors.append(f"{label}.provider is unsupported: {provider!r}")
        if row.get("authority") not in AUTHORITY: errors.append(f"{label}.authority must be one of {list(AUTHORITY)}")
        for key in ("provenance", "version"):
            if not isinstance(row.get(key), str) or not row[key].strip(): errors.append(f"{label}.{key} must be non-empty")
        applicability = row.get("applicability")
        if not isinstance(applicability, dict): errors.append(f"{label}.applicability must be an object")
        else:
            paths = applicability.get("paths", [])
            if not isinstance(paths, list) or any(not isinstance(x, str) or not _safe_glob(x) for x in paths): errors.append(f"{label}.applicability.paths contains invalid globs")
            risks = applicability.get("risk_levels", ["low", "standard", "high"])
            if not isinstance(risks, list) or any(x not in {"low", "standard", "high"} for x in risks): errors.append(f"{label}.applicability.risk_levels is invalid")
        supports = row.get("supports", {})
        if not isinstance(supports, dict) or not isinstance(supports.get("requirement_types"), list) or not isinstance(supports.get("evidence_providers"), list): errors.append(f"{label}.supports must declare requirement_types and evidence_providers")
        runtime = row.get("runtime")
        if not isinstance(runtime, dict) or runtime.get("kind") != "command": errors.append(f"{label}.runtime.kind must be command")
        else:
            argv = runtime.get("argv")
            if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv): errors.append(f"{label}.runtime.argv is invalid")
            else:
                normalized = (tuple(argv), runtime.get("cwd", "."))
                if normalized in invocations: errors.append(f"duplicate verifier invocation: {identity}")
                invocations.add(normalized)
        if not isinstance(row.get("mandatory_kernel", False), bool): errors.append(f"{label}.mandatory_kernel must be boolean")
    return errors


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or (pattern.endswith("/**") and path.startswith(pattern[:-3].rstrip("/") + "/")) or (not any(c in pattern for c in "*?[") and (path == pattern or path.startswith(pattern.rstrip("/") + "/")))


def evidence_requirements(requirements: dict, acceptance: dict) -> list[dict]:
    criteria_by_req: dict[str, list[dict]] = {}
    for criterion in acceptance.get("criteria", []):
        if isinstance(criterion, dict) and criterion.get("required", True): criteria_by_req.setdefault(criterion.get("requirement_id"), []).append(criterion)
    output = []
    for req in requirements.get("requirements", []):
        rid = req.get("id")
        edges = [edge for c in criteria_by_req.get(rid, []) for edge in c.get("evidence", []) if isinstance(edge, dict)]
        output.append({"id": f"ER-{rid}", "requirement_id": rid, "minimum_authority": req.get("minimum_evidence_authority", "TESTED"), "requirement_type": req.get("type", "behavior"), "implementation_paths": req.get("implementation_paths", []), "acceptable_verifiers": sorted({e.get("check_id") for e in edges if isinstance(e.get("check_id"), str)}), "acceptable_providers": sorted({e.get("provider") for e in edges if isinstance(e.get("provider"), str)})})
    return output


def plan(registry: list[dict], evidence_reqs: list[dict], changed_paths: list[str], risk_level: str, repository_facts: dict | None = None) -> dict:
    errors = validate_registry(registry)
    by_id = {v.get("id"): v for v in registry if isinstance(v, dict) and isinstance(v.get("id"), str)}
    selected = {v["id"] for v in registry if isinstance(v, dict) and v.get("mandatory_kernel")}
    assignments = []
    for er in evidence_reqs:
        candidates = []
        for vid in er.get("acceptable_verifiers", []):
            v = by_id.get(vid)
            if not v: continue
            app, supports = v.get("applicability", {}), v.get("supports", {})
            paths = app.get("paths", [])
            applicable = (not paths or any(_matches(path, pattern) for path in changed_paths for pattern in paths)) and risk_level in app.get("risk_levels", ["low", "standard", "high"])
            supported = er.get("requirement_type") in supports.get("requirement_types", []) and bool(set(er.get("acceptable_providers", [])) & set(supports.get("evidence_providers", [])))
            if applicable and supported and authority_at_least(v.get("authority"), er.get("minimum_authority")): candidates.append(v)
        if not candidates:
            errors.append(f"{er.get('id')} has no applicable verifier with sufficient declared authority")
            assignments.append({"evidence_requirement_id": er.get("id"), "requirement_id": er.get("requirement_id"), "verifier_id": None})
            continue
        chosen = sorted(candidates, key=lambda v: (AUTHORITY.index(v["authority"]), v["id"]))[0]
        selected.add(chosen["id"])
        assignments.append({"evidence_requirement_id": er["id"], "requirement_id": er["requirement_id"], "verifier_id": chosen["id"]})
    rows = []
    for vid in sorted(selected):
        v = by_id.get(vid)
        if v: rows.append({"verifier_id": vid, "authority": v["authority"], "provider": v["provider"], "runtime": v["runtime"], "mandatory_kernel": bool(v.get("mandatory_kernel")), "establishes": sorted(a["evidence_requirement_id"] for a in assignments if a["verifier_id"] == vid)})
    portable = {"schema_version": 1, "risk_level": risk_level, "changed_paths": sorted(changed_paths), "repository_facts_digest": canonical_digest(repository_facts or {}), "steps": rows, "assignments": assignments, "errors": errors}
    return {**portable, "status": "PASS" if not errors else "INCONCLUSIVE", "plan_digest": canonical_digest(portable)}


def environment_fingerprint() -> dict:
    value = {"os": os.name, "platform": platform.system(), "machine": platform.machine(), "python": platform.python_version(), "executable": os.path.basename(sys.executable)}
    return {**value, "digest": canonical_digest(value)}


def receipt(verifier: dict, step: dict, subject: dict, intent_digest: str, result: str, observations: list[dict], started_at: str, ended_at: str) -> dict:
    if result not in RESULTS: raise ValueError(f"invalid receipt result: {result}")
    invocation = {"argv": step["runtime"]["argv"], "cwd": step["runtime"].get("cwd", "."), "timeout_sec": int(step["runtime"].get("timeout_sec", 600))}
    body = {"schema_version": 1, "verifier": {"id": verifier["id"], "version": verifier["version"], "provider": verifier["provider"], "provenance": verifier["provenance"], "declared_authority": verifier["authority"]}, "subject": subject, "intent_digest": intent_digest, "environment": environment_fingerprint(), "invocation": invocation, "result": result, "observations": observations, "establishes": step.get("establishes", []), "started_at": started_at, "ended_at": ended_at}
    return {**body, "receipt_digest": canonical_digest(body)}


def evaluate(plan_value: dict, receipts: list[dict], evidence_reqs: list[dict], subject: dict, intent_digest: str) -> dict:
    errors, coverage = list(plan_value.get("errors", [])), []
    receipt_map = {r.get("verifier", {}).get("id"): r for r in receipts}
    registry_steps = {s.get("verifier_id"): s for s in plan_value.get("steps", [])}
    for er in evidence_reqs:
        assignment = next((a for a in plan_value.get("assignments", []) if a.get("evidence_requirement_id") == er.get("id")), None)
        r = receipt_map.get(None if not assignment else assignment.get("verifier_id")); passed = False; reason = "missing receipt"
        if r:
            step = registry_steps.get(r.get("verifier", {}).get("id"), {})
            valid_digest = r.get("receipt_digest") == canonical_digest({k:v for k,v in r.items() if k != "receipt_digest"})
            passed = r.get("result") == "PASS" and r.get("subject") == subject and r.get("intent_digest") == intent_digest and er.get("id") in r.get("establishes", []) and authority_at_least(r.get("verifier", {}).get("declared_authority"), er.get("minimum_authority")) and valid_digest and er.get("id") in step.get("establishes", [])
            reason = "established" if passed else "receipt failed authority, subject, intent, integrity, result, or scope validation"
        if not passed: errors.append(f"{er.get('id')} not established: {reason}")
        coverage.append({"evidence_requirement_id": er.get("id"), "requirement_id": er.get("requirement_id"), "verifier_id": None if not assignment else assignment.get("verifier_id"), "status": "PASS" if passed else "INCONCLUSIVE"})
    failed = any(r.get("result") == "FAIL" for r in receipts)
    return {"schema_version": 1, "status": "FAIL" if failed else "PASS" if not errors else "INCONCLUSIVE", "errors": sorted(set(errors)), "coverage": coverage, "summary": {"required": len(evidence_reqs), "established": sum(c["status"] == "PASS" for c in coverage)}}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
