# KEEL upgrade remaining plan

Status: `FROZEN / SUBORDINATE TO KERNEL MIGRATION AUTHORITY`

The sole forward authority is [`docs/control-plane/KERNEL_REDESIGN.md`](../../control-plane/KERNEL_REDESIGN.md). This roadmap preserves landed P0/P1/P2 and prior sequencing as historical planning evidence. P3-P7 and D1 feature expansion is frozen; later work must use an M1-M6 migration stage and may not resume this sequence directly.

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
- P3 → **FROZEN**, superseded as feature expansion; runtime-profile work may occur only in an authorized migration stage.
- P4 → **BLOCKED** and **FROZEN**, with no execution authority; landing/runtime work may occur only under the redesign migration contract and required authorization.
- P5 → **FROZEN**, unavailable as feature expansion.
- P6 → **FROZEN**, unavailable as feature expansion.
- P7 → **FROZEN**, unavailable as feature expansion.
- D1 → **DEFERRED** and **FROZEN**, not an active prerequisite or authorized expansion.

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

P0, P1, and P2 are landed compatibility baselines. All feature expansion above P2 is frozen. The next eligible work is M1 contract-fixture migration planning under `KEEL-KERNEL-REDESIGN-v1`; this roadmap grants no implementation or integration authorization.
