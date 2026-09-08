import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import topology_router

mission = json.loads((ROOT / ".keel/tests/fixtures/mission-v2/v1.json").read_text())
before = json.dumps(mission, sort_keys=True)
result = topology_router.recommend(mission)
assert result["status"] == "PASS" and result["read_only"] is True
assert result["policy"] == "read-only-constraints-no-scheduling"
b = result["constraints"]["keel:work-unit:legacy.b"]
assert b["hard_dependencies"] == ["keel:work-unit:legacy.a"]
assert not ({"roles", "agent", "model", "effort", "schedule", "dispatch", "complexity"} & set(json.dumps(result).lower().replace('"', '').split()))
assert json.dumps(mission, sort_keys=True) == before
assert topology_router.recommend(mission, "missing")["status"] == "INVALID"
print(json.dumps({"status": "PASS", "checks": ["canonical-adapter", "constraints-only", "deterministic", "read-only"]}))
