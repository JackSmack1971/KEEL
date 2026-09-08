# KEEL upgrade audit

This is the authoritative section-level matrix for `docs/KEEL_UPGRADES.md`. Every numbered source section is accounted for exactly once below, either as an executable requirement, contextual/strategic material, superseded material, or explicitly deferred/out-of-scope material. Status is based on repository evidence, not plan or ledger phase.

## Authoritative requirement matrix

| Source sections | Requirement | Status | Owner for unresolved work | Repository evidence / remaining boundary |
|---|---|---|---|---|
| 1–3 | Governed change contracts, verified candidates, scope, effects, and landing integrity | COMPLETE | — | `.keel/ledger/`, `docs/control-plane/KEEL.md`, and lifecycle verification provide this substrate. |
| 4 | Effect capabilities and authorization semantics | PARTIAL | P6 | `.keel/contracts.json` and effect checks exist; richer effect ontology and runtime enforcement remain. |
| 5 | Mission execution through a governed runtime | BLOCKED | P4 | No authorized runtime/provider and operator authorization are evidenced. |
| 6–7 | Mission graph semantics and deterministic decomposition/planning | COMPLETE (P2 SCHEMA/PLANNING) | — | `keel.mission/v2` provides typed dependencies, deterministic serialization, bounded decomposition, P1 uncertainty propagation, and read-only advisory frontiers; execution remains outside P2. |
| 8 | Repository intelligence and codebase mapping | COMPLETE (P1 FOUNDATION) | — | `.keel/lib/repository_intelligence.py`, independent P1 fixtures/tests, and landed KEEL evidence at `c31dc0ff9e48135f9ce7fe2746df1684f68f4a5d` / `refs/keel/ledger/p1-repository-intelligence-foundation`. |
| 9 | Query-driven context compilation | PARTIAL | P5 | `keel context` compiles bounded provenance-aware context; query/topology-aware behavior remains. |
| 10 | Avoid redundant context/prompt injection | PARTIAL | P5 | Bounded context compilation exists; broader adaptive context-budget policy remains. |
| 11 | First-class adaptive workflow engine | PARTIAL | P5 | Routed workflow/protocol capabilities exist; deterministic adaptive workflow obligations remain. |
| 12 | Dynamically activated domain intelligence | PARTIAL | P3 | P1 supplies evidence-backed static domain/adapter facts; runtime activation remains outside P1. |
| 13 | Executable repository command discovery | COMPLETE (P1 FOUNDATION) | — | P1 command registry preserves existence, source class, provenance, support, runtime availability, authorization, precedence, and negative states in the landed repository-intelligence contract. |
| 14–15 | Portable verification and extracted-package behavior | COMPLETE | — | P0 provides repository-relative provenance-bearing command resolution, explicit unavailable/ambiguous/unproven/unauthorized states, and non-Git copied/extracted bootstrap classification; canonical config has no creator-machine path or D1 check. |
| 16–17 | Installation, upgrade, and compatibility contract | COMPLETE | — | P0 adds deterministic compatible/incompatible/unsupported/missing-metadata/migration-required foundations while preserving read-only preflight, authorized apply, backup, rollback, and installer/live orchestration boundaries. |
| 18 | Runtime capability detection and trust handshake | PARTIAL | P3 | Static/project capability evidence exists; actual runtime capability, trust, and hook readiness remain unobserved. |
| 19 | Dynamic topology/router behavior | PARTIAL | P5 | `keel route` emits deterministic roles and verification breadth; runtime dispatch remains. |
| 20 | Optional cross-model review policy | PARTIAL | P6 | Review/evidence boundaries exist; runtime/provider review policy remains unimplemented. |
| 21 | Topology-aware context compilation | PARTIAL | P5 | Bounded context compiler exists; topology-aware compilation remains. |
| 22 | Typed evidence graph assertions | PARTIAL | P6 | Evidence graph and configured providers exist; richer providers and independent runtime evidence remain. |
| 23–24 | Change-aware verification and verification-command provenance | PARTIAL | P6 | Configured checks and lifecycle verification exist; change-aware selection/discovery remains. |
| 25 | Developer UX | PARTIAL | P7 | Inspection and eligibility projections exist; complete execution UX remains. |
| 26 | `keel run` and mission dispatch | BLOCKED | P4 | Dispatch contracts exist, but authorized runtime/provider, credentials, and operator authorization are absent. |
| 27 | No unnecessary ceremony for obvious changes | CONTEXTUAL | — | Durable doctrine already exists in repository workflow policy; this is not an independent upgrade requirement. |
| 28–29 | Distinguish invariants from bureaucracy; reduce documentation entropy | CONTEXTUAL | — | Strategic design guidance, represented where appropriate by existing policy and maintenance practice. |
| 30 | Separate framework history from consumer-repository state | COMPLETE | — | P0 classifies framework, consumer, generated-consumer, machine-local, and runtime/history artifacts and rejects prohibited package leakage. |
| 31 | KEELBench strategic importance | CONTEXTUAL | — | Strategic rationale, not an executable requirement. |
| 32–33 | KEELBench implementation, corpus, authority, trials, scoring, and empirical evaluation | DEFERRED | D1 | Existing `.keel/bench/` contracts/artifacts are preserved; no benchmark work is authorized. |
| 34 | Mutation testing of control-plane invariants | PARTIAL | P6 | The source requires mutation testing; no mutation run is claimed here, so the gap remains active and independent of D1. |
| 35–36 | Property-based lifecycle invariants and formal lifecycle state machine | PARTIAL | P6 | Lifecycle mechanisms and tests exist; property/state-machine coverage remains. |
| 37–38 | Rich effect ontology and tool-semantic inference | PARTIAL | P6 | Contracts and conservative argv inference exist; semantic tool/API inference remains. |
| 39–40 | Reproducible environment and supply-chain attestation | COMPLETE | — | P0 provides deterministic repository-relative file attestation with provenance and explicit `UNVERIFIED_RUNTIME` when runtime evidence is unavailable; no supply-chain or D1 claim is fabricated. |
| 41 | Brownfield repository intelligence | COMPLETE (P1 FOUNDATION) | — | P1 landed read-only brownfield graph, authority, dependency, impact, changed-path, and generated-provenance evidence with independent negative fixtures. |
| 42 | Continuously refreshed project context | PARTIAL | P5 | Bounded context compilation exists; continuous refresh remains. |
| 43–44 | Self-improvement and reviewed mistake handling | PARTIAL | P7 | Observation validation and entropy scans exist; reviewed promotion/scheduling remains. |
| 45 | Policy compiler | PARTIAL | P7 | Policy doctrine exists; compiled policy capability remains. |
| 46 | Invariant ownership | PARTIAL | P7 | Maintenance/control-plane ownership exists; broader invariant ownership remains. |
| 47–49 | Architecture enforcement, impact analysis, and Git-history learning | PARTIAL | P7 | P1 landed architecture-source, dependency, and changed-path impact evidence; broader enforcement and Git-history learning remain outside P1. |
| 50–51 | Evidence-derived risk and explicit uncertainty | PARTIAL | P5 | Risk/evidence contracts exist; richer evidence-derived uncertainty remains. |
| 52–53 | Reversible execution and experiment changes | COMPLETE (P2 PLANNING BOUNDARY) | — | P2 represents effects, authorization references, reversibility/retry/integration expectations, inheritance, and unresolved execution prerequisites without granting or executing effects. |
| 54–57 | Semantic diff, verification-quality protection, independent verification, and scope laundering detection | PARTIAL | P6 | Scope and lifecycle verification exist; semantic and independent verification strengthening remains. |
| 58–59 | Structured CLI output and CLI-as-API | PARTIAL | P7 | Several structured projections exist; complete structured surface remains. |
| 60–61 | Lifecycle event sourcing and correlation IDs | PARTIAL | P7 | Lifecycle telemetry/status projections exist; event/correlation breadth remains. |
| 62 | Local dashboard eventually | CONTEXTUAL | — | Explicitly eventual strategic guidance, not current executable work. |
| 63–64 | Product positioning and competitive comparison | CONTEXTUAL | — | Contextual strategy, not independent executable upgrades. |
| 65–66 | Target architecture and proposed layer model | SUPERSEDED/CONTEXTUAL | — | Strategic proposals are superseded where they conflict with intentionally unchosen architecture; otherwise contextual only. |
| 67–70 | Recommended priority, rule, metric, and final assessment | CONTEXTUAL | — | Strategic guidance and assessment, not independent executable requirements. |
| 71 | Supplied competitive-audit reconciliation | CONTEXTUAL | — | Review/context material; its actionable requirements are represented in the executable rows above. |

