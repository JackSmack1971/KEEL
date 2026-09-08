from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import change_graph as cg


def fixture(name: str) -> dict:
    return json.loads((ROOT / ".keel/tests/fixtures/change-graph" / name).read_text(encoding="utf-8"))


graph = cg.adapt_v2(fixture("valid.json"))
assert cg.validate(graph) == []
assert graph["identity"] == "keel.change-graph/v1"
assert {record["kind"] for record in graph["records"]} == {"work-unit", "requirement", "edge", "effect-request", "evidence-requirement"}
assert not any(record["kind"] == "capability-grant" for record in graph["records"])

work = [record for record in graph["records"] if record["kind"] == "work-unit"]
for node in work:
    assert not ({"dependencies", "authorization_refs", "capability_state", "planning_status", "lifecycle_expectations", "roles"} & set(node))
    assert not ({"dependencies", "authorization_refs", "capability_state", "planning_status", "lifecycle_expectations", "roles"} & set(node["attributes"]))
assert all(edge["edge_type"] == "HARD_DEPENDENCY" for edge in graph["records"] if edge["kind"] == "edge")

def errors(mutator) -> str:
    case = copy.deepcopy(graph); mutator(case)
    return "\n".join(cg.validate(case))


assert "graph_id is invalid" in errors(lambda case: case.__setitem__("graph_id", "Bad/ID"))
assert "duplicate record identity" in errors(lambda case: case["records"].append(copy.deepcopy(case["records"][0])))

def missing_endpoint(case):
    edge = next(item for item in case["records"] if item["kind"] == "edge")
    edge["target_id"] = "keel:work-unit:checkout-v2.missing"
assert "missing target endpoint" in errors(missing_endpoint)

def duplicate_edge(case):
    edge = copy.deepcopy(next(item for item in case["records"] if item["kind"] == "edge"))
    edge["identity"] = "keel:edge:checkout-v2.duplicate"
    case["records"].append(edge)
assert "duplicate edge" in errors(duplicate_edge)

def self_edge(case):
    edge = next(item for item in case["records"] if item["kind"] == "edge")
    edge["target_id"] = edge["source_id"]
assert "self dependency" in errors(self_edge)

def cycle(case):
    edge = copy.deepcopy(next(item for item in case["records"] if item["kind"] == "edge"))
    edge["identity"] = "keel:edge:checkout-v2.reverse"
    edge["source_id"], edge["target_id"] = edge["target_id"], edge["source_id"]
    case["records"].append(edge)
assert "hard dependency cycle" in errors(cycle)

def bad_resource(case):
    node = next(item for item in case["records"] if item["kind"] == "work-unit")
    node["attributes"]["resource_claims"] = [{"resource": "repo:../outside", "mode": "EXCLUSIVE"}]
assert "invalid repository-relative path" in errors(bad_resource)

def malformed_requirement(case):
    req = next(item for item in case["records"] if item["kind"] == "requirement")
    req["obligation"] = ""
assert "obligation must be a non-empty string" in errors(malformed_requirement)

def malformed_evidence(case):
    evidence = next(item for item in case["records"] if item["kind"] == "evidence-requirement")
    evidence["boundary"] = ""
assert "boundary must be a non-empty string" in errors(malformed_evidence)

def invalid_provenance(case): case["provenance"]["source_digest"] = "fixture"
assert "malformed content digest" in errors(invalid_provenance)

# Equal exclusive claims affect a future scheduler, not structural validity.
conflict = copy.deepcopy(graph)
for node in [item for item in conflict["records"] if item["kind"] == "work-unit"]:
    node["attributes"]["resource_claims"] = [{"resource": "repo:src/checkout", "mode": "EXCLUSIVE"}]
assert cg.validate(conflict) == []

reordered = {key: graph[key] for key in reversed(graph)}
reordered["records"] = list(reversed(reordered["records"]))
assert cg.serialize(graph) == cg.serialize(reordered)
assert cg.serialize(json.loads(cg.serialize(graph))) == cg.serialize(graph)

frontier = cg.frontier(graph)
assert frontier["read_only"] is True and frontier["status"] == "READY"
assert frontier["runnable"] == ["keel:work-unit:checkout-v2.contract"]
advanced = cg.frontier(graph, {"keel:work-unit:checkout-v2.contract": "COMPLETE"})
assert advanced["runnable"] == ["keel:work-unit:checkout-v2.backend"]

result = subprocess.run([sys.executable, str(ROOT / ".keel/bin/keel.py"), "change-graph", "validate", str(ROOT / ".keel/tests/fixtures/change-graph/valid.json")], cwd=ROOT, text=True, capture_output=True)
assert result.returncode == 0, result.stderr
assert json.loads(result.stdout)["status"] == "PASS"

print(json.dumps({"status": "PASS", "checks": ["authority", "identities", "endpoints", "duplicate-edges", "self-dependency", "cycles", "resources", "requirements", "evidence", "provenance", "serialization", "frontier", "cli"]}, sort_keys=True))
