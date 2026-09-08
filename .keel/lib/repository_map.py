"""Legacy repository-map projection over the canonical FactGraph."""
from __future__ import annotations
import json
from pathlib import Path
import fact_graph


def _row(path: str, rule: str) -> dict:
    return {"path": path, "rule": rule}


def build(root: Path) -> dict:
    graph = fact_graph.build(root)
    resources = sorted(f.subject for f in graph.select("resource") if f.subject != ".")
    dirs = sorted({str(Path(path).parent.as_posix()) for path in resources if Path(path).parent.as_posix() != "."})
    topology = [_row(path, "top-level-directory") for path in sorted({p.split("/", 1)[0] for p in dirs if "/" not in p})]
    modules = [_row(f.subject, "module-root-child") for f in graph.select("module")]
    entrypoints = [_row(f.subject, "entrypoint-name") for f in graph.select("entrypoint")]
    tests = [_row(f.subject, "test-path-or-name") for f in graph.select("test")]
    commands = [_row(f.subject, "command-file") for f in graph.select("command-candidate")]
    dependencies = [_row(f.subject, "dependency-manifest") for f in graph.select("dependency-manifest")]
    source = [_row(f.subject, "source-classification") for f in graph.select("source-class") if f.value == "SOURCE" and f.subject.startswith(("src/", "app/", "lib/", "packages/", "services/", "cmd/"))]
    semantic_imports = sorted((f.value for f in graph.select("python-import")), key=lambda row: (row["source"], row["line"], row["target"]))
    analyses = graph.select("dependency-analysis")
    failures = [f for f in analyses if f.value == "FAILED"]
    ownership_sources = graph.select("ownership-source")
    rules = [f.value for f in graph.select("ownership-rule")]
    ownership = {"status": "AVAILABLE" if ownership_sources else "UNAVAILABLE", "source": ownership_sources[0].subject if ownership_sources else None, "provenance": "literal CODEOWNERS rules; no identity validation" if ownership_sources else "no supported CODEOWNERS source found", "rules": rules}
    return {"schema_version": 3, "root": ".", "rules_version": 1, "counts": {"files": len(resources), "directories": len(dirs)}, "topology": topology, "modules": modules, "entrypoints": entrypoints, "tests": tests, "commands": commands, "dependencies": dependencies, "source": source, "semantic_imports": semantic_imports, "ownership": ownership, "analyzers": {"python": {"status": "PARTIAL" if failures else "COMPLETE", "analyzer": "python-ast", "files_analyzed": len(analyses) - len(failures), "files_failed": len(failures), "provenance": "canonical FactGraph python adapter; stdlib-ast; repository source bytes"}}, "policy": "derived-navigation-evidence-only"}


def write(root: Path, result: dict) -> Path:
    target = root / ".keel" / "knowledge" / "repository-map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
