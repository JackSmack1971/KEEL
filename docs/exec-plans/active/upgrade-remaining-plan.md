# KEEL upgrade remaining plan

This is the sole active top-level KEEL upgrade roadmap. The authoritative classifications are in [`docs/control-plane/UPGRADE_AUDIT.md`](../../control-plane/UPGRADE_AUDIT.md). A workstream is not authorized for implementation merely because it appears here.

## Execution sequence

### P0 — Portable verification and bootstrap contract
Objective: Remove creator-machine dependencies and establish reliable package/bootstrap/version states.

Status: **COMPLETE / LANDED** under KEEL change `p0-portable-verification-bootstrap-contract`. P1 remains unstarted.

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
- Every implementation plan has an explicit KEEL change ID and exact repository-relative scope.
- Every implementation plan names its dependencies and prerequisites, and a blocked plan cannot start until each named prerequisite is evidenced.
- Every implementation plan states concrete implementation requirements and distinguishes required behavior from optional design suggestions.
- Every implementation plan names the exact repository-native verification command or commands for each acceptance check wherever known. If a command is not knowable at planning time, the plan defines deterministic command discovery and requires the resolved command to be recorded before completion.
- Every implementation plan defines expected result and exit behavior for each positive and negative acceptance command, including required status/artifact transitions and prohibited findings that must be absent.
- Every implementation plan contains acceptance criteria, exact acceptance evidence, and at least one negative/failure acceptance case.
- Every implementation plan states the durable completion evidence required; plan status, documentation claims, or ledger phase alone never constitute completion evidence.
- Every implementation plan explicitly handles unavailable runtime, platform, provider, authorization, or external verification using an established classification such as `VERIFIED`, `FAILED`, `BLOCKED`, or `UNVERIFIED_RUNTIME`. Unavailable verification must never silently become `PASS`, and runtime behavior cannot be `VERIFIED` without direct runtime evidence.
- Plans do not authorize implementation merely by existing.
- Benchmark-related paths are excluded from active scopes.
- Runtime, external, and empirical behavior cannot be claimed without direct evidence.
- Generated artifacts are changed only through their declared producer where applicable.
- Completion requires repository-native verification and durable completion evidence, not plan status or ledger phase.
- Individual workstream ExecPlans are created only when that workstream is authorized for implementation.

P0 is complete and independently landed under its single authorized KEEL change. P4 remains blocked pending its runtime/provider and authorization prerequisites; D1 remains deferred and outside all active dependencies.

## Current handoff

The P0 plan and ledger are the durable completion evidence for the landed work. The next authorized change may begin P1 only as a separate scoped workstream and change ID after reviewing this evidence. P4 remains blocked, and all D1 work remains deferred.
