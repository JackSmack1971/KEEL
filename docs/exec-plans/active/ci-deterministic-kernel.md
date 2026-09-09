# ExecPlan: deterministic hosted kernel CI proof

Status: `ACTIVE`

## Objective and success evidence
Add a thin GitHub Actions surface that invokes one repository-owned deterministic verifier from fresh Ubuntu and Windows checkouts. Success requires visible category results, drift and hygiene failure probes, explicit unavailable-runtime reporting, local full-suite success, hosted runner evidence, and exact candidate/landed Git proof.

## Non-goals
No live Codex/model invocation, API credential, paid provider path, control-plane redesign, macOS claim without current proof, or later North-Star implementation.

## Verified context
Baseline commit is `d9498d5acbebd533d1707642089e7f624c275884` on local branch `work`; the repository has no configured remote or local `main` ref, so actual remote `main` and hosted checks cannot yet be observed locally. The dependency-free tests are executable files rather than one discoverable unittest suite. The bootstrap manifest has a declared producer and drift check. Static hook tests explicitly do not prove installed runtime activation.

## Assumptions to test
- Every canonical `test_*.py` entry point succeeds under a single portable Python subprocess runner.
- Git-backed tests configure their own identity and behave equivalently on hosted Windows.
- Hosted CI does not provide `codex`; the smoke reporter must therefore emit `UNVERIFIED_RUNTIME` without executing a model.
- macOS is excluded because current Linux-only local evidence cannot establish full suite behavior there.

## Risk / autonomy / permission boundaries
This is a high-risk control-plane-adjacent and external-CI change. The workflow uses read-only contents permission, receives no secrets, sets bytecode suppression, and never launches Codex. PR creation and any remote landing are external effects requiring the requested delivery path and available repository authorization; missing remote/credentials are blockers, not fabricated evidence.

## Milestones
### M1 — Repository-owned verifier
- Action: implement explicit categories, deterministic subprocess execution, manifest/config drift checks, runtime absence reporting, and hygiene scanning.
- Observation: category/result JSON lines and nonzero status on any failed check.
- Verification: contract tests plus intentional drift/hygiene/regression probes.
- Exit criteria: all AC mappings are mechanically inspectable.

### M2 — Hosted workflow and documentation
- Action: add a thin Linux/Windows matrix and reconcile CI trust-boundary docs.
- Observation: YAML contains setup only and calls the repository verifier.
- Verification: structural contract tests and documentation contract.
- Exit criteria: no secret/model path and no live-runtime claim.

### M3 — Exact verification and delivery
- Action: run complete suite, KEEL verify/evidence, commit, seal, create PR, observe hosted jobs, and use authorized landing transaction.
- Observation: exact-subject receipts, candidate seal, hosted job conclusions, landed anchor.
- Verification: clean landed `main` rerun on Linux and Windows.
- Exit criteria: all ACs have genuine evidence or work stops with an explicit blocker.

## Baseline
`python3 -B -m unittest discover -s .keel/tests -p 'test_*.py' -v` exits 0 but discovers only six unittest-style tests; other canonical test files execute through their own entry points. No Git remote or `main` ref is configured in this checkout.

## Progress log
- 2026-09-09: inspected governance, current local commit/refs, test inventory, canonical verifier registry, generated-manifest contract, runtime smoke semantics, and active plans.

## Decision log
- Use an explicit repository-owned category manifest, not shell globbing in YAML, to keep OS behavior and output equivalent.
- Exclude macOS until complete hosted evidence exists; Linux and Windows are the required proven matrix.
- Treat runtime absence as a successful *truthfulness check* only when the smoke payload itself says `UNVERIFIED_RUNTIME`; never label it live PASS.

## Failure branches / blockers
A missing remote, GitHub authorization, hosted runner access, merge authorization, or landed-main checkout blocks the corresponding external acceptance criteria. Any platform divergence, generated drift, forbidden artifact, or model/credential surface blocks sealing/landing.

## Final verification
Pending implementation.

## Completion / handoff
Pending exact candidate verification, PR, authorized landing, and landed-main re-verification.
- 2026-09-09: implemented the thin Linux/Windows workflow, repository-owned category runner, explicit non-live runtime path, hygiene scanning, scope support for `.github`, contract tests, manifest registration, and trust-boundary documentation.
- 2026-09-09: full local deterministic runner passed. Perturbation probes produced nonzero exits for a bytecode cache directory, canonical manifest byte drift, and a temporary failing `test_ci_failure_probe.py`; the probe file was removed.

Local verification establishes implementation behavior only. Hosted Linux/Windows execution, actual current remote `main`, independent review, PR checks, authorized landing, and landed-main re-verification remain pending external evidence and must not be inferred from local success.
