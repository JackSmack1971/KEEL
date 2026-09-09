# Change ci-deterministic-kernel

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Establish deterministic zero-incremental-cost hosted Linux and Windows CI proof for the existing portable KEEL kernel, with truthful runtime boundaries and no control-plane redesign beyond CI verifiability.

## Requirements
- `REQ-01` Hosted GitHub Actions runs the fresh-checkout deterministic suite on Linux and Windows; macOS exclusion is reasoned from current portability evidence.
- `REQ-02` The CI suite visibly exercises public CLI, ledger/kernel, scheduler, evidence, Git proof/candidate/landing, portability/install, documentation/contracts, hook wire-contract, and Codex App Server fixture categories.
- `REQ-03` The runtime-dependent Codex smoke reports PASS, a genuine failure, or UNVERIFIED_RUNTIME and never converts runtime absence into live verification.
- `REQ-04` CI makes no model/API calls, uses no paid-service credential, and adds no incremental AI-cost mechanism.
- `REQ-05` CI fails when the generated bootstrap manifest or validated configuration drifts from its declared source.
- `REQ-06` CI performs deterministic cache, temporary-artifact, and Python bytecode hygiene checks.
- `REQ-07` The workflow YAML remains thin and delegates validation to repository-owned Python tooling.
- `REQ-08` Authoritative documentation explicitly limits hosted CI proof to repository behavior and excludes live Codex hook/runtime activation.
- `REQ-09` A fresh checkout of the candidate executes the full deterministic suite successfully.
- `REQ-10` A temporary deliberately failing kernel-test probe makes the repository-owned CI command fail and is not landed.
- `REQ-11` Hosted-CI Codex runtime absence is explicitly reported as UNVERIFIED_RUNTIME.
- `REQ-12` Canonical serialization, path handling, Git proof, and ledger validation have equivalent pass/fail behavior on Linux and Windows.
- `REQ-13` Affected plans and architecture/control-plane/verification documentation are reconciled without advancing a later North-Star stage.

## Non-goals
- Do not activate or invoke a live Codex/model runtime in hosted CI.
- Do not add API keys, paid credentials, provider fallbacks, credit purchase, account rotation, or rate-limit evasion.
- Do not redesign kernel lifecycle, authorization, scheduler, evidence, or Git landing semantics.
- Do not implement or mark any later North-Star roadmap stage complete.
- Do not add macOS unless the complete dependency-free suite is proven credential-free and portable.

## Scope
- `.github/workflows/deterministic-kernel.yml`
- `.keel/ci/verify.py`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `.keel/lib/canonical_ledger.py`
- `.keel/tests/smoke_codex_app_server.py`
- `.keel/tests/test_canonical_ledger.py`
- `.keel/tests/test_deterministic_ci.py`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `docs/control-plane/TESTING_CI_GENERATED.md`
- `docs/control-plane/VERIFICATION.md`
- `docs/exec-plans/active/ci-deterministic-kernel.md`
- `docs/exec-plans/completed/ci-deterministic-kernel.md`

## Consequences
- A falsely green workflow could misrepresent cross-platform kernel correctness or live runtime activation.
- A CI command that reaches Codex or credentials could violate ZERO_INCREMENTAL_COST.
- Platform-specific command or path behavior could silently diverge.
