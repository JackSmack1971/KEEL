import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import mission_v2


FIX = ROOT / ".keel/tests/fixtures/mission-v2"
valid = json.loads((FIX / "valid.json").read_text(encoding="utf-8"))
oracle = json.loads((FIX / "oracle.json").read_text(encoding="utf-8"))


def codes(result):
    return {item["code"] for item in result.get("errors", [])}


assert mission_v2.validate(valid, ROOT)["status"] == oracle["valid_status"]
assert mission_v2.frontier(valid)["dependency_ready"] == oracle["frontier_dependency_ready"]
assert mission_v2.frontier(valid)["capability_ready"] == oracle["frontier_capability_ready"]
assert mission_v2.frontier(valid)["executable"] is oracle["frontier_executable"]
first = mission_v2.serialize(valid)
assert first == mission_v2.serialize(json.loads(first))
assert "timestamp" not in first and "hostname" not in first and "process_id" not in first


def invalid_with(mutator):
    case = copy.deepcopy(valid)
    mutator(case)
    return mission_v2.validate(case, ROOT)


cycle = invalid_with(lambda m: m["dependencies"].append({"from": "contract", "to": "backend", "type": "HARD_PREREQUISITE"}))
assert oracle["cycle_code"] in codes(cycle)
missing = invalid_with(lambda m: m["dependencies"].append({"from": "backend", "to": "absent", "type": "HARD_PREREQUISITE"}))
assert oracle["missing_code"] in codes(missing)
duplicate = invalid_with(lambda m: m["dependencies"].append({"from": "backend", "to": "contract", "type": "HARD_PREREQUISITE"}))
assert oracle["duplicate_code"] in codes(duplicate)
self_dep = invalid_with(lambda m: m["dependencies"].append({"from": "contract", "to": "contract", "type": "HARD_PREREQUISITE"}))
assert oracle["self_code"] in codes(self_dep)
bad_type = invalid_with(lambda m: m["dependencies"].append({"from": "backend", "to": "contract", "type": "NOPE"}))
assert oracle["type_code"] in codes(bad_type)

conflict = copy.deepcopy(valid)
conflict["nodes"][1]["resources"] = [{"id": "checkout-contract", "exclusive": True}]
assert oracle["resource_code"] in codes(mission_v2.validate(conflict, ROOT))
unsupported = copy.deepcopy(valid)
unsupported["nodes"][0]["capability_state"]["python"] = "UNSUPPORTED"
assert oracle["unsupported_capability_code"] in codes(mission_v2.validate(unsupported, ROOT))
runtime = copy.deepcopy(valid)
runtime["nodes"][0]["capability_state"]["python"] = "RUNTIME_REQUIRED"
assert mission_v2.validate(runtime, ROOT)["status"] == oracle["runtime_capability_status"]
assert mission_v2.frontier(runtime)["runtime_ready"] == []

missing_auth = copy.deepcopy(valid)
missing_auth["nodes"][0]["authorization_refs"] = []
assert oracle["missing_auth_code"] in codes(mission_v2.validate(missing_auth, ROOT))
excess = copy.deepcopy(valid)
excess["authorizations"]["auth-local"]["effects"] = []
assert oracle["excess_auth_code"] in codes(mission_v2.validate(excess, ROOT))
unknown_effect = copy.deepcopy(valid)
unknown_effect["nodes"][0]["allowed_effects"] = ["provider.invoke"]
assert "BLOCKED/UNKNOWN_EFFECT" in codes(mission_v2.validate(unknown_effect, ROOT))

bad_scope = copy.deepcopy(valid); bad_scope["nodes"][0]["scope"] = "../escape"
assert oracle["invalid_scope_code"] in codes(mission_v2.validate(bad_scope, ROOT))
bad_acceptance = copy.deepcopy(valid); bad_acceptance["nodes"][0]["acceptance_criteria"] = []
assert oracle["invalid_acceptance_code"] in codes(mission_v2.validate(bad_acceptance, ROOT))

parent = copy.deepcopy(valid["nodes"][0]); parent["uncertainty"] = ["UNKNOWN: ownership"]
child = copy.deepcopy(valid["nodes"][1]); child["node_id"] = "child"; child["scope"] = "src/other"
assert oracle["child_escape_code"] in {x["code"] for x in mission_v2.decompose(parent, [child], ROOT)["errors"]}
child["scope"] = "src/checkout/child"; child["allowed_effects"] = ["git.local.commit"]
assert oracle["child_effect_code"] in {x["code"] for x in mission_v2.decompose(parent, [child], ROOT)["errors"]}
child["allowed_effects"] = []
decomposed = mission_v2.decompose(parent, [child], ROOT)
assert decomposed["status"] == "VALID" and decomposed["nodes"][0]["uncertainty"] == ["UNKNOWN: ownership"] and decomposed["read_only"] is True

v1 = json.loads((FIX / "v1.json").read_text(encoding="utf-8"))
normalized = mission_v2.normalize_v1(v1)
assert normalized["planning_status"] == oracle["v1_status"]
assert normalized["provenance"]["source_schema"] == oracle["v1_source_schema"]
assert normalized["nodes"][1]["dependencies"] == ["a"]
assert mission_v2.validate(normalized, ROOT)["status"] == "VALID"

assert mission_v2.validate(valid, ROOT, {"status": "CONFLICTING"})["status"] == "BLOCKED"
assert oracle["p1_conflict_code"] in codes(mission_v2.validate(valid, ROOT, {"status": "CONFLICTING"}))
assert oracle["p1_unsupported_code"] in codes(mission_v2.validate(valid, ROOT, {"status": "UNSUPPORTED"}))

# P2 returns planning data only; no dispatcher, executor, worktree, or authorization API exists.
projection = mission_v2.frontier(valid)
assert projection["executable"] is False and "dispatch" not in projection and "authorization_grant" not in projection
print(json.dumps({"status": "PASS", "checks": ["schema", "graph", "resources", "capabilities", "effects", "decomposition", "frontier", "v1-normalization", "determinism", "p1-uncertainty", "prohibited-execution", "independent-oracle"]}))
