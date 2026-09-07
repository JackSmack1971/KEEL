from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

import capability_resolver

CORE_CAPABILITIES = ["repository-legibility", "keel-spec-ledger", "security", "provenance-audit", "autonomy-permissions"]
ROLE_PROFILES = {
    "executor": ["docs/control-plane/COMMANDS.md", "docs/control-plane/ENVIRONMENTS.md"],
    "verifier": ["docs/control-plane/VERIFICATION.md", "docs/control-plane/TESTING_CI_GENERATED.md"],
    "reviewer": ["ARCHITECTURE.md", "docs/control-plane/ARCHITECTURE_ENFORCEMENT.md"],
    "risk-reviewer": ["docs/control-plane/DECISION_MODEL.md", "docs/control-plane/SECURITY_DATA_SUPPLY_CHAIN.md"],
}


def _read(path: Path, limit: int = 4000) -> str:
    if not path.is_file(): return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _document_provenance(root: Path, docs: list[str]) -> list[dict]:
    records = []
    for document in docs:
        candidate = (root / document).resolve()
        try:
            relative = candidate.relative_to(root.resolve()).as_posix()
        except ValueError:
            records.append({"path": document, "status": "OUTSIDE_REPOSITORY"})
            continue
        if not candidate.is_file():
            records.append({"path": relative, "status": "MISSING"})
            continue
        records.append({"path": relative, "status": "PRESENT", "sha256": _sha256(candidate)})
    return records


def _material_lines(text: str, limit: int = 12) -> list[str]:
    out=[]
    for line in text.splitlines():
        s=line.strip()
        if not s or s.startswith("<!--"): continue
        if s.startswith("#"): continue
        out.append(s)
        if len(out)>=limit: break
    return out


def _parse_registry(root: Path) -> dict[str,str]:
    p=root/"docs/control-plane/CAPABILITY_REGISTRY.md"; out={}
    if not p.is_file(): return out
    for line in p.read_text(encoding="utf-8",errors="replace").splitlines():
        if not line.startswith("|"): continue
        cells=[x.strip() for x in line.strip("|").split("|")]
        if len(cells)>=3 and cells[0] not in {"ID","---"}:
            out[cells[0]]=cells[2]
    return out


