# KEEL upgrade audit

This is the authoritative requirement matrix for the executable upgrade proposals in `docs/KEEL_UPGRADES.md`. Status is based on repository evidence, not plan or ledger phase. Strategic comparison, advice, and target architecture are recorded separately and are not silently promoted to executable requirements.

## Authoritative requirement matrix

Each executable requirement is represented once. Rows combine source sections only when they describe one bounded capability.

| Source sections | Requirement | Status | Repository evidence / remaining boundary |
|---|---|---|---|
| 1–3 | Preserve governed changes, verified candidates, scope, and effects | COMPLETE | `.keel/ledger/`, `docs/control-plane/KEEL.md`, and lifecycle verification provide the existing control-plane substrate. |
| 5 | Requirements and acceptance traceability | COMPLETE | `requirements.json`, `acceptance.json`, evidence graph, and verification enforce the currently defined contract. Richer automatic specification generation is a separate future capability. |
| 6 | Typed evidence graph | PARTIAL | `.keel/lib/evidence_graph.py` and configured check IDs provide local typed coverage; richer providers and independent runtime evidence remain. |
| 7 | Capability resolution | PARTIAL | `keel discover` and resolver tests provide local classification; runtime/provider discovery and policy activation remain outside the current evidence. |
| 4 | Mission schema, decomposition, DAG, and planning | PARTIAL | `keel mission` validates contracts, computes a read-only frontier, and emits dispatch contracts; richer decomposition remains. |
| 8, 13, 16, 41, 47–50 | Repository intelligence, commands, ownership, architecture, impact, history, and uncertainty | PARTIAL | `keel map` provides deterministic provenance-bearing facts, commands, Python imports, and CODEOWNERS discovery; policy and deeper architecture/impact/history intelligence remain. |
| 9, 21, 42 | Context compilation and refresh | PARTIAL | `keel context` compiles bounded provenance-aware context; topology-aware refresh and continuous context remain. |
| 10 | Reusable engineering protocols | PARTIAL | The routed `engineering-protocols` skill exists; behavioral effectiveness and deeper references remain unverified. |
| 12, 19 | Dynamic topology and compute routing | PARTIAL | `keel route` emits deterministic roles, effort capabilities, and verification breadth; runtime provider/model dispatch remains. |
| 14, 15, 39, 40 | Portable verification, environment/worktree reproducibility, and supply-chain evidence | PARTIAL | Local worktree and contract primitives exist; creator-machine-independent bootstrap/package/version proof and supply-chain attestation remain. |
| 17, 37, 38 | Effect ontology, inference, and enforcement | PARTIAL | Effect contracts and conservative argv inference exist; tool/API semantic inference and runtime authorization remain. |
| 18 | Runtime capability handshake | PARTIAL | Static/project capability evidence exists, but actual runtime capability, trust, hook readiness, and graceful degradation are not fully observed. |
| 20, 60, 61 | Lifecycle telemetry, event/correlation projections, and economics | PARTIAL | Lifecycle duration/outcome and status projections exist; broader correlations and runtime token/cost/human-effort telemetry remain. |
| 22–24, 54–57 | Verification selection, semantic diff, scope laundering, and independent evidence | PARTIAL | Typed assertions, configured evidence, scope checks, and lifecycle verification exist; change-aware selection, semantic diff and broader invariant enforcement remain. |
| 25, 58, 59 | Developer UX and structured CLI/API projections | PARTIAL | `init --check`, `review`, `ship`, `map`, `route`, `compat`, `entropy`, `mission`, and `next` projections exist; full `run` UX and complete structured API remain. |
| 26 | Mission execution and integration | BLOCKED | No authorized runtime/provider and operator authorization are evidenced. Planning may proceed; execution cannot. |
| 27 | `keel next` | COMPLETE | `keel next` is a read-only legal-action/blocker projection with focused repository tests. |
| 32–34 | KEELBench benchmark and empirical evaluation | DEFERRED | `.keel/bench/` contracts and historical artifacts are preserved; implementation, corpus, authority, paired trials, scoring, comparison, promotion, and benchmark telemetry are paused. |
| 43–46 | Feedback, entropy, learning, policy compilation, and invariant ownership | PARTIAL | Observation validation, queue/target projections, entropy scans, and maintenance skills exist; promotion, scheduling, target execution, and policy/invariant ownership remain. |
| 25, 30, 40 | Installation, version, upgrade, migration, and consumer portability | PARTIAL | Version/compatibility checks and tested config migration/rollback primitives exist; installer, live authorized orchestration, and external version checks remain. |
| 4, 13 | External issue/PR integrations | DEFERRED | No tracker adapter or authorization exists; it is outside P0–P7 until integration prerequisites are supplied. |

## Contextual or superseded material

Sections 11 (scope doctrine), 28–29 (comparative recommendations and documentation-size guidance), 62 (eventual dashboard), 63–64 (product positioning and competitive comparison), and 65–70 (target architecture, layer-model proposals, metrics, and final assessment) are contextual strategy, not independent executable requirements. Any target architecture proposal that conflicts with intentionally unchosen architecture is superseded by the verified architecture/control-plane documents. Section 68 is a durable constraint only where already represented by repository policy.

## Traceability and authority

The executable gaps above map to the workstreams in [the sole active upgrade roadmap](../exec-plans/active/upgrade-remaining-plan.md). Historical bounded slices and superseded planning reasoning are indexed in [the completed-plan archive](../exec-plans/completed/upgrade-planning-archive.md). `.keel/ledger/*` remains implementation evidence for its own change IDs; it does not, by itself, prove a broader row COMPLETE.
