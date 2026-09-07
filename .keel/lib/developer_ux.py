from __future__ import annotations
import json
from pathlib import Path

def init_check(root: Path) -> dict:
    import keel_core
    from lifecycle import inventory
    doctor_errors = keel_core.doctor(root); compatibility = inventory(root)
    return {"schema_version": 1, "status": "READY" if not doctor_errors and compatibility["status"] == "COMPATIBLE" else "NOT_READY", "read_only": True, "doctor": {"status": "PASS" if not doctor_errors else "FAIL", "errors": doctor_errors}, "compatibility": compatibility, "external": {"codex_version": "UNVERIFIED", "runtime_hooks": "UNVERIFIED"}, "mutation": "NONE"}

def review(root: Path, change_id: str | None = None) -> dict:
    import keel_core
    cid = change_id or keel_core.active_change(root)
    result = {"schema_version": 1, "read_only": True, "change_id": cid, "status": "IDLE" if not cid else "AVAILABLE", "lifecycle": keel_core.status_summary(root, cid) if cid else {"active_change": None, "keel": "IDLE"}, "next": keel_core.next_action(root, cid)}
    if not cid: return result
    ledger = keel_core.ledger_dir(root, cid); evidence = ledger / "evidence-graph.json"
    result["evidence"] = json.loads(evidence.read_text(encoding="utf-8")) if evidence.is_file() else None
    ref = f"refs/keel/candidates/{cid}"
    result["candidate"] = keel_core.candidate_status(root, cid) if keel_core.run_git(root, ["show-ref", "--verify", ref], check=False).returncode == 0 else None
    return result

def ship_eligibility(root: Path, change_id: str | None = None) -> dict:
    import keel_core
    cid = change_id or keel_core.active_change(root)
    if not cid: return {"schema_version": 1, "status": "INELIGIBLE", "read_only": True, "reason": "no active change", "permission": "NOT_GRANTED"}
    verified, reason = keel_core.current_verified(root, cid); ref = f"refs/keel/candidates/{cid}"
    sealed = keel_core.run_git(root, ["show-ref", "--verify", ref], check=False).returncode == 0; eligible = verified and sealed
    return {"schema_version": 1, "status": "ELIGIBLE" if eligible else "INELIGIBLE", "read_only": True, "change_id": cid, "verified": verified, "verification_reason": reason, "sealed_candidate": sealed, "permission": "NOT_GRANTED", "integration": "NOT_PERFORMED", "next": "authorized integration followed by keel anchor" if eligible else "complete verification and seal the candidate"}
