import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import telemetry

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); path = root / "verification.json"
    path.write_text(json.dumps({"status": "PASS", "checks": [{"id": "a", "exit_code": 0, "duration_ms": 12}, {"id": "b", "exit_code": 1, "duration_ms": 8}]}), encoding="utf-8")
    before = path.read_bytes(); result = telemetry.summarize(path)
    assert result["status"] == "PASS" and result["metrics"]["wall_time_ms"]["value"] == 20
    assert result["metrics"]["checks_failed"]["value"] == 1 and result["metrics"]["cost"]["status"] == "UNAVAILABLE"
    assert path.read_bytes() == before
    assert telemetry.summarize(root / "missing.json")["status"] == "UNAVAILABLE"
    runtime = root / "runtime.json"
    runtime.write_text(json.dumps({"metrics": {"tokens": 42, "retries": 2}}), encoding="utf-8")
    measured = telemetry.summarize(path, runtime)
    assert measured["metrics"]["tokens"]["value"] == 42 and measured["metrics"]["retries"]["value"] == 2
    assert measured["metrics"]["cost"]["status"] == "UNAVAILABLE"
print(json.dumps({"status": "PASS", "checks": ["aggregation", "unavailable-metrics", "missing-input", "read-only"]}))
