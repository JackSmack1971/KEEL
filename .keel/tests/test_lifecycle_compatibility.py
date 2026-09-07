import json
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import lifecycle

result = lifecycle.inventory(ROOT)
assert result["status"] == "COMPATIBLE"
assert result["external"]["codex_version"] == "UNVERIFIED"
assert {"framework", "config_schema", "contract_schema", "ledger_schema", "skill_schema", "bootstrap_manifest_schema"} <= set(result["supported"])
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); (root / ".keel/ledger/example").mkdir(parents=True); (root / ".keel/config.json").parent.mkdir(parents=True, exist_ok=True)
    for path, value in ((root / ".keel/config.json", {"schema_version": 99}), (root / ".keel/contracts.json", {"schema_version": 1}), (root / ".control-plane/bootstrap-manifest.json", {"schema_version": 2}), (root / ".keel/ledger/example/state.json", {"schema_version": 7, "phase": "EXECUTE"})):
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value), encoding="utf-8")
    (root / ".agents/skills/foo").mkdir(parents=True); (root / ".agents/skills/foo/SKILL.md").write_text("---\nname: foo\n---\n", encoding="utf-8")
    before = json.dumps((root / ".keel/ledger/example/state.json").read_bytes().decode(), sort_keys=True)
    stale = lifecycle.inventory(root)
    assert stale["status"] == "MIGRATION_REQUIRED" and stale["findings"]
    assert json.dumps((root / ".keel/ledger/example/state.json").read_bytes().decode(), sort_keys=True) == before
print(json.dumps({"status": "PASS", "checks": ["version-inventory", "stale-detection", "migration-plan", "read-only"]}))
