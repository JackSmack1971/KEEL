"""Read-only keel.mission/v2 schema and planning contract.

This module validates and projects supplied mission/P1 evidence.  It never
changes ledgers, allocates resources, invokes providers, or executes effects.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_ID = "keel.mission"
SCHEMA_VERSION = 2
IDENTITY = f"{SCHEMA_ID}/v{SCHEMA_VERSION}"
V1_IDENTITY = "keel.mission/v1"
MISSION_STATUSES = {"VALID", "INVALID", "BLOCKED", "DEFERRED", "UNKNOWN", "RUNTIME_REQUIRED", "MIGRATION_REQUIRED", "UNSUPPORTED"}
DEPENDENCY_TYPES = {"HARD_PREREQUISITE", "ORDERING_ONLY", "ARTIFACT_DATA", "REVIEW_VERIFICATION", "INTEGRATION"}
CAPABILITY_STATES = {"STATIC_VERIFIED", "RUNTIME_REQUIRED", "UNKNOWN", "UNSUPPORTED", "UNAVAILABLE"}
EFFECTS = {"filesystem.write", "git.local.commit", "git.remote.push", "vcs.merge", "package.publish", "database.migrate", "cloud.deploy", "infra.apply", "issue.modify", "email.send", "secret.read"}
_IDENTITY_VALUES = {"hostname", "host", "process_id", "pid", "timestamp", "created_at", "absolute_path", "environment", "env"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _path(root: Path, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("INVALID_SCOPE")
    raw = value.replace("\\", "/")
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            raw = candidate.resolve().relative_to(root.resolve()).as_posix()
        except ValueError as exc:
            raise ValueError("INVALID_SCOPE") from exc
    parsed = PurePosixPath(raw)
    if any(part in {"..", ""} for part in parsed.parts) or raw.startswith("/"):
        raise ValueError("INVALID_SCOPE")
    return parsed.as_posix() or "."


def _error(code: str, node_id: str | None = None, detail: str | None = None) -> dict[str, str]:
    result = {"classification": code.split("/", 1)[0], "code": code}
    if node_id:
        result["node_id"] = node_id
    if detail:
        result["detail"] = detail
    return result


def canonical(document: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with stable key-independent array ordering."""
    result = json.loads(json.dumps(document, ensure_ascii=False))
    result["schema_id"] = SCHEMA_ID
    result["schema_version"] = SCHEMA_VERSION
    result["identity"] = IDENTITY
    if isinstance(result.get("nodes"), list):
        result["nodes"] = sorted(result["nodes"], key=lambda x: x.get("node_id", "") if isinstance(x, dict) else "")
        for node in result["nodes"]:
            if not isinstance(node, dict):
                continue
            for key in ("dependencies", "required_capabilities", "authorization_refs", "inputs", "expected_outputs"):
                if isinstance(node.get(key), list):
                    node[key] = sorted(node[key], key=_json)
    if isinstance(result.get("dependencies"), list):
        result["dependencies"] = sorted(result["dependencies"], key=lambda x: (x.get("from", ""), x.get("to", ""), x.get("type", "")))
    return result


