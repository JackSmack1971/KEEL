# Proposal

## Problem / why
KEEL governs individual changes but has no machine-validated objective-level work graph. This prevents safe dependency ordering and runnable-frontier guidance without introducing an autonomous scheduler.

## Objective
Add a repository-owned mission contract with deterministic DAG validation, dependency frontier computation, and read-only status projection from child KEEL ledgers.

## Non-goals
No agent dispatch, worktree creation, tracker integration, external effects, automatic ledger transitions, or bypass of per-change governance.

## Success evidence
Mission fixtures and focused tests prove valid DAGs, cycle/missing-dependency rejection, frontier ordering, and child-ledger status projection. Existing control-plane validation remains passing.

## Open decisions
Mission files are explicit JSON contracts under `.keel/missions/`; scheduling remains an external/future layer.
