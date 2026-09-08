"""Compatibility capability projection over canonical FactGraph evidence."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
import fact_graph

IGNORE_DIRS = fact_graph.IGNORE_DIRS | {".keel", ".control-plane"}
RESOLVER_SCHEMA_VERSION = 2
RESOLVER_RULES_VERSION = 1
RULES = fact_graph.CAPABILITY_RULES
SOURCE_GLOBS = fact_graph.SOURCE_GLOBS
NON_SOURCE_GLOBS = fact_graph.NON_SOURCE_GLOBS
_match = fact_graph.match


def iter_repo_paths(root: Path, ignore_dirs: Iterable[str] | None = None) -> list[str]:
    config = {"capability_resolver": {"ignore_dirs": list(ignore_dirs or ()) + [".keel", ".control-plane"]}}
    return list(fact_graph.snapshot(root, config).paths)


def classify_path(path: str, config: dict | None = None) -> str:
    cls = (config or {}).get("source_classification", {}) or {}
    for pattern in cls.get("explicit_source_globs", []):
        if isinstance(pattern, str) and _match(path, pattern): return "SOURCE"
    for pattern in cls.get("explicit_non_source_globs", []):
        if isinstance(pattern, str) and _match(path, pattern): return "NON_SOURCE"
    for pattern in cls.get("detected_source_globs", []):
        if isinstance(pattern, str) and _match(path, pattern): return "SOURCE"
    if any(_match(path, pattern) for pattern in NON_SOURCE_GLOBS): return "NON_SOURCE"
    if any(_match(path, pattern) for pattern in SOURCE_GLOBS): return "SOURCE"
    return "UNKNOWN"


def resolve(root: Path, config: dict | None = None) -> dict:
    config = config or {}; maximum = int((config.get("capability_resolver", {}) or {}).get("max_evidence_per_capability", 12))
    graph = fact_graph.build(root, config)
    capabilities = {}
    for fact in graph.select("capability-candidate"):
        value = dict(fact.value); details = value.pop("evidence_details")[:maximum]; evidence = value.pop("evidence")
        capabilities[fact.subject] = {"status": value["status"], "confidence": fact.confidence, "evidence": evidence[:maximum], "evidence_details": details}
    source_facts = graph.select("source-class")
    by_path: dict[str, list] = {}
    for fact in source_facts: by_path.setdefault(fact.subject, []).append(fact)
    source_classes = {path: classify_path(path, config) for path in sorted(by_path)}
    explicit_source = (config.get("source_classification", {}) or {}).get("explicit_source_globs", [])
    explicit_non = (config.get("source_classification", {}) or {}).get("explicit_non_source_globs", [])
    conflicts=[]
    for path in sorted(by_path):
        s=[pat for pat in explicit_source if isinstance(pat,str) and _match(path,pat)]; n=[pat for pat in explicit_non if isinstance(pat,str) and _match(path,pat)]
        if s and n: conflicts.append({"status":"CONFLICT","path":path,"reason":"matches explicit source and non-source classifiers","source_globs":s,"non_source_globs":n,"fact_ids":[f.id for f in by_path[path]]})
    unknown=[p for p,v in source_classes.items() if v=="UNKNOWN"]
    # fact_ids are canonical detail; omitted from v2 compatibility shape.
    for row in conflicts: row.pop("fact_ids")
    return {"schema_version":2,"rules_version":1,"capabilities":capabilities,"conflicts":conflicts,"path_count":len(by_path),"source_classification":{"counts":{"SOURCE":sum(v=="SOURCE" for v in source_classes.values()),"NON_SOURCE":sum(v=="NON_SOURCE" for v in source_classes.values()),"UNKNOWN":len(unknown)},"unknown_paths":unknown[:maximum],"unknown_paths_truncated":len(unknown)>maximum},"policy":"advisory-evidence-only"}


def write_resolution(root: Path, result: dict) -> Path:
    out=root/".keel"/"knowledge"/"capabilities.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"); return out
