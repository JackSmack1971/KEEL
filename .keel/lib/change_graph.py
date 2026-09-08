"""Canonical, pure planning graph and explicit legacy mission adapters.

The graph contains canonical semantic-kernel records.  Dependencies exist only
as ``HARD_DEPENDENCY`` Edge records; frontier is a read-only projection over
those edges and caller-supplied completion state.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import semantic_kernel as sk


SCHEMA_ID = "keel.change-graph"
SCHEMA_VERSION = 1
IDENTITY = "keel.change-graph/v1"
GRAPH_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EDGE_TYPES = {"HARD_DEPENDENCY", "IMPLEMENTS", "REQUIRES_EVIDENCE", "REQUESTS_EFFECT"}
PLAN_KINDS = {"requirement", "work-unit", "edge", "effect-request", "evidence-requirement"}
CLAIM_MODES = {"SHARED", "EXCLUSIVE"}


class GraphError(ValueError):
    pass


def _digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _identity(kind: str, graph_id: str, local_id: str) -> str:
    safe = re.sub(r"[^a-z0-9._-]", "-", local_id.lower()).strip("-.")
    if not safe:
        raise GraphError(f"cannot normalize empty {kind} identity")
    return f"keel:{kind}:{graph_id}.{safe}"[: 5 + len(kind) + 1 + 128]


def _provenance(source_schema: str, source_digest: str, adapter: str) -> sk.Provenance:
    return sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, f"{source_schema}@{source_digest};adapter={adapter}")


def _common(kind: str, identity: str, provenance: sk.Provenance, *, unknown: bool = False) -> dict[str, Any]:
    return {
        "schema": f"keel.{kind}", "schema_version": 1, "identity": identity,
        "provenance": provenance, "knowledge": sk.Knowledge.UNKNOWN if unknown else sk.Knowledge.KNOWN,
    }


def _claim(path: str, mode: str = "EXCLUSIVE") -> dict[str, str]:
    resource = sk.ResourceIdentity(sk.ResourceKind.REPOSITORY if path == "." else sk.ResourceKind.REPOSITORY_PATH, path)
    return {"resource": resource.identity, "mode": mode}


def _record_documents(records: list[sk.Record]) -> list[dict[str, Any]]:
    return sorted((sk.to_document(record) for record in records), key=lambda item: item["identity"])


def _graph(graph_id: str, objective: str, records: list[sk.Record], source: Mapping[str, Any], source_schema: str, adapter: str, uncertainty: list[str]) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID, "schema_version": SCHEMA_VERSION, "identity": IDENTITY,
        "graph_id": graph_id, "objective": objective, "records": _record_documents(records),
        "provenance": {"kind": "NORMALIZATION", "source_schema": source_schema,
                       "source_digest": _digest(source), "adapter": adapter},
        "uncertainty": sorted(set(uncertainty)),
    }


def _validate_provenance(value: Any, errors: list[str]) -> None:
    expected = {"kind", "source_schema", "source_digest", "adapter"}
    if not isinstance(value, dict) or set(value) != expected:
        errors.append("graph provenance must contain exactly kind, source_schema, source_digest, adapter")
        return
    if value.get("kind") not in {"DIRECT_OBSERVATION", "NORMALIZATION"}:
        errors.append("graph provenance kind is invalid")
    for key in ("source_schema", "adapter"):
        if not isinstance(value.get(key), str) or not value[key].strip(): errors.append(f"graph provenance {key} is invalid")
    try: sk.validate_digest(value.get("source_digest"))
    except sk.ModelError as exc: errors.append(str(exc))


def validate(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict): return ["change graph must be an object"]
    required = {"schema_id", "schema_version", "identity", "graph_id", "objective", "records", "provenance", "uncertainty"}
    if set(document) != required:
        errors.append("change graph fields must exactly match the canonical schema")
    if document.get("schema_id") != SCHEMA_ID or document.get("schema_version") != 1 or document.get("identity") != IDENTITY:
        errors.append("unsupported change graph schema identity/version")
    graph_id = document.get("graph_id")
    if not isinstance(graph_id, str) or not GRAPH_ID_RE.fullmatch(graph_id): errors.append("graph_id is invalid")
    if not isinstance(document.get("objective"), str) or not document.get("objective", "").strip(): errors.append("objective must be non-empty")
    if not isinstance(document.get("uncertainty"), list) or not all(isinstance(x, str) and x.strip() for x in document.get("uncertainty", [])):
        errors.append("uncertainty must be a list of non-empty strings")
    _validate_provenance(document.get("provenance"), errors)
    raw_records = document.get("records")
    if not isinstance(raw_records, list) or not raw_records: return sorted(set(errors + ["records must be a non-empty list"]))
    records: list[sk.Record] = []
    identities: set[str] = set()
    for index, raw in enumerate(raw_records):
        try:
            record = sk.decode(raw)
            if record.KIND not in PLAN_KINDS: raise GraphError(f"record kind {record.KIND} is not valid in a planning graph")
            if record.identity in identities: raise GraphError(f"duplicate record identity: {record.identity}")
            if isinstance(graph_id, str) and GRAPH_ID_RE.fullmatch(graph_id) and not record.identity.startswith(f"keel:{record.KIND}:{graph_id}."):
                raise GraphError(f"record identity is outside graph namespace: {record.identity}")
            identities.add(record.identity); records.append(record)
        except (sk.ModelError, GraphError, TypeError) as exc: errors.append(f"records[{index}]: {exc}")
    work_ids = {r.identity for r in records if isinstance(r, sk.WorkUnit)}
    edge_keys: set[tuple[str, str, str]] = set()
    hard: dict[str, set[str]] = {identity: set() for identity in work_ids}
    for record in records:
        if isinstance(record, sk.WorkUnit):
            allowed = {"requirements", "scope_claims", "resource_claims", "effect_requests", "evidence_requirements", "risk_policy", "retry_policy", "recovery_policy", "uncertainty"}
            unknown = set(record.attributes) - allowed
            if unknown: errors.append(f"{record.identity}: prohibited or unknown work-local fields: {', '.join(sorted(unknown))}")
            for field, kind in (("requirements", "requirement"), ("effect_requests", "effect-request"), ("evidence_requirements", "evidence-requirement")):
                refs = record.attributes.get(field, ())
                if not isinstance(refs, (list, tuple)) or len(refs) != len(set(refs)):
                    errors.append(f"{record.identity}: malformed {field}"); continue
                for ref in refs:
                    try: sk.validate_identity(ref, kind)
                    except sk.ModelError as exc: errors.append(f"{record.identity}: {exc}"); continue
                    if ref not in identities: errors.append(f"{record.identity}: missing {field} record {ref}")
            for claim in record.attributes.get("resource_claims", ()):
                if not isinstance(claim, Mapping) or set(claim) != {"resource", "mode"} or claim.get("mode") not in CLAIM_MODES:
                    errors.append(f"{record.identity}: malformed resource claim"); continue
                value = claim.get("resource", "")
                try:
                    if value == "repo:.": sk.ResourceIdentity(sk.ResourceKind.REPOSITORY, ".")
                    elif isinstance(value, str) and value.startswith("repo:"): sk.ResourceIdentity(sk.ResourceKind.REPOSITORY_PATH, value[5:])
                    else: raise sk.ModelError("resource identity must start with repo:")
                except sk.ModelError as exc: errors.append(f"{record.identity}: {exc}")
        if isinstance(record, sk.Edge):
            if record.edge_type not in EDGE_TYPES: errors.append(f"{record.identity}: invalid edge type {record.edge_type}")
            if record.source_id not in identities: errors.append(f"{record.identity}: missing source endpoint {record.source_id}")
            if record.target_id not in identities: errors.append(f"{record.identity}: missing target endpoint {record.target_id}")
            key = (record.source_id, record.target_id, record.edge_type)
            if key in edge_keys: errors.append(f"duplicate edge: {key}")
            edge_keys.add(key)
            if record.edge_type == "HARD_DEPENDENCY":
                if record.source_id == record.target_id: errors.append(f"{record.identity}: self dependency")
                if record.source_id not in work_ids or record.target_id not in work_ids: errors.append(f"{record.identity}: hard dependency endpoints must be work units")
                elif record.source_id != record.target_id: hard[record.source_id].add(record.target_id)
        if isinstance(record, sk.EvidenceRequirement) and (record.subject_id not in identities or record.subject_id not in work_ids):
            errors.append(f"{record.identity}: evidence subject must be a graph work unit")
        if isinstance(record, sk.EffectRequest) and (record.subject_id not in identities or record.subject_id not in work_ids):
            errors.append(f"{record.identity}: effect subject must be a graph work unit")
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting: errors.append(f"hard dependency cycle includes {node}"); return
        if node in visited: return
        visiting.add(node)
        for dependency in sorted(hard.get(node, ())): visit(dependency)
        visiting.remove(node); visited.add(node)
    for node in sorted(hard): visit(node)
    return sorted(set(errors))


def serialize(document: Mapping[str, Any]) -> str:
    errors = validate(document)
    if errors: raise GraphError("invalid change graph: " + "; ".join(errors))
    normalized = dict(document)
    normalized["records"] = sorted(document["records"], key=lambda item: item["identity"])
    normalized["uncertainty"] = sorted(set(document["uncertainty"]))
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def frontier(document: Mapping[str, Any], state: Mapping[str, str] | None = None) -> dict[str, Any]:
    errors = validate(document)
    if errors: return {"status": "INVALID", "runnable": [], "blocked": [], "errors": errors, "read_only": True}
    records = [sk.decode(raw) for raw in document["records"]]
    work = sorted(r.identity for r in records if isinstance(r, sk.WorkUnit))
    dependencies = {identity: set() for identity in work}
    for record in records:
        if isinstance(record, sk.Edge) and record.edge_type == "HARD_DEPENDENCY": dependencies[record.source_id].add(record.target_id)
    supplied = dict(state or {})
    complete = {identity for identity in work if supplied.get(identity) == "COMPLETE"}
    pending = [identity for identity in work if identity not in complete]
    runnable = [identity for identity in pending if dependencies[identity] <= complete]
    return {"status": "COMPLETE" if not pending else "READY" if runnable else "BLOCKED", "runnable": runnable,
            "blocked": [identity for identity in pending if identity not in runnable], "complete": sorted(complete),
            "errors": [], "read_only": True}


def adapt_v1(source: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source, Mapping) or source.get("schema_version") != 1 or not isinstance(source.get("work"), dict):
        raise GraphError("unsupported mission v1 document")
    graph_id = source.get("mission_id"); objective = source.get("objective")
    if not isinstance(graph_id, str) or not GRAPH_ID_RE.fullmatch(graph_id) or not isinstance(objective, str) or not objective.strip():
        raise GraphError("mission v1 identity/objective is invalid")
    digest = _digest(source); prov = _provenance("keel.mission/v1", digest, "mission-v1-to-change-graph-v1")
    records: list[sk.Record] = []; uncertainty = ["legacy mission v1 omitted work-local objectives, scope/effect/evidence constraints, and runtime-independent readiness inputs"]
    root_req = sk.Requirement(**_common("requirement", _identity("requirement", graph_id, "mission-success"), prov, unknown=True), obligation="; ".join(source.get("success_criteria", [])) or "UNKNOWN: legacy mission supplied no success criteria")
    records.append(root_req)
    work = source["work"]
    for node_id in sorted(work):
        item = work[node_id]
        if not isinstance(item, Mapping): raise GraphError(f"mission v1 work item {node_id} is malformed")
        wid = _identity("work-unit", graph_id, node_id)
        records.append(sk.WorkUnit(**_common("work-unit", wid, prov, unknown=True), objective=f"UNKNOWN: legacy work item {node_id} omitted an objective", attributes={"requirements": [root_req.identity], "risk_policy": item.get("risk", "UNKNOWN"), "uncertainty": uncertainty}))
    for node_id in sorted(work):
        deps = work[node_id].get("depends_on", [])
        if not isinstance(deps, list): raise GraphError(f"mission v1 dependencies for {node_id} are malformed")
        for dep in sorted(deps):
            eid = _identity("edge", graph_id, f"hard-{node_id}-{dep}")
            records.append(sk.Edge(**_common("edge", eid, prov), source_id=_identity("work-unit", graph_id, node_id), target_id=_identity("work-unit", graph_id, dep), edge_type="HARD_DEPENDENCY"))
    result = _graph(graph_id, objective, records, source, "keel.mission/v1", "mission-v1-to-change-graph-v1", uncertainty)
    errors = validate(result)
    if errors: raise GraphError("legacy mission v1 normalization failed: " + "; ".join(errors))
    return result


def adapt_v2(source: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source, Mapping) or source.get("schema_id") != "keel.mission" or source.get("schema_version") != 2:
        raise GraphError("unsupported mission v2 document")
    graph_id = source.get("mission_id"); objective = source.get("objective")
    if not isinstance(graph_id, str) or not GRAPH_ID_RE.fullmatch(graph_id) or not isinstance(objective, str) or not objective.strip():
        raise GraphError("mission v2 identity/objective is invalid")
    digest = _digest(source); prov = _provenance("keel.mission/v2", digest, "mission-v2-to-change-graph-v1")
    records: list[sk.Record] = []; uncertainty: list[str] = []
    node_ids: set[str] = set()
    for node in sorted(source.get("nodes", []), key=lambda item: item.get("node_id", "")):
        node_id = node.get("node_id")
        if not isinstance(node_id, str) or not GRAPH_ID_RE.fullmatch(node_id) or node_id in node_ids: raise GraphError("mission v2 node identity is invalid or duplicated")
        node_ids.add(node_id); wid = _identity("work-unit", graph_id, node_id)
        requirements: list[str] = []
        criteria = node.get("acceptance_criteria", [])
        if not isinstance(criteria, list) or not all(isinstance(x, str) and x.strip() for x in criteria): raise GraphError(f"mission v2 acceptance criteria for {node_id} are malformed")
        for index, criterion in enumerate(criteria):
            rid = _identity("requirement", graph_id, f"{node_id}-{index}"); requirements.append(rid)
            records.append(sk.Requirement(**_common("requirement", rid, prov), obligation=criterion))
        claims = []
        scope = node.get("scope")
        if isinstance(scope, str): claims.append(_claim(scope, "EXCLUSIVE" if node.get("exclusivity") else "SHARED"))
        for resource in node.get("resources", []):
            if not isinstance(resource, Mapping) or not isinstance(resource.get("id"), str): raise GraphError(f"mission v2 resource for {node_id} is malformed")
            # Legacy opaque resource IDs are preserved as uncertainty, not invented repository paths.
            uncertainty.append(f"legacy opaque resource {node_id}:{resource['id']} has no canonical repository identity")
        local_uncertainty = list(node.get("uncertainty", [])) if isinstance(node.get("uncertainty", []), list) else []
        effect_ids = [_identity("effect-request", graph_id, f"{node_id}-{index}") for index, _ in enumerate(node.get("allowed_effects", []))]
        policy = node.get("verification_policy", {})
        checks = policy.get("checks", []) if isinstance(policy, Mapping) else []
        evidence_ids = [_identity("evidence-requirement", graph_id, f"{node_id}-{index}") for index, _ in enumerate(checks)]
        ignored_local = sorted(name for name in ("required_capabilities", "capability_state", "authorization_refs", "inputs", "expected_outputs", "review_policy", "integration_policy", "lifecycle_expectations", "planning_status") if name in node)
        if ignored_local: local_uncertainty.append("legacy fields remain source-provenanced but are not canonical work intent: " + ", ".join(ignored_local))
        attrs: dict[str, Any] = {"requirements": requirements, "scope_claims": claims, "resource_claims": claims, "effect_requests": effect_ids, "evidence_requirements": evidence_ids, "uncertainty": local_uncertainty}
        if isinstance(node.get("retry_policy"), Mapping): attrs["retry_policy"] = dict(node["retry_policy"])
        records.append(sk.WorkUnit(**_common("work-unit", wid, prov, unknown=bool(local_uncertainty)), objective=node.get("objective", "UNKNOWN: legacy node omitted objective"), attributes=attrs))
        for index, effect in enumerate(node.get("allowed_effects", [])):
            eid = effect_ids[index]
            records.append(sk.EffectRequest(**_common("effect-request", eid, prov), effect_type=effect, subject_id=wid))
        for index, check in enumerate(checks):
            evid = evidence_ids[index]
            records.append(sk.EvidenceRequirement(**_common("evidence-requirement", evid, prov), subject_id=wid, boundary="candidate", claim=str(check)))
        if node.get("allowed_effects"):
            uncertainty.append(f"legacy allowed effects for {node_id} were normalized as requests, never grants")
    top_edges = source.get("dependencies", [])
    if not isinstance(top_edges, list): raise GraphError("mission v2 dependencies are malformed")
    # Top-level dependencies are the legacy authority. Node duplicates are checked for equivalence only.
    expected = {(edge.get("from"), edge.get("to")) for edge in top_edges if isinstance(edge, Mapping) and edge.get("type") == "HARD_PREREQUISITE"}
    node_deps = {(node.get("node_id"), dep) for node in source.get("nodes", []) for dep in node.get("dependencies", [])}
    if expected != node_deps: raise GraphError("mission v2 duplicate dependency representations disagree")
    for source_id, target_id in sorted(expected):
        eid = _identity("edge", graph_id, f"hard-{source_id}-{target_id}")
        records.append(sk.Edge(**_common("edge", eid, prov), source_id=_identity("work-unit", graph_id, source_id), target_id=_identity("work-unit", graph_id, target_id), edge_type="HARD_DEPENDENCY"))
    ignored = [name for name in ("authorizations", "planning_status") if name in source]
    if ignored: uncertainty.append("legacy authorization/runtime/lifecycle/planning fields were not imported as canonical planning authority: " + ", ".join(sorted(ignored)))
    result = _graph(graph_id, objective, records, source, "keel.mission/v2", "mission-v2-to-change-graph-v1", uncertainty)
    errors = validate(result)
    if errors: raise GraphError("legacy mission v2 normalization failed: " + "; ".join(errors))
    return result


def normalize(source: Mapping[str, Any]) -> dict[str, Any]:
    if source.get("schema_id") == SCHEMA_ID: return dict(source)
    if source.get("schema_id") == "keel.mission" and source.get("schema_version") == 2: return adapt_v2(source)
    if source.get("schema_version") == 1 and "work" in source: return adapt_v1(source)
    raise GraphError("unsupported planning document")
