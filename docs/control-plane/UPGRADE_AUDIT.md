# KEEL upgrade audit

This is the current-state audit against `docs/KEEL_UPGRADES.md`. Status means executable repository evidence exists, not merely a documented intention.

| Upgrade area | Status | Evidence / remaining work |
|---|---|---|
| Requirements and acceptance traceability | Partially implemented | `requirements.json`, `acceptance.json`, evidence graph, and verification enforce coverage; typed requirement/priority/evidence metadata and implementation-surface paths are now schema-checked, while richer automatic spec generation remains absent. |
| Capability resolution | Implemented | `.keel/lib/capability_resolver.py`, `keel discover`, resolver tests; advisory statuses remain policy-neutral. |
| Context compilation | Implemented | `.keel/lib/context_compiler.py`, provenance metadata, context tests. |
| KEELBench | Implemented as harness | Paired-trial schema, validation, creation, and scoring exist; empirical superiority remains unvalidated until real trials are run. |
| `keel next` | Implemented | Read-only lifecycle guidance and focused tests. |
| Worktrees and environment contracts | Implemented as local primitives | Safe worktree commands and declarative contract inspection exist; mission-level orchestration is absent. |
| Repository mapping / knowledge graph | Partially implemented | `keel map` emits deterministic, provenance-bearing topology/module/entrypoint/test/command/dependency facts, Python AST imports, and literal CODEOWNERS rules when available; architecture inference and an actual ownership policy remain absent. |
| Missions / work DAG | Partially implemented | `keel mission` validates contracts, computes a read-only dependency frontier/status projection, and emits isolated dispatch contracts; runtime dispatch, mission verification, retries, and integration remain absent. |
| Reconciliation | Implemented as read-only kernel | `keel reconcile` compares Git, ledger, environment, compatibility, contracts, and next action; repair/retry/integration adapters remain future work. |
| Evidence providers | Partially implemented | Declared provider types validate through configured check IDs and literal exit status; native repository `file_exists` and narrow JSON `schema` evidence now evaluate locally. Browser/log/metric/trace/device adapters remain project-specific. |
| Effect capabilities | Partially implemented | Effect names are validated against `.keel/contracts.json`; `keel effects` conservatively infers recognized argv capabilities and reports undeclared mismatches without authorization. Runtime tool/API inference and capability-aware authorization enforcement remain absent. |
| Dynamic topology / compute routing | Partially implemented | `keel route` emits deterministic complexity, model-independent effort capabilities, roles, and verification breadth; runtime dispatch and provider/model mapping remain external. |
| Reusable engineering protocols | Partially implemented | The routed `engineering-protocols` skill covers debugging, architecture, dependency, migration, security, performance, frontend runtime, test remediation, incident, and release concerns; behavioral evaluation and deeper domain-specific references remain future work. |
| Learning loop / entropy service | Partially implemented | Reviewed observation validation, deterministic queue and target-plan projections, and non-destructive entropy scans now exist; promotion, external ingestion, scheduled operation, and target eval execution remain. |
| Developer UX | Partially implemented | `init --check`, `review`, `ship` eligibility, mission, map, route, compat, and entropy projections exist; `run`/agent dispatch remains deferred until an authorized execution runtime exists. |
| Version / install / upgrade / migration | Partially implemented | `keel version`, `compat`, `migrate --check`, and `migrate --plan` inventory/preflight repository-owned versions; the tested migration registry supports config 1→2 with atomic backup/rollback primitives. Installer, live authorized migration orchestration, and external Codex version checks remain. |
| Issue/PR integrations | Deferred | No external tracker adapter; correctly requires separate authorization and runtime prerequisites. |

## Source-section traceability

The numbered recommendations in `docs/KEEL_UPGRADES.md` map exactly once below. Strategy, competitor synthesis, and positioning sections are recorded as context rather than silently converted into executable runtime claims.

| Source sections | Mapped audit evidence | Current status |
|---|---|---|
| 1–4 | Lifecycle, evidence graph, effects, audit framing, and mission DAG | Partial: governance foundation exists; mission execution remains absent |
| 5–10 | Requirements, evidence graph, capability resolution, repository map, context compilation, protocols | Partial-to-implemented: local kernels exist; richer generation, ownership policy, and behavioral evaluation remain |
| 11 | Scope doctrine and bounded agent organization | Contextual design constraint |
| 12–14 | Topology/routing, parallel execution, and worktree/environment isolation | Partial-to-implemented: deterministic recommendations and local worktree primitives exist; runtime dispatch remains absent |
| 15–17 | Multimodal evidence, stack-agnostic discovery, effect detection/enforcement | Partial: provider contracts and conservative local inference exist; runtime adapters and authorization enforcement remain |
| 18–19 | Reconciliation and `keel next` | Implemented read-only kernels |
| 20–21 | Economics/telemetry and KEEL Evals | Partial: lifecycle telemetry and benchmark harness exist; runtime economics and empirical trials remain |
| 22–24 | Learning/entropy service and developer experience | Partial: review/queue/inspection projections exist; promotion, scheduling, target execution, and authorized `run` remain |
| 25 | Installation, version, and migration | Partial: inventory, compatibility, and tested config migration/rollback exist; installer/live orchestration remains |
| 26–28 | Competitor synthesis, target architecture, and first roadmap | Context and durable workstream plan; not independent executable features |
| 29–36 | Runtime/kernel expansion, verification depth, and evaluation direction | Strategy/context or prerequisite-dependent work; no unsupported completion claim |
| 37–44 | Effect semantics, reproducibility, repository intelligence, and feedback loop | Partial: local contracts and projections exist; semantic/runtime evidence and promotion remain |
| 45–51 | Policy compilation, invariant ownership, architecture/impact, risk, and uncertainty | Planned repository-intelligence and verification-quality work; no policy is inferred from derived views |
| 52–57 | Reversibility, semantic diff, oracle independence, and laundering resistance | Partial governance substrate; adversarial and independent-oracle depth remains |
| 58–61 | Structured CLI/API, lifecycle events, and correlation | Partial local projections; stable API and cross-tool event contracts remain |
| 62 | Dashboard/product surface | Explicitly deferred until orchestration/API prerequisites exist |
| 63–70 | Positioning, competitor comparison, target architecture, sequencing, doctrine, and metrics | Strategy/context; not independently missing runtime features |

Remaining executable work is tracked in [the durable workstream plan](../exec-plans/active/upgrade-remaining-plan.md) and the repository-owned `plans/` dependency order. The authoritative upgrade brief is not modified by this reconciliation. Plan 004 remains the next implementation change after this documentation change and must establish portability/runtime contracts before mission execution is claimed.
