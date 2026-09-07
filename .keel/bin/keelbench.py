#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
ROOT_DEFAULT = HERE.parents[2]
CONDITIONS = ("baseline", "keel")
REQUIRED_SCENARIOS = {"bugfix", "feature", "refactor", "dependency-upgrade", "migration", "security-remediation", "frontend-change", "performance-regression", "brownfield-investigation", "multi-service-change", "release", "failure-recovery"}
REQUIRED_METRICS = {"task_success", "acceptance_coverage", "introduced_regressions", "scope_violations", "unauthorized_effects", "human_interventions", "tokens", "wall_time_sec", "tool_calls", "commands", "retries", "merge_conflicts", "ci_failures", "review_findings"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(root: Path, scenario_id: str) -> dict:
    corpus = load(root / ".keel/bench/corpus.json")
    row = next((x for x in corpus.get("scenarios", []) if x.get("id") == scenario_id), None)
    if row is None:
        raise RuntimeError(f"unknown scenario id: {scenario_id}")
    return row


def validate(root: Path) -> list[str]:
    errors = []
    try:
        corpus = load(root / ".keel/bench/corpus.json")
    except Exception as exc:
        return [f"corpus invalid: {exc}"]
    try:
        schema = load(root / ".keel/bench/telemetry-schema.json")
    except Exception as exc:
        return [f"telemetry schema invalid: {exc}"]
    scenarios = [x for x in corpus.get("scenarios", []) if isinstance(x, dict)]
    missing = sorted(REQUIRED_SCENARIOS - {x.get("type") for x in scenarios})
    if missing:
        errors.append("missing benchmark scenario types: " + ", ".join(missing))
    ids = [x.get("id") for x in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("duplicate benchmark scenario ids")
    missing_metrics = sorted(REQUIRED_METRICS - set(schema.get("run_metrics", [])))
    if missing_metrics:
        errors.append("telemetry schema missing metrics: " + ", ".join(missing_metrics))
    if "equivalent starting state" not in schema.get("comparison_rule", ""):
        errors.append("telemetry schema comparison_rule must require equivalent starting state")
    return errors


def _trial_id(scenario_id: str, seed: str, start_state_id: str, rubric_version: str) -> str:
    raw = "\0".join((scenario_id, seed, start_state_id, rubric_version))
    return "trial-" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _run_payload(trial: dict, condition: str, replicate: int) -> dict:
    return {
        "schema_version": 2,
        "run_id": f"{trial['trial_id']}-r{replicate:03d}-{condition}",
        "trial_id": trial["trial_id"],
        "scenario_id": trial["scenario_id"],
        "scenario_type": trial["scenario_type"],
        "condition": condition,
        "replicate": replicate,
        "seed": trial["seed"],
        "start_state_id": trial["start_state_id"],
        "start_state_digest": trial["start_state_digest"],
        "rubric_version": trial["rubric_version"],
        "status": "PENDING",
        "metrics": {key: None for key in sorted(REQUIRED_METRICS)},
        "events": [],
        "critical_violation": False,
        "notes": "",
    }


def new_trial(root: Path, scenario_id: str, replicates: int, seed: str, start_state_id: str, start_state_digest: str, out: Path) -> None:
    if replicates < 1:
        raise RuntimeError("replicates must be >= 1")
    scenario = _scenario(root, scenario_id)
    rubric = str(scenario.get("rubric_version", "1"))
    trial = {"schema_version": 2, "trial_id": _trial_id(scenario_id, seed, start_state_id, rubric), "scenario_id": scenario_id, "scenario_type": scenario["type"], "rubric_version": rubric, "seed": seed, "replicates": replicates, "start_state_id": start_state_id, "start_state_digest": start_state_digest, "conditions": list(CONDITIONS), "status": "PLANNED", "runs": []}
    out.mkdir(parents=True, exist_ok=True)
    for replicate in range(1, replicates + 1):
        for condition in CONDITIONS:
            name = f"r{replicate:03d}-{condition}.json"
            payload = _run_payload(trial, condition, replicate)
            (out / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            trial["runs"].append({"run_id": payload["run_id"], "condition": condition, "replicate": replicate, "path": name})
    (out / "trial.json").write_text(json.dumps(trial, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def new_run(root: Path, scenario: str, condition: str, out: Path, trial_id: str | None = None, replicate: int | None = None, seed: str | None = None, start_state_id: str = "", start_state_digest: str = "") -> None:
    row = _scenario(root, scenario)
    payload = {"schema_version": 2, "run_id": out.stem, "trial_id": trial_id, "scenario_id": scenario, "scenario_type": row["type"], "condition": condition, "replicate": replicate, "seed": seed, "start_state_id": start_state_id, "start_state_digest": start_state_digest, "rubric_version": str(row.get("rubric_version", "1")), "status": "PENDING", "metrics": {key: None for key in sorted(REQUIRED_METRICS)}, "events": [], "critical_violation": False, "notes": ""}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_run_path(trial_dir: Path, rel: str) -> Path:
    path = (trial_dir / rel).resolve()
    try:
        path.relative_to(trial_dir.resolve())
    except ValueError:
        raise RuntimeError(f"run path escapes trial directory: {rel}")
    return path


def validate_trial(trial_dir: Path, root: Path) -> dict:
    errors = []
    event_types = set(load(root / ".keel/bench/telemetry-schema.json").get("event_types", []))
    try:
        trial = load(trial_dir / "trial.json")
    except Exception as exc:
        return {"status": "FAIL", "errors": [f"trial manifest invalid: {exc}"]}
    required = ("trial_id", "scenario_id", "scenario_type", "rubric_version", "seed", "replicates", "start_state_id", "start_state_digest", "conditions", "runs")
    errors.extend(f"trial manifest missing {key}" for key in required if key not in trial)
    if errors:
        return {"status": "FAIL", "errors": errors}
    try:
        scenario = _scenario(root, trial["scenario_id"])
        if trial["scenario_type"] != scenario.get("type"):
            errors.append("trial scenario_type disagrees with corpus")
        if str(trial["rubric_version"]) != str(scenario.get("rubric_version", "1")):
            errors.append("trial rubric_version disagrees with corpus")
    except Exception as exc:
        errors.append(str(exc))
    if trial.get("conditions") != list(CONDITIONS):
        errors.append("trial conditions must be exactly baseline and keel")
    if not isinstance(trial.get("replicates"), int) or trial["replicates"] < 1:
        errors.append("trial replicates must be a positive integer")
    if not isinstance(trial.get("start_state_id"), str) or not trial["start_state_id"].strip():
        errors.append("trial start_state_id is required")
    if not isinstance(trial.get("start_state_digest"), str) or not trial["start_state_digest"].strip():
        errors.append("trial start_state_digest is required")
    entries = trial.get("runs") if isinstance(trial.get("runs"), list) else []
    expected = {(condition, replicate) for replicate in range(1, trial.get("replicates", 0) + 1) for condition in CONDITIONS}
    seen, runs = set(), []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("run manifest entries must be objects")
            continue
        key = (entry.get("condition"), entry.get("replicate"))
        if key in seen:
            errors.append(f"duplicate run pair: {key}")
        seen.add(key)
        try:
            run = load(_safe_run_path(trial_dir, entry["path"]))
        except Exception as exc:
            errors.append(f"run {entry.get('run_id')} invalid: {exc}")
            continue
        runs.append(run)
        for key_name in ("trial_id", "scenario_id", "scenario_type", "seed", "start_state_id", "start_state_digest", "rubric_version"):
            if run.get(key_name) != trial.get(key_name):
                errors.append(f"run {run.get('run_id')} {key_name} disagrees with trial")
        if run.get("condition") not in CONDITIONS or run.get("replicate") not in range(1, trial["replicates"] + 1):
            errors.append(f"run {run.get('run_id')} has invalid condition or replicate")
        if run.get("status") != "COMPLETE":
            errors.append(f"run {run.get('run_id')} is not COMPLETE")
        metrics = run.get("metrics") if isinstance(run.get("metrics"), dict) else {}
        missing = sorted(REQUIRED_METRICS - set(metrics))
        if missing:
            errors.append(f"run {run.get('run_id')} missing metrics: {', '.join(missing)}")
        elif any(metrics[key] is None for key in REQUIRED_METRICS):
            errors.append(f"run {run.get('run_id')} contains incomplete metrics")
        elif not isinstance(metrics.get("task_success"), bool) or any(isinstance(metrics[key], bool) or not isinstance(metrics[key], (int, float)) for key in REQUIRED_METRICS - {"task_success"}):
            errors.append(f"run {run.get('run_id')} contains incorrectly typed metrics")
        events = run.get("events")
        if not isinstance(events, list):
            errors.append(f"run {run.get('run_id')} events must be a list")
        else:
            for event in events:
                if not isinstance(event, dict) or event.get("type") not in event_types:
                    errors.append(f"run {run.get('run_id')} contains an unknown telemetry event type")
    if seen != expected:
        errors.append("trial must contain exactly one complete baseline/keel pair for every replicate")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "trial_id": trial.get("trial_id"), "scenario_id": trial.get("scenario_id"), "replicates": trial.get("replicates"), "runs": runs}


def _metric_summary(rows: list[dict]) -> dict:
    result = {}
    for metric in ("tokens", "wall_time_sec", "tool_calls", "commands", "human_interventions"):
        values = [row["metrics"].get(metric) for row in rows if isinstance(row["metrics"].get(metric), (int, float))]
        result[f"median_{metric}"] = None if not values else statistics.median(values)
    successes = [1.0 if row["metrics"].get("task_success") is True else 0.0 for row in rows]
    result["task_success_rate"] = None if not successes else sum(successes) / len(successes)
    result["mean_acceptance_coverage"] = statistics.mean(row["metrics"]["acceptance_coverage"] for row in rows)
    return result


def score_trials(paths: list[Path], root: Path) -> dict:
    trial_results, errors = [], []
    for path in paths:
        trial_dir = path if path.is_dir() else path.parent
        result = validate_trial(trial_dir, root)
        if result["status"] != "PASS":
            errors.extend(f"{trial_dir}: {error}" for error in result["errors"])
            continue
        runs = {(run["condition"], run["replicate"]): run for run in result["runs"]}
        pairs = []
        for replicate in range(1, result["replicates"] + 1):
            baseline, keel = runs[("baseline", replicate)], runs[("keel", replicate)]
            pairs.append({"replicate": replicate, "baseline": baseline["metrics"], "keel": keel["metrics"], "task_success_delta": (1 if keel["metrics"]["task_success"] else 0) - (1 if baseline["metrics"]["task_success"] else 0), "acceptance_coverage_delta": keel["metrics"]["acceptance_coverage"] - baseline["metrics"]["acceptance_coverage"]})
        baseline_rows = [runs[("baseline", r)] for r in range(1, result["replicates"] + 1)]
        keel_rows = [runs[("keel", r)] for r in range(1, result["replicates"] + 1)]
        trial_results.append({"trial_id": result["trial_id"], "scenario_id": result["scenario_id"], "replicates": result["replicates"], "pairs": pairs, "conditions": {"baseline": _metric_summary(baseline_rows), "keel": _metric_summary(keel_rows)}})
    output = {"schema_version": 2, "status": "PASS" if not errors else "FAIL", "errors": errors, "trials": trial_results, "empirical_claim": "UNVALIDATED"}
    if trial_results:
        baseline_rate = statistics.mean(t["conditions"]["baseline"]["task_success_rate"] for t in trial_results)
        keel_rate = statistics.mean(t["conditions"]["keel"]["task_success_rate"] for t in trial_results)
        error_reduction = None if baseline_rate >= 1 else ((1 - baseline_rate) - (1 - keel_rate)) / (1 - baseline_rate)
        output["comparison"] = {"paired_trial_count": len(trial_results), "baseline_task_success_rate": baseline_rate, "keel_task_success_rate": keel_rate, "absolute_task_success_uplift": keel_rate - baseline_rate, "relative_error_reduction": error_reduction, "paired_task_success_deltas": [pair["task_success_delta"] for t in trial_results for pair in t["pairs"]]}
    return output


def legacy_score(paths: list[Path]) -> dict:
    """Keep old fixture compatibility, explicitly excluding it from empirical claims."""
    rows = []
    for path in paths:
        for file in sorted(path.glob("*.json")) if path.is_dir() else [path]:
            try:
                rows.append(load(file))
            except Exception:
                pass
    groups = {condition: [row.get("metrics") or {} for row in rows if row.get("condition") == condition] for condition in CONDITIONS}
    output = {"schema_version": 1, "runs": {key: len(value) for key, value in groups.items()}, "conditions": {}, "empirical_claim": "UNVALIDATED", "legacy_unpaired": True}
    for condition, values in groups.items():
        successes = [1.0 if value.get("task_success") is True else 0.0 for value in values if value.get("task_success") is not None]
        output["conditions"][condition] = {"task_success_rate": None if not successes else sum(successes) / len(successes)}
    if all(output["conditions"][condition]["task_success_rate"] is not None for condition in CONDITIONS):
        baseline_rate = output["conditions"]["baseline"]["task_success_rate"]
        keel_rate = output["conditions"]["keel"]["task_success_rate"]
        output["comparison"] = {"absolute_task_success_uplift": keel_rate - baseline_rate, "relative_error_reduction": None if baseline_rate >= 1 else ((1 - baseline_rate) - (1 - keel_rate)) / (1 - baseline_rate), "paired": False}
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="KEELBench reproducible paired-evaluation harness")
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    trial = sub.add_parser("new-trial")
    trial.add_argument("--scenario", required=True); trial.add_argument("--replicates", type=int, default=1); trial.add_argument("--seed", required=True); trial.add_argument("--start-state-id", required=True); trial.add_argument("--start-state-digest", required=True); trial.add_argument("--out", type=Path, required=True)
    run = sub.add_parser("new-run")
    run.add_argument("--scenario", required=True); run.add_argument("--condition", choices=CONDITIONS, required=True); run.add_argument("--out", type=Path, required=True); run.add_argument("--trial-id"); run.add_argument("--replicate", type=int); run.add_argument("--seed"); run.add_argument("--start-state-id", default=""); run.add_argument("--start-state-digest", default="")
    score = sub.add_parser("score"); score.add_argument("paths", nargs="+", type=Path)
    check = sub.add_parser("validate-trial"); check.add_argument("trial", type=Path)
    args = parser.parse_args(); root = args.root.resolve()
    try:
        if args.cmd == "validate":
            errors = validate(root); print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors}, indent=2)); return 0 if not errors else 1
        if args.cmd == "new-trial":
            new_trial(root, args.scenario, args.replicates, args.seed, args.start_state_id, args.start_state_digest, args.out); print(args.out); return 0
        if args.cmd == "new-run":
            new_run(root, args.scenario, args.condition, args.out, args.trial_id, args.replicate, args.seed, args.start_state_id, args.start_state_digest); print(args.out); return 0
        if args.cmd == "validate-trial":
            result = validate_trial(args.trial.resolve(), root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "PASS" else 1
        if args.cmd == "score":
            result = score_trials(args.paths, root) if any(path.is_dir() and (path / "trial.json").is_file() for path in args.paths) else legacy_score(args.paths)
            print(json.dumps(result, indent=2, sort_keys=True)); return 0 if result.get("status", "PASS") == "PASS" else 1
    except Exception as exc:
        print(f"KEELBENCH ERROR: {exc}", file=sys.stderr); return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
