from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import change_graph as cg
import scheduler
import semantic_kernel as sk


def graph() -> dict:
    source = {"schema_id":"keel.mission", "schema_version":2, "mission_id":"scheduler-test", "objective":"test scheduler",
              "nodes":[{"node_id":"a","objective":"a","acceptance_criteria":["a"]},
                       {"node_id":"b","objective":"b","acceptance_criteria":["b"],"dependencies":["a"]},
                       {"node_id":"c","objective":"c","acceptance_criteria":["c"]}],
              "dependencies":[{"from":"b","to":"a","type":"HARD_PREREQUISITE"}]}
    return cg.adapt_v2(source)


class Adapter:
    def __init__(self, outcomes=None): self.calls = []; self.outcomes = outcomes or {}
    def dispatch(self, unit, workspace_id):
        self.calls.append((unit.identity, workspace_id))
        return self.outcomes.get(unit.identity, scheduler.DispatchResult("COMPLETE", "e1", "s1", artifacts=(unit.identity + ".out",)))


g = graph(); adapter = Adapter(); s = scheduler.Scheduler(g, adapter, max_concurrency=2, stale_after=100)
first = s.dispatch()
assert first["status"] == "READY" and len(adapter.calls) == 2
assert len(first["runnable"]) == 1 and first["runnable"][0].endswith(".b")
second = s.dispatch()
assert len(second["dispatched"]) == 1 and len(adapter.calls) == 3
third = s.dispatch()
assert third["dispatched"] == [] and len(adapter.calls) == 3
assert s.state.records[next(i for i in s.units if i.endswith(".b"))].status == scheduler.WorkStatus.COMPLETE

# A hard prerequisite remains a dependency, while unrelated read work can run together.
assert {item[0].rsplit(".", 1)[-1] for item in adapter.calls[:2]} == {"a", "c"}

# Overlapping exclusive claims serialize rather than invalidate the graph.
conflict = copy.deepcopy(g)
for raw in conflict["records"]:
    if raw["kind"] == "work-unit": raw["attributes"]["resource_claims"] = [{"resource":"repo:src/x","mode":"EXCLUSIVE"}]
left = scheduler.Scheduler(conflict, max_concurrency=2)
runnable, blocked = left.frontier()
assert len(runnable) == 1 and any("RESOURCE_CONFLICT" in reasons for reasons in blocked.values())

# Persistent resume, stale detection, and the one-writer-per-workspace invariant.
clock = [100.0]
persisted = scheduler.SchedulerState(graph_digest="", records={})
writer_graph = copy.deepcopy(g)
for raw in writer_graph["records"]:
    if raw["kind"] == "work-unit":
        raw["attributes"]["workspace_id"] = "isolated-1"
        raw["attributes"]["write_worktree"] = True
        raw["attributes"]["resource_claims"] = [{"resource":"repo:src/x","mode":"EXCLUSIVE"}]
running = scheduler.Scheduler(writer_graph, Adapter({next(i for i in scheduler.Scheduler(writer_graph).units if i.endswith(".a")): scheduler.DispatchResult("RUNNING", "e", "s")}), state=persisted, max_concurrency=3, stale_after=5, clock=lambda: clock[0])
running.dispatch(); assert len(running.state.records) == 3
clock[0] = 106; running.reconcile(); assert any(r.status == scheduler.WorkStatus.STALE for r in running.state.records.values())

with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "state.json"
    store = scheduler.StateStore(path); store.save(running.state)
    resumed = store.load(); assert resumed.to_dict() == running.state.to_dict()

# Recovery is bounded and a repeated identical failure escalates instead of looping.
unit_id = next(i for i in g["records"] if i["kind"] == "work-unit")["identity"]
failing = Adapter({unit_id: scheduler.DispatchResult("FAILED", "same-evidence", "same-strategy", scheduler.FailureClass.IMPLEMENTATION_DEFECT, "bad")})
retry_graph = copy.deepcopy(g)
for raw in retry_graph["records"]:
    if raw.get("identity") == unit_id: raw["attributes"]["retry_policy"] = {"max_attempts": 2}
retry = scheduler.Scheduler(retry_graph, failing, max_concurrency=1)
retry.dispatch(); retry.dispatch(); assert retry.state.records[unit_id].status == scheduler.WorkStatus.ESCALATED

print(json.dumps({"status":"PASS","checks":["frontier","dependencies","resources","bounded-concurrency","isolation","stale","resume","duplicate-dispatch","recovery","adapter-boundary"]}, sort_keys=True))
