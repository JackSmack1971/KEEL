# Proposal

## Problem / why
The P0 foundation exposes deterministic path/import and command/provenance primitives, but the repository still lacks one bounded, read-only intelligence contract for graph facts, command discovery, ownership, architecture, dependencies, changed-path impact, and generated-artifact provenance. The unresolved P1 audit rows therefore remain only partially satisfied.

## Objective
Implement the bounded, read-only P1 repository-intelligence foundation described by the active ExecPlan, with independent behavioral fixtures and oracles, then complete the KEEL verification, seal, landing, and anchor lifecycle.

## Non-goals
No runtime execution or mission orchestration; no provider authorization or external effects; no P2–P7 or D1 implementation; no Git-history mutation, arbitrary command execution, hooks, credentials, migrations, or benchmark/corpus work.

## Success evidence
The canonical module and tests prove every P1 positive and negative contract case; `PLAN_READINESS` and `IMPLEMENTATION_ACCEPTANCE` independently pass; the committed candidate is sealed, landed, independently reverified, anchored, and reconciled into the audit/roadmap without instantiating downstream work.

## Open decisions
Adapters are limited to the explicitly evidenced Python, JSON/KEEL, command/config, capability, and existing CODEOWNERS parsers. Runtime handshakes, execution, deployment, external effects, P2–P7, and D1 remain excluded.
