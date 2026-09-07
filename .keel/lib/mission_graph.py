from __future__ import annotations

import json
import re
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
RISKS = {"trivial", "standard", "high"}
TERMINAL = {"LANDED"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(mission: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(mission, dict):
        return ["mission must be an object"]
    if mission.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(mission.get("mission_id"), str) or not ID_RE.fullmatch(mission.get("mission_id", "")):
        errors.append("mission_id must be a valid lowercase identifier")
    if not isinstance(mission.get("objective"), str) or not mission.get("objective", "").strip():
        errors.append("objective must be a non-empty string")
    if not isinstance(mission.get("success_criteria"), list) or not mission.get("success_criteria") or not all(isinstance(x, str) and x.strip() for x in mission.get("success_criteria", [])):
        errors.append("success_criteria must be a non-empty list of strings")
    work = mission.get("work")
    if not isinstance(work, dict) or not work:
        errors.append("work must be a non-empty object")
        return errors
    for key, item in work.items():
        if not isinstance(key, str) or not ID_RE.fullmatch(key):
            errors.append(f"invalid work change id: {key!r}")
            continue
        if not isinstance(item, dict):
            errors.append(f"work.{key} must be an object")
            continue
        if item.get("risk") not in RISKS:
            errors.append(f"work.{key}.risk must be trivial|standard|high")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(dep, str) or not ID_RE.fullmatch(dep) for dep in deps):
            errors.append(f"work.{key}.depends_on must be a list of valid identifiers")
            continue
        if len(deps) != len(set(deps)):
            errors.append(f"work.{key}.depends_on contains duplicates")
        if key in deps:
            errors.append(f"work.{key} cannot depend on itself")
        for dep in deps:
            if dep not in work:
                errors.append(f"work.{key} depends on missing node {dep}")
    if errors:
        return sorted(set(errors))
    visiting, visited = set(), set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"dependency cycle includes {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in mission["work"][node].get("depends_on", []):
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(work):
        visit(node)
    return sorted(set(errors))


def child_status(root: Path, change_id: str) -> str:
    import keel_core

    ledger = root / ".keel" / "ledger" / change_id
    state = ledger / "state.json"
    if not state.is_file():
        return "NOT_STARTED"
    phase = json.loads(state.read_text(encoding="utf-8")).get("phase", "UNKNOWN")
    landed = keel_core.run_git(root, ["show-ref", "--hash", "--verify", f"refs/keel/ledger/{change_id}"], check=False)
    if landed.returncode == 0:
        return "LANDED"
    candidate = keel_core.run_git(root, ["show-ref", "--hash", "--verify", f"refs/keel/candidates/{change_id}"], check=False)
    if candidate.returncode == 0 and phase == "SHIP":
        return "SHIP"
    return str(phase)


def plan(root: Path, mission: dict) -> dict:
    errors = validate(mission)
    if errors:
        return {"schema_version": 1, "status": "INVALID", "errors": errors}
    work = mission["work"]
    statuses = {node: child_status(root, node) for node in sorted(work)}
    landed = {node for node, status in statuses.items() if status in TERMINAL}
    runnable = [node for node in sorted(work) if statuses[node] == "NOT_STARTED" and all(dep in landed for dep in work[node].get("depends_on", []))]
    blocked = [node for node in sorted(work) if statuses[node] == "NOT_STARTED" and node not in runnable]
    in_progress = [node for node, status in statuses.items() if status not in {"NOT_STARTED", "LANDED"}]
    complete = len(landed) == len(work)
    state = "COMPLETE" if complete else "READY" if runnable else "IN_PROGRESS" if in_progress else "BLOCKED"
    return {"schema_version": 1, "status": state, "mission_id": mission["mission_id"], "statuses": statuses, "runnable": runnable, "blocked": blocked, "in_progress": in_progress, "landed": sorted(landed), "errors": []}
