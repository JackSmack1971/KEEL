# KEEL upgrade remaining plan — historical roadmap

Status: `HISTORICAL COPY — NOT AUTHORITATIVE`

This is a preserved historical copy of the roadmap. Its sequence and
boundaries are historical context only. The current authoritative roadmap is
[`../../control-plane/KEEL_FORWARD_AUTHORITY.md`](../../control-plane/KEEL_FORWARD_AUTHORITY.md).

## Execution sequence

```text
P0 → P1 → P2 → P3 → P4

P1 → P5
P2 → P5
P3 → P5
P1 + P2 + P5 → P6
P6 → P7
```

P0 is complete and independently landed under `p0-portable-verification-bootstrap-contract`. P4 remains blocked pending an authorized runtime/provider and operator authorization. D1 remains deferred and is not a dependency of P0–P7.

## Historical workstream boundaries

- P1: deterministic, provenance-bearing repository graph, command, ownership, architecture, dependency, impact, and generated-artifact intelligence.
- P2: mission schema and planning.
- P3: runtime capability handshake.
- P4: bounded mission execution through an authorized runtime.
- P5: adaptive workflow and context/routing.
- P6: verification and lifecycle integrity.
- P7: non-benchmark feedback and observability.
- D1: benchmark and evaluation, deferred.

Plans do not authorize implementation merely by existing. Every implementation plan requires an explicit KEEL change ID, exact scope, acceptance evidence, repository-native verification, and durable completion evidence. Runtime, external, irreversible, and empirical behavior cannot be claimed without direct evidence. Generated artifacts are changed only through declared producers.

See `docs/control-plane/UPGRADE_AUDIT.md` for the authoritative section-level classifications and the active P1 ExecPlan for the current handoff.