def compile_packet(root: Path, change_id: str, state: dict, config: dict, ledger_dir: Path, changed_paths: list[str] | None = None) -> tuple[str, dict]:
    discovery_path=root/".keel/knowledge/capabilities.json"
    discovery_source = "resolver"
    if discovery_path.is_file():
        try: discovery=json.loads(discovery_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError): discovery=capability_resolver.resolve(root, config)
        else: discovery_source = "cached"
    else:
        discovery=capability_resolver.resolve(root, config)
    registry=_parse_registry(root)
    scope=_read(ledger_dir/"scope.txt", 3000)
    relevant=[]
    for cid in CORE_CAPABILITIES:
        relevant.append({"id":cid,"reason":"always relevant to governed writes","registry_status":registry.get(cid,"UNKNOWN")})
    scope_tokens=[x.strip().replace("*","") for x in scope.splitlines() if x.strip() and not x.startswith("#")]
    for cid, row in (discovery.get("capabilities") or {}).items():
        if row.get("status") not in {"DETECTED","LIKELY"}: continue
        evidence=row.get("evidence") or []
        direct = any(any(tok and (tok in ev or ev.startswith(tok.rstrip("/"))) for tok in scope_tokens) for ev in evidence)
        if direct or cid in {"testing-evals","quality-static-analysis","build-toolchain"}:
            relevant.append({"id":cid,"reason":"discovery evidence intersects change or verification surface","evidence":evidence[:4],"registry_status":registry.get(cid,"UNKNOWN")})
    # de-duplicate while preserving core-first order
    seen=set(); rel=[]
    for row in relevant:
        if row["id"] in seen: continue
        seen.add(row["id"]); rel.append(row)

    mapping=(config.get("context_compiler",{}) or {}).get("capability_docs",{})
    docs=[]
    for d in (config.get("context_compiler",{}) or {}).get("always_docs",[]):
        if isinstance(d,str) and d not in docs: docs.append(d)
    for row in rel:
        for d in mapping.get(row["id"],[]):
            if d not in docs: docs.append(d)

    proposal=" ".join(_material_lines(_read(ledger_dir/"proposal.md", 5000),8))
    delta="\n".join(_material_lines(_read(ledger_dir/"delta.md", 5000),12))
    risk=_read(ledger_dir/"risk.json",2000).strip(); effects=_read(ledger_dir/"effects.json",2000).strip()
    acceptance=_read(ledger_dir/"acceptance.json",3500).strip()
    lines=[
        f"# KEEL Context Packet — {change_id}","",
        f"Phase: `{state.get('phase')}`  Base: `{state.get('base_commit')}`  Mode: `{state.get('mode')}`","",
        "## Objective", proposal or "UNRESOLVED", "",
        "## Delta", delta or "UNRESOLVED", "",
        "## Scope", "```text", scope.strip() or "UNRESOLVED", "```", "",
        "## Risk / effects", "```json", risk or "{}", "```", "```json", effects or "{}", "```", "",
        "## Acceptance contract", "```json", acceptance or "{}", "```", "",
        "## Relevant capabilities",
    ]
    for row in rel:
        ev = ", ".join(row.get("evidence",[])[:3])
        lines.append(f"- `{row['id']}` [{row.get('registry_status','UNKNOWN')}]: {row['reason']}" + (f" — {ev}" if ev else ""))
    lines += ["", "## Load next (only if needed)"] + [f"- `{d}`" for d in docs]
    if changed_paths:
        lines += ["", "## Current changed paths"] + [f"- `{p}`" for p in changed_paths[:30]]
    lines += ["", "## Decision reminder", "Use repository evidence, not remembered assumptions. Before a consequential transition, re-read the current ledger artifacts and obtain the evidence required by acceptance.json. Keep raw command/log output outside the main orchestration thread."]
    text="\n".join(lines)+"\n"
    max_chars=int((config.get("context_compiler",{}) or {}).get("max_chars",12000))
    if len(text)>max_chars:
        text=text[:max_chars-120]+"\n\n[TRUNCATED BY KEEL CONTEXT BUDGET — load referenced artifacts directly if required]\n"
    meta={
        "schema_version": 2,
        "change_id": change_id,
        "phase": state.get("phase"),
        "relevant_capabilities": rel,
        "documents": docs,
        "document_provenance": _document_provenance(root, docs),
        "discovery": {"source": discovery_source, "path": ".keel/knowledge/capabilities.json"},
        "chars": len(text),
        "budget": max_chars,
    }
    return text,meta


def write_packet(root: Path, change_id: str, text: str, meta: dict) -> tuple[Path,Path]:
    out=root/".keel/context"; out.mkdir(parents=True,exist_ok=True)
    md=out/f"{change_id}.md"; js=out/f"{change_id}.json"
    md.write_text(text,encoding="utf-8"); js.write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return md,js


def _query_tokens(query) -> list[str]:
    if isinstance(query, str):
        values = query.split()
    elif isinstance(query, list):
        values = query
    else:
        values = []
    return sorted({str(value).strip().lower() for value in values if str(value).strip()})


