from __future__ import annotations

import json
import re
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
STATES = {"OBSERVED", "REVIEWED", "EVALUATED", "PROMOTED"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _repo_path(root: Path, value: str) -> Path | None:
    target = (root / value).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def validate_observation(root: Path, observation: dict) -> list[str]:
    errors = []
    if not isinstance(observation, dict):
        return ["observation must be an object"]
    if observation.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(observation.get("observation_id"), str) or not ID_RE.fullmatch(observation.get("observation_id", "")):
        errors.append("observation_id must be a valid lowercase identifier")
    for key in ("source", "observed_at", "summary", "failure_class"):
        if not isinstance(observation.get(key), str) or not observation.get(key, "").strip():
            errors.append(f"{key} must be a non-empty string")
    state = observation.get("state")
    if state not in STATES:
        errors.append("state must be OBSERVED|REVIEWED|EVALUATED|PROMOTED")
    evidence = observation.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for item in evidence:
            if not isinstance(item, str) or not item.strip():
                errors.append("evidence entries must be non-empty paths")
            elif _repo_path(root, item) is None or not _repo_path(root, item).is_file():
                errors.append(f"evidence path is missing or outside repository: {item}")
    if state in {"REVIEWED", "EVALUATED", "PROMOTED"}:
        for key in ("reviewer", "reviewed_at"):
            if not isinstance(observation.get(key), str) or not observation.get(key, "").strip():
                errors.append(f"{key} is required for state {state}")
    if state in {"EVALUATED", "PROMOTED"} and (not isinstance(observation.get("evaluation_reference"), str) or not observation.get("evaluation_reference", "").strip()):
        errors.append(f"evaluation_reference is required for state {state}")
    if state == "PROMOTED" and (not isinstance(observation.get("promotion_change_id"), str) or not ID_RE.fullmatch(observation.get("promotion_change_id", ""))):
        errors.append("promotion_change_id is required for state PROMOTED")
    return sorted(set(errors))


def status(root: Path, observation: dict) -> dict:
    errors = validate_observation(root, observation)
    state = observation.get("state") if isinstance(observation, dict) else None
    return {"schema_version": 1, "status": "INVALID" if errors else "PASS", "observation_id": observation.get("observation_id") if isinstance(observation, dict) else None, "state": state, "eligible_for_evaluation": not errors and state == "REVIEWED", "eligible_for_promotion": not errors and state == "EVALUATED", "errors": errors}


def entropy_scan(root: Path) -> dict:
    findings = []
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "node_modules", "dist", "build", "target", ".venv", "venv"} for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in LINK_RE.findall(text):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = (path.parent / target.split("#", 1)[0]).resolve()
            try:
                target_path.relative_to(root.resolve())
            except ValueError:
                findings.append({"kind": "broken-link", "path": path.relative_to(root).as_posix(), "target": target})
                continue
            if target and not target_path.exists():
                findings.append({"kind": "broken-link", "path": path.relative_to(root).as_posix(), "target": target})
    active = root / "docs" / "exec-plans" / "active"
    if active.is_dir():
        for path in sorted(active.glob("*.md")):
            if path.name == "README.md":
                continue
            ledger = root / ".keel" / "ledger" / path.stem / "state.json"
            if not ledger.is_file():
                findings.append({"kind": "orphaned-active-plan", "path": path.relative_to(root).as_posix(), "target": f".keel/ledger/{path.stem}/state.json"})
    if not (root / ".keel" / "knowledge" / "repository-map.json").is_file():
        findings.append({"kind": "missing-derived-map", "path": ".keel/knowledge/repository-map.json", "target": "keel map"})
    findings.sort(key=lambda row: (row["kind"], row["path"], row["target"]))
    return {"schema_version": 1, "status": "PASS", "read_only": True, "finding_count": len(findings), "findings": findings}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
