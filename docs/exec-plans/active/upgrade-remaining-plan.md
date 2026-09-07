# Remaining KEEL upgrade workstreams

This plan is the durable handoff for the rows still marked partial or deferred in `docs/control-plane/UPGRADE_AUDIT.md`.

| Workstream | Boundary | Prerequisite | Acceptance evidence | Status |
|---|---|---|---|---|
| Repository ownership/architecture facts | Add explicit ownership sources and bounded architecture relations to the derived map; never infer authority from filenames alone. | Repository ownership policy and authoritative source files. | Deterministic map tests, provenance, conflict findings, strict validation. | Partial: CODEOWNERS discovery implemented; policy/architecture relations remain |
| Feedback promotion/scheduling/target evaluation | Queue valid observations for evaluation/promotion; promotion remains a reviewed KEEL write and target execution remains separate. | Reviewed observations and a representative target corpus. | Queue eligibility, provenance, target-eval result, authorized change ledger. | Partial: queue implemented; corpus/scheduling/target execution remain |
| Schema migration and rollback | Add versioned repository-owned migrations with preflight, backup/rollback contract, and recovery tests. | Operator-approved live migration policy and additional real legacy fixtures. | Fixture migration, rollback restoration, compatibility verification. | Partial: config 1→2 engine implemented; live orchestration/installer remain |
| Agent `run` and mission dispatch | Connect advisory dispatch contracts to an authorized execution runtime, worktree allocator, retry policy, and integration boundary. | Runtime/provider, credentials, and operator authorization. | Isolated dry run, failure recovery, evidence graph, no unauthorized integration. | Partial: dispatch contracts implemented; runtime execution deferred |
| Evidence adapters | Native local file/schema evidence exists; implement browser/log/metric/trace/device adapters behind configured provider contracts. | Project-specific connector/runtime and data-access authorization for runtime providers. | Native adapter tests plus real provider evidence. | Partial: local adapters implemented; runtime providers deferred |
| External tracker/PR integration | Add issue/PR read/write adapters with explicit effects and authorization. | Tracker identity, credentials, API contract, and integration policy. | Mock contract tests plus authorized sandbox operation. | Deferred |
| KEELBench empirical value | Run paired repeated trials from equivalent starts using a fixed representative corpus and rubric. | Representative tasks, baseline, and evaluation authority. | Reproducible trial artifacts and statistically defensible comparison. | Empirical prerequisite |

The effect-capability inference slice is implemented and anchored; runtime tool/API inference and authorization enforcement remain separate from this advisory analyzer.
