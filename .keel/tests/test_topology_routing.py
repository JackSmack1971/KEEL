import copy
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import topology_router
mission = {"schema_version": 1, "mission_id": "routing", "objective": "Route work", "success_criteria": ["stable"], "work": {"tiny": {"risk": "trivial", "depends_on": []}, "normal": {"risk": "standard", "depends_on": []}, "complex": {"risk": "standard", "depends_on": ["tiny", "normal"]}, "critical": {"risk": "high", "depends_on": ["tiny", "normal", "complex"]}}}
before = json.dumps(mission, sort_keys=True)
result = topology_router.recommend(mission)
assert result["status"] == "PASS"
assert result["recommendations"]["tiny"]["complexity"] == "trivial"
assert result["recommendations"]["normal"]["effort_capability"] == "balanced"
assert result["recommendations"]["complex"]["complexity"] == "complex"
assert result["recommendations"]["critical"]["complexity"] == "critical"
assert all("model" not in json.dumps(row).lower() for row in result["recommendations"].values())
assert json.dumps(mission, sort_keys=True) == before
invalid = copy.deepcopy(mission); invalid["work"]["tiny"]["risk"] = "unknown"
assert topology_router.recommend(invalid)["status"] == "INVALID"
print(json.dumps({"status": "PASS", "checks": ["complexity", "capability-only", "deterministic", "read-only"]}))
