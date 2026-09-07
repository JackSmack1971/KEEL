from __future__ import annotations

import ast
import json
from pathlib import Path

IGNORE_DIRS = {".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__"}
MODULE_ROOTS = {"src", "app", "lib", "packages", "services", "cmd", "modules", "components"}
DEPENDENCY_MANIFESTS = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json", "Package.swift"}
COMMAND_FILES = {"Makefile", "CMakeLists.txt", "Taskfile.yml", "Taskfile.yaml", "justfile", "tox.ini", ".pre-commit-config.yaml"}


def _ignored(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part in IGNORE_DIRS for part in parts) or parts[:2] == (".keel", "knowledge")


def _row(path: str, rule: str) -> dict:
    return {"path": path, "rule": rule}


def _python_semantics(root: Path, files: list[str]) -> tuple[dict, list[dict]]:
    python_files = [path for path in files if path.endswith(".py")]
    modules = {}
    for path in python_files:
        rel = Path(path).with_suffix("").as_posix()
        if rel.endswith("/__init__"):
            rel = rel[:-9]
        modules[rel.replace("/", ".")] = path
        modules.setdefault(Path(path).stem, path)
    imports = []
    failures = []
    for path in python_files:
        source = root / path
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=path)
        except (OSError, SyntaxError) as exc:
            failures.append({"path": path, "error": type(exc).__name__, "analyzer": "python-ast"})
            continue
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
    return {"status": "PARTIAL" if failures else "COMPLETE", "analyzer": "python-ast", "files_analyzed": len(python_files) - len(failures), "files_failed": len(failures), "provenance": "stdlib-ast; repository source bytes"}, sorted(imports, key=lambda row: (row["source"], row["line"], row["target"]))


def _ownership(root: Path) -> dict:
    candidates = [Path("CODEOWNERS"), Path(".github/CODEOWNERS"), Path("docs/CODEOWNERS")]
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
        return {"status": "AVAILABLE", "source": relative.as_posix(), "provenance": "literal CODEOWNERS rules; no identity validation", "rules": rules}
    return {"status": "UNAVAILABLE", "source": None, "provenance": "no supported CODEOWNERS source found", "rules": []}


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
    analyzer, semantic_imports = _python_semantics(root, files)
    return {"schema_version": 3, "root": ".", "rules_version": 1, "counts": {"files": len(files), "directories": len(dirs)}, "topology": topology, "modules": modules, "entrypoints": entrypoints, "tests": tests, "commands": commands, "dependencies": dependencies, "source": source, "semantic_imports": semantic_imports, "ownership": _ownership(root), "analyzers": {"python": analyzer}, "policy": "derived-navigation-evidence-only"}


def write(root: Path, result: dict) -> Path:
    target = root / ".keel" / "knowledge" / "repository-map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
