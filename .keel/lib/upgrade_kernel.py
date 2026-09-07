from __future__ import annotations

import json
from pathlib import Path
import lifecycle

FRAMEWORK_VERSION = "0.1.0"
SUPPORTED_EVIDENCE_PROVIDERS = {"command", "unit_test", "browser", "visual", "log_query", "metric_query", "trace_query", "schema", "security", "benchmark", "hardware", "human_review", "external_ci", "changed_path"}
SUPPORTED_EFFECT_CAPABILITIES = {"filesystem.write", "git.local.commit", "git.remote.push", "vcs.merge", "package.publish", "database.migrate", "cloud.deploy", "infra.apply", "issue.modify", "email.send", "secret.read"}

def contract_report(root: Path) -> dict:
    path = root / ".keel" / "contracts.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    providers, effects = data.get("evidence_providers", []), data.get("effect_capabilities", [])
    errors = []
    if not isinstance(providers, list) or any(x not in SUPPORTED_EVIDENCE_PROVIDERS for x in providers): errors.append("contracts.evidence_providers contains an unsupported provider")
    if not isinstance(effects, list) or any(x not in SUPPORTED_EFFECT_CAPABILITIES for x in effects): errors.append("contracts.effect_capabilities contains an unsupported capability")
    return {"schema_version": 1, "status": "PASS" if not errors else "FAIL", "evidence_providers": providers, "effect_capabilities": effects, "errors": errors}

def version_report(root: Path) -> dict:
    config = json.loads((root / ".keel" / "config.json").read_text(encoding="utf-8"))
    contracts = contract_report(root)
    compatible = config.get("schema_version") == 2 and contracts["status"] == "PASS"
    from lifecycle import inventory
    life = inventory(root)
    return {"framework": "KEEL", "framework_version": FRAMEWORK_VERSION, "supported_config_schema": [2], "config_schema": config.get("schema_version"), "contract_schema": contracts["schema_version"], "compatibility": "COMPATIBLE" if compatible and life["status"] == "COMPATIBLE" else "INCOMPATIBLE", "lifecycle": life, "adoption": lifecycle.adoption_plan(root), "upgrade": lifecycle.upgrade_plan(root), "errors": ([] if compatible and life["status"] == "COMPATIBLE" else ["repository metadata is outside the supported KEEL compatibility envelope"]) + contracts["errors"]}

def reconcile(root: Path, change_id: str | None = None) -> dict:
    import keel_core
    cid = change_id or keel_core.active_change(root)
    git = keel_core.run_git(root, ["status", "--short"], check=True)
    version = version_report(root)
    contracts = contract_report(root)
    result = {"schema_version": 1, "change_id": cid, "read_only": True, "git": {"head": keel_core.head_commit(root), "status_short": git.stdout.splitlines()}, "ledger": keel_core.status_summary(root, cid) if cid else None, "environment": keel_core.environment_contract(root), "next": keel_core.next_action(root, cid), "version": version, "contracts": contracts}
    result["status"] = "PASS" if version["compatibility"] == "COMPATIBLE" and contracts["status"] == "PASS" else "FAIL"
    return result
