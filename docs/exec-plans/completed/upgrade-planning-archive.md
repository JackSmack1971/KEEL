# Upgrade planning archive

Documents in this directory are historical implementation slices or superseded
planning reasoning. They cannot authorize or direct current implementation.
The current forward authority is
[`../../control-plane/KEEL_FORWARD_AUTHORITY.md`](../../control-plane/KEEL_FORWARD_AUTHORITY.md).

## Completed bounded slices

Archived slices (with corresponding `.keel/ledger/*` evidence where present):

`capability-resolver-operationalization`, `context-compiler-operationalization`, `developer-ux-surface`, `effect-inference`, `engineering-protocols-skill`, `environment-contracts`, `evidence-graph-traceability`, `evidence-status-reconciliation`, `feedback-entropy-loop`, `feedback-evaluation-queue`, `feedback-target-plans`, `goal-plan-entropy`, `lifecycle-compatibility`, `lifecycle-telemetry`, `mission-dispatch-plan`, `mission-status-reconciliation`, `mission-work-graph`, `next-action-computation`, `ownership-source-discovery`, `provider-effect-contracts`, `repository-map`, `repository-semantic-map`, `schema-evidence-adapter`, `schema-migration-engine`, `telemetry-status-reconciliation`, `topology-routing`, `typed-spec-metadata`, `typed-surface-enforcement`, `upgrade-progress-reconciliation`, `upgrade-source-traceability`, and `worktree-lifecycle`.

Some named slices have no standalone plan file in the current tree; their repository evidence is retained in ledger/audit history.

## Superseded top-level plans

`upgrades-audit-runtime-kernel`, `keel-upgrade-goal`, `final-plan-reconciliation`, `final-audit-trace-reconciliation`, `remaining-plan-completeness`, and `upgrade-final-status-reconciliation` are superseded by the consolidated active roadmap. Their reasoning is retained in the archived files.

## Benchmark/evaluation pause

Benchmark-related work is deferred. No active benchmark plan is authorized. `keelbench-operationalization` and `post-landing-benchmark-reconciliation` have no standalone plan file in the current tree; related ledger or `.keel/bench/` artifacts remain historical and do not authorize execution. Benchmark references in archived plans are historical only.
