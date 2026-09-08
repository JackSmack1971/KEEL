from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import re
from pathlib import Path


PASS = "VERIFIED"
UNVERIFIED_RUNTIME = "UNVERIFIED_RUNTIME"
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def _finding(status: str, reason: str, **details) -> dict:
    return {"status": status, "reason": reason, **details}


def _literal_argv(argv) -> tuple[bool, str]:
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
        return False, "argv must be a non-empty list of literal strings"
    if any("$" in x or "`" in x or "&&" in x or "||" in x or ";" in x for x in argv):
        return False, "shell interpolation is not permitted"
    return True, "ok"


def resolve_command(root: Path, declaration: dict | None = None, candidates: list[dict] | None = None, authorized: bool = True) -> dict:
    """Resolve one verification command without guessing or silently skipping it."""
    if declaration is not None:
        argv = declaration.get("argv")
        ok, reason = _literal_argv(argv)
        if not ok:
            return _finding("FAILED", reason, source="declared")
        if any(Path(part).is_absolute() or WINDOWS_ABSOLUTE_RE.match(part) for part in argv):
            return _finding("FAILED", "absolute creator-machine command path is not portable", source="declared", argv=argv)
        if declaration.get("requires_authorization") and not authorized:
            return _finding("BLOCKED", "command authorization is required", source="declared", argv=argv)
        executable = argv[0]
        if executable.startswith("."):
            executable_path = (root / executable).resolve()
            try:
                executable_path.relative_to(root.resolve())
            except ValueError:
                return _finding("FAILED", "command executable escapes repository", source="declared", argv=argv)
            available = executable_path.is_file()
        else:
            available = shutil.which(executable) is not None
        if available:
            for argument in argv[1:]:
                if argument.startswith(".") and not (root / argument).exists():
                    available = False
                    break
        if not available:
            return _finding("UNAVAILABLE", "declared command executable is unavailable", source="declared", argv=argv)
        return _finding(PASS, "declared repository-relative command is executable", source="declared", argv=argv, provenance=declaration.get("provenance", "runtime contract"))

    valid = []
    proven_unavailable = []
    unproven = []
    for candidate in candidates or []:
        if not isinstance(candidate, dict):
            continue
        argv = candidate.get("argv")
        ok, reason = _literal_argv(argv)
        provenance = candidate.get("provenance")
        if not ok or not provenance or candidate.get("repository_owned") is not True:
            unproven.append(candidate)
            continue
        if any(Path(part).is_absolute() or WINDOWS_ABSOLUTE_RE.match(part) for part in argv):
            unproven.append(candidate)
            continue
        available = shutil.which(argv[0]) is not None or (argv[0].startswith(".") and (root / argv[0]).is_file())
        if not available:
            proven_unavailable.append(candidate)
            continue
        valid.append(candidate)
    if len(valid) == 0:
        if unproven:
            return _finding(UNVERIFIED_RUNTIME, "discovered command candidate exists but provenance/trust is unproven", candidates=unproven)
        if proven_unavailable:
            return _finding("UNAVAILABLE", "provenance-bearing discovered command is unavailable", candidates=proven_unavailable)
        return _finding("UNSUPPORTED", "zero valid provenance-bearing discovered commands", candidates=len(candidates or []))
    if len(valid) > 1:
        return _finding("AMBIGUOUS", "multiple valid discovered commands", candidates=valid)
    if valid[0].get("requires_authorization") and not authorized:
        return _finding("BLOCKED", "discovered command authorization is required", candidates=valid)
    return _finding(PASS, "one provenance-bearing discovered command selected", source="discovered", **valid[0])


def config_portability(root: Path, config: dict) -> dict:
    findings = []
    for command in config.get("verification_commands", []):
        result = resolve_command(root, command)
        if result["status"] != PASS:
            findings.append({"id": command.get("id"), **result})
    return {"status": PASS if not findings else "FAILED", "findings": findings}


def classify_git_state(path: Path, requires_git: bool = False) -> dict:
    try:
        result = subprocess.run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], text=True, capture_output=True)
    except OSError as exc:
        return _finding("UNAVAILABLE", "Git executable is unavailable", error=str(exc))
    if result.returncode == 0 and result.stdout.strip() == "true":
        return _finding("VALID_GIT_REPOSITORY", "Git authority is available")
    error = (result.stderr or result.stdout).strip()
    if "not a git repository" in error.lower():
        return _finding("BLOCKED" if requires_git else "NOT_A_GIT_REPOSITORY", "Git authority is absent", operation_requires_git=requires_git)
    return _finding("FAILED", "Git failed for a reason other than NOT_A_GIT_REPOSITORY", error=error)


