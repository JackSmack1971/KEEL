import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import schema_migrations as sm

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); keel = root / ".keel"; keel.mkdir(); path = keel / "config.json"
    legacy = {"schema_version": 1, "capability_resolver": {"ignore_dirs": []}}
    path.write_text(json.dumps(legacy), encoding="utf-8")
    before = path.read_bytes()
    plan = sm.preflight(path)
    assert plan["status"] == "READY" and plan["read_only"] is True and path.read_bytes() == before
    result = sm.apply(path, root / "backup")
    assert result["status"] == "APPLIED" and json.loads(path.read_text())["schema_version"] == 2
    assert Path(result["backup"]).read_bytes() == before
    restored = sm.rollback(path, Path(result["backup"]))
    assert restored["status"] == "ROLLED_BACK" and path.read_bytes() == before
    path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
    try:
        sm.preflight(path)
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported schema was accepted")
    path.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
    assert sm.preflight(path)["status"] == "CURRENT"
print(json.dumps({"status": "PASS", "checks": ["preflight", "atomic-apply", "backup", "rollback", "unsupported-version"]}))
