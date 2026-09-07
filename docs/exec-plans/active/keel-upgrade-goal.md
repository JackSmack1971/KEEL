# Long-horizon goal: KEEL upgrade audit and implementation

## Outcome

Audit `docs/KEEL_UPGRADES.md` against executable repository evidence, implement actionable missing capabilities, and leave prerequisite-dependent external work explicitly planned rather than falsely claimed complete.

## Constraints

- Repository evidence is authoritative.
- Every write uses a standard KEEL change unless clearly trivial.
- Preserve one change-id/one writer, scope confinement, acceptance evidence, authorization, sealed candidates, and landed anchors.
- Do not claim runtime provider, external Codex, tracker, installer, or empirical KEELBench behavior without direct evidence.

## Current evidence

- Implemented: capability resolution, context compilation, evidence traceability, KEELBench harness, `next`, worktree/environment primitives, reconciliation, compatibility inspection.
- Partial and implemented slices: repository map, mission DAG/frontier, topology routing, provider/effect contracts, engineering protocols, feedback/entropy inspection, lifecycle compatibility.
- Remaining: actual runtime provider adapters, command/tool effect inference, mission dispatch/retry/integration, semantic import/ownership mapping, promotion/scheduling, real installer/schema migrations/rollback, `run`, external tracker/PR adapters, and empirical paired KEELBench trials.

## Stopping rule

Do not mark the objective complete while an actionable local gap lacks implementation and verification. Mark prerequisite-dependent external capabilities as deferred only when the missing runtime/provider/target is recorded as the blocker and no safe repository-local implementation can prove the behavior.

## Next action after this UX slice

Reconcile the audit and determine whether remaining items are safely implementable locally or require explicit external prerequisites; run real KEELBench paired trials only when representative start states and a fixed rubric exist.
