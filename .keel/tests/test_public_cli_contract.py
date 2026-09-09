import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ["python3", ".keel/bin/keel.py"]


def run(*args):
    return subprocess.run(CLI + list(args), cwd=ROOT, text=True, capture_output=True)


help_result = run("--help")
assert help_result.returncode == 0
assert all(name not in help_result.stdout for name in ("change-graph", "candidate-status", "record-authorization", "landing"))
assert all(name in help_result.stdout for name in ("doctor", "init", "start", "status", "next", "run", "verify", "land", "explain", "audit"))

for command in ("status", "next", "explain", "audit"):
    result = run(command)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert isinstance(payload.get("schema"), str), payload

status = json.loads(run("status").stdout)
assert status["lifecycle"] in {"IDLE", "UNSEALED", "SEALED", "INTEGRATING", "LANDED", "STALE", "EXECUTE", "PLAN", "DISCUSS"}, status
assert isinstance(status["readiness"], str), status
assert status["autonomous_codex"]["status"] == "BLOCKED", status
assert json.loads(run("explain").stdout)["decision"] == "BLOCKED"

run_result = run("run")
assert run_result.returncode == 1
assert json.loads(run_result.stdout)["status"] == "BLOCKED"
print("Public CLI contract tests PASS")
