from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

import keel_core
import mission_graph


class BoundaryViolation(RuntimeError):
    """A mission attempted to cross a Change-owned boundary."""


def capability_handshake(root: Path) -> dict:
    """Report explicit local/runtime capabilities without inferring policy."""
    config = keel_core.read_json(root / ".keel/config.json")
    declared = config.get("runtime_capabilities", {})
    local = {
        "python": True,
        "git": keel_core.run_git(root, ["rev-parse", "--git-dir"], check=False).returncode == 0,
        "ledger": (root / ".keel/ledger").is_dir(),
        "worktrees": True,
    }
    external = {
        "provider": declared.get("provider", "UNKNOWN"),
        "codex_version": "UNKNOWN",
        "hooks": "UNKNOWN",
    }
    missing = sorted(name for name, present in local.items() if not present)
    return {
        "schema_version": 1,
        "status": "READY" if not missing else "BLOCKED",
        "local": local,
        "external": external,
        "missing": missing,
        "inference": "none",
    }


def _run_path(root: Path, mission_id: str, change_id: str) -> Path:
    path = root / ".keel/mission" / mission_id / "runs" / f"{change_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _isolated_worktree(root: Path, mission_id: str, change_id: str, commit: str) -> Path:
    target = Path(tempfile.mkdtemp(prefix=f"keel-{mission_id}-{change_id}-", dir=str(root.parent)))
    target.rmdir()
    keel_core.worktree_create(root, f"{mission_id}-{change_id}", str(target), commit=commit)
    return target


def _child_contract(root: Path, change_id: str) -> dict:
    ledger = root / ".keel/ledger" / change_id
    state_path = ledger / "state.json"
    if not state_path.is_file():
        raise BoundaryViolation(f"child Change ledger is required: {change_id}")
    state = keel_core.read_json(state_path)
    if state.get("change_id") != change_id:
        raise BoundaryViolation(f"child ledger identity mismatch: {change_id}")
    if state.get("phase") not in {"EXECUTE", "VERIFY", "SHIP"}:
        raise BoundaryViolation(f"child Change is not executable: {change_id}")
    return state


def _validate_execution_result(root: Path, change_id: str, result: dict) -> None:
    if not isinstance(result, dict):
        raise BoundaryViolation(f"child executor returned a non-object result: {change_id}")
    if result.get("authorization_granted") or result.get("seal") or result.get("fabricated_evidence"):
        raise BoundaryViolation(f"mission executor attempted a Change-owned operation: {change_id}")
    if result.get("verification_status") == "FAIL" or result.get("integration") not in {None, "NOT_PERFORMED"}:
        raise BoundaryViolation(f"mission executor supplied invalid verification/integration state: {change_id}")
    scope_path = root / ".keel/ledger" / change_id / "scope.txt"
    if result.get("changed_paths") and scope_path.is_file():
        patterns = keel_core.parse_scope(scope_path)
        outside = [path for path in result["changed_paths"] if not keel_core.scope_match(path, patterns)]
        if outside:
            raise BoundaryViolation(f"child result escaped declared scope: {','.join(outside)}")
    if result.get("commit"):
        current = keel_core.head_commit(root)
        if result["commit"] != current:
            raise BoundaryViolation("child result substituted a different Git state")


def _validate_verification_result(root: Path, change_id: str, result: dict) -> None:
    if not isinstance(result, dict) or result.get("status") not in {"PASS", "SHIP", "VERIFIED"}:
        raise BoundaryViolation(f"authoritative child verification did not pass: {change_id}")
    _validate_execution_result(root, change_id, result)


def dispatch(root: Path, mission: dict) -> dict:
    """Shared dispatch surface; planning never becomes a second policy authority."""
    errors = mission_graph.validate(mission)
    if errors:
        return {"schema_version": 1, "status": "INVALID", "errors": errors}
    result = mission_graph.dispatch_plan(root, mission)
    result["dispatch_policy"] = "shared-mission-runtime"
    for contract in result.get("dispatch", []):
        contract["execution"] = "READY"
    return result


def run(
    root: Path,
    mission: dict,
    *,
    executor: Callable[[Path, str, dict], dict] | None = None,
    max_retries: int = 0,
) -> dict:
    """Execute the runnable frontier through ordinary child Change ledgers.

    An embedding provider may supply ``executor``. The CLI uses the built-in
    verifier for already-created child Changes; it never accepts mission-owned
    commands or grants effects.
    """
    errors = mission_graph.validate(mission)
    if errors:
        return {"schema_version": 1, "status": "INVALID", "errors": errors}
    if not isinstance(max_retries, int) or not 0 <= max_retries <= 3:
        return {"schema_version": 1, "status": "INVALID", "errors": ["max_retries must be between 0 and 3"]}
    handshake = capability_handshake(root)
    if handshake["status"] != "READY":
        return {"schema_version": 1, "status": "BLOCKED", "reason": "runtime-capability-missing", "capabilities": handshake}
    frontier = mission_graph.plan(root, mission)
    if frontier["status"] == "INVALID":
        return frontier
    results = []
    targets = list(frontier["runnable"])
    targets.extend(node for node, status in frontier["statuses"].items() if status in {"EXECUTE", "VERIFY"} and node not in targets)
    for change_id in targets:
        state = _child_contract(root, change_id)
        isolated_root = _isolated_worktree(root, mission["mission_id"], change_id, keel_core.head_commit(root))
        run_path = _run_path(root, mission["mission_id"], change_id)
        attempts = 0
        result = None
        boundary_failure = False
        while attempts <= max_retries:
            attempts += 1
            try:
                if executor is None:
                    result = keel_core.verify_change(isolated_root, change_id)
                else:
                    execution_result = executor(isolated_root, change_id, state)
                    _validate_execution_result(isolated_root, change_id, execution_result)
                    result = keel_core.verify_change(isolated_root, change_id)
                _validate_verification_result(isolated_root, change_id, result)
                break
            except Exception as exc:
                boundary_failure = isinstance(exc, BoundaryViolation)
                result = {"status": "FAILED", "error": str(exc)}
                if attempts > max_retries:
                    break
        record = {"schema_version": 1, "mission_id": mission["mission_id"], "change_id": change_id, "attempts": attempts, "status": result.get("status"), "integration": "NOT_PERFORMED", "isolation": "dedicated-worktree", "result": result}
        try:
            if not boundary_failure:
                run_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            results.append(record)
        finally:
            keel_core.worktree_retire(root, str(isolated_root), force=True)
    return {"schema_version": 1, "status": "PASS" if all(row["status"] in {"PASS", "SHIP", "VERIFIED"} for row in results) else "FAILED", "mission_id": mission["mission_id"], "results": results, "integration": "NOT_PERFORMED"}


def integrate(root: Path, mission_id: str, change_id: str) -> dict:
    """Refuse integration unless a separate authorized integration path exists."""
    path = _run_path(root, mission_id, change_id)
    if not path.is_file():
        raise BoundaryViolation("mission run evidence is required before integration")
    record = keel_core.read_json(path)
    if record.get("status") not in {"PASS", "SHIP", "VERIFIED"}:
        raise BoundaryViolation("only a verified child Change may be integrated")
    raise BoundaryViolation("mission runtime cannot grant integration authorization")
