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
| Repository mapping / knowledge graph | Missing | No `keel map` or provenance-backed topology/module/dependency outputs. |
| Missions / work DAG | Partially implemented | `keel mission` now validates mission contracts and computes a read-only dependency frontier/status projection; dispatch, mission verification, retries, and integration remain absent. |
| Reconciliation | Implemented as read-only kernel | `keel reconcile` compares Git, ledger, environment, compatibility, contracts, and next action; repair/retry/integration adapters remain future work. |
| Evidence providers | Contract only | Provider-neutral names are defined and validated; browser/log/metric/trace/device adapters are not implemented. |
| Effect capabilities | Contract only | Capability vocabulary is declared and validated; command/tool capability declaration and enforcement are not yet wired into authorization. |
| Dynamic topology / compute routing | Missing | No complexity estimator or capability-based routing output. |
| Reusable engineering protocols | Missing | Only lifecycle/control-plane skills are repository-owned; debugging, migration, security, performance, and release protocols remain to be designed. |
| Learning loop / entropy service | Policy only | Durable feedback and entropy doctrine exists; reviewed observation intake, promotion, and scheduled scans are absent. |
| Developer UX | Partial | Core inspection commands are present; `init`, `run`, `review`, `ship`, and mission UX are absent. |
| Version / install / upgrade / migration | Initial compatibility primitive | `keel version` reports framework/config/contract compatibility; installer, upgrade, schema migration, rollback, and Codex/skill version checks remain. |
| Issue/PR integrations | Deferred | No external tracker adapter; correctly requires separate authorization and runtime prerequisites. |

The remaining items should be delivered as separate standard KEEL changes, ordered by uncertainty reduction: repository mapping, mission/work graph, topology/compute routing, provider adapters, controlled learning/entropy service, then installer/schema migration and external integrations.
