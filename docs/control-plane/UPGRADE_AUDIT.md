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
| Repository mapping / knowledge graph | Partially implemented | `keel map` now emits deterministic, provenance-bearing topology/module/entrypoint/test/command/dependency facts; semantic import graphs, ownership, and architecture inference remain absent. |
| Missions / work DAG | Partially implemented | `keel mission` now validates mission contracts and computes a read-only dependency frontier/status projection; dispatch, mission verification, retries, and integration remain absent. |
| Reconciliation | Implemented as read-only kernel | `keel reconcile` compares Git, ledger, environment, compatibility, contracts, and next action; repair/retry/integration adapters remain future work. |
| Evidence providers | Partially implemented | Declared provider types now validate through configured check IDs and literal exit status; browser/log/metric/trace/device adapters remain project-specific. |
| Effect capabilities | Partially implemented | Effect names are validated against `.keel/contracts.json` and required for external/irreversible effects; command/tool inference and capability-aware authorization policy remain absent. |
| Dynamic topology / compute routing | Partially implemented | `keel route` emits deterministic complexity, model-independent effort capabilities, roles, and verification breadth; runtime dispatch and provider/model mapping remain external. |
| Reusable engineering protocols | Partially implemented | The routed `engineering-protocols` skill covers debugging, architecture, dependency, migration, security, performance, frontend runtime, test remediation, incident, and release concerns; behavioral evaluation and deeper domain-specific references remain future work. |
| Learning loop / entropy service | Partially implemented | Reviewed observation validation and deterministic non-destructive entropy scans now exist; promotion, external ingestion, scheduled operation, and target eval execution remain. |
| Developer UX | Partial | Core inspection commands are present; `init`, `run`, `review`, `ship`, and mission UX are absent. |
| Version / install / upgrade / migration | Initial compatibility primitive | `keel version` reports framework/config/contract compatibility; installer, upgrade, schema migration, rollback, and Codex/skill version checks remain. |
| Issue/PR integrations | Deferred | No external tracker adapter; correctly requires separate authorization and runtime prerequisites. |

The remaining items should be delivered as separate standard KEEL changes, ordered by uncertainty reduction: repository mapping, mission/work graph, topology/compute routing, provider adapters, controlled learning/entropy service, then installer/schema migration and external integrations.
