from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import change_graph as cg
import scheduler


class LocalAdapter:
    def __init__(self): self.calls = []
    def dispatch(self, unit, workspace_id):
        self.calls.append((unit.identity, workspace_id))
        return scheduler.DispatchResult("COMPLETE", "local", "smoke")


source = {"schema_id":"keel.mission", "schema_version":2, "mission_id":"local-smoke", "objective":"local",
          "nodes":[{"node_id":"prepare","objective":"prepare","acceptance_criteria":["done"]},
                   {"node_id":"verify","objective":"verify","acceptance_criteria":["done"],"dependencies":["prepare"]}],
          "dependencies":[{"from":"verify","to":"prepare","type":"HARD_PREREQUISITE"}]}
graph = cg.adapt_v2(source); adapter = LocalAdapter()
with tempfile.TemporaryDirectory() as directory:
    store = scheduler.StateStore(Path(directory) / "scheduler.json")
    run = scheduler.Scheduler(graph, adapter, state=store.load(), max_concurrency=1)
    run.dispatch(); store.save(run.state)
    resumed = scheduler.Scheduler(graph, adapter, state=store.load(), max_concurrency=1)
    resumed.dispatch(); store.save(resumed.state)
    assert all(record.status == scheduler.WorkStatus.COMPLETE for record in resumed.state.records.values())
    assert len(adapter.calls) == 2 and len({workspace for _, workspace in adapter.calls}) == 2
print(json.dumps({"status":"PASS","external_effects":False,"isolated_workunits":2}, sort_keys=True))
