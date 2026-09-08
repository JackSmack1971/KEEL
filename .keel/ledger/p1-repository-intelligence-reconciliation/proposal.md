# Proposal

## Problem / why
The P1 implementation is landed and anchored, but the authoritative audit, active roadmap, and subordinate plan still describe the workstream as current/in progress.

## Objective
Reconcile those documents to the anchored P1 evidence, preserve downstream locks, and archive the completed subordinate ExecPlan without changing implementation or lifecycle evidence.

## Non-goals
No implementation changes, no P2–P7 or D1 work, no generated artifacts, no runtime/external effects, and no manual lifecycle-record edits.

## Success evidence
The audit cites the landed P1 commit/anchor and marks the mapped rows complete; the roadmap marks P1 landed while preserving P2 not instantiated, P4 blocked, P5–P7 future/locked, and D1 deferred; the P1 plan is moved to completed; strict checks and diff validation pass.

## Open decisions
None; the anchored P1 ledger is the source for landed evidence.
