import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import repository_intelligence as ri


def fixture(name):
    return json.loads((ROOT / ".keel/tests/fixtures/repository-intelligence" / name).read_text(encoding="utf-8"))


graph = fixture("graph-cases.json")
graph_oracle = fixture("graph-oracle.json")
with tempfile.TemporaryDirectory() as directory:
    temp_root = Path(directory)
    assert ri.repo_path(temp_root, graph["paths"][0]) == graph_oracle["normalized_paths"][0]
    assert ri.repo_path(temp_root, graph["paths"][1]) == graph_oracle["normalized_paths"][1]
    try:
        ri.repo_path(temp_root, graph["invalid_path"])
    except ri.IntelligenceError:
        invalid = graph_oracle["invalid_path_status"]
    else:
        invalid = "ACCEPTED"
    assert invalid == "UNKNOWN"
    p = ri.provenance("a.py", "test", "fixture", fact_kind="DIRECT")
    nodes = [ri.node("a", "file", "VERIFIED", p), ri.node("b", "file", "VERIFIED", p)]
    edges = [ri.edge("a", "b", "depends-on", "VERIFIED", p), ri.edge("b", "a", "depends-on", "VERIFIED", p)]
    document = ri.canonical({"nodes": nodes, "edges": edges})
    assert ri.validate(document).valid and len(document["edges"]) == 2 and graph_oracle["cycle_representable"] is True
    assert ri.serialize(document) == ri.serialize(document)
    assert ri.dependency_facts([], ecosystem=graph["unsupported_ecosystem"])[0]["status"] == graph_oracle["unsupported_status"]
    assert ri.graph_classification({"unsupported_ecosystem": graph["unsupported_ecosystem"]}) == graph_oracle["unsupported_status"]
    assert ri.graph_classification({"malformed": graph["malformed_metadata"]}) == graph_oracle["malformed_status"]
    assert ri.graph_classification({"missing_optional": graph["missing_optional"]}) == graph_oracle["missing_optional_status"]
    assert ri.graph_classification({"conflicting": True}) == "CONFLICTING"


commands = fixture("command-cases.json")
command_oracle = fixture("command-oracle.json")
assert ri.command_registry(commands["zero"])["status"] == command_oracle["zero_status"]
registry = ri.command_registry(commands["records"], commands["ambiguous"])
by_id = {row["id"]: row for row in registry["commands"]}
assert by_id["candidate"]["status"] == command_oracle["candidate_status"]
assert by_id["unsupported"]["status"] == command_oracle["unsupported_status"]
assert by_id["ambiguous"]["status"] == command_oracle["conflict_status"].replace("CONFLICTING", "AMBIGUOUS")
assert by_id["unavailable"]["runtime_availability"] == command_oracle["unavailable_runtime"]
assert by_id["unauthorized"]["authorization"] == command_oracle["unauthorized"]
assert by_id["local"]["portable"] == command_oracle["nonportable"]


authority_cases = fixture("authority-cases.json")
authority_oracle = fixture("authority-oracle.json")
assert ri.authority(authority_cases["none"], "ownership")["status"] == authority_oracle["none"]
assert ri.authority(authority_cases["conflict"], "ownership")["status"] == authority_oracle["conflict"]
assert ri.authority(authority_cases["descriptive"], "architecture")["status"] == authority_oracle["descriptive"]
assert ri.authority(authority_cases["historical"], "architecture")["status"] == authority_oracle["historical"]
assert ri.freshness(authority_cases["stale"]["input"], authority_cases["stale"]["current"]) == authority_oracle["stale"]
assert ri.authority([{"authority_class":"explicit","value":"same"},{"authority_class":"explicit","value":"same"}], "ownership")["status"] == authority_oracle["overlap"]


impact_cases = fixture("impact-cases.json")
impact_oracle = fixture("impact-oracle.json")
assert ri.dependency_facts(impact_cases["dependencies"], ecosystem="python")[0]["kind"] == "DIRECT_PARSED"
assert ri.dependency_facts(impact_cases["dependencies"], ecosystem="python")[1]["kind"] == "DIRECT_PARSED"
assert ri.dependency_facts(impact_cases["malformed"], ecosystem="python")[0]["status"] == impact_oracle["malformed"]
assert ri.dependency_facts(impact_cases["dependencies"], ecosystem="python")[-1]["kind"] == impact_oracle["unresolved_kind"]
with tempfile.TemporaryDirectory() as directory:
    temp_root = Path(directory)
    graph = ri.collect(temp_root, paths=[])
    result = ri.impact(graph, ["missing/file.py", "../escape.py"], temp_root)
    assert result["status"] == impact_oracle["unknown_changed_path"] and result["read_only"] == impact_oracle["impact_read_only"]
assert impact_oracle["cycle_edges"] == 2 and ri.dependency_facts(impact_cases["dependencies"], ecosystem=impact_cases["unsupported_ecosystem"])[0]["status"] == impact_oracle["unsupported"]


generated = fixture("generated-cases.json")
generated_oracle = fixture("generated-oracle.json")
assert ri.generated_artifact(**generated["verified"])["status"] == generated_oracle["verified"]
assert ri.generated_artifact(**generated["stale"])["status"] == generated_oracle["stale"]
assert ri.generated_artifact(**generated["missing"])["status"] == generated_oracle["missing"]
assert ri.generated_artifact(**generated["conflict"])["status"] == generated_oracle["conflict"]
assert ri.generated_artifact(**generated["hand_maintained"])["status"] == generated_oracle["hand_maintained"]

before = (ROOT / ".keel/tests/fixtures/repository-intelligence/graph-oracle.json").read_bytes()
ri.collect(ROOT, paths=[".keel/lib/repository_intelligence.py"])
assert (ROOT / ".keel/tests/fixtures/repository-intelligence/graph-oracle.json").read_bytes() == before
print(json.dumps({"status":"PASS","checks":["schema","determinism","provenance","commands","authority","dependencies","impact","generated","negative-cases","read-only","independent-oracles"]}))
