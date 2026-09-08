import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import codex_adapter_kernel as adapter
import runtime_authorization as runtime


class FakeKernel:
    INTEGRATION_PREFIXES = ("git push", "git merge", "gh pr create", "gh pr merge")
    def __init__(self, phase="EXECUTE", active="change", bad_state=False):
        self.phase, self.active, self.bad_state = phase, active, bad_state
    def active_change(self, root):
        if self.bad_state: raise ValueError("corrupt state")
        return self.active
    def state(self, root, cid): return {"phase":self.phase, "base_commit":"base"}
    def ledger_dir(self, root, cid): return root / ".keel/ledger" / cid
    def parse_scope(self, path): return ["src/**", "docs/**"]
    def scope_match(self, path, scope): return path.startswith(("src/", "docs/"))
    def changed_paths(self, root, base): return []
    def head_commit(self, root): return "head"
    def diff_scope_errors(self, root, cid): return ([], ["src/change.py"])
    def current_verified(self, root, cid): return (self.phase == "SHIP", "not verified")
    def candidate_status(self, root, cid): return {"status":"SEALED"}
    def compile_context(self, root, cid, write=True): return {"text":"X" * 1000}
    def read_json(self, path): return {"hook_summary_max_chars":300}
    def record_bypass(self, root, cid, reason, session): self.bypass = (cid, reason, session)


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    q = adapter.normalize_query({"hook_event_name":"PreToolUse", "tool_name":"apply_patch",
        "tool_input":{"patch":"*** Update File: src/a.py\n+x"}}, "PreToolUse")
    assert adapter.tool_family(q.tool_name) == "local-write"
    assert adapter.tool_paths(q, root) == ("src/a.py",)
    assert adapter.query(FakeKernel(), root, q).kind is adapter.OutcomeKind.ALLOW

    outside = adapter.normalize_query({"hook_event_name":"PreToolUse", "tool_name":"Write",
        "tool_input":{"file_path":"other/a.py"}}, "PreToolUse")
    denied = adapter.query(FakeKernel(), root, outside)
    assert denied.kind is adapter.OutcomeKind.DENY and "scope" in denied.reason

    unknown_write = adapter.normalize_query({"hook_event_name":"PreToolUse", "tool_name":"Write",
        "tool_input":{"opaque":"x"}}, "PreToolUse")
    assert adapter.query(FakeKernel(), root, unknown_write).kind is adapter.OutcomeKind.DENY

    mcp = adapter.normalize_query({"hook_event_name":"PreToolUse", "tool_name":"mcp__db__query",
        "tool_input":{"query":"select 1"}}, "PreToolUse")
    mcp_out = adapter.query(FakeKernel(), root, mcp)
    assert adapter.tool_family(mcp.tool_name) == "mcp-function" and mcp_out.kind is adapter.OutcomeKind.ALLOW
    assert mcp_out.coverage == ("mcp-function",)
    read_path = adapter.normalize_query({"hook_event_name":"PreToolUse", "tool_name":"Read",
        "tool_input":{"file_path":"outside/read-only.txt"}}, "PreToolUse")
    assert adapter.query(FakeKernel(), root, read_path).kind is adapter.OutcomeKind.ALLOW

    context = adapter.normalize_query({"hook_event_name":"UserPromptSubmit"}, "UserPromptSubmit")
    context_out = adapter.query(FakeKernel(), root, context)
    assert context_out.kind is adapter.OutcomeKind.CONTEXT and len(context_out.context) == 300

    corrupt = adapter.query(FakeKernel(bad_state=True), root, q)
    assert corrupt.kind is adapter.OutcomeKind.DENY
    post = adapter.normalize_query({"hook_event_name":"PostToolUse", "tool_name":"mcp__fs__write",
        "tool_input":{"path":"src/a.py"}}, "PostToolUse")
    observed = adapter.query(FakeKernel(), root, post)
    assert observed.effect_already_occurred and "cannot be undone" in observed.reason

outside_decision = runtime.evaluate_repository_enforcement(
    authority=runtime.RepositoryAuthority.OUTSIDE, enforcement_expected=True, trusted_state=False)
unknown_decision = runtime.evaluate_repository_enforcement(
    authority=runtime.RepositoryAuthority.UNKNOWN, enforcement_expected=True, trusted_state=False)
explicit = runtime.evaluate_repository_enforcement(
    authority=runtime.RepositoryAuthority.APPLIES, enforcement_expected=True,
    trusted_state=False, policy_permits=True)
assert outside_decision.permitted and not outside_decision.fail_closed
assert not unknown_decision.permitted and unknown_decision.fail_closed
assert explicit.permitted

hooks = json.loads((ROOT / ".codex/hooks.json").read_text())
assert hooks["hooks"]["PreToolUse"][0]["matcher"] == "*"
assert hooks["hooks"]["PostToolUse"][0]["matcher"] == "*"
for phase in ("keel-discuss.toml", "keel-plan.toml", "keel-verify.toml", "keel-ship.toml"):
    assert not (ROOT / ".codex/agents" / phase).exists()
hook_source = (ROOT / ".keel/hooks/keel_hook.py").read_text()
for forbidden in ("scope_match(", "current_verified(", "phase_write_allowed", "evidence-graph"):
    assert forbidden not in hook_source
assert "reconciler" not in (ROOT / ".keel/lib/codex_adapter_kernel.py").read_text().lower()
print(json.dumps({"status":"PASS", "checks":["normalization", "runtime-policy", "bounded-context", "local-mcp-coverage", "post-effect-honesty", "thin-hook", "dynamic-agents", "no-reconciler"]}))
