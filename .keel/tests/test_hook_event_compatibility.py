import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = ROOT / ".keel/hooks/keel_hook.py"
spec = importlib.util.spec_from_file_location("keel_hook_under_test", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(hook)

hook._validate_event_name("context", {"hook_event_name": "SessionStart"})
hook._validate_event_name("context", {"hook_event_name": "UserPromptSubmit"})
hook._validate_event_name("context", {})

try:
    hook._validate_event_name("context", {"hook_event_name": "Stop"})
except ValueError as exc:
    assert "expected 'SessionStart'" in str(exc)
else:
    raise AssertionError("unrelated context event was accepted")

try:
    hook._validate_event_name("pre-tool", {"hook_event_name": "UserPromptSubmit"})
except ValueError:
    pass
else:
    raise AssertionError("UserPromptSubmit was accepted for pre-tool")

print({"status": "PASS", "checks": ["SessionStart", "UserPromptSubmit", "strict-unrelated-event"]})
