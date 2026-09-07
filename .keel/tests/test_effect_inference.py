import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import effect_inference as ei

assert ei.infer_argv(["git", "push", "origin", "main"])[0]["capability"] == "git.remote.push"
assert ei.infer_argv(["terraform", "apply", "plan.out"])[0]["capability"] == "infra.apply"
assert ei.infer_argv(["python", "-B", "test.py"]) == []
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / ".keel").mkdir()
    (root / ".keel" / "config.json").write_text(json.dumps({"verification_commands": [{"id": "push", "argv": ["git", "push"]}]}), encoding="utf-8")
    result = ei.audit(root, None)
    assert result["status"] == "PASS" and result["read_only"] is True
print(json.dumps({"status": "PASS", "checks": ["mapping", "unknown-neutrality", "advisory-boundary", "read-only"]}))
