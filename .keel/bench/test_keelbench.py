from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("keelbench", ROOT / ".keel/bin/keelbench.py")
KEELBENCH = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(KEELBENCH)


def complete_trial(trial_dir: Path) -> None:
    manifest = json.loads((trial_dir / "trial.json").read_text())
    for entry in manifest["runs"]:
        path = trial_dir / entry["path"]
        run = json.loads(path.read_text())
        run["status"] = "COMPLETE"
        run["metrics"] = {key: (True if key == "task_success" else 1) for key in KEELBENCH.REQUIRED_METRICS}
        run["events"] = [{"type": "run_completed", "sequence": 1}]
        path.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")


def copy_trial(source: Path, target: Path) -> None:
    target.mkdir()
    for item in source.iterdir():
        (target / item.name).write_text(item.read_text())


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="keelbench-test-") as raw:
        root = Path(raw)
        (root / ".keel/bench").mkdir(parents=True)
        for name in ("corpus.json", "telemetry-schema.json"):
            (root / ".keel/bench" / name).write_text((ROOT / ".keel/bench" / name).read_text())

        trial = root / "trial-a"
        KEELBENCH.new_trial(root, "KB-01-bugfix", 2, "seed-1", "state-1", "digest-1", trial)
        complete_trial(trial)
        valid = KEELBENCH.validate_trial(trial, root)
        assert valid["status"] == "PASS", valid
        scored = KEELBENCH.score_trials([trial], root)
        assert scored["status"] == "PASS" and scored["comparison"]["paired_trial_count"] == 1
        assert scored["empirical_claim"] == "UNVALIDATED"
        assert scored["trials"][0]["conditions"]["baseline"]["mean_penalty"] == scored["trials"][0]["conditions"]["keel"]["mean_penalty"]
        assert KEELBENCH.benchmark_transition("VERIFIED", "REQ-1", {"status": "PASS", "requirement_id": "REQ-1", "paired_trial_count": 1, "reproducible_improvement": True})["status"] == "REJECTED"
        assert KEELBENCH.benchmark_transition("IMPLEMENTED", "REQ-1", {"status": "PASS", "requirement_id": "REQ-1", "paired_trial_count": 2, "reproducible_improvement": True})["status"] == "REJECTED"

        for entry in json.loads((trial / "trial.json").read_text())["runs"]:
            path = trial / entry["path"]
            run = json.loads(path.read_text())
            run["metrics"]["task_success"] = entry["condition"] == "keel"
            if entry["condition"] == "baseline": run["critical_violation"] = True
            path.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
        improved = KEELBENCH.score_trials([trial], root)
        assert improved["reproducible_improvement"] is True

        broken = root / "trial-b"
        copy_trial(trial, broken)
        manifest = json.loads((broken / "trial.json").read_text())
        manifest["runs"] = manifest["runs"][:-1]
        (broken / "trial.json").write_text(json.dumps(manifest, indent=2))
        invalid = KEELBENCH.validate_trial(broken, root)
        assert invalid["status"] == "FAIL" and any("exactly one complete" in error for error in invalid["errors"])

        mismatch = root / "trial-c"
        copy_trial(trial, mismatch)
        run_path = mismatch / "r001-keel.json"
        run = json.loads(run_path.read_text())
        run["start_state_digest"] = "wrong"
        run_path.write_text(json.dumps(run, indent=2))
        invalid = KEELBENCH.validate_trial(mismatch, root)
        assert invalid["status"] == "FAIL" and any("start_state_digest" in error for error in invalid["errors"])

        first, second = root / "trial-d1", root / "trial-d2"
        KEELBENCH.new_trial(root, "KB-01-bugfix", 1, "seed-2", "state-2", "digest-2", first)
        KEELBENCH.new_trial(root, "KB-01-bugfix", 1, "seed-2", "state-2", "digest-2", second)
        assert (first / "trial.json").read_text() == (second / "trial.json").read_text()
    print("KEELBench tests PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