def serialize(document: dict[str, Any]) -> str:
    return json.dumps(canonical(document), ensure_ascii=False, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def _provenance(value: Any, errors: list[dict[str, str]], where: str) -> None:
    if not isinstance(value, dict) or not value.get("source_schema") or not value.get("source_digest"):
        errors.append(_error("INVALID/INVALID_PROVENANCE", detail=where))


def validate(mission: Any, root: Path | None = None, p1: dict[str, Any] | None = None) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve()
    errors: list[dict[str, str]] = []
    if not isinstance(mission, dict):
        return {"status": "INVALID", "errors": [_error("INVALID/INVALID_MISSION")]}
    if mission.get("schema_id") != SCHEMA_ID or mission.get("schema_version") != SCHEMA_VERSION or mission.get("identity") != IDENTITY:
        errors.append(_error("INVALID/INVALID_SCHEMA_IDENTITY"))
    required = ("mission_id", "objective", "success_criteria", "nodes", "dependencies", "planning_status", "provenance", "serialization_policy")
    for field in required:
        if field not in mission:
            errors.append(_error("INVALID/MISSING_REQUIRED_FIELD", detail=field))
    if not isinstance(mission.get("mission_id"), str) or not mission.get("mission_id"):
        errors.append(_error("INVALID/INVALID_MISSION_ID"))
    if not isinstance(mission.get("objective"), str) or not mission.get("objective", "").strip():
        errors.append(_error("INVALID/INVALID_OBJECTIVE"))
    if not isinstance(mission.get("success_criteria"), list) or not mission.get("success_criteria") or not all(isinstance(x, str) and x.strip() for x in mission.get("success_criteria", [])):
        errors.append(_error("INVALID/INVALID_ACCEPTANCE_CRITERIA"))
    _provenance(mission.get("provenance"), errors, "mission")
    nodes = mission.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append(_error("INVALID/MISSING_NODES")); nodes = []
    ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("node_id"), str) or not node.get("node_id"):
            errors.append(_error("INVALID/INVALID_NODE")); continue
        node_id = node["node_id"]
        if node_id in ids: errors.append(_error("INVALID/DUPLICATE_NODE", node_id)); continue
        ids.add(node_id)
        for field in ("objective", "scope", "acceptance_criteria", "dependencies", "required_capabilities", "capability_state", "allowed_effects", "authorization_refs", "resources", "exclusivity", "inputs", "expected_outputs", "verification_policy", "review_policy", "retry_policy", "integration_policy", "lifecycle_expectations", "provenance", "uncertainty", "planning_status"):
            if field not in node: errors.append(_error("INVALID/MISSING_NODE_FIELD", node_id, field))
        try: _path(root, node.get("scope"))
        except ValueError: errors.append(_error("INVALID/INVALID_SCOPE", node_id))
        if not isinstance(node.get("acceptance_criteria"), list) or not node.get("acceptance_criteria") or not all(isinstance(x, str) and x.strip() for x in node.get("acceptance_criteria", [])):
            errors.append(_error("INVALID/INVALID_ACCEPTANCE_CRITERIA", node_id))
        _provenance(node.get("provenance"), errors, node_id)
        states = node.get("capability_state", {})
        if not isinstance(states, dict): states = {}
        for cap in node.get("required_capabilities", []) if isinstance(node.get("required_capabilities"), list) else []:
            state = states.get(cap, "UNKNOWN")
            if state not in CAPABILITY_STATES: errors.append(_error("INVALID/INVALID_CAPABILITY_STATE", node_id, cap))
            if state == "UNSUPPORTED": errors.append(_error("BLOCKED/UNSUPPORTED_CAPABILITY", node_id, cap))
    deps = mission.get("dependencies")
    if not isinstance(deps, list): deps = []; errors.append(_error("INVALID/INVALID_DEPENDENCIES"))
    seen: set[tuple[str, str, str]] = set()
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in ids}
    for dep in deps:
        if not isinstance(dep, dict) or dep.get("type") not in DEPENDENCY_TYPES:
            errors.append(_error("INVALID/INVALID_DEPENDENCY_TYPE")); continue
        edge = (dep.get("from"), dep.get("to"), dep.get("type"))
        if edge in seen: errors.append(_error("INVALID/DUPLICATE_DEPENDENCY")); continue
        seen.add(edge)
        if dep.get("from") == dep.get("to"): errors.append(_error("INVALID/SELF_DEPENDENCY", dep.get("from"))); continue
        if dep.get("from") not in ids or dep.get("to") not in ids: errors.append(_error("INVALID/MISSING_DEPENDENCY")); continue
        adjacency[dep["to"]].append(dep["from"])
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node_id: str) -> None:
        if node_id in visiting: errors.append(_error("INVALID/DEPENDENCY_CYCLE", node_id)); return
        if node_id in visited: return
        visiting.add(node_id)
        for parent in adjacency.get(node_id, []): visit(parent)
        visiting.remove(node_id); visited.add(node_id)
    for node_id in sorted(ids): visit(node_id)
    resources: dict[str, str] = {}
    for node in nodes:
        if not isinstance(node, dict): continue
        for resource in node.get("resources", []) if isinstance(node.get("resources"), list) else []:
            if isinstance(resource, str): rid, exclusive = resource, True
            elif isinstance(resource, dict): rid, exclusive = resource.get("id"), bool(resource.get("exclusive", False))
            else: rid, exclusive = None, False
            if exclusive and rid in resources and resources[rid] != node.get("node_id"):
                errors.append(_error("BLOCKED/RESOURCE_CONFLICT", node.get("node_id"), rid))
            if exclusive and rid: resources[rid] = node.get("node_id")
        for effect in node.get("allowed_effects", []) if isinstance(node.get("allowed_effects"), list) else []:
            if effect not in EFFECTS: errors.append(_error("BLOCKED/UNKNOWN_EFFECT", node.get("node_id"), str(effect)))
        allowed = set(node.get("allowed_effects", []))
        auth = mission.get("authorizations", {})
        refs = node.get("authorization_refs", [])
        if allowed and not refs: errors.append(_error("BLOCKED/MISSING_AUTHORIZATION", node.get("node_id")))
        granted = set()
        for ref in refs if isinstance(refs, list) else []:
            record = auth.get(ref) if isinstance(auth, dict) else None
            if not isinstance(record, dict): continue
            granted.update(record.get("effects", []))
        if allowed - granted and refs: errors.append(_error("BLOCKED/EFFECT_AUTHORIZATION_EXCEEDED", node.get("node_id")))
    if isinstance(p1, dict):
        state = p1.get("status")
        if state in {"CONFLICTING", "AMBIGUOUS"}: errors.append(_error(state))
        if state == "UNSUPPORTED": errors.append(_error("UNSUPPORTED/P1_EVIDENCE"))
    status = "INVALID" if any(e["classification"] == "INVALID" for e in errors) else "BLOCKED" if errors else "VALID"
    return {"status": status, "errors": sorted(errors, key=_json), "identity": IDENTITY}


