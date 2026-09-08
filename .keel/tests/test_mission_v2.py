"""Minimal mission-v2 compatibility proof; ChangeGraph tests own semantics."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import change_graph as cg
import mission_v2

source = json.loads((ROOT / ".keel/tests/fixtures/mission-v2/valid.json").read_text())
first = mission_v2.normalize(source)
second = mission_v2.normalize(json.loads(json.dumps(source)))
assert cg.serialize(first) == cg.serialize(second)
assert mission_v2.validate(source)["status"] == "VALID"
assert mission_v2.frontier(source)["read_only"] is True
assert first["provenance"]["source_schema"] == "keel.mission/v2"
assert first["uncertainty"]
assert not any(record["kind"] in {"capability-grant", "runtime-profile"} for record in first["records"])
assert "authorizations" in " ".join(first["uncertainty"])
print(json.dumps({"status": "PASS", "checks": ["v2-adapter", "determinism", "uncertainty", "no-invented-authority"]}, sort_keys=True))
