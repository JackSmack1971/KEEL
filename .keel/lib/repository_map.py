from __future__ import annotations

import ast
import json
from pathlib import Path

IGNORE_DIRS = {".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__"}
MODULE_ROOTS = {"src", "app", "lib", "packages", "services", "cmd", "modules", "components"}
DEPENDENCY_MANIFESTS = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json", "Package.swift"}
COMMAND_FILES = {"Makefile", "CMakeLists.txt", "Taskfile.yml", "Taskfile.yaml", "justfile", "tox.ini", ".pre-commit-config.yaml"}
GENERATED_NAMES = {"generated", "gen", "dist", "build", "target", "vendor"}
RUNTIME_NAMES = {"main.py", "__main__.py", "index.js", "index.ts", "index.tsx", "server.py", "app.py", "wsgi.py", "asgi.py"}


def _ignored(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part in IGNORE_DIRS for part in parts) or parts[:2] == (".keel", "knowledge")


def _row(path: str, rule: str) -> dict:
    return {"path": path, "rule": rule}


def _python_semantics(root: Path, files: list[str]) -> tuple[dict, list[dict], list[dict]]:
    python_files = [path for path in files if path.endswith(".py")]
    modules = {}
    for path in python_files:
        rel = Path(path).with_suffix("").as_posix()
        if rel.endswith("/__init__"):
            rel = rel[:-9]
        modules[rel.replace("/", ".")] = path
        modules.setdefault(Path(path).stem, path)
    imports = []
    symbols = []
    failures = []
    for path in python_files:
        source = root / path
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=path)
        except (OSError, SyntaxError) as exc:
            failures.append({"path": path, "error": type(exc).__name__, "analyzer": "python-ast"})
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append({"path": path, "name": node.name, "kind": type(node).__name__, "line": node.lineno, "analyzer": "python-ast", "provenance": "repository source bytes"})
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [(item.name, 0) for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * node.level + (node.module or "")
                names = [(prefix + ("." if prefix and node.module else "") + item.name, node.level) for item in node.names]
            for target, level in names:
                lookup = target.lstrip(".")
                if level:
                    parent = Path(path).parent.parts
                    base = list(parent[: max(0, len(parent) - level + 1)])
                    lookup = ".".join(base + ([lookup] if lookup else []))
                local = modules.get(lookup) or modules.get(lookup.split(".")[0])
                kind = "local" if local else ("relative-unresolved" if level else "external")
                imports.append({"source": path, "target": target, "resolved": local, "kind": kind, "line": node.lineno, "analyzer": "python-ast"})
    return {"status": "PARTIAL" if failures else "COMPLETE", "analyzer": "python-ast", "files_analyzed": len(python_files) - len(failures), "files_failed": len(failures), "provenance": "stdlib-ast; repository source bytes"}, sorted(imports, key=lambda row: (row["source"], row["line"], row["target"])), sorted(symbols, key=lambda row: (row["path"], row["line"], row["name"]))


def _ownership(root: Path) -> dict:
    candidates = [Path("CODEOWNERS"), Path(".github/CODEOWNERS"), Path("docs/CODEOWNERS")]
    found = []
    for relative in candidates:
        path = root / relative
        if not path.is_file():
            continue
        rules = []
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) >= 2:
                rules.append({"pattern": parts[0], "owners": parts[1:], "line": number})
        found.append({"source": relative.as_posix(), "rules": rules})
    if len(found) > 1:
        return {"status": "CONFLICT", "source": [row["source"] for row in found], "provenance": "multiple CODEOWNERS candidates; authority unresolved", "rules": [], "candidates": found}
    if found:
        return {"status": "AVAILABLE", "source": found[0]["source"], "provenance": "literal CODEOWNERS rules; no identity validation", "rules": found[0]["rules"]}
    return {"status": "UNAVAILABLE", "source": None, "provenance": "no supported CODEOWNERS source found", "rules": []}


