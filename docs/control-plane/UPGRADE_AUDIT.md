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
| Repository mapping / knowledge graph | Partially implemented | `keel map` emits deterministic, provenance-bearing topology/module/entrypoint/test/command/dependency facts plus Python AST import relationships; ownership and architecture inference remain absent. |
| Missions / work DAG | Partially implemented | `keel mission` now validates mission contracts and computes a read-only dependency frontier/status projection; dispatch, mission verification, retries, and integration remain absent. |
| Reconciliation | Implemented as read-only kernel | `keel reconcile` compares Git, ledger, environment, compatibility, contracts, and next action; repair/retry/integration adapters remain future work. |
| Evidence providers | Partially implemented | Declared provider types now validate through configured check IDs and literal exit status; browser/log/metric/trace/device adapters remain project-specific. |
| Effect capabilities | Partially implemented | Effect names are validated against `.keel/contracts.json` and required for external/irreversible effects; command/tool inference and capability-aware authorization policy remain absent. |
| Dynamic topology / compute routing | Partially implemented | `keel route` emits deterministic complexity, model-independent effort capabilities, roles, and verification breadth; runtime dispatch and provider/model mapping remain external. |
| Reusable engineering protocols | Partially implemented | The routed `engineering-protocols` skill covers debugging, architecture, dependency, migration, security, performance, frontend runtime, test remediation, incident, and release concerns; behavioral evaluation and deeper domain-specific references remain future work. |
| Learning loop / entropy service | Partially implemented | Reviewed observation validation and deterministic non-destructive entropy scans now exist; promotion, external ingestion, scheduled operation, and target eval execution remain. |
| Developer UX | Partially implemented | `init --check`, `review`, `ship` eligibility, mission, map, route, compat, and entropy projections exist; `run`/agent dispatch remains deferred until an authorized execution runtime exists. |
| Version / install / upgrade / migration | Partially implemented | `keel version`, `compat`, and `migrate --check` inventory framework/config/contract/ledger/skill/manifest versions and produce read-only migration findings; installer, actual migrations, rollback, and external Codex version checks remain. |
| Issue/PR integrations | Deferred | No external tracker adapter; correctly requires separate authorization and runtime prerequisites. |

Remaining local work is bounded to semantic repository ownership/import mapping, command/tool effect inference, deeper protocol references and evaluation, learning promotion/scheduling/target evaluation, actual installer/schema migrations with rollback, and a real `run` surface. Mission dispatch/retries/integration, provider adapters, tracker/PR integrations, and external Codex/runtime checks require authorized external runtimes or services. KEELBench superiority also remains an empirical work item requiring representative paired trials.
