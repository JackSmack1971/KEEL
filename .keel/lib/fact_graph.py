"""Canonical, deterministic repository FactGraph and read-only adapter SPI.

Adapters inspect repository evidence and emit facts/edges.  They never execute
commands, grant authority, or turn filename heuristics into policy declarations.
"""
from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Protocol

SCHEMA = "keel.fact-graph/v1"
IGNORE_DIRS = {".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv", "__pycache__"}
MODULE_ROOTS = {"src", "app", "lib", "packages", "services", "cmd", "modules", "components"}
DEPENDENCY_MANIFESTS = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json", "Package.swift"}
COMMAND_FILES = {"Makefile", "CMakeLists.txt", "Taskfile.yml", "Taskfile.yaml", "justfile", "tox.ini", ".pre-commit-config.yaml"}
SOURCE_GLOBS = ["src/**", "app/**", "lib/**", "packages/**", "services/**", "cmd/**", "firmware/**", "embedded/**", "infra/**", "migrations/**", "**/*.c", "**/*.cc", "**/*.cpp", "**/*.cxx", "**/*.h", "**/*.hpp", "**/*.cs", "**/*.go", "**/*.java", "**/*.kt", "**/*.kts", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx", "**/*.vue", "**/*.svelte", "**/*.astro", "**/*.py", "**/*.rb", "**/*.rs", "**/*.swift", "**/*.scala", "**/*.lua", "**/*.php", "**/*.r", "**/*.R", "**/*.Rmd", "**/*.sql", "**/*.sol", "**/*.zig", "**/*.proto", "**/*.graphql", "**/*.gql", "**/*.cue", "**/*.nix", "**/*.hcl", "**/*.tf", "**/*.tfvars", "**/*.ipynb", "**/*.glsl", "**/*.vert", "**/*.frag", "**/*.wgsl", "Dockerfile", "Dockerfile.*", "Makefile", "CMakeLists.txt", "BUILD", "WORKSPACE", "MODULE.bazel", "**/*.bzl"]
NON_SOURCE_GLOBS = ["docs/**", "**/*.md", "**/*.mdx", "LICENSE*", "README*", "CHANGELOG*", ".github/ISSUE_TEMPLATE/**"]
CAPABILITY_RULES = {
 "build-toolchain": {"candidate": ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts", "*.sln", "*.csproj", "Gemfile", "composer.json", "mix.exs", "Package.swift", "CMakeLists.txt", "Makefile", "BUILD", "WORKSPACE", "MODULE.bazel"]},
 "dependencies-supply-chain": {"candidate": ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "uv.lock", "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock", "packages.lock.json"], "weak": ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "Gemfile", "composer.json"]},
 "testing-evals": {"candidate": ["pytest.ini", "tox.ini", "tests/**", "test/**", "spec/**", "evals/**"]},
 "quality-static-analysis": {"candidate": ["eslint.config.*", ".eslintrc*", "ruff.toml", ".ruff.toml", "mypy.ini", ".golangci.yml", ".pre-commit-config.yaml"]},
 "generated-artifacts": {"weak": ["generated/**", "gen/**", "*.generated.*", "*_pb2.py", "*.pb.go"]},
 "environments-worktrees": {"candidate": ["Dockerfile", "Dockerfile.*", "docker-compose.yml", "compose.yml", ".devcontainer/**"]},
 "privacy-data": {"weak": ["migrations/**", "prisma/schema.prisma", "db/**", "database/**", "schema.sql"]},
 "api-contracts": {"candidate": ["openapi.json", "openapi.yaml", "**/*.proto", "**/*.graphql"]},
 "ui-browser-a11y-i18n": {"weak": ["playwright.config.*", "cypress.config.*", "src/**/*.tsx", "src/**/*.jsx", "public/**", "locales/**"]},
 "performance-capacity-cost": {"weak": ["bench/**", "benches/**", "benchmark/**", "benchmarks/**", "k6.*"]},
 "observability": {"weak": ["otel-collector*.yml", "prometheus.yml", "grafana/**", "observability/**", "telemetry/**"]},
 "ci-cd": {"candidate": [".github/workflows/**", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/**"]},
 "release-deploy-rollback": {"weak": ["release/**", ".releaserc*", "helm/**", "charts/**", "deploy/**"]},
 "migrations-backup-dr": {"candidate": ["migrations/**", "alembic/**", "prisma/migrations/**", "db/migrate/**"]},
 "infra-iac": {"candidate": ["**/*.tf", "terraform/**", "k8s/**", "kubernetes/**", "helm/**", "charts/**"]},
 "ml-data-agent-evals": {"weak": ["evals/**", "datasets/**", "data/**", "notebooks/**", "**/*.ipynb", "ml/**", "models/**", "prompts/**", "agents/**"]},
 "embedded-hardware-safety": {"candidate": ["platformio.ini", "firmware/**", "embedded/**", "hardware/**", "boards/**"]},
 "external-integrations-mcp": {"weak": [".mcp.json", "mcp.json", "mcp/**", "plugins/**", "integrations/**"]},
}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _digest(value: Any) -> str:
    return hashlib.sha256((_json(value) if not isinstance(value, bytes) else value).encode("utf-8") if isinstance((_json(value) if not isinstance(value, bytes) else value), str) else value).hexdigest()

def match(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or (pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:])) or (pattern.endswith("/**") and path.startswith(pattern[:-3].rstrip("/") + "/"))

@dataclass(frozen=True)
class Provenance:
    adapter: str
    source: str | None
    source_digest: str | None
    authority_class: str = "observed"
    rule: str | None = None

@dataclass(frozen=True)
class Fact:
    kind: str
    subject: str
    value: Any
    provenance: Provenance
    knowledge: str = "KNOWN"
    support: str = "SUPPORTED"
    freshness: str = "CURRENT"
    confidence: float = 1.0
    id: str = ""
    def normalized(self) -> "Fact":
        identity = self.id or "fact:" + _digest({"kind": self.kind, "subject": self.subject, "value": self.value, "provenance": asdict(self.provenance), "knowledge": self.knowledge, "support": self.support, "freshness": self.freshness, "confidence": self.confidence})
        return Fact(self.kind, self.subject, self.value, self.provenance, self.knowledge, self.support, self.freshness, self.confidence, identity)

@dataclass(frozen=True)
class Edge:
    relation: str
    source: str
    target: str
    provenance: Provenance
    knowledge: str = "KNOWN"
    support: str = "SUPPORTED"
    inputs: tuple[str, ...] = ()
    id: str = ""
    def normalized(self) -> "Edge":
        identity = self.id or "edge:" + _digest({"relation": self.relation, "source": self.source, "target": self.target, "provenance": asdict(self.provenance), "knowledge": self.knowledge, "support": self.support, "inputs": sorted(self.inputs)})
        return Edge(self.relation, self.source, self.target, self.provenance, self.knowledge, self.support, tuple(sorted(set(self.inputs))), identity)

@dataclass(frozen=True)
class RepositorySnapshot:
    root: Path = field(compare=False, repr=False)
    paths: tuple[str, ...]
    digests: dict[str, str] = field(compare=False)
    config: dict[str, Any] = field(default_factory=dict, compare=False)

@dataclass(frozen=True)
class AdapterEmission:
    facts: tuple[Fact, ...] = ()
    edges: tuple[Edge, ...] = ()

class RepositoryAdapter(Protocol):
    name: str
    def collect(self, snapshot: RepositorySnapshot) -> AdapterEmission: ...

@dataclass(frozen=True)
class FactGraph:
    facts: tuple[Fact, ...]
    edges: tuple[Edge, ...]
    source_digest: str
    schema: str = SCHEMA

    def as_dict(self) -> dict[str, Any]:
        facts = [dict(asdict(f), provenance=asdict(f.provenance)) for f in self.facts]
        edges = [dict(asdict(e), provenance=asdict(e.provenance), inputs=list(e.inputs)) for e in self.edges]
        return {"schema": self.schema, "source_digest": self.source_digest, "facts": facts, "edges": edges}

    def serialize(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"

    def select(self, kind: str, subject: str | None = None) -> list[Fact]:
        return [f for f in self.facts if f.kind == kind and (subject is None or f.subject == subject)]

    def resolution(self, kind: str, subject: str) -> dict[str, Any]:
        rows = self.select(kind, subject)
        if not rows:
            return {"status": "UNKNOWN", "selected": None, "evidence": []}
        rank = {"declared": 0, "explicit": 1, "observed": 2, "heuristic": 3, "derived": 4}
        all_values = {_json(row.value) for row in rows}
        if len(all_values) > 1:
            return {"status": "CONFLICTING", "selected": None, "evidence": [row.id for row in rows], "precedence": "DECISION_REQUIRED"}
        best = min(rank.get(row.provenance.authority_class, 99) for row in rows)
        preferred = [row for row in rows if rank.get(row.provenance.authority_class, 99) == best]
        values = {_json(row.value) for row in preferred}
        return {"status": preferred[0].knowledge, "selected": preferred[0].value, "evidence": [row.id for row in rows], "precedence": sorted(rank, key=rank.get)}

    def freshness_against(self, root: Path) -> dict[str, str]:
        def state(item: Fact | Edge) -> str:
            p = item.provenance
            if p.adapter == "git" and p.source_digest:
                result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
                return "CURRENT" if result.returncode == 0 and result.stdout.strip() == p.source_digest else "STALE"
            if not p.source or not p.source_digest: return "UNKNOWN"
            source = root / p.source
            return "CURRENT" if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == p.source_digest else "STALE"
        return {item.id: state(item) for item in (*self.facts, *self.edges)}

    def impact(self, paths: Iterable[str]) -> dict[str, Any]:
        frontier = set(paths); reached = set(frontier); selected: list[str] = []
        changed = True
        while changed:
            changed = False
            for edge in self.edges:
                if edge.source in reached or edge.target in reached:
                    if edge.id not in selected: selected.append(edge.id)
                    for endpoint in (edge.source, edge.target):
                        if endpoint not in reached: reached.add(endpoint); changed = True
        return {"status": "KNOWN" if frontier else "UNKNOWN", "paths": sorted(frontier), "impacted": sorted(reached - frontier), "edge_ids": sorted(selected), "read_only": True}


def snapshot(root: Path, config: dict[str, Any] | None = None) -> RepositorySnapshot:
    root = root.resolve(); ignored = set(((config or {}).get("capability_resolver", {}) or {}).get("ignore_dirs", [])) | IGNORE_DIRS
    paths, digests = [], {}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in ignored for part in rel.parts[:-1]) or rel.parts[:2] == (".keel", "knowledge"):
            continue
        if path.is_file() or path.is_symlink():
            portable = PurePosixPath(*rel.parts).as_posix(); paths.append(portable)
            try: digests[portable] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError: digests[portable] = ""
    return RepositorySnapshot(root, tuple(sorted(set(paths))), digests, config or {})

class FilesystemAdapter:
    name = "filesystem"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        facts = [Fact("resource", ".", {"type": "repository"}, Provenance(self.name, None, _digest(s.digests)))]
        for path in s.paths:
            p = Provenance(self.name, path, s.digests.get(path))
            facts.append(Fact("resource", path, {"type": "file"}, p))
        return AdapterEmission(tuple(facts))

class GitAdapter:
    name = "git"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        try:
            proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=s.root, text=True, capture_output=True, timeout=5, check=False)
            commit = proc.stdout.strip() if proc.returncode == 0 else None
        except OSError: commit = None
        p = Provenance(self.name, ".git", commit, "observed", "git-metadata-read-only")
        return AdapterEmission((Fact("git-head", ".", commit, p, "KNOWN" if commit else "UNKNOWN", "SUPPORTED" if commit else "UNSUPPORTED"),))

class StructureAdapter:
    name = "repository-structure"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        facts: list[Fact] = []; edges: list[Edge] = []
        dirs = sorted({str(PurePosixPath(path).parent) for path in s.paths if str(PurePosixPath(path).parent) != "."})
        for path in s.paths:
            p = Provenance(self.name, path, s.digests.get(path), "heuristic")
            name = PurePosixPath(path).name
            for kind, yes in (("test", path.startswith(("tests/", "test/", "spec/", "evals/")) or name.startswith("test_")), ("entrypoint", name in {"main.py", "__main__.py", "index.js", "index.ts", "index.tsx"} or path.startswith(("bin/", "cmd/"))), ("dependency-manifest", name in DEPENDENCY_MANIFESTS)):
                if yes: facts.append(Fact(kind, path, True, p, confidence=.65))
            if name in COMMAND_FILES or path in {".keel/config.json", ".codex/config.toml"} or path.startswith(("scripts/", ".github/workflows/")):
                facts.append(Fact("command-candidate", path, {"source": path}, p, confidence=.65))
            explicit_s = [x for x in ((s.config.get("source_classification", {}) or {}).get("explicit_source_globs", [])) if isinstance(x, str) and match(path, x)]
            explicit_n = [x for x in ((s.config.get("source_classification", {}) or {}).get("explicit_non_source_globs", [])) if isinstance(x, str) and match(path, x)]
            if explicit_s: facts.append(Fact("source-class", path, "SOURCE", Provenance(self.name, ".keel/config.json", s.digests.get(".keel/config.json"), "explicit", str(explicit_s))))
            if explicit_n: facts.append(Fact("source-class", path, "NON_SOURCE", Provenance(self.name, ".keel/config.json", s.digests.get(".keel/config.json"), "explicit", str(explicit_n))))
            if not explicit_s and not explicit_n:
                value = "NON_SOURCE" if any(match(path, x) for x in NON_SOURCE_GLOBS) else "SOURCE" if any(match(path, x) for x in SOURCE_GLOBS) else "UNKNOWN"
                facts.append(Fact("source-class", path, value, p, "UNKNOWN" if value == "UNKNOWN" else "INFERRED", confidence=.55))
        for directory in dirs:
            if len(PurePosixPath(directory).parts) == 2 and PurePosixPath(directory).parts[0] in MODULE_ROOTS:
                facts.append(Fact("module", directory, True, Provenance(self.name, directory, None, "heuristic"), "INFERRED", confidence=.6))
        return AdapterEmission(tuple(facts), tuple(edges))

class CapabilityAdapter:
    name = "ecosystem-candidates"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        facts = []
        for capability, rule in sorted(CAPABILITY_RULES.items()):
            strong = [p for p in s.paths if any(match(p, x) for x in rule.get("candidate", []))]
            weak = [p for p in s.paths if any(match(p, x) for x in rule.get("weak", []))]
            evidence = strong or weak; patterns = rule.get("candidate", []) if strong else rule.get("weak", [])
            value = {"status": "DETECTED" if strong else "LIKELY" if weak else "UNKNOWN", "evidence": evidence, "evidence_details": [{"path": path, "patterns": [pat for pat in patterns if match(path, pat)], "kind": "detected" if strong else "likely"} for path in evidence]}
            facts.append(Fact("capability-candidate", capability, value, Provenance(self.name, None, _digest([s.digests.get(x) for x in strong or weak]), "heuristic", "filename/glob-candidate-only"), "INFERRED" if strong or weak else "UNKNOWN", confidence=1.0 if strong else .65 if weak else 0.0))
        known_manifests = set(DEPENDENCY_MANIFESTS)
        for path in s.paths:
            name = PurePosixPath(path).name
            if name.endswith((".toml", ".json", ".xml")) and name not in known_manifests and ("package" in name.lower() or "project" in name.lower()):
                facts.append(Fact("ecosystem-support", path, "UNSUPPORTED", Provenance(self.name, path, s.digests.get(path), "observed", "no-installed-adapter"), "UNKNOWN", "UNSUPPORTED"))
        return AdapterEmission(tuple(facts))

class PythonAdapter:
    name = "python-ast"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        files = [p for p in s.paths if p.endswith(".py")]; modules = {}
        for path in files:
            mod = str(PurePosixPath(path).with_suffix("")).replace("/", ".")
            if mod.endswith(".__init__"): mod = mod[:-9]
            modules[mod] = path; modules.setdefault(PurePosixPath(path).stem, path)
        facts: list[Fact] = []; edges: list[Edge] = []
        for path in files:
            p = Provenance(self.name, path, s.digests.get(path), "observed", "stdlib-ast")
            try: tree = ast.parse((s.root / path).read_text(encoding="utf-8"), filename=path)
            except (OSError, SyntaxError):
                facts.append(Fact("dependency-analysis", path, "FAILED", p, "UNKNOWN", "SUPPORTED")); continue
            facts.append(Fact("dependency-analysis", path, "COMPLETE", p))
            analysis = facts[-1].normalized()
            for node in ast.walk(tree):
                names = [x.name for x in node.names] if isinstance(node, ast.Import) else [((node.module + ".") if node.module else "") + x.name for x in node.names] if isinstance(node, ast.ImportFrom) else []
                for target in names:
                    lookup = target
                    if isinstance(node, ast.ImportFrom) and node.level:
                        parent = list(PurePosixPath(path).parent.parts)
                        lookup = ".".join(parent[:max(0, len(parent) - node.level + 1)] + ([target] if target else []))
                    resolved = modules.get(lookup) or modules.get(lookup.split(".")[0]); destination = resolved or "external:" + (target or "<unknown>")
                    facts.append(Fact("python-import", f"{path}:{node.lineno}:{target}", {"source": path, "target": target, "resolved": resolved, "kind": "local" if resolved else "external", "line": node.lineno, "analyzer": self.name}, p))
                    edges.append(Edge("depends-on", path, destination, p, "KNOWN" if resolved else "PARTIAL", "SUPPORTED", (analysis.id,)))
        return AdapterEmission(tuple(facts), tuple(edges))

class CodeownersAdapter:
    name = "codeowners"
    def collect(self, s: RepositorySnapshot) -> AdapterEmission:
        facts=[]; edges=[]
        for candidate in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"):
            if candidate not in s.paths: continue
            p=Provenance(self.name,candidate,s.digests.get(candidate),"declared","literal-rules")
            facts.append(Fact("ownership-source", candidate, True, p))
            for number,line in enumerate((s.root/candidate).read_text(encoding="utf-8",errors="replace").splitlines(),1):
                parts=line.strip().split()
                if parts and not parts[0].startswith("#") and len(parts)>=2:
                    facts.append(Fact("ownership-rule", f"{candidate}:{number}", {"pattern":parts[0],"owners":parts[1:]},p))
            break
        return AdapterEmission(tuple(facts),tuple(edges))

def build(root: Path, config: dict[str, Any] | None = None, adapters: Iterable[RepositoryAdapter] | None = None) -> FactGraph:
    s = snapshot(root, config)
    providers = tuple(adapters or (FilesystemAdapter(), GitAdapter(), StructureAdapter(), CapabilityAdapter(), PythonAdapter(), CodeownersAdapter()))
    facts: list[Fact] = []; edges: list[Edge] = []
    for adapter in providers:
        emission = adapter.collect(s); facts.extend(f.normalized() for f in emission.facts); edges.extend(e.normalized() for e in emission.edges)
    facts.sort(key=lambda f: (f.kind, f.subject, f.id)); edges.sort(key=lambda e: (e.relation, e.source, e.target, e.id))
    return FactGraph(tuple(facts), tuple(edges), _digest(s.digests))
