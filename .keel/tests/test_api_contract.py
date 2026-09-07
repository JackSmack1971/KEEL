import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import api_contract, evidence_graph, keel_core

ids = api_contract.correlation("change-1", mission_id="mission:one", run_id="run:one", evidence_id="evidence:one")
assert api_contract.envelope({"status":"PASS", "value": 1}, ids)["api_version"] == 1
try: api_contract.correlation("../forged")
except ValueError: pass
else: raise AssertionError("invalid correlation identifier accepted")
declaration = evidence_graph.provider_declaration("browser")
assert declaration["enabled"] is False and declaration["authorization"] == "domain-only"
assert evidence_graph.redact_provider_result({"token":"secret"})["token"] == "[REDACTED]"
try: evidence_graph.provider_declaration("browser", enabled=True)
except ValueError: pass
else: raise AssertionError("enabled provider declaration accepted")
with tempfile.TemporaryDirectory() as d:
    root = Path(d); (root / ".keel/ledger/c").mkdir(parents=True)
    (root / ".keel/ledger/c/state.json").write_text(json.dumps({"change_id":"c", "correlation":{"change_id":"c", "run_id":"run:c"}}))
    keel_core.append_event(root, "c", "TEST", "PASS")
    event = json.loads((root / ".keel/ledger/c/gate-log.jsonl").read_text().splitlines()[0])
    assert event["correlation"]["run_id"] == "run:c"
print(json.dumps({"status":"PASS", "checks":["versioned-envelope", "correlation-validation", "provider-disabled", "redaction", "event-correlation"]}))
