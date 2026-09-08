# ExecPlan: Receipt-authoritative verification

Status: `COMPLETE`

## Objective and success evidence
Replace flat command/evidence-graph authority with registry-selected exact-subject receipts. Hostile fixtures must disprove authority confusion, subject drift, unrelated green checks, duplicate registration, and uncovered requirements.

## Non-goals
Candidate/landing redesign, historical ledger rewrites, and remote provider implementation.

## Verified context
`keel_core.verify_change` executes every configured command before `evidence_graph.evaluate`; seal and anchor consume stable `verification.json` fields. Active config contains a duplicate and a historical SHA-pinned command.

## Assumptions to test
Path applicability plus explicit requirement IDs can choose sufficient local verifiers deterministically while compatibility consumers use projections.

## Risk / autonomy / permission boundaries
High-blast-radius control-plane migration. Fail closed. No external effects. Preserve old ledgers and seal semantics.

## Milestones
### M1 — Contracts and planner
Implement authority, registry validation, requirements, deterministic planning, receipts, and evaluation. Hostile fixtures are the exit evidence.
### M2 — Lifecycle migration
Make verification plan, execute, receipt, evaluate, then project old views. Receipt coverage must control SHIP.
### M3 — Configuration and docs
Remove duplicate/SHA-pinned active checks, retain a small kernel, document migration, and regenerate declared artifacts.

## Baseline
Direct executable tests passed; `unittest discover` found zero tests because repository tests are script-style and exited 5.

## Progress log
- 2026-09-08: proposal approved and current flow inspected.
- 2026-09-08: receipt authority, lifecycle projection, registry migration, hostile fixtures, documentation, and generated manifest completed; selected and full suites passed.

## Decision log
- Authority order: ASSERTED < INSPECTED < TESTED < RUNTIME_OBSERVED < INDEPENDENTLY_REVIEWED < FORMALLY_VERIFIED.
- Legacy files remain generated projections.

## Failure branches / blockers
Uncovered requirements, duplicate registry identity, unavailable verifier, receipt mismatch, or FAIL/INCONCLUSIVE blocks verification.

## Final verification
Run selected KEEL verification, hostile tests, all direct scripts, and diff checks; commit and seal.

## Completion / handoff
Commit current branch, create PR, seal exact commit, and integrate/anchor only when authorized and topology permits.
