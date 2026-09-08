"""Read-only, deterministic repository intelligence for KEEL P1.

This module consumes supplied repository evidence.  It never executes a discovered
command or treats an implementation-local guess as repository authority.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import fact_graph

SCHEMA_ID = "keel.repository-intelligence"
SCHEMA_VERSION = 1
SCHEMA = f"{SCHEMA_ID}/v{SCHEMA_VERSION}"
FACT_KINDS = {"DIRECT", "NORMALIZED", "DERIVED"}
STATUSES = {"VERIFIED", "UNKNOWN", "UNSUPPORTED", "UNAVAILABLE", "UNVERIFIED_RUNTIME", "AMBIGUOUS", "CONFLICTING", "FAILED", "BLOCKED", "STALE", "PARTIAL", "HISTORICAL/SUPERSEDED"}
NODE_TYPES = {"repository", "directory", "file", "module", "symbol", "package", "service", "test", "command", "configuration", "dependency", "ownership-source", "architecture-source", "generated-artifact", "runtime-surface"}
RELATIONS = {"contains", "member-of", "declares", "depends-on", "generated-from", "produced-by", "owned-by", "governed-by", "architecture-source-for", "command-declared-by", "references", "impacts", "impacted-by"}
COMMAND_SOURCES = ("REPOSITORY_DECLARED", "KEEL_CONFIG_DECLARED", "PROJECT_METADATA_DERIVED", "DISCOVERED_CANDIDATE")
SOURCE_RANK = {name: index for index, name in enumerate(COMMAND_SOURCES)}


class IntelligenceError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors), "warnings": list(self.warnings)}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def repo_path(root: Path, value: str | os.PathLike[str]) -> str:
    """Return a portable repository-relative POSIX path or reject it."""
    raw = os.fspath(value).replace("\\", "/")
    candidate = Path(raw)
    root = root.resolve()
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            raw = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise IntelligenceError("path is outside repository root") from exc
    parsed = PurePosixPath(raw)
    if raw == "" or any(part == ".." for part in parsed.parts):
        raise IntelligenceError("path escapes repository root")
    result = parsed.as_posix()
    return "." if result in {"", "."} else result


def provenance(source_artifact: str | None, source_type: str, adapter: str, *, rule: str | None = None, fact_kind: str = "DIRECT", source_digest: str | None = None, location: str | None = None) -> dict[str, Any]:
    if fact_kind not in FACT_KINDS:
        raise IntelligenceError(f"invalid fact kind: {fact_kind}")
    result = {"source_artifact": source_artifact, "source_type": source_type, "adapter": adapter, "derivation_rule": rule, "fact_kind": fact_kind}
    if source_digest:
        result["source_digest"] = source_digest
    if location:
        result["location"] = location
    return result


def node(node_id: str, node_type: str, status: str, evidence: dict[str, Any], **attributes: Any) -> dict[str, Any]:
    if node_type not in NODE_TYPES or status not in STATUSES:
        raise IntelligenceError("invalid node type or status")
    result = {"id": node_id, "type": node_type, "status": status, "provenance": evidence}
    result.update({key: value for key, value in attributes.items() if value is not None})
    return result


def edge(source: str, target: str, relation: str, status: str, evidence: dict[str, Any], *, inputs: Iterable[str] = ()) -> dict[str, Any]:
    if relation not in RELATIONS or status not in STATUSES:
        raise IntelligenceError("invalid relationship or status")
    result = {"from": source, "to": target, "relation": relation, "status": status, "provenance": evidence}
    values = sorted(set(inputs))
    if values:
        result["input_fact_ids"] = values
    return result


def canonical(document: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize without dropping conflicting evidence or cycles."""
    result = dict(document)
    result["schema_id"] = SCHEMA_ID
    result["schema_version"] = SCHEMA_VERSION
    result["nodes"] = sorted((dict(item) for item in result.get("nodes", [])), key=lambda item: (item.get("type", ""), item.get("id", ""), _json(item)))
    result["edges"] = sorted((dict(item) for item in result.get("edges", [])), key=lambda item: (item.get("relation", ""), item.get("from", ""), item.get("to", ""), item.get("status", ""), (item.get("provenance") or {}).get("source_artifact") or "", (item.get("provenance") or {}).get("derivation_rule") or "", _json(item)))
    return result


