"""Conditional live smoke; absence is explicitly UNVERIFIED_RUNTIME."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "lib"))
from codex_app_server_adapter import CodexAppServerAdapter, AdapterError


def main():
    if "--no-live-runtime" in sys.argv:
        print(json.dumps({"status": "UNVERIFIED_RUNTIME", "reason": "live Codex runtime is intentionally disabled in deterministic CI"}, sort_keys=True))
        return 0
    executable = shutil.which("codex")
    if executable is None:
        print(json.dumps({"status": "UNVERIFIED_RUNTIME", "reason": "codex executable is not installed or reachable"}, sort_keys=True))
        return 0
    try:
        version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5, check=False).stdout.strip()
        with CodexAppServerAdapter.launch((executable, "app-server", "--listen", "stdio://"), timeout=8) as client:
            observation = client.initialize_and_inspect()
            thread_id = client.start_thread()
        print(json.dumps({"status": "PASS", "runtime": version, "thread_id_observed": bool(thread_id),
                          "protocol_version": observation.protocol_version,
                          "capability_status": observation.capability_status,
                          "account_state_observed": bool(observation.account)}, sort_keys=True))
    except (AdapterError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "UNVERIFIED_RUNTIME", "reason": str(exc)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
