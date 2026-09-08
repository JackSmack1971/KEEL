"""Minimal mission-v1 compatibility proof; ChangeGraph tests own semantics."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import change_graph as cg
import mission_graph

source = json.loads((ROOT / ".keel/tests/fixtures/mission-v2/v1.json").read_text())
graph = mission_graph.normalize(source)
assert mission_graph.validate(source) == []
assert graph["provenance"]["source_schema"] == "keel.mission/v1"
assert graph["uncertainty"] and all(record["kind"] != "capability-grant" for record in graph["records"])
assert cg.serialize(graph) == cg.serialize(mission_graph.normalize(json.loads(json.dumps(source))))
frontier = mission_graph.plan(ROOT, source)
assert frontier["read_only"] is True and frontier["runnable"] == ["keel:work-unit:legacy.a"]
assert not hasattr(mission_graph, "dispatch_plan")
print(json.dumps({"status": "PASS", "checks": ["v1-adapter", "determinism", "uncertainty", "read-only-frontier", "no-dispatch"]}, sort_keys=True))