def serialize(document: dict[str, Any]) -> str:
    return json.dumps(canonical(document), ensure_ascii=False, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def validate(document: Any, *, expected_schema: str = SCHEMA) -> ValidationResult:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ValidationResult(False, ("document must be an object",))
    if f"{document.get('schema_id')}/v{document.get('schema_version')}" != expected_schema:
        errors.append("schema identity/version mismatch")
    nodes = document.get("nodes", []); edges = document.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        errors.append("nodes and edges must be arrays")
        return ValidationResult(False, tuple(errors))
    ids = set()
    for item in nodes:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str): errors.append("node identity missing")
        else: ids.add(item["id"])
        if isinstance(item, dict) and item.get("type") not in NODE_TYPES: errors.append("invalid node type")
        if isinstance(item, dict) and item.get("status") not in STATUSES: errors.append("invalid node status")
        _validate_provenance(item.get("provenance") if isinstance(item, dict) else None, errors)
    for item in edges:
        if not isinstance(item, dict): errors.append("edge must be an object"); continue
        if item.get("from") not in ids or item.get("to") not in ids: errors.append("edge endpoint is not a declared node")
        if item.get("relation") not in RELATIONS: errors.append("invalid relationship")
        if item.get("status") not in STATUSES: errors.append("invalid edge status")
        _validate_provenance(item.get("provenance"), errors)
        if item.get("status") == "DERIVED" and not item.get("input_fact_ids"): errors.append("derived edge requires input facts")
    return ValidationResult(not errors, tuple(sorted(set(errors))))


def graph_classification(evidence: Any) -> str:
    """Classify graph input without inventing a fact from malformed evidence."""
    if not isinstance(evidence, dict):
        return "FAILED"
    if evidence.get("unsupported_ecosystem"):
        return "UNSUPPORTED"
    if evidence.get("malformed"):
        return "FAILED"
    if evidence.get("conflicting"):
        return "CONFLICTING"
    if evidence.get("missing_optional"):
        return "UNKNOWN"
    return "VERIFIED"


def _validate_provenance(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict): errors.append("provenance missing"); return
    for key in ("source_artifact", "source_type", "adapter", "fact_kind"):
        if key not in value: errors.append(f"provenance missing {key}")
    if value.get("fact_kind") not in FACT_KINDS: errors.append("invalid provenance fact kind")
    if value.get("fact_kind") == "DERIVED" and not value.get("derivation_rule"): errors.append("derived provenance requires derivation rule")


def _status(value: str | None, fallback: str = "UNKNOWN") -> str:
    return value if value in STATUSES else fallback


