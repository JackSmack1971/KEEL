import io
import json
import queue
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "lib"))

import codex_app_server_adapter as adapter
import runtime_authorization as ra
import scheduler
import git_proof


class FakeStdout:
    def __init__(self):
        self.items = queue.Queue()

    def put(self, value): self.items.put(value)
    def close(self): self.items.put(None)
    def __iter__(self):
        while True:
            value = self.items.get()
            if value is None: return
            yield value


class FakeProcess:
    def __init__(self):
        self.stdout = FakeStdout()
        self.stdin = self
        self.returncode = None
        self.writes = []
        self.closed = False

    def write(self, value):
        self.writes.append(json.loads(value))
        request = self.writes[-1]
        method = request["method"]
        if "id" not in request:
            return len(value)
        request_id = request["id"]
        if method == "initialize":
            self.stdout.put(json.dumps({"id": request_id, "result": {"userAgent": "codex-test", "platformFamily": "windows", "platformOs": "windows"}}) + "\n")
        elif method == "account/read":
            self.stdout.put(json.dumps({"id": request_id, "result": {"account": None, "requiresOpenaiAuth": False}}) + "\n")
        elif method == "thread/start":
            self.stdout.put(json.dumps({"id": request_id, "result": {"thread": {"id": "thr_test"}}}) + "\n")
        elif method == "thread/resume":
            self.stdout.put(json.dumps({"id": request_id, "result": {"thread": {"id": request["params"]["threadId"]}}}) + "\n")
        elif method == "turn/start":
            self.stdout.put(json.dumps({"id": request_id, "result": {"turn": {"id": "turn_test"}}}) + "\n")
            self.stdout.put(json.dumps({"method": "turn/started", "params": {"turn": {"id": "turn_test", "status": "inProgress"}}}) + "\n")
            self.stdout.put(json.dumps({"method": "item/started", "params": {"item": {"id": "item_test", "type": "agentMessage"}}}) + "\n")
            self.stdout.put(json.dumps({"method": "item/completed", "params": {"item": {"id": "item_test", "type": "agentMessage"}}}) + "\n")
            self.stdout.put(json.dumps({"method": "turn/completed", "params": {"turn": {"id": "turn_test", "status": "completed"}}}) + "\n")
        return len(value)

    def flush(self): pass
    def close(self): self.closed = True; self.stdout.close()
    def poll(self): return self.returncode
    def wait(self, timeout=None): self.returncode = 0; return 0
    def terminate(self): self.returncode = 143; self.stdout.close()
    def kill(self): self.returncode = -9; self.stdout.close()


def profile():
    return ra.observe_runtime(identity="keel:runtime-profile:test", runtime="codex", source="fixture",
                              observations={name: "OBSERVED" for name in ra.REQUIRED_RUNTIME_SURFACES})


def included_cost():
    return {"auth_mode":"MANAGED_CHATGPT", "provider":"CODEX", "entitlement":"INCLUDED",
            "rate_limit":"AVAILABLE", "paid_continuation":"UNAVAILABLE", "reset_credit":"UNAVAILABLE"}


def test_documented_lifecycle_and_bounded_turn():
    process = FakeProcess()
    client = adapter.CodexAppServerAdapter(process, request_timeout=1)
    observed = client.initialize_and_inspect()
    assert observed.status == "PASS" and observed.capability_status == "STABLE_DOCUMENTED_SURFACE"
    assert client.start_thread() == "thr_test"
    assert client.resume_thread("thr_test") == "thr_test"
    turn = client.submit_turn("thr_test", "hello", profile=profile(), cost_observations=included_cost(), max_events=8)
    assert [event["method"] for event in turn.events] == ["turn/started", "item/started", "item/completed", "turn/completed"]
    client.close()
    client.close()
    assert process.closed


def test_cost_preflight_blocks_before_turn_request():
    process = FakeProcess()
    client = adapter.CodexAppServerAdapter(process, request_timeout=1)
    client.initialize_and_inspect()
    client.start_thread()
    try:
        client.submit_turn("thr_test", "hello", profile=profile(), cost_observations=None)
    except adapter.AdapterError as exc:
        assert "ZERO_INCREMENTAL_COST BLOCKED" in str(exc)
    else:
        assert False, "blocked preflight must prevent turn/start"
    assert not any(item["method"] == "turn/start" for item in process.writes)
    client.close()


