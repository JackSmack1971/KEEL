import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import codex_adapter_kernel as hook

hook.normalize_query({"hook_event_name":"SessionStart"}, "SessionStart")
hook.normalize_query({"hook_event_name":"UserPromptSubmit"}, "UserPromptSubmit")
hook.normalize_query({}, "SessionStart")
try:
    hook.normalize_query({"hook_event_name":"Stop"}, "SessionStart")
except ValueError as exc:
    assert "expected 'SessionStart'" in str(exc)
else:
    raise AssertionError("unrelated event was accepted")
print({"status":"PASS", "checks":["SessionStart", "UserPromptSubmit", "strict-unrelated-event"]})
