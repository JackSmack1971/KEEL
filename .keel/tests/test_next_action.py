from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch


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


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()


def _write_anchor_evidence(root: Path, change_id: str, candidate: str, landed: str, digest: str, *, noted_candidate: str | None = None) -> None:
    _git(root, "update-ref", f"refs/keel/candidates/{change_id}", candidate)
    _git(root, "update-ref", f"refs/keel/ledger/{change_id}", landed)
    _git(root, "notes", "--ref=keel", "add", "-f", "-m", "\n".join([
        f"keel-change-id: {change_id}",
        f"sealed-candidate: {noted_candidate or candidate}",
        f"landed-commit: {landed}",
        "integration-relation: candidate-ancestor",
        f"verified-content-digest: {digest}",
    ]), landed)
    audit = root / ".keel" / "audit"
    audit.mkdir(parents=True, exist_ok=True)
    (audit / "anchors.jsonl").write_text(json.dumps({
        "change_id": change_id,
        "candidate_commit": candidate,
        "landed_commit": landed,
        "content_digest": digest,
    }) + "\n", encoding="utf-8")


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

        with tempfile.TemporaryDirectory() as anchored_directory:
            anchored_root = Path(anchored_directory)
            _git(anchored_root, "init", "-q")
            _git(anchored_root, "config", "user.email", "test@example.com")
            _git(anchored_root, "config", "user.name", "Test")
            (anchored_root / "marker").write_text("fixture", encoding="utf-8")
            _git(anchored_root, "add", "marker")
            _git(anchored_root, "commit", "-q", "-m", "fixture")
            commit = _git(anchored_root, "rev-parse", "HEAD")
            _write_state(anchored_root, "SHIP")
            with patch.object(core, "current_verified", return_value=(False, "unrelated active change")), patch.object(
                core, "candidate_status", return_value={"commit": commit, "content_digest": "digest"}
            ):
                _write_anchor_evidence(anchored_root, "change-1", commit, commit, "digest")
                anchored = core.next_action(anchored_root, "change-1")
                assert anchored["status"] == "IDLE"
                assert anchored["recommended_action"] is None
                assert core.next_action(anchored_root)["status"] == "IDLE"

            with patch.object(core, "current_verified", return_value=(True, "ok")), patch.object(
                core, "candidate_status", return_value={"commit": commit, "content_digest": "digest"}
            ):
                _git(anchored_root, "update-ref", "-d", "refs/keel/ledger/change-1")
                pending = core.next_action(anchored_root, "change-1")
                assert pending["recommended_action"]["id"] == "integrate-anchor"

                _git(anchored_root, "update-ref", "refs/keel/ledger/change-1", commit)
                (anchored_root / ".keel" / "audit" / "anchors.jsonl").write_text("{}\n", encoding="utf-8")
                invalid = core.next_action(anchored_root, "change-1")
                assert invalid["status"] == "BLOCKED"
                assert invalid["blockers"][0]["id"] == "invalid-anchor-evidence"

                _write_anchor_evidence(anchored_root, "change-1", commit, commit, "digest", noted_candidate="different-candidate")
                mismatch = core.next_action(anchored_root, "change-1")
                assert mismatch["status"] == "BLOCKED"
                assert mismatch["blockers"][0]["id"] == "invalid-anchor-evidence"


if __name__ == "__main__":
    main()
