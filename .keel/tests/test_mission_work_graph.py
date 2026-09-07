import copy
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import mission_graph

BASE = {"schema_version": 1, "mission_id": "checkout-v2", "objective": "Deliver checkout v2", "success_criteria": ["Existing checkout remains usable"], "work": {"contract": {"risk": "standard", "depends_on": []}, "backend": {"risk": "standard", "depends_on": ["contract"]}, "frontend": {"risk": "standard", "depends_on": ["contract"]}, "cutover": {"risk": "high", "depends_on": ["backend", "frontend"]}}}
assert mission_graph.validate(BASE) == []
cycle = copy.deepcopy(BASE); cycle["work"]["contract"]["depends_on"] = ["cutover"]
assert any("cycle" in error for error in mission_graph.validate(cycle))
missing = copy.deepcopy(BASE); missing["work"]["backend"]["depends_on"] = ["absent"]
assert any("missing node" in error for error in mission_graph.validate(missing))
result = mission_graph.plan(ROOT, BASE)
assert result["status"] == "READY" and result["runnable"] == ["contract"]
assert result["statuses"] == {"backend": "NOT_STARTED", "contract": "NOT_STARTED", "cutover": "NOT_STARTED", "frontend": "NOT_STARTED"}
dispatch = mission_graph.dispatch_plan(ROOT, BASE)
assert dispatch["dispatch"][0]["change_id"] == "contract"
assert dispatch["dispatch"][0]["isolation"] == "dedicated-worktree"
invalid = copy.deepcopy(BASE); invalid["work"]["contract"]["depends_on"] = ["cutover"]
assert mission_graph.dispatch_plan(ROOT, invalid)["status"] == "INVALID"
before = json.dumps(BASE, sort_keys=True)
mission_graph.plan(ROOT, BASE)
assert json.dumps(BASE, sort_keys=True) == before
print(json.dumps({"status": "PASS", "checks": ["schema", "cycle", "frontier", "dispatch-contract", "read-only"]}))
