# KEEL upgrade remaining plan

This is the sole active top-level KEEL upgrade roadmap. The authoritative classifications are in [`docs/control-plane/UPGRADE_AUDIT.md`](../../control-plane/UPGRADE_AUDIT.md). A workstream is not authorized for implementation merely because it appears here.

## Execution sequence

### P0 — Portable verification and bootstrap contract
Objective: Remove creator-machine dependencies and establish reliable package/bootstrap/version states.

### P1 — Repository intelligence foundation
Objective: Build deterministic, provenance-bearing repository graph, command, ownership, architecture, dependency, impact, and generated-artifact intelligence.

### P2 — Mission schema and planning
Objective: Create expressive, deterministic, decomposable mission contracts without executing them.

### P3 — Runtime capability handshake
Objective: Observe actual runtime capabilities, trust state, hook readiness, and graceful-degradation state before dispatch.

### P4 — Mission execution
Objective: Execute bounded mission waves through an authorized runtime.

Status: **BLOCKED** until an authorized runtime/provider and operator authorization exist.

### P5 — Adaptive workflow and context/routing
Objective: Make workflow obligations, role-specific context, capability routing, uncertainty handling, and blast-radius reasoning evidence-driven and deterministic.

### P6 — Verification and lifecycle integrity
Objective: Strengthen typed assertions, verification selection, semantic diff protection, lifecycle/property invariants, effect semantics, independent evidence, and reproducibility.

### P7 — Non-benchmark feedback and observability
Objective: Improve lifecycle traceability, correlations, CLI/API projections, invariant ownership, and non-benchmark observation without performing empirical evaluation.

### D1 — Benchmark and evaluation
Status: **DEFERRED**. D1 is paused and is not a prerequisite for P0–P7.

Deferred scope includes benchmark implementation; corpus construction or expansion; evaluation authority; baseline-vs-KEEL paired trials; scoring; empirical comparison; benchmark-driven promotion; and benchmark telemetry experiments. Existing `.keel/bench/` contracts, schemas, ledgers, preparation, telemetry, and historical evidence remain preserved.

## Dependencies

```text
P0 → P1 → P2 → P3 → P4

P1 → P5
P2 → P5
P3 → P5
P1 + P2 + P5 → P6
P6 → P7
```

D1 is paused and is not a dependency of any active workstream.

## Execution-safety contract

- There is one active plan per authorized workstream.
- Every implementation plan has repository-relative scope, a KEEL change ID, exact acceptance evidence, and at least one negative/failure acceptance case.
- Plans do not authorize implementation merely by existing.
- Benchmark-related paths are excluded from active scopes.
- A blocked workstream cannot start until its named prerequisite is evidenced.
- Runtime, external, and empirical behavior cannot be claimed without direct evidence.
- Generated artifacts are changed only through their declared producer where applicable.
- Completion requires repository-native verification, not plan status or ledger phase.
- Individual workstream ExecPlans are created only when that workstream is authorized for implementation.

## Current handoff

Completed bounded slices remain historical evidence in [`docs/exec-plans/completed/`](../completed/). The next authorized change must create one scoped workstream plan and change ID, identify prerequisite evidence, and satisfy the contract above. P4 remains blocked, and all D1 work remains deferred.
