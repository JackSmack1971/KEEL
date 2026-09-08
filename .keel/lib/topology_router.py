"""Read-only constraint projection over the canonical ChangeGraph.

The historical ``recommend`` name is retained for API compatibility, but this
module no longer selects effort, agents, personas, dispatch, or schedules.
"""
from __future__ import annotations

from pathlib import Path

import change_graph
import semantic_kernel as sk


def recommend(source: dict, change_id: str | None = None) -> dict:
    try:
        graph = change_graph.normalize(source)
    except (change_graph.GraphError, TypeError, ValueError) as exc:
        return {"schema_version": 1, "status": "INVALID", "errors": [str(exc)], "read_only": True}
    errors = change_graph.validate(graph)
    if errors: return {"schema_version": 1, "status": "INVALID", "errors": errors, "read_only": True}
    records = [sk.decode(raw) for raw in graph["records"]]
    work = {record.identity: record for record in records if isinstance(record, sk.WorkUnit)}
    if change_id:
        canonical = change_id if change_id.startswith("keel:work-unit:") else f"keel:work-unit:{graph['graph_id']}.{change_id}"
        if canonical not in work: return {"schema_version": 1, "status": "INVALID", "errors": [f"unknown work unit: {change_id}"], "read_only": True}
        selected = [canonical]
    else: selected = sorted(work)
    dependencies = {identity: [] for identity in work}
    for record in records:
        if isinstance(record, sk.Edge) and record.edge_type == "HARD_DEPENDENCY": dependencies[record.source_id].append(record.target_id)
    constraints = {
        identity: {
            "hard_dependencies": sorted(dependencies[identity]),
            "resource_claims": list(work[identity].attributes.get("resource_claims", ())),
            "effect_requests": list(work[identity].attributes.get("effect_requests", ())),
            "evidence_requirements": list(work[identity].attributes.get("evidence_requirements", ())),
        } for identity in selected
    }
    return {"schema_version": 1, "status": "PASS", "graph_id": graph["graph_id"], "constraints": constraints,
            "policy": "read-only-constraints-no-scheduling", "errors": [], "read_only": True}


def load(path: Path) -> dict:
    return change_graph.load(path)
