# KEEL upgrade audit

This is the current-state audit against `docs/KEEL_UPGRADES.md`. Status means executable repository evidence exists, not merely a documented intention.

| Upgrade area | Status | Evidence / remaining work |
|---|---|---|
| Requirements and acceptance traceability | Implemented | `requirements.json`, `acceptance.json`, evidence graph, and verification enforce coverage. |
| Capability resolution | Implemented | `.keel/lib/capability_resolver.py`, `keel discover`, resolver tests; advisory statuses remain policy-neutral. |
| Context compilation | Implemented | `.keel/lib/context_compiler.py`, provenance metadata, context tests. |
| KEELBench | Implemented as harness | Paired-trial schema, validation, creation, and scoring exist; empirical superiority remains unvalidated until real trials are run. |
| `keel next` | Implemented | Read-only lifecycle guidance and focused tests. |
| Worktrees and environment contracts | Implemented as local primitives | Safe worktree commands and declarative contract inspection exist; mission-level orchestration is absent. |
| Repository mapping / knowledge graph | Partially implemented | `keel map` emits deterministic, provenance-bearing topology/module/entrypoint/test/command/dependency facts, Python AST imports, and literal CODEOWNERS rules when available; architecture inference and an actual ownership policy remain absent. |
| Missions / work DAG | Partially implemented | `keel mission` validates contracts, computes a read-only dependency frontier/status projection, and emits isolated dispatch contracts; runtime dispatch, mission verification, retries, and integration remain absent. |
| Reconciliation | Implemented as read-only kernel | `keel reconcile` compares Git, ledger, environment, compatibility, contracts, and next action; repair/retry/integration adapters remain future work. |
| Evidence providers | Partially implemented | Declared provider types now validate through configured check IDs and literal exit status; browser/log/metric/trace/device adapters remain project-specific. |
| Effect capabilities | Partially implemented | Effect names are validated against `.keel/contracts.json`; `keel effects` conservatively infers recognized argv capabilities and reports undeclared mismatches without authorization. Runtime tool/API inference and capability-aware authorization enforcement remain absent. |
| Dynamic topology / compute routing | Partially implemented | `keel route` emits deterministic complexity, model-independent effort capabilities, roles, and verification breadth; runtime dispatch and provider/model mapping remain external. |
| Reusable engineering protocols | Partially implemented | The routed `engineering-protocols` skill covers debugging, architecture, dependency, migration, security, performance, frontend runtime, test remediation, incident, and release concerns; behavioral evaluation and deeper domain-specific references remain future work. |
| Learning loop / entropy service | Partially implemented | Reviewed observation validation, deterministic queue and target-plan projections, and non-destructive entropy scans now exist; promotion, external ingestion, scheduled operation, and target eval execution remain. |
| Developer UX | Partially implemented | `init --check`, `review`, `ship` eligibility, mission, map, route, compat, and entropy projections exist; `run`/agent dispatch remains deferred until an authorized execution runtime exists. |
| Version / install / upgrade / migration | Partially implemented | `keel version`, `compat`, `migrate --check`, and `migrate --plan` inventory/preflight repository-owned versions; the tested migration registry supports config 1→2 with atomic backup/rollback primitives. Installer, live authorized migration orchestration, and external Codex version checks remain. |
| Issue/PR integrations | Deferred | No external tracker adapter; correctly requires separate authorization and runtime prerequisites. |

## Source-section traceability

The numbered recommendations in `docs/KEEL_UPGRADES.md` map as follows; sections that synthesize competitor observations are recorded as context, not treated as missing runtime features.

| Source sections | Mapped audit evidence | Current status |
|---|---|---|
| 1-3 | Lifecycle, evidence graph, effects, and audit framing | Implemented foundation |
| 4 | Missions / work DAG | Partial: validation/frontier and advisory dispatch contracts; runtime execution remains |
| 5 | Requirements and acceptance traceability | Partial: machine-readable links exist; richer typed specification model remains |
| 6 | Evidence graph | Implemented |
| 7 | Capability resolver | Implemented local resolver; runtime discovery remains advisory |
| 8 | Repository mapping / knowledge graph | Partial: classifications and Python imports; ownership/architecture facts remain |
| 9 | Context compiler | Implemented |
| 10 | Reusable engineering protocols | Partial: routed skill; behavioral evaluation/deeper references remain |
| 11 | Scope doctrine / avoid giant agent organization | Contextual design constraint |
| 12 | Dynamic topology / compute routing | Partial: deterministic recommendation; runtime dispatch remains |
| 13 | Parallel execution | Partial: worktree primitives; automated orchestration remains |
| 14 | Worktree/environment isolation | Implemented as local primitives |
| 15 | Multimodal verification | Partial: provider contracts; real adapters remain |
| 16 | Stack-agnostic source discovery | Partial: configurable classification; language-specific semantic analysis currently Python |
| 17 | Effect detection/enforcement | Partial: conservative argv inference; runtime tool/API inference and authorization enforcement remain |
| 18-19 | Reconciliation and `keel next` | Implemented read-only kernels |
| 20 | Economics / telemetry | Partial: routing and benchmark schemas; real cost/latency telemetry remains |
| 21 | KEEL Evals | Harness implemented; representative empirical trials remain |
| 22-23 | Learning and entropy service | Partial: validated observations, queue, and deterministic scan; promotion/scheduling/target execution remain |
| 24 | Developer experience | Partial: inspection and eligibility projections; authorized `run` remains |
| 25 | Installation/version/migration | Partial: inventory and compatibility checks; installer/migrations/rollback remain |
| 26-27 | Competitor synthesis and target architecture | Context plus constraints represented by the mapped rows; not independent executable features |
| 28 | Recommended roadmap | Durable workstream plan in `docs/exec-plans/active/upgrade-remaining-plan.md` |

Remaining work is tracked in [the durable workstream plan](../exec-plans/active/upgrade-remaining-plan.md). Ownership-source discovery, feedback evaluation queueing, schema migration preflight/apply/rollback primitives, and advisory effect inference are implemented partial slices; their policy, corpus, live-orchestration, and runtime boundaries remain. Next local work is bounded to deeper target-evaluation planning and protocol/economics evidence. Execution runtime, evidence adapters, tracker/PR integration, external Codex checks, and KEELBench superiority require the prerequisites recorded in that plan.
