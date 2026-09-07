from __future__ import annotations

import json
from pathlib import Path


UNAVAILABLE = {"value": None, "status": "UNAVAILABLE", "source": "runtime instrumentation not present"}


def summarize(verification_path: Path, runtime_path: Path | None = None) -> dict:
    if not verification_path.is_file():
        return {"schema_version": 1, "status": "UNAVAILABLE", "read_only": True, "source": str(verification_path), "metrics": {"checks_total": {"value": None, "status": "UNAVAILABLE", "source": "verification.json missing"}}}
    try:
        document = json.loads(verification_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"schema_version": 1, "status": "INVALID", "read_only": True, "source": str(verification_path), "errors": [f"verification JSON invalid: {type(exc).__name__}"]}
    checks = document.get("checks") if isinstance(document.get("checks"), list) else []
    durations = [row.get("duration_ms", 0) for row in checks if isinstance(row, dict) and isinstance(row.get("duration_ms", 0), (int, float))]
    passed = sum(1 for row in checks if isinstance(row, dict) and row.get("exit_code") == 0)
    failed = sum(1 for row in checks if isinstance(row, dict) and row.get("exit_code") not in (0, None))
    metrics = {
        "checks_total": {"value": len(checks), "status": "MEASURED", "source": "verification.json.checks"},
        "checks_passed": {"value": passed, "status": "MEASURED", "source": "verification.json.checks.exit_code"},
        "checks_failed": {"value": failed, "status": "MEASURED", "source": "verification.json.checks.exit_code"},
        "wall_time_ms": {"value": sum(durations), "status": "MEASURED", "source": "verification.json.checks.duration_ms"},
        "commands": {"value": len(checks), "status": "MEASURED", "source": "verification.json.checks"},
        "tokens": UNAVAILABLE,
        "cost": UNAVAILABLE,
        "human_interventions": UNAVAILABLE,
        "retries": UNAVAILABLE,
        "merge_conflicts": UNAVAILABLE,
    }
    sources = [str(verification_path)]
    if runtime_path is not None and runtime_path.is_file():
        try: runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        except (OSError, ValueError): runtime = {}
        supplied = runtime.get("metrics") if isinstance(runtime, dict) else {}
        if isinstance(supplied, dict):
            for key in ("tokens", "cost", "human_interventions", "retries", "merge_conflicts"):
                value = supplied.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool): metrics[key] = {"value": value, "status": "MEASURED", "source": f"{runtime_path.name}.metrics.{key}"}
            sources.append(str(runtime_path))
    return {"schema_version": 1, "status": "PASS", "read_only": True, "source": sources, "verification_status": document.get("status"), "metrics": metrics}


def for_change(root: Path, change_id: str | None) -> dict:
    if not change_id:
        return {"schema_version": 1, "status": "UNAVAILABLE", "read_only": True, "error": "change_id is required", "metrics": {}}
    path = root / ".keel" / "ledger" / change_id / "verification.json"
    result = summarize(path)
    result["change_id"] = change_id
    return result
