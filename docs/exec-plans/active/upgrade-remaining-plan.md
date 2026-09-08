# KEEL upgrade remaining plan

Status: `AUTHORITATIVE PROGRAM ROADMAP`

Requirement and status authority is [`docs/control-plane/UPGRADE_AUDIT.md`](../../control-plane/UPGRADE_AUDIT.md). Workstream execution plans are subordinate and do not replace this roadmap.

## Execution sequence

```text
P0 → P1 → P2 → P3 → P4
P1 → P5
P2 → P5
P3 → P5
P1 + P2 + P5 → P6
P6 → P7
```

## Workstream state

- P0 → **VERIFIED COMPLETE**, landed under `p0-portable-verification-bootstrap-contract`.
- P1 → **VERIFIED COMPLETE / LANDED**, under KEEL change `p1-repository-intelligence-foundation`, anchored at `c31dc0ff9e48135f9ce7fe2746df1684f68f4a5d`.
- P2 → **VERIFIED COMPLETE / LANDED**, under KEEL change `p2-mission-schema-planning`; schema/planning is complete and execution remains excluded.
- P3 → **FUTURE**, with no dependency shortcut.
- P4 → **BLOCKED** until an authorized runtime/provider and operator authorization exist.
- P5 → **FUTURE**, unavailable through dependency shortcuts.
- P6 → **FUTURE**, requires P1 + P2 + P5.
- P7 → **FUTURE**, requires P6.
- D1 → **DEFERRED**, not an active prerequisite.

## Workstream boundaries

- P1: deterministic, provenance-bearing repository graph, command, ownership, architecture, dependency, impact, and generated-artifact intelligence.
- P2: mission schema and planning without execution.
- P3: runtime capability handshake.
- P4: bounded mission execution through an authorized runtime.
- P5: adaptive workflow and context/routing.
- P6: verification and lifecycle integrity.
- P7: non-benchmark feedback and observability.
- D1: benchmark and evaluation, deferred.

Plans do not authorize implementation merely by existing. Every implementation plan requires an explicit KEEL change ID, exact scope, acceptance evidence, repository-native verification, and durable completion evidence. Generated artifacts change only through proven producers. Runtime, external, irreversible, and empirical behavior require direct evidence and authorization.

## Current handoff

P1 is landed and P2 schema/planning is implemented under its subordinate plan with completion evidence. No execution runtime is activated by this reconciliation: P4 remains blocked, P5–P7 remain future/locked, and D1 remains deferred.
