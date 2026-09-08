"""Temporary mission-v2 read adapter for the canonical ChangeGraph API.

This compatibility module deliberately exposes no v2-native planning model.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import change_graph


IDENTITY = "keel.mission/v2"


def load(path: Path) -> dict[str, Any]:
    return change_graph.load(path)


def normalize(source: dict[str, Any]) -> dict[str, Any]:
    return change_graph.adapt_v2(source)


def normalize_v1(source: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    del root
    return change_graph.adapt_v1(source)


def validate(source: Any, root: Path | None = None, p1: dict[str, Any] | None = None) -> dict[str, Any]:
    del root, p1
    try:
        graph = change_graph.adapt_v2(source)
        errors = change_graph.validate(graph)
        return {"status": "VALID" if not errors else "INVALID", "errors": errors, "identity": IDENTITY,
                "canonical_identity": change_graph.IDENTITY}
    except (change_graph.GraphError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "errors": [str(exc)], "identity": IDENTITY,
                "canonical_identity": change_graph.IDENTITY}


def frontier(source: dict[str, Any], *, state: dict[str, str] | None = None, p1_by_node: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    del p1_by_node
    try:
        return change_graph.frontier(change_graph.adapt_v2(source), state)
    except (change_graph.GraphError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "runnable": [], "blocked": [], "errors": [str(exc)], "read_only": True}


def serialize(source: dict[str, Any]) -> str:
    return change_graph.serialize(change_graph.adapt_v2(source))
