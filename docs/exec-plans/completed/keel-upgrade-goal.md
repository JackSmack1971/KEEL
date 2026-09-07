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
- Partial and implemented slices: repository map, mission DAG/frontier/dispatch contracts, topology routing, typed requirements/evidence surfaces, provider/effect contracts, native schema evidence, advisory effect inference, engineering protocols, feedback/entropy inspection and target plans, lifecycle telemetry/compatibility, and the tested config migration/rollback engine.
- Remaining: repository ownership policy/architecture relations, feedback scheduling/promotion/target execution, live migration orchestration/installer, deeper protocol evaluation, mission dispatch/retry/integration, runtime provider adapters, `run`, external tracker/PR adapters, external Codex checks, and empirical paired KEELBench trials. Advisory command effect inference, native schema evidence, mission dispatch contracts, lifecycle telemetry, and the config migration/rollback engine are implemented; runtime tool/API inference, token/cost/human metrics, and authorization enforcement remain.
- Source coverage: numbered recommendations 1-28 are explicitly mapped in `docs/control-plane/UPGRADE_AUDIT.md`; contextual competitor sections are separated from executable capability claims.

## Stopping rule

Do not mark the objective complete while an actionable local gap lacks implementation and verification. Mark prerequisite-dependent external capabilities as deferred only when the missing runtime/provider/target is recorded as the blocker and no safe repository-local implementation can prove the behavior.

## Next action after the current slices

Continue with the remaining local evidence/protocol/economics slices only where repository-local behavior can be proven; do not start external or empirical work until its recorded prerequisite exists.
