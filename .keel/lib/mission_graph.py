"""Temporary mission-v1 read adapter for the canonical ChangeGraph API."""
from __future__ import annotations

from pathlib import Path

import change_graph


def load(path: Path) -> dict:
    return change_graph.load(path)


def normalize(mission: dict) -> dict:
    return change_graph.adapt_v1(mission)


def validate(mission: dict) -> list[str]:
    try:
        return change_graph.validate(normalize(mission))
    except (change_graph.GraphError, TypeError, ValueError) as exc:
        return [str(exc)]


def plan(root: Path, mission: dict, state: dict[str, str] | None = None) -> dict:
    del root
    try:
        return change_graph.frontier(normalize(mission), state)
    except (change_graph.GraphError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "runnable": [], "blocked": [], "errors": [str(exc)], "read_only": True}
