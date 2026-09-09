#!/usr/bin/env python3
"""Portable, deterministic CI entry point. It never starts a Codex runtime."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / ".keel" / "tests"
CATEGORY_FILES = {
    "public-cli": {"test_public_cli_contract.py"},
    "ledger-kernel": {"test_canonical_ledger.py", "test_change_graph.py", "test_fact_graph.py", "test_ledger_migration.py", "test_runtime_authorization.py", "test_semantic_kernel.py"},
    "scheduler": {"test_scheduler.py", "smoke_scheduler.py"},
    "evidence": {"test_evidence_class_lifecycle.py", "test_evidence_graph.py", "test_evidence_system.py"},
    "git-proof-candidate-landing": {"test_candidate_attestation.py", "test_git_attestation_lifecycle.py", "test_git_proof.py", "test_landing_transaction.py"},
    "portability-bootstrap-install": {"test_environment_contract.py", "test_lifecycle_compatibility.py", "test_p0_contract.py", "test_portability_installation.py", "test_schema_migrations.py", "test_worktree_lifecycle.py"},
    "documentation-contracts": {"test_compatibility_retirement.py", "test_documentation_contract.py"},
    "hook-wire-contract": {"test_codex_adapter_kernel.py", "test_codex_hook_wire_contract.py", "test_hook_event_compatibility.py"},
    "codex-app-server-fixtures": {"test_codex_app_server_adapter.py", "test_codex_cost_preflight.py"},
}
FORBIDDEN_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


def emit(kind: str, **values: object) -> None:
    print(json.dumps({"kind": kind, **values}, sort_keys=True), flush=True)


def run(argv: list[str], category: str) -> bool:
    emit("check_start", category=category, argv=argv)
    result = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
    emit("check_result", category=category, status="PASS" if result.returncode == 0 else "FAIL", exit_code=result.returncode)
    return result.returncode == 0


def categorized_tests() -> list[tuple[str, Path]]:
    assigned = {name for names in CATEGORY_FILES.values() for name in names}
    rows: list[tuple[str, Path]] = []
    available = {p.name: p for p in TEST_ROOT.glob("test_*.py")}
    available["smoke_scheduler.py"] = TEST_ROOT / "smoke_scheduler.py"
    for category, names in CATEGORY_FILES.items():
        missing = names - available.keys()
        if missing:
            raise RuntimeError(f"{category} references missing tests: {sorted(missing)}")
        rows.extend((category, available[name]) for name in sorted(names))
    rows.extend(("remaining-kernel", available[name]) for name in sorted(available.keys() - assigned))
    return rows


def suite() -> bool:
    ok = True
    for category, path in categorized_tests():
        ok = run([sys.executable, "-B", str(path.relative_to(ROOT))], category) and ok
    for category, argv in (
        ("generated-manifest-drift", [sys.executable, "-B", ".keel/bin/keel.py", "manifest"]),
        ("validated-config", [sys.executable, "-B", ".keel/bin/keel.py", "compat"]),
    ):
        ok = run(argv, category) and ok
    return ok


def runtime_unavailable() -> bool:
    # CI proves the unavailable-runtime reporting branch without launching Codex.
    argv = [sys.executable, "-B", ".keel/tests/smoke_codex_app_server.py", "--no-live-runtime"]
    emit("check_start", category="codex-runtime-boundary", argv=argv)
    result = subprocess.run(argv, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        payload = {"status": "FAIL", "reason": "runtime smoke did not emit one JSON result"}
    status = payload.get("status")
    ok = result.returncode == 0 and status == "UNVERIFIED_RUNTIME"
    emit("check_result", category="codex-runtime-boundary", status=status if ok else "FAIL", exit_code=result.returncode, observation=payload)
    return ok


def hygiene() -> bool:
    offenders = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if ".git" in rel.parts:
            continue
        if any(part in FORBIDDEN_PARTS for part in rel.parts) or path.suffix in FORBIDDEN_SUFFIXES or path.name.endswith(".tmp-keel"):
            offenders.append(rel.as_posix())
    emit("hygiene_result", status="PASS" if not offenders else "FAIL", offenders=offenders)
    return not offenders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("all", "suite", "runtime", "hygiene"), nargs="?", default="all")
    args = parser.parse_args(argv)
    checks = []
    if args.command in {"all", "hygiene"}: checks.append(hygiene())
    if args.command in {"all", "suite"}: checks.append(suite())
    if args.command in {"all", "runtime"}: checks.append(runtime_unavailable())
    if args.command == "all": checks.append(hygiene())
    status = "PASS" if all(checks) else "FAIL"
    emit("ci_result", status=status, live_codex_runtime_verified=False)
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