def normalize_v1(v1: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    if not isinstance(v1, dict) or v1.get("schema_version") != 1:
        return {"status": "UNSUPPORTED", "errors": [_error("UNSUPPORTED/SOURCE_SCHEMA")]}
    source = json.loads(json.dumps(v1, ensure_ascii=False, sort_keys=True))
    nodes = []
    for node_id, item in sorted(v1.get("work", {}).items()):
        deps = item.get("depends_on", []) if isinstance(item, dict) else []
        nodes.append({"node_id": node_id, "objective": f"v1 work item {node_id}", "scope": ".", "acceptance_criteria": ["UNKNOWN: v1 did not specify node acceptance"], "dependencies": sorted(deps), "required_capabilities": [], "capability_state": {}, "allowed_effects": [], "authorization_refs": [], "resources": [], "exclusivity": False, "inputs": [], "expected_outputs": [], "verification_policy": {"status": "UNKNOWN"}, "review_policy": {"status": "UNKNOWN"}, "retry_policy": {"status": "UNKNOWN"}, "integration_policy": {"status": "UNKNOWN"}, "lifecycle_expectations": {"status": "UNKNOWN"}, "provenance": {"source_schema": V1_IDENTITY, "source_digest": digest(source), "adapter": "v1-to-v2", "rule": "preserve-work-item-meaning"}, "uncertainty": ["UNKNOWN: v1 omitted v2 planning fields"], "planning_status": "MIGRATION_REQUIRED"})
    dependencies = [{"from": node_id, "to": dep, "type": "HARD_PREREQUISITE"} for node_id, item in sorted(v1.get("work", {}).items()) for dep in sorted(item.get("depends_on", []))]
    return {"schema_id": SCHEMA_ID, "schema_version": 2, "identity": IDENTITY, "mission_id": v1.get("mission_id"), "objective": v1.get("objective"), "success_criteria": list(v1.get("success_criteria", [])), "nodes": nodes, "dependencies": dependencies, "planning_status": "MIGRATION_REQUIRED", "provenance": {"source_schema": V1_IDENTITY, "source_digest": digest(source), "adapter": "v1-to-v2", "rule": "preserve-v1-meaning"}, "serialization_policy": {"encoding": "UTF-8", "line_endings": "LF", "ordering": "canonical", "identity_values": "forbidden"}, "authorizations": {}}


def frontier(mission: dict[str, Any], *, p1_by_node: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    check = validate(mission, p1=p1_by_node.get("mission") if p1_by_node else None)
    if check["status"] in {"INVALID", "UNSUPPORTED"}: return {**check, "dependency_ready": [], "capability_ready": [], "authorization_ready": [], "runtime_ready": [], "executable": False}
    nodes = {node["node_id"]: node for node in mission["nodes"]}
    by_id = p1_by_node or {}
    blocked = {e.get("node_id") for e in check["errors"] if e.get("node_id")}
    dep_edges = mission.get("dependencies", [])
    dependency_ready = [node_id for node_id in sorted(nodes) if node_id not in blocked and not nodes[node_id].get("dependencies")]
    capability_ready = [node_id for node_id in dependency_ready if all(nodes[node_id].get("capability_state", {}).get(cap, "UNKNOWN") == "STATIC_VERIFIED" for cap in nodes[node_id].get("required_capabilities", []))]
    authorization_ready = [node_id for node_id in capability_ready if not any(e.get("node_id") == node_id and e["code"].startswith("BLOCKED/") and "AUTHORIZATION" in e["code"] for e in check["errors"])]
    runtime_ready = [node_id for node_id in authorization_ready if all(nodes[node_id].get("capability_state", {}).get(cap) == "STATIC_VERIFIED" for cap in nodes[node_id].get("required_capabilities", [])) and by_id.get(node_id, {}).get("runtime_observed") is True]
    return {"status": "BLOCKED" if check["status"] == "BLOCKED" else "VALID", "dependency_ready": dependency_ready, "capability_ready": capability_ready, "authorization_ready": authorization_ready, "runtime_ready": runtime_ready, "executable": False, "errors": check["errors"]}


def decompose(parent: dict[str, Any], children: list[dict[str, Any]], root: Path | None = None) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve(); result = []
    parent_scope = _path(root, parent.get("scope", "."))
    for child in sorted(children, key=lambda x: x.get("node_id", "")):
        node = json.loads(json.dumps(child, ensure_ascii=False)); node["node_id"] = f"{parent['node_id']}/{node.get('node_id', '')}"
        try: scope = _path(root, node.get("scope")); within = scope == parent_scope or scope.startswith(parent_scope.rstrip("/") + "/") or parent_scope == "."
        except ValueError: within = False; scope = str(node.get("scope"))
        if not within: return {"status": "BLOCKED", "errors": [_error("BLOCKED/CHILD_SCOPE_ESCAPE", node["node_id"])]}
        if not set(node.get("allowed_effects", [])) <= set(parent.get("allowed_effects", [])): return {"status": "BLOCKED", "errors": [_error("BLOCKED/CHILD_EFFECT_EXCEEDS_AUTHORIZATION", node["node_id"])]}
        node["scope"] = scope; node["uncertainty"] = sorted(set(parent.get("uncertainty", [])) | set(node.get("uncertainty", []))); result.append(node)
    return {"status": "VALID", "nodes": result, "read_only": True}