def test_malformed_frame_timeout_and_cleanup():
    process = FakeProcess()
    client = adapter.CodexAppServerAdapter(process, request_timeout=0.05)
    process.stdout.put("{not-json}\n")
    try:
        client.initialize_and_inspect()
    except adapter.MalformedMessage:
        pass
    else:
        assert False, "malformed frame must fail closed"
    client.close()
    assert process.closed


def test_transport_policy_and_scheduler_boundary():
    source = (Path(__file__).parents[1] / "lib" / "codex_app_server_adapter.py").read_text(encoding="utf-8").lower()
    scheduler = (Path(__file__).parents[1] / "lib" / "scheduler.py").read_text(encoding="utf-8").lower()
    assert "openai_api_key" not in source and "websocket" not in source and "process/spawn" not in source
    assert "subprocess" not in scheduler


def envelope():
    subject = git_proof.head_commit(Path(__file__).resolve().parents[2])
    workspace = scheduler.WorkspaceBinding("workspace-1", str(Path(__file__).resolve().parents[2]), subject)
    return scheduler.DispatchEnvelope("change-1", "work-1", subject, subject, workspace,
        "intent-1", "graph-1", "authority-1", profile().identity, ra.runtime_profile_digest(profile()),
        "context-1", "bounded governed context", "implement governed work", ("REQ-1",),
        (".keel/lib/**",), (("repo:.keel/lib", "EXCLUSIVE"),), ("AC-1",),
        "evidence-plan-1", "stop on drift", "report observation; KEEL verifies")


def test_governed_dispatch_uses_workspace_and_observes_only():
    process = FakeProcess()
    client = adapter.CodexAppServerAdapter(process, request_timeout=1, runtime_profile=profile(), cost_observations=included_cost())
    governed = envelope(); result = client.dispatch(governed)
    assert result.outcome == "OBSERVED" and result.observation is not None
    assert result.observation.thread_id == "thr_test" and result.observation.turn_id == "turn_test"
    thread = next(item for item in process.writes if item.get("method") == "thread/start")
    assert thread["params"]["cwd"] == governed.workspace.path
    turn = next(item for item in process.writes if item.get("method") == "turn/start")
    payload = json.loads(turn["params"]["input"][0]["text"])
    assert payload == governed.to_dict() and payload["objective"] != turn["params"]["input"][0]["text"]
    client.close()


def test_runtime_profile_mismatch_fails_before_thread_creation():
    process=FakeProcess(); client=adapter.CodexAppServerAdapter(process,request_timeout=1,runtime_profile=profile(),cost_observations=included_cost())
    result=client.dispatch(scheduler.DispatchEnvelope(**{**envelope().__dict__,"runtime_profile_digest":"stale"}))
    assert result.outcome=="FAILED" and not any(item.get("method")=="thread/start" for item in process.writes)
    client.close()


def test_objective_only_dispatch_is_impossible_and_preflight_precedes_model():
    process = FakeProcess(); client = adapter.CodexAppServerAdapter(process, request_timeout=1, runtime_profile=profile())
    try: client.dispatch(type("Unit", (), {"objective":"only"})())
    except ValueError: pass
    else: assert False, "objective-only dispatch must be rejected"
    result = client.dispatch(envelope())
    assert result.outcome == "FAILED" and result.failure_class.value == "AUTHORIZATION_BLOCK"
    assert not any(item.get("method") == "turn/start" for item in process.writes)
    client.close()


if __name__ == "__main__":
    test_documented_lifecycle_and_bounded_turn()
    test_cost_preflight_blocks_before_turn_request()
    test_malformed_frame_timeout_and_cleanup()
    test_transport_policy_and_scheduler_boundary()
    test_governed_dispatch_uses_workspace_and_observes_only()
    test_runtime_profile_mismatch_fails_before_thread_creation()
    test_objective_only_dispatch_is_impossible_and_preflight_precedes_model()
    print(json.dumps({"status": "PASS", "checks": ["handshake", "account", "thread-create", "thread-resume", "bounded-turn-events", "cost-gate", "malformed-frame", "idempotent-shutdown", "transport-policy", "scheduler-boundary", "governed-dispatch", "workspace-cwd", "observation-only", "objective-only-rejected"]}, sort_keys=True))
