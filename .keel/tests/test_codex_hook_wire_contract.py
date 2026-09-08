import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".keel/hooks/keel_hook.py"

def invoke(action, payload, cwd=ROOT, raw=None):
    proc = subprocess.run(["python", "-B", str(HOOK), action], cwd=cwd,
        input=raw if raw is not None else json.dumps(payload), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = json.loads(proc.stdout) if proc.stdout.strip() else {}
    assert proc.returncode == 0, proc.stderr
    return output

allowed = invoke("pre-tool", {"hook_event_name":"PreToolUse", "cwd":str(ROOT),
    "tool_name":"Read", "tool_input":{"file_path":"AGENTS.md"}, "session_id":"wire"})
assert allowed == {}

denied = invoke("pre-tool", {"hook_event_name":"PreToolUse", "cwd":str(ROOT),
    "tool_name":"Write", "tool_input":{"file_path":"outside-scope.txt", "content":"x"}})
assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"

mcp = invoke("pre-tool", {"hook_event_name":"PreToolUse", "cwd":str(ROOT),
    "tool_name":"mcp__example__read", "tool_input":{"query":"harmless"}})
assert mcp == {}

post = invoke("post-tool", {"hook_event_name":"PostToolUse", "cwd":str(ROOT),
    "tool_name":"mcp__example__read", "tool_input":{"query":"harmless"}})
assert "cannot undo" in post["hookSpecificOutput"]["additionalContext"]

invalid = invoke("pre-tool", {}, raw="not-json")
assert invalid["hookSpecificOutput"]["permissionDecision"] == "deny"
mismatch = invoke("pre-tool", {"hook_event_name":"Stop", "cwd":str(ROOT)})
assert mismatch["hookSpecificOutput"]["permissionDecision"] == "deny"

with tempfile.TemporaryDirectory() as td:
    outside = invoke("pre-tool", {"hook_event_name":"PreToolUse", "cwd":td,
        "tool_name":"Write", "tool_input":{"file_path":"x"}}, cwd=Path(td))
    assert outside == {}  # conclusive non-repository: outside KEEL authority

print(json.dumps({"status":"PASS", "evidence_class":"STATIC_WIRE_FIXTURE_ONLY",
    "installed_runtime_enforcement_proven":False,
    "checks":["current-shaped-local", "mcp-function", "deny-output", "post-effect-output", "malformed-fail-closed", "outside-authority-fail-open"]}))