def select_v2(root: Path, config: dict, role: str, query, changed_paths: list[str], graph: dict | None = None, impact: dict | None = None) -> dict:
    """Select additive context from explicit role/query/impact inputs."""
    from repository_map import analyze_impact, build

    compiler = config.get("context_compiler", {}) or {}
    requested_role = role
    role = role if role in ROLE_PROFILES else "executor"
    tokens = _query_tokens(query)
    graph = graph if isinstance(graph, dict) else build(root)
    impact = impact if isinstance(impact, dict) else analyze_impact(graph, changed_paths)
    selected: dict[str, dict] = {}

    def add(path: str, reason: str, confidence: str) -> None:
        if not isinstance(path, str) or not path.strip():
            return
        normalized = path.replace("\\", "/")
        row = selected.setdefault(normalized, {"path": normalized, "reasons": [], "confidence": confidence, "provenance": "context compiler configuration"})
        if reason not in row["reasons"]:
            row["reasons"].append(reason)
        if confidence == "HIGH":
            row["confidence"] = confidence

    for document in compiler.get("always_docs", []):
        add(document, "mandatory-configured-context", "HIGH")
    role_docs = compiler.get("role_docs", {}) or {}
    for document in role_docs.get(role, ROLE_PROFILES[role]):
        add(document, f"role-profile:{role}", "HIGH")

    category_docs = compiler.get("impact_docs", {}) or {}
    categories = {category for row in impact.get("classifications", []) for category in row.get("categories", [])}
    for category in sorted(categories):
        for document in category_docs.get(category, []):
            add(document, f"impact:{category}", "MEDIUM")

    capability_docs = compiler.get("capability_docs", {}) or {}
    changed_text = " ".join(changed_paths).lower()
    for capability, documents in capability_docs.items():
        if any(token in capability.lower() for token in tokens) or any(token in changed_text for token in capability.lower().split("-")):
            for document in documents:
                add(document, f"query-or-impact-capability:{capability}", "MEDIUM")

    warnings = []
    graph_status = graph.get("architecture", {}).get("status", "UNAVAILABLE")
    if graph_status in {"UNAVAILABLE", "CONFLICT"}:
        warnings.append({"code": "graph-uncertain", "status": graph_status, "action": "widen-context-and-verification"})
        add("ARCHITECTURE.md", "uncertain-architecture-fallback", "HIGH")
    if impact.get("risk") in {"UNKNOWN", "WIDEN_VERIFICATION"}:
        warnings.append({"code": "impact-uncertain", "status": impact.get("risk"), "action": "widen-context-and-verification"})
        add("docs/control-plane/VERIFICATION.md", "uncertain-impact-fallback", "HIGH")
    if requested_role not in ROLE_PROFILES:
        warnings.append({"code": "unsupported-role", "status": "UNAVAILABLE", "action": "fallback-to-executor"})

    rows = [selected[path] for path in sorted(selected)]
    provenance = _document_provenance(root, [row["path"] for row in rows])
    return {
        "schema_version": 1,
        "status": "AVAILABLE",
        "role": role,
        "query": tokens,
        "documents": rows,
        "document_provenance": provenance,
        "graph": {"schema_version": graph.get("schema_version"), "policy": graph.get("policy"), "status": graph_status, "provenance": "repository_map.build; derived-only"},
        "impact": {"status": impact.get("status", "UNAVAILABLE"), "risk": impact.get("risk", "UNKNOWN"), "probable_dependents": impact.get("probable_dependents", [])[:20], "probable_tests": impact.get("probable_tests", [])[:20], "provenance": impact.get("policy", "advisory-only")},
        "warnings": warnings,
        "monotonicity": {"mandatory_documents_retained": all(any(row["path"] == document for row in rows) for document in compiler.get("always_docs", [])), "policy": "intelligence may add context and warnings but may not remove mandatory context"},
        "policy": "derived-navigation-evidence-only",
    }


def compile_packet_v2(root: Path, change_id: str, state: dict, config: dict, ledger_dir: Path, changed_paths: list[str] | None = None, role: str = "executor", query=None) -> tuple[str, dict]:
    changed_paths = changed_paths or []
    selection = select_v2(root, config, role, query, changed_paths)
    proposal = " ".join(_material_lines(_read(ledger_dir / "proposal.md", 5000), 8))
    lines = [
        f"# KEEL Context Packet v2 — {change_id}", "",
        f"Phase: {state.get('phase')}  Role: {selection['role']}  Base: {state.get('base_commit')}", "",
        "## Objective", proposal or "UNRESOLVED", "",
        "## Selection basis", f"Query: {', '.join(selection['query']) or 'none'}",
        f"Graph: {selection['graph']['status']}  Impact risk: {selection['impact']['risk']}", "",
        "## Selected context",
    ]
    for row in selection["documents"]:
        lines.append(f"- {row['path']} ({row['confidence']}) — {'; '.join(row['reasons'])}")
    if selection["warnings"]:
        lines += ["", "## Warnings"] + [f"- {row['code']}: {row['action']}" for row in selection["warnings"]]
    lines += ["", "## Monotonicity", "- Mandatory configured documents retained.", "- Intelligence is derived navigation evidence only.", ""]
    text = "\n".join(lines)
    max_chars = int((config.get("context_compiler", {}) or {}).get("max_chars", 12000))
    if len(text) > max_chars:
        text = text[:max_chars - 80] + "\n\n[TRUNCATED BY KEEL CONTEXT BUDGET]\n"
    selection["chars"] = len(text)
    selection["budget"] = max_chars
    return text, {"schema_version": 3, "change_id": change_id, "phase": state.get("phase"), "selection": selection}