def command_registry(declarations: Iterable[dict[str, Any]], candidates: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    rows = [dict(item) for item in declarations] + [dict(item, source_class="DISCOVERED_CANDIDATE") for item in candidates]
    if not rows:
        return {"status": "UNKNOWN", "commands": [], "availability": "UNKNOWN"}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in rows:
        identity = item.get("id") or item.get("name") or item.get("argv", [None])[0]
        if not isinstance(identity, str) or identity.startswith(("/", "\\")) or (len(identity) > 1 and identity[1] == ":"):
            item["status"] = "UNKNOWN"; item["portable"] = False; identity = identity or "<invalid>"
        item.setdefault("source_class", "DISCOVERED_CANDIDATE")
        item.setdefault("exists", False)
        item.setdefault("support", "UNKNOWN")
        item.setdefault("runtime_availability", "UNKNOWN")
        item.setdefault("authorization", "UNKNOWN")
        item.setdefault("provenance", provenance(item.get("source_artifact"), "command", "repository-intelligence", fact_kind="DIRECT"))
        grouped.setdefault(identity, []).append(item)
    output = []
    for identity in sorted(grouped):
        values = grouped[identity]
        authorities = {item.get("source_class") for item in values}
        top = min(SOURCE_RANK.get(item.get("source_class"), 99) for item in values)
        selected = [item for item in values if SOURCE_RANK.get(item.get("source_class"), 99) == top]
        conflict = len({_json({key: value for key, value in item.items() if key != "provenance"}) for item in selected}) > 1
        item = dict(sorted(selected, key=_json)[0])
        item["id"] = identity
        item["status"] = "CONFLICTING" if conflict else _status(item.get("status"), "VERIFIED" if item.get("exists") else "UNKNOWN")
        if len(values) > 1 and not conflict and len(authorities) > 1: item["precedence"] = "RESOLVED"
        argv = item.get("argv") or []
        if any(isinstance(value, str) and (value.startswith(("/", "\\\\")) or (len(value) > 1 and value[1] == ":")) for value in argv):
            item["portable"] = False
            item["status"] = "UNKNOWN"
        if item.get("source_class") not in COMMAND_SOURCES: item["status"] = "UNSUPPORTED"
        if item.get("source_class") == "DISCOVERED_CANDIDATE" and item.get("runtime_availability") == "UNKNOWN": item["status"] = "UNVERIFIED_RUNTIME"
        if len(values) > 1 and all(value.get("source_class") == "DISCOVERED_CANDIDATE" for value in values): item["status"] = "AMBIGUOUS"
        output.append(item)
    return {"status": "VERIFIED", "commands": output, "availability": "KNOWN"}


def authority(sources: Iterable[dict[str, Any]], kind: str) -> dict[str, Any]:
    rows = [dict(item) for item in sources]
    if not rows: return {"status": "UNKNOWN", "authority": None, "sources": []}
    rank = {"explicit": 0, "descriptive": 1, "derived": 2, "generated": 3, "historical": 4}
    active = [item for item in rows if item.get("freshness") != "HISTORICAL/SUPERSEDED" and item.get("kind", kind) != "historical"]
    if not active: return {"status": "HISTORICAL/SUPERSEDED", "authority": None, "sources": sorted(rows, key=_json)}
    best = min(rank.get(item.get("authority_class"), 99) for item in active)
    selected = [item for item in active if rank.get(item.get("authority_class"), 99) == best]
    values = {_json(item.get("value")) for item in selected}
    status = "CONFLICTING" if len(values) > 1 else ("AMBIGUOUS" if len(selected) > 1 else _status(selected[0].get("status"), "VERIFIED"))
    chosen = selected[0].get("value") if len(values) == 1 else None
    return {"status": status, "authority": chosen, "sources": sorted(rows, key=_json), "kind": kind}


def freshness(input_digest: str | None, current_digest: str | None, superseded: bool = False) -> str:
    if superseded: return "HISTORICAL/SUPERSEDED"
    if not input_digest or not current_digest: return "UNKNOWN"
    return "VERIFIED" if input_digest == current_digest else "STALE"


def python_dependencies(root: Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    files = sorted(set(paths)); modules = {Path(path).with_suffix("").as_posix().replace("/", "."): path for path in files if path.endswith(".py")}
    edges: list[dict[str, Any]] = []
    for path in files:
        if not path.endswith(".py"): continue
        try: tree = ast.parse((root / path).read_text(encoding="utf-8"), filename=path)
        except (OSError, SyntaxError): edges.append({"source": path, "status": "FAILED", "kind": "UNSUPPORTED_SOURCE"}); continue
        for item in ast.walk(tree):
            targets = [node.name for node in item.names] if isinstance(item, ast.Import) else [item.module or ""] if isinstance(item, ast.ImportFrom) else []
            for target in targets:
                resolved = modules.get(target) or modules.get(target.split(".")[0])
                edges.append({"source": path, "target": resolved or target, "status": "VERIFIED" if resolved else "PARTIAL", "kind": "DIRECT_PARSED" if resolved else "EXTERNAL", "adapter": "python-ast"})
    return sorted(edges, key=_json)


def dependency_facts(facts: Iterable[dict[str, Any]], *, ecosystem: str | None = None) -> list[dict[str, Any]]:
    if ecosystem not in {None, "python", "keel-json"}: return [{"status": "UNSUPPORTED", "kind": "UNSUPPORTED_SOURCE"}]
    return sorted((dict(item) for item in facts), key=_json)


def changed_paths(root: Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    result = []
    for value in paths:
        try: result.append({"path": repo_path(root, value), "status": "VERIFIED"})
        except IntelligenceError: result.append({"path": str(value).replace("\\", "/"), "status": "UNKNOWN"})
    return sorted(result, key=_json)


def impact(document: dict[str, Any], paths: Iterable[str], root: Path) -> dict[str, Any]:
    normalized = changed_paths(root, paths); ids = {row["path"] for row in normalized if row["status"] == "VERIFIED"}
    edges = []
    for item in document.get("edges", []):
        if item.get("from") in ids or item.get("to") in ids:
            derived = dict(item); derived["relation"] = "impacts"; derived["provenance"] = provenance("<impact>", "derived-impact", "repository-intelligence", rule="changed-path-graph-projection", fact_kind="DERIVED"); derived["input_fact_ids"] = [digest(item)]
            edges.append(derived)
    return {"status": "VERIFIED" if normalized and all(row["status"] == "VERIFIED" for row in normalized) else "UNKNOWN", "read_only": True, "changed_paths": normalized, "edges": sorted(edges, key=_json)}


def generated_artifact(artifact: str, *, producer: str | None, input_digest: str | None = None, artifact_digest: str | None = None, claimed_generated: bool = True, producer_conflict: bool = False) -> dict[str, Any]:
    if not claimed_generated: return {"artifact": artifact, "status": "UNKNOWN", "generated": False, "reason": "hand-maintained claim rejected"}
    if producer_conflict: return {"artifact": artifact, "status": "CONFLICTING", "generated": True}
    if not producer: return {"artifact": artifact, "status": "BLOCKED", "generated": True}
    state = freshness(input_digest, artifact_digest)
    return {"artifact": artifact, "status": "VERIFIED" if state == "VERIFIED" else "STALE" if state == "STALE" else "UNKNOWN", "generated": True, "producer": producer}


def collect(root: Path, *, paths: Iterable[str] = ()) -> dict[str, Any]:
    requested = sorted(repo_path(root, path) for path in paths)
    graph = fact_graph.build(root)
    resources = {fact.subject: fact for fact in graph.select("resource") if not requested or fact.subject in requested or fact.subject == "."}
    nodes = []
    for path, fact in sorted(resources.items()):
        source_type = "repository" if path == "." else "repository-file"
        nodes.append(node(path, "repository" if path == "." else "file", "VERIFIED", provenance(fact.provenance.source, source_type, fact.provenance.adapter, fact_kind="DIRECT", source_digest=fact.provenance.source_digest)))
    edges = []
    for relation in graph.edges:
        if relation.relation != "depends-on" or (requested and relation.source not in requested):
            continue
        if relation.source not in resources:
            continue
        if relation.target not in resources:
            resources[relation.target] = None
            nodes.append(node(relation.target, "package" if relation.target.startswith("external:") else "file", "UNKNOWN" if relation.target.startswith("external:") else "VERIFIED", provenance(relation.provenance.source, "dependency", relation.provenance.adapter, fact_kind="NORMALIZED", source_digest=relation.provenance.source_digest)))
        edges.append(edge(relation.source, relation.target, "depends-on", "VERIFIED" if relation.knowledge == "KNOWN" else "PARTIAL", provenance(relation.provenance.source, "dependency", relation.provenance.adapter, fact_kind="NORMALIZED", source_digest=relation.provenance.source_digest)))
    return canonical({"schema_id": SCHEMA_ID, "schema_version": SCHEMA_VERSION, "nodes": nodes, "edges": edges, "policy": "advisory-evidence-only", "canonical_source": fact_graph.SCHEMA, "canonical_source_digest": graph.source_digest})
