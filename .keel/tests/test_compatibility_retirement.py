"""Mechanical M6 guard: one kernel path, narrow legacy-ledger compatibility."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

retired = [
    ".control-plane",
    ".keel/lib/mission_graph.py",
    ".keel/lib/mission_v2.py",
    ".keel/lib/topology_router.py",
    ".keel/lib/repository_map.py",
    ".keel/lib/repository_intelligence.py",
    ".keel/lib/developer_ux.py",
    ".keel/lib/upgrade_kernel.py",
    ".keel/lib/feedback_entropy.py",
    ".keel/templates/acceptance.json",
    ".keel/templates/authorization.json",
    ".keel/templates/proposal.md",
    "plans/findings.json",
]
assert all(not (ROOT / path).exists() for path in retired)

cli_source = (ROOT / ".keel/bin/keel.py").read_text()
for obsolete in ("mission", "mission-v2", "route", "map", "feedback", "entropy", "init", "review", "ship"):
    assert f'add_parser("{obsolete}")' not in cli_source
for canonical in ("change-graph", "facts", "ledger", "verify", "seal", "anchor"):
    assert f'add_parser("{canonical}")' in cli_source

manifest = json.loads((ROOT / ".keel/bootstrap-manifest.json").read_text())
assert manifest["producer"]["source"] == ".keel/lib/p0_contract.py"
assert all(not path.startswith(".control-plane/") for path in manifest["files"])
assert ".keel/lib/fact_graph.py" in manifest["files"]

assert (ROOT / ".keel/maintenance/feedback_entropy.py").is_file()
assert "not part of the KEEL kernel" in (ROOT / ".keel/maintenance/README.md").read_text()
for name in ("FRONTEND.md", "RELIABILITY.md", "SECURITY.md", "RELEASE.md"):
    assert "Non-authoritative target-project template" in (ROOT / "policies/templates" / name).read_text()

for role in ("explorer.toml", "reviewer.toml", "risk-reviewer.toml"):
    assert (ROOT / ".codex/agents" / role).is_file()
for module in ("candidate_attestation.py", "git_proof.py", "canonical_ledger.py", "runtime_authorization.py"):
    assert (ROOT / ".keel/lib" / module).is_file()

ledger_source = (ROOT / ".keel/lib/canonical_ledger.py").read_text()
assert "keel.legacy-ledger/v1" in ledger_source
assert "preserved_legacy" in ledger_source
core_source = (ROOT / ".keel/lib/keel_core.py").read_text()
anchor_source = core_source.split("def anchor(", 1)[1].split("def discover_capabilities", 1)[0]
assert "verify_commit_tree" in anchor_source
assert 'show_commit_json(root, sha, change_id, "state.json")' not in anchor_source

print(json.dumps({"status": "PASS", "checks": ["retired-paths", "single-cli", "canonical-manifest", "optional-maintenance", "policy-packs", "protected-invariants", "legacy-ledger-reader"]}))
