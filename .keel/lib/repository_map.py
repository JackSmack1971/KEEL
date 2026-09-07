from __future__ import annotations

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
    return {"schema_version": 1, "root": ".", "rules_version": 1, "counts": {"files": len(files), "directories": len(dirs)}, "topology": topology, "modules": modules, "entrypoints": entrypoints, "tests": tests, "commands": commands, "dependencies": dependencies, "source": source, "policy": "derived-navigation-evidence-only"}


def write(root: Path, result: dict) -> Path:
    target = root / ".keel" / "knowledge" / "repository-map.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