def classify_bootstrap(root: Path, requires_git: bool = False) -> dict:
    manifest = root / ".control-plane" / "bootstrap-manifest.json"
    if not manifest.is_file():
        return _finding("INCOMPLETE_BOOTSTRAP", "bootstrap manifest is missing")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _finding("MALFORMED_BOOTSTRAP", "bootstrap manifest is not valid JSON", error=str(exc))
    required = {"schema_version", "bootstrapper", "files"}
    if not required <= set(data) or not isinstance(data.get("files"), dict):
        return _finding("MALFORMED_BOOTSTRAP", "bootstrap manifest lacks required metadata")
    git = classify_git_state(root, requires_git)
    if git["status"] == "VALID_GIT_REPOSITORY":
        return _finding("VALID_GIT_REPOSITORY", "complete bootstrap with Git authority", producer=data.get("producer"))
    if git["status"] == "NOT_A_GIT_REPOSITORY":
        return _finding("COPIED_EXTRACTED_FRAMEWORK", "valid bootstrap metadata without Git authority", producer=data.get("producer"))
    return _finding(git["status"], "bootstrap state inherits Git classification", git=git)


def artifact_boundary(paths: list[str]) -> dict:
    classes = {}
    prohibited = []
    for raw in sorted(paths):
        path = raw.replace("\\", "/")
        if path.startswith((".keel/ledger/", ".keel/audit/", ".git/")) or path in {".keel/active-change", ".control-plane/runtime-validation.json"}:
            kind = "runtime_history"
        elif path.startswith((".keel/", ".codex/", ".agents/skills/", ".control-plane/")):
            kind = "framework"
        elif path.startswith(("dist/", "build/", "coverage/", ".cache/")):
            kind = "generated_consumer"
        elif path.startswith((".venv/", "venv/", "node_modules/")) or Path(path).is_absolute():
            kind = "machine_local"
        else:
            kind = "consumer"
        classes[path] = kind
        if kind != "framework":
            prohibited.append({"path": path, "class": kind})
    return {"status": PASS if not prohibited else "FAILED", "classes": classes, "prohibited": prohibited}


def classify_compatibility(metadata: dict, supported_version: str = "0.1.0", migrations: set[str] | None = None) -> dict:
    if not isinstance(metadata, dict) or "version" not in metadata:
        return _finding("MISSING_METADATA", "required version metadata is missing")
    version = metadata.get("version")
    if version == supported_version:
        return _finding("COMPATIBLE", "version is supported", version=version)
    if migrations and version in migrations:
        return _finding("MIGRATION_REQUIRED", "version has a registered migration", version=version)
    if isinstance(version, str) and version.split(".", 1)[0].isdigit() and version.split(".", 1)[0] == supported_version.split(".", 1)[0]:
        return _finding("INCOMPATIBLE", "version is in the family but outside the supported contract", version=version)
    return _finding("UNSUPPORTED", "version is outside the supported contract", version=version)


def attest(root: Path, paths: list[str], runtime_available: bool = True) -> dict:
    entries = []
    for rel in sorted(paths):
        path = (root / rel).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            return _finding("FAILED", "attestation path escapes repository", path=rel)
        if not path.is_file():
            return _finding("FAILED", "attestation input is missing", path=rel)
        entries.append({"path": rel.replace("\\", "/"), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    status = PASS if runtime_available else UNVERIFIED_RUNTIME
    return {"status": status, "root": ".", "entries": entries, "runtime": "AVAILABLE" if runtime_available else "UNAVAILABLE"}


def manifest_producer(root: Path, write: bool = False) -> dict:
    path = root / ".control-plane" / "bootstrap-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["producer"] = {"command": ["python", ".keel/bin/keel.py", "manifest", "--write"], "source": ".keel/lib/p0_contract.py"}
    for rel in sorted(data.get("files", {})):
        target = root / rel
        if not target.is_file():
            return _finding("FAILED", "manifest-listed input is missing", path=rel)
        data["files"][rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    for seed in data.get("seed_sources", []):
        target = root / seed["path"]
        if not target.is_file():
            return _finding("FAILED", "manifest-listed seed input is missing", path=seed["path"])
        seed["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    encoded = json.dumps(data, indent=2, sort_keys=False) + "\n"
    current = path.read_text(encoding="utf-8")
    if write:
        path.write_bytes(encoded.encode("utf-8"))
    elif current != encoded:
        return {"status": "FAILED", "reason": "generated manifest drift requires producer regeneration", "producer": data["producer"], "digest": hashlib.sha256(encoded.encode()).hexdigest()}
    return {"status": "WRITTEN" if write else "VERIFIED", "producer": data["producer"], "digest": hashlib.sha256(encoded.encode()).hexdigest()}


def generated_artifact_status(root: Path) -> dict:
    path = root / ".control-plane" / "bootstrap-manifest.json"
    if not path.is_file():
        return _finding("BLOCKED", "generated artifact is missing")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _finding("FAILED", "generated artifact is malformed", error=str(exc))
    producer = data.get("producer")
    if not isinstance(producer, dict) or not producer.get("command") or not producer.get("source"):
        return _finding("BLOCKED", "generated artifact has no trusted producer")
    if not (root / producer["source"]).is_file():
        return _finding(UNVERIFIED_RUNTIME, "generated artifact producer is unavailable", producer=producer)
    result = manifest_producer(root, write=False)
    return result if result["status"] != "VERIFIED" else _finding(PASS, "generated artifact matches its producer", producer=producer, digest=result["digest"])