def _structured_source(root: Path, names: tuple[str, ...], kind: str) -> dict:
    candidates = [Path(name) for name in names if (root / name).is_file()]
    if not candidates:
        return {"status": "UNAVAILABLE", "source": None, "provenance": f"no supported {kind} source found", "facts": []}
    parsed = []
    for candidate in candidates:
        try:
            value = json.loads((root / candidate).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parsed.append({"source": candidate.as_posix(), "error": type(exc).__name__})
            continue
        parsed.append({"source": candidate.as_posix(), "value": value})
    valid = [row for row in parsed if "value" in row]
    if len(valid) != len(parsed):
        return {"status": "CONFLICT", "source": [row["source"] for row in parsed], "provenance": f"invalid {kind} source present", "facts": [], "candidates": parsed}
    if len(valid) > 1 and {json.dumps(row["value"], sort_keys=True) for row in valid}.__len__() > 1:
        return {"status": "CONFLICT", "source": [row["source"] for row in valid], "provenance": f"conflicting {kind} sources", "facts": [], "candidates": parsed}
    value = valid[0]["value"]
    facts = value if isinstance(value, list) else value.get("facts", []) if isinstance(value, dict) else []
    return {"status": "AVAILABLE", "source": valid[0]["source"], "provenance": f"repository-owned {kind} JSON; advisory only", "facts": facts if isinstance(facts, list) else []}


def _command_intelligence(root: Path, files: list[str]) -> list[dict]:
    rows = []
    for path in files:
        name = Path(path).name
        if name in COMMAND_FILES or path == ".keel/config.json" or path.startswith(".github/workflows/"):
            confidence = "HIGH" if name in {"Makefile", "pyproject.toml", "package.json", "tox.ini"} else "MEDIUM"
            rows.append({"path": path, "source": "repository-file", "confidence": confidence, "provenance": "literal command-bearing file; semantics not executed"})
    return rows


def _generated_surfaces(files: list[str]) -> list[dict]:
    return [{"path": path, "rule": "generated-name-or-surface", "provenance": "path/name convention; non-authoritative"} for path in files if any(part in GENERATED_NAMES for part in Path(path).parts) or Path(path).name.endswith((".generated.py", ".generated.ts", ".g.cs"))]


def analyze_impact(result: dict, changed_paths: list[str]) -> dict:
    changed = set(changed_paths)
    imports = result.get("semantic_imports", [])
    dependents = sorted({row["source"] for row in imports if row.get("resolved") in changed or row.get("target") in changed})
    tests = sorted({row["path"] for row in result.get("tests", []) if any(Path(row["path"]).stem in Path(path).stem for path in changed)})
    classifications = []
    markers = {"public_api": ("api", "openapi", "schema"), "permissions": ("auth", "permission", "policy"), "dependencies": ("lock", "requirements", "package", "pyproject", "cargo"), "security": ("security", "secret", "crypto"), "deployment": ("docker", "deploy", "workflow"), "verification_surface": ("test", "verify", "config", "contract")}
    for path in sorted(changed):
        lower = path.lower()
        kinds = sorted(kind for kind, needles in markers.items() if any(needle in lower for needle in needles))
        classifications.append({"path": path, "categories": kinds, "provenance": "path marker classification; advisory", "uncertainty": "HIGH" if not kinds else "MEDIUM"})
    return {"status": "AVAILABLE", "changed_paths": sorted(changed), "probable_dependents": dependents, "probable_tests": tests, "classifications": classifications, "risk": "WIDEN_VERIFICATION" if any(row["categories"] for row in classifications) else "UNKNOWN", "policy": "advisory-only"}


def build(root: Path) -> dict:
    files = []
    dirs = set()
    for path in root.rglob("*"):
        if _ignored(path, root):
            continue
        rel = path.relative_to(root).as_posix()
        if path.is_dir():
            dirs.add(rel)
        elif path.is_file() or path.is_symlink():
            files.append(rel)
    files = sorted(files)
    topology = [_row(name, "top-level-directory") for name in sorted({path.split("/", 1)[0] for path in dirs if "/" not in path and path})]
    modules = []
    for path in sorted(dirs):
        parts = path.split("/")
        if len(parts) == 2 and parts[0] in MODULE_ROOTS:
            modules.append(_row(path, "module-root-child"))
    entrypoints = [_row(path, "entrypoint-name") for path in files if Path(path).name in {"main.py", "__main__.py", "index.js", "index.ts", "index.tsx"} or path.startswith("bin/") or path.startswith("cmd/")]
    tests = [_row(path, "test-path-or-name") for path in files if path.startswith(("tests/", "test/", "spec/", "evals/")) or Path(path).name.startswith("test_") or ".test." in path or "_test." in path]
    commands = [_row(path, "command-file") for path in files if Path(path).name in COMMAND_FILES or path in {".keel/config.json", ".codex/config.toml"} or path.startswith(("scripts/", ".github/workflows/"))]
    dependencies = [_row(path, "dependency-manifest") for path in files if Path(path).name in DEPENDENCY_MANIFESTS or Path(path).name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "poetry.lock", "uv.lock", "go.sum", "Gemfile.lock"}]
    source = [_row(path, "source-classification") for path in files if path.startswith(("src/", "app/", "lib/", "packages/", "services/", "cmd/"))]
    analyzer, semantic_imports, symbols = _python_semantics(root, files)
    result = {"schema_version": 4, "root": ".", "rules_version": 2, "counts": {"files": len(files), "directories": len(dirs)}, "topology": topology, "modules": modules, "entrypoints": entrypoints, "tests": tests, "commands": commands, "command_intelligence": _command_intelligence(root, files), "dependencies": dependencies, "source": source, "semantic_imports": semantic_imports, "symbols": symbols, "generated_surfaces": _generated_surfaces(files), "runtime_surfaces": [{"path": path, "provenance": "entrypoint filename convention; advisory"} for path in files if Path(path).name in RUNTIME_NAMES], "ownership": _ownership(root), "architecture": _structured_source(root, (".keel/architecture.json", "architecture.json"), "architecture"), "analyzers": {"python": analyzer}, "policy": "derived-navigation-evidence-only"}
    result["impact_contract"] = {"status": "AVAILABLE", "provenance": "analyze_impact over derived facts", "policy": "advisory-only"}
    return result


def write(root: Path, result: dict) -> Path:
    target = root / ".keel" / "knowledge" / "repository-map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