## Cross-cutting reconciliation

| Requirement | Status | Owner | Evidence / remaining boundary |
|---|---|---|---|
| Reconciliation of Git, ledger, environment, compatibility, contracts, and next action | PARTIAL | P7 | `keel reconcile` provides a read-only comparison/kernel; repair, retry, and integration-boundary behavior remain. |

This cross-cutting row is not a second source-section count: it is the explicitly requested bounded capability classification for the implemented reconciliation surface.

## Authority boundaries

Unresolved executable rows map to exactly one P0–P7 owner, except explicitly BLOCKED P4 and DEFERRED D1 rows. This document is requirement/status authority; [upgrade-remaining-plan.md](../exec-plans/active/upgrade-remaining-plan.md) is program sequence/dependency authority; and each subordinate active workstream ExecPlan is bounded execution authority. Historical ExecPlans under `docs/exec-plans/completed/` and `.keel/ledger/*` are evidence only and never prove broader upgrade completion. A workstream plan must not supersede or replace the global roadmap.

## Landed P1 evidence

P1 implementation acceptance passed independently before commit `c31dc0ff9e48135f9ce7fe2746df1684f68f4a5d`; the candidate was sealed and the landed tree was anchored at `refs/keel/ledger/p1-repository-intelligence-foundation` with `LANDED_COMPLETION`. P2 schema/planning is now implemented under its own KEEL change; this reconciliation does not instantiate P3–P7 or execute D1.
