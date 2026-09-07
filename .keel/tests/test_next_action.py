from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_core():
    lib = ROOT / ".keel" / "lib"
    import sys
    sys.path.insert(0, str(lib))
    path = lib / "keel_core.py"
    spec = importlib.util.spec_from_file_location("keel_core_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_state(root: Path, phase: str) -> tuple[Path, bytes]:
    ledger = root / ".keel" / "ledger" / "change-1"
    ledger.mkdir(parents=True, exist_ok=True)
    state = ledger / "state.json"
    state.write_text(json.dumps({"change_id": "change-1", "phase": phase, "mode": "standard", "base_commit": "abc"}), encoding="utf-8")
    return state, state.read_bytes()


def main() -> None:
    core = _load_core()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        idle = core.next_action(root)
        assert idle["status"] == "IDLE"
        assert idle["recommended_action"] is None

        expected = {
            "DISCUSS": "gate-discuss",
            "PLAN": "gate-plan",
            "EXECUTE": "verify",
            "VERIFY": "verify",
        }
        for phase, action_id in expected.items():
            state, before = _write_state(root, phase)
            result = core.next_action(root, "change-1")
            assert result["status"] == "ACTIONABLE"
            assert result["recommended_action"]["id"] == action_id
            assert state.read_bytes() == before
            state.unlink()
            state.parent.rmdir()
            state.parent.parent.rmdir()

        state, before = _write_state(root, "SHIP")
        stale = core.next_action(root, "change-1")
        assert stale["status"] == "BLOCKED"
        assert stale["blockers"][0]["id"] == "stale-verification"
        assert stale["recommended_action"]["id"] == "reopen"
        assert state.read_bytes() == before
        print("Next-action tests PASS")


if __name__ == "__main__":
    main()
