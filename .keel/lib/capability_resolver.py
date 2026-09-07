from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Iterable

IGNORE_DIRS = {".git", ".keel", ".control-plane", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__"}

# Detection is intentionally conservative: evidence is reported, policy is never silently activated.
RULES = {
    "build-toolchain": {
        "detected": ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts", "*.sln", "*.csproj", "Gemfile", "composer.json", "mix.exs", "Package.swift", "CMakeLists.txt", "Makefile", "BUILD", "WORKSPACE", "MODULE.bazel"],
    },
    "dependencies-supply-chain": {
        "detected": ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "uv.lock", "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock", "packages.lock.json"],
        "likely": ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "Gemfile", "composer.json"],
    },
    "testing-evals": {
        "detected": ["pytest.ini", "vitest.config.*", "jest.config.*", "playwright.config.*", "cypress.config.*", "tox.ini", "tests/**", "test/**", "spec/**", "evals/**"],
    },
    "quality-static-analysis": {
        "detected": ["eslint.config.*", ".eslintrc*", "ruff.toml", ".ruff.toml", "mypy.ini", ".golangci.yml", ".golangci.yaml", "clippy.toml", "biome.json", "biome.jsonc", ".pre-commit-config.yaml", "sonar-project.properties"],
    },
    "generated-artifacts": {
        "likely": ["generated/**", "gen/**", "openapi.json", "openapi.yaml", "openapi.yml", "*.generated.*", "*.g.cs", "*_pb2.py", "*.pb.go"],
    },
    "environments-worktrees": {
        "detected": ["Dockerfile", "Dockerfile.*", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", ".devcontainer/**"],
    },
    "privacy-data": {
        "likely": ["migrations/**", "prisma/schema.prisma", "alembic.ini", "db/**", "database/**", "schema.sql"],
    },
    "api-contracts": {
        "detected": ["openapi.json", "openapi.yaml", "openapi.yml", "**/*.proto", "**/*.graphql", "**/*.gql", "asyncapi.*"],
    },
    "ui-browser-a11y-i18n": {
        "likely": ["playwright.config.*", "cypress.config.*", "src/**/*.tsx", "src/**/*.jsx", "src/**/*.vue", "src/**/*.svelte", "app/**/*.tsx", "pages/**/*.tsx", "public/**", "locales/**", "i18n/**"],
    },
    "performance-capacity-cost": {
        "likely": ["bench/**", "benches/**", "benchmark/**", "benchmarks/**", "k6.*", "artillery.*", "locustfile.py"],
    },
    "observability": {
        "likely": ["otel-collector*.yml", "otel-collector*.yaml", "prometheus.yml", "prometheus.yaml", "grafana/**", "observability/**", "telemetry/**"],
    },
    "ci-cd": {
        "detected": [".github/workflows/**", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/**", "azure-pipelines.yml", "bitbucket-pipelines.yml"],
    },
    "release-deploy-rollback": {
        "likely": ["release/**", ".releaserc*", "release-please-config.json", "helm/**", "charts/**", "deploy/**"],
    },
    "migrations-backup-dr": {
        "detected": ["migrations/**", "alembic/**", "prisma/migrations/**", "db/migrate/**"],
    },
    "infra-iac": {
        "detected": ["**/*.tf", "terraform/**", "pulumi.*", "Pulumi.*.yaml", "k8s/**", "kubernetes/**", "helm/**", "charts/**", "cdk.json"],
    },
    "ml-data-agent-evals": {
        "likely": ["evals/**", "datasets/**", "data/**", "notebooks/**", "**/*.ipynb", "ml/**", "models/**", "prompts/**", "agents/**"],
    },
    "embedded-hardware-safety": {
        "detected": ["platformio.ini", "firmware/**", "embedded/**", "hardware/**", "boards/**"],
    },
    "external-integrations-mcp": {
        "likely": [".mcp.json", "mcp.json", "mcp/**", "plugins/**", "integrations/**"],
    },
}

SOURCE_GLOBS = [
    "src/**", "app/**", "lib/**", "packages/**", "services/**", "cmd/**", "firmware/**", "embedded/**", "infra/**", "migrations/**",
    "**/*.c", "**/*.cc", "**/*.cpp", "**/*.cxx", "**/*.h", "**/*.hpp", "**/*.cs", "**/*.go", "**/*.java", "**/*.kt", "**/*.kts",
    "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.vue", "**/*.svelte", "**/*.astro", "**/*.py", "**/*.rb", "**/*.rs", "**/*.swift",
    "**/*.scala", "**/*.lua", "**/*.php", "**/*.r", "**/*.R", "**/*.Rmd", "**/*.sql", "**/*.sol", "**/*.zig", "**/*.proto", "**/*.graphql",
    "**/*.gql", "**/*.cue", "**/*.nix", "**/*.hcl", "**/*.tf", "**/*.tfvars", "**/*.ipynb", "**/*.glsl", "**/*.vert", "**/*.frag", "**/*.wgsl",
    "Dockerfile", "Dockerfile.*", "Makefile", "CMakeLists.txt", "BUILD", "WORKSPACE", "MODULE.bazel", "**/*.bzl",
]
NON_SOURCE_GLOBS = ["docs/**", "**/*.md", "**/*.mdx", "LICENSE*", "README*", "CHANGELOG*", ".github/ISSUE_TEMPLATE/**"]


def _match(path: str, pattern: str) -> bool:
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:]):
        return True
    if pattern.endswith("/**") and path.startswith(pattern[:-3].rstrip("/") + "/"):
        return True
    return False


