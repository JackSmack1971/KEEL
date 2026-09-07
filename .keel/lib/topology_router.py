from __future__ import annotations
import json
from pathlib import Path
import mission_graph

def recommend(mission: dict, change_id: str | None = None) -> dict:
    errors = mission_graph.validate(mission)
    if errors:
        return {"schema_version": 1, "status": "INVALID", "errors": errors}
    work = mission["work"]
    selected = [change_id] if change_id else sorted(work)
    unknown = sorted(set(selected) - set(work))
    if unknown:
        return {"schema_version": 1, "status": "INVALID", "errors": [f"unknown work item: {item}" for item in unknown]}
    recommendations = {}
    for node in selected:
        item, dependencies = work[node], len(work[node].get("depends_on", []))
        risk = item["risk"]
        if risk == "trivial":
            values = ("trivial", "fast", ["executor", "verifier"], "focused")
        elif risk == "high" and dependencies >= 3:
            values = ("critical", "max", ["explorer", "risk-reviewer", "executor", "verifier", "reviewer"], "full")
        elif risk == "high" or dependencies >= 2:
            values = ("complex", "deep", ["explorer", "risk-reviewer", "executor", "verifier", "reviewer"], "broad")
        else:
            values = ("standard", "balanced", ["explorer", "executor", "verifier"], "standard")
        complexity, effort, roles, breadth = values
        recommendations[node] = {"complexity": complexity, "effort_capability": effort, "roles": roles, "verification_breadth": breadth, "dependency_count": dependencies, "risk": risk}
    return {"schema_version": 1, "status": "PASS", "mission_id": mission["mission_id"], "recommendations": recommendations, "policy": "advisory-capabilities-only", "errors": []}

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
