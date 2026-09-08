from __future__ import annotations

import json
import re
import canonical_ledger
from pathlib import Path

SUPPORTED = {"framework": "0.1.0", "config_schema": 2, "contract_schema": 1, "ledger_schema": 1, "skill_schema": 1, "bootstrap_manifest_schema": 2}
SUPPORTED_EVIDENCE_PROVIDERS = {"command", "unit_test", "browser", "visual", "log_query", "metric_query", "trace_query", "schema", "security", "benchmark", "hardware", "human_review", "external_ci", "changed_path"}
SUPPORTED_EFFECT_CAPABILITIES = {"filesystem.write", "git.local.commit", "git.remote.push", "vcs.merge", "package.publish", "database.migrate", "cloud.deploy", "infra.apply", "issue.modify", "email.send", "secret.read"}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path) -> dict:
    findings, skills, ledgers = [], [], []
    config = _json(root / ".keel/config.json")
    contracts = _json(root / ".keel/contracts.json")
    manifest = _json(root / ".keel/bootstrap-manifest.json")
    if config.get("schema_version") != SUPPORTED["config_schema"]:
        findings.append({"kind": "config-schema", "path": ".keel/config.json", "expected": SUPPORTED["config_schema"], "actual": config.get("schema_version"), "action": "run a versioned KEEL config migration"})
    if contracts.get("schema_version") != SUPPORTED["contract_schema"]:
        findings.append({"kind": "contract-schema", "path": ".keel/contracts.json", "expected": SUPPORTED["contract_schema"], "actual": contracts.get("schema_version"), "action": "run a versioned contract migration"})
    if manifest.get("schema_version") != SUPPORTED["bootstrap_manifest_schema"]:
        findings.append({"kind": "manifest-schema", "path": ".keel/bootstrap-manifest.json", "expected": SUPPORTED["bootstrap_manifest_schema"], "actual": manifest.get("schema_version"), "action": "regenerate or migrate the bootstrap manifest"})
    ledger_root = root / ".keel/ledger"
    if ledger_root.is_dir():
        ledger_dirs = sorted({p.parent for p in ledger_root.glob("*/state.json")} | {p.parent for p in ledger_root.glob("*/intent.json")})
        for directory in ledger_dirs:
            if (directory / "intent.json").is_file():
                intent=canonical_ledger.load_intent(directory); canonical_ledger.read_events(directory); row={"change_id":intent["change_id"],"schema_version":2,"phase":canonical_ledger.phase(directory),"reader":"canonical"}; ledgers.append(row); continue
            state_path=directory / "state.json"
            state = _json(state_path); row = {"change_id": state_path.parent.name, "schema_version": state.get("schema_version"), "phase": state.get("phase"), "reader":"keel.legacy-ledger/v1"}; ledgers.append(row)
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


def contract_report(root: Path) -> dict:
    """Validate the canonical contract vocabulary without a second upgrade kernel."""
    data = _json(root / ".keel/contracts.json")
    providers, effects = data.get("evidence_providers", []), data.get("effect_capabilities", [])
    errors = []
    if not isinstance(providers, list) or any(item not in SUPPORTED_EVIDENCE_PROVIDERS for item in providers):
        errors.append("contracts.evidence_providers contains an unsupported provider")
    if not isinstance(effects, list) or any(item not in SUPPORTED_EFFECT_CAPABILITIES for item in effects):
        errors.append("contracts.effect_capabilities contains an unsupported capability")
    return {"schema_version": 1, "status": "PASS" if not errors else "FAIL", "evidence_providers": providers, "effect_capabilities": effects, "errors": errors}


def version_report(root: Path) -> dict:
    """Report the single supported kernel and repository compatibility envelope."""
    config = _json(root / ".keel/config.json")
    contracts = contract_report(root)
    repository = inventory(root)
    compatible = config.get("schema_version") == SUPPORTED["config_schema"] and contracts["status"] == "PASS" and repository["status"] == "COMPATIBLE"
    return {"framework": "KEEL", "framework_version": SUPPORTED["framework"], "supported_config_schema": [SUPPORTED["config_schema"]], "config_schema": config.get("schema_version"), "contract_schema": contracts["schema_version"], "compatibility": "COMPATIBLE" if compatible else "INCOMPATIBLE", "lifecycle": repository, "errors": [] if compatible else ["repository metadata is outside the supported KEEL compatibility envelope"] + contracts["errors"]}


def reconcile(root: Path, change_id: str | None = None) -> dict:
    """Compose canonical read-only lifecycle queries; never repair or mutate state."""
    import keel_core
    cid = change_id or keel_core.active_change(root)
    version = version_report(root)
    contracts = contract_report(root)
    result = {"schema_version": 1, "change_id": cid, "read_only": True, "git": {"head": keel_core.head_commit(root), "status_short": keel_core.run_git(root, ["status", "--short"], check=True).stdout.splitlines()}, "ledger": keel_core.status_summary(root, cid) if cid else None, "environment": keel_core.environment_contract(root), "next": keel_core.next_action(root, cid), "version": version, "contracts": contracts}
    result["status"] = "PASS" if version["compatibility"] == "COMPATIBLE" and contracts["status"] == "PASS" else "FAIL"
    return result
