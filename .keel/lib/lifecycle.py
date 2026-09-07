from __future__ import annotations

import json
import re
from pathlib import Path

SUPPORTED = {"framework": "0.1.0", "config_schema": 2, "contract_schema": 1, "ledger_schema": 1, "skill_schema": 1, "bootstrap_manifest_schema": 2}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path) -> dict:
    findings, skills, ledgers = [], [], []
    config = _json(root / ".keel/config.json")
    contracts = _json(root / ".keel/contracts.json")
    manifest = _json(root / ".control-plane/bootstrap-manifest.json")
    if config.get("schema_version") != SUPPORTED["config_schema"]:
        findings.append({"kind": "config-schema", "path": ".keel/config.json", "expected": SUPPORTED["config_schema"], "actual": config.get("schema_version"), "action": "run a versioned KEEL config migration"})
    if contracts.get("schema_version") != SUPPORTED["contract_schema"]:
        findings.append({"kind": "contract-schema", "path": ".keel/contracts.json", "expected": SUPPORTED["contract_schema"], "actual": contracts.get("schema_version"), "action": "run a versioned contract migration"})
    if manifest.get("schema_version") != SUPPORTED["bootstrap_manifest_schema"]:
        findings.append({"kind": "manifest-schema", "path": ".control-plane/bootstrap-manifest.json", "expected": SUPPORTED["bootstrap_manifest_schema"], "actual": manifest.get("schema_version"), "action": "regenerate or migrate the bootstrap manifest"})
    ledger_root = root / ".keel/ledger"
    if ledger_root.is_dir():
        for state_path in sorted(ledger_root.glob("*/state.json")):
            state = _json(state_path); row = {"change_id": state_path.parent.name, "schema_version": state.get("schema_version"), "phase": state.get("phase")}; ledgers.append(row)
            if state.get("schema_version") != SUPPORTED["ledger_schema"]:
                findings.append({"kind": "ledger-schema", "path": state_path.relative_to(root).as_posix(), "expected": SUPPORTED["ledger_schema"], "actual": state.get("schema_version"), "action": "migrate this ledger under a dedicated KEEL change"})
    for skill_path in sorted((root / ".agents/skills").glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(?ms)^---\s*.*?^metadata:\s*\n(?:^[ \t]+.*\n)*?^[ \t]+version:\s*[\"']?([^\"'\s]+)", text)
        version = match.group(1) if match else "UNVERSIONED"
        row = {"skill": skill_path.parent.name, "version": version}; skills.append(row)
        if version != str(SUPPORTED["skill_schema"]):
            findings.append({"kind": "skill-version", "path": skill_path.relative_to(root).as_posix(), "expected": str(SUPPORTED["skill_schema"]), "actual": version, "action": "add or migrate the skill version metadata"})
    findings.sort(key=lambda row: (row["kind"], row["path"]))
    return {"schema_version": 1, "status": "COMPATIBLE" if not findings else "MIGRATION_REQUIRED", "supported": SUPPORTED, "repository": {"framework": SUPPORTED["framework"], "config_schema": config.get("schema_version"), "contract_schema": contracts.get("schema_version"), "bootstrap_manifest_schema": manifest.get("schema_version")}, "ledgers": ledgers, "skills": skills, "external": {"codex_version": "UNVERIFIED", "runtime_hooks": "UNVERIFIED"}, "findings": findings, "read_only": True}


def adoption_plan(root: Path) -> dict:
    """Classify a clean, existing, or incomplete repository without mutating it."""
    markers = {
        "config": (root / ".keel/config.json").is_file(),
        "contracts": (root / ".keel/contracts.json").is_file(),
        "manifest": (root / ".control-plane/bootstrap-manifest.json").is_file(),
    }
    if all(markers.values()):
        status, action = "EXISTING", "ADOPT"
    elif not any(markers.values()):
        status, action = "CLEAN", "BOOTSTRAP"
    else:
        status, action = "INCOMPLETE", "REPAIR"
    return {"schema_version": 1, "status": status, "action": action, "markers": markers, "read_only": True, "mutation": "NONE", "external": {"codex_version": "UNKNOWN", "runtime_hooks": "UNKNOWN"}}


def upgrade_plan(root: Path) -> dict:
    """Return a deterministic upgrade/migration plan; never applies it implicitly."""
    compatibility = inventory(root)
    return {"schema_version": 1, "status": "CURRENT" if compatibility["status"] == "COMPATIBLE" else "READY", "read_only": True, "mutation": "NONE", "compatibility": compatibility, "actions": [] if compatibility["status"] == "COMPATIBLE" else [row["action"] for row in compatibility["findings"]]}