def iter_repo_paths(root: Path, ignore_dirs: Iterable[str] | None = None) -> list[str]:
    ignored = set(ignore_dirs or ()) | IGNORE_DIRS
    out: list[str] = []
    for p in root.rglob("*"):
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(part in ignored for part in p.relative_to(root).parts[:-1]):
            continue
        if p.is_file() or p.is_symlink():
            out.append(rel)
    return sorted(set(out))


def classify_path(path: str, config: dict | None = None) -> str:
    """Return SOURCE, NON_SOURCE, or UNKNOWN. Unknown is intentionally conservative to callers."""
    config = config or {}
    cls = config.get("source_classification", {}) if isinstance(config, dict) else {}
    explicit_source = cls.get("explicit_source_globs", []) if isinstance(cls, dict) else []
    explicit_non = cls.get("explicit_non_source_globs", []) if isinstance(cls, dict) else []
    for pat in explicit_source:
        if isinstance(pat, str) and _match(path, pat):
            return "SOURCE"
    for pat in explicit_non:
        if isinstance(pat, str) and _match(path, pat):
            return "NON_SOURCE"
    for pat in NON_SOURCE_GLOBS:
        if _match(path, pat):
            return "NON_SOURCE"
    for pat in SOURCE_GLOBS:
        if _match(path, pat):
            return "SOURCE"
    return "UNKNOWN"


def resolve(root: Path, config: dict | None = None) -> dict:
    config = config or {}
    ignore = (config.get("capability_resolver", {}) or {}).get("ignore_dirs", [])
    max_evidence = int((config.get("capability_resolver", {}) or {}).get("max_evidence_per_capability", 12))
    paths = iter_repo_paths(root, ignore)
    caps: dict[str, dict] = {}
    for cap, rule in RULES.items():
        detected = sorted({p for p in paths for pat in rule.get("detected", []) if _match(p, pat)})
        likely = sorted({p for p in paths for pat in rule.get("likely", []) if _match(p, pat)})
        if detected:
            status, confidence, ev = "DETECTED", 1.0, detected
        elif likely:
            status, confidence, ev = "LIKELY", 0.65, likely
        else:
            status, confidence, ev = "UNKNOWN", 0.0, []
        caps[cap] = {"status": status, "confidence": confidence, "evidence": ev[:max_evidence]}

    # Conflicts are explicit rather than silently resolved.
    conflicts = []
    source_classes = {p: classify_path(p, config) for p in paths}
    for p, cls in source_classes.items():
        explicit_s = [pat for pat in (config.get("source_classification", {}) or {}).get("explicit_source_globs", []) if isinstance(pat, str) and _match(p, pat)]
        explicit_n = [pat for pat in (config.get("source_classification", {}) or {}).get("explicit_non_source_globs", []) if isinstance(pat, str) and _match(p, pat)]
        if explicit_s and explicit_n:
            conflicts.append({"path": p, "reason": "matches explicit source and non-source classifiers", "source_globs": explicit_s, "non_source_globs": explicit_n})

    return {
        "schema_version": 1,
        "capabilities": caps,
        "conflicts": conflicts,
        "path_count": len(paths),
        "policy": "advisory-evidence-only",
    }


def write_resolution(root: Path, result: dict) -> Path:
    out = root / ".keel" / "knowledge" / "capabilities.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
