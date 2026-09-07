# Control-Plane Capability Registry

Statuses: `ACTIVE`, `CONDITIONAL`, `DEFERRED`, `BLOCKED`, `NOT_APPLICABLE`.

Every consequential project specialty must map here or be added as a new domain. `CONDITIONAL` means the area is deliberately represented but must not be configured until its activation trigger is evidenced.

| ID | Capability | Status | Activation trigger / current evidence | Definition-of-ready evidence |
|---|---|---|---|---|
| repository-legibility | Indexed repository knowledge, capability discovery and progressive disclosure | ACTIVE | Control-plane scaffold + context compiler exist | Root map + docs index + bounded compiled task context + durable decisions |
| instruction-architecture | Root/nested AGENTS scope and instruction precedence | ACTIVE | Root AGENTS exists | Root <=100 lines; nested only for material scope differences |
| requirements-product | Product/requirements/stakeholder success contract | CONDITIONAL | Activate when project objective is supplied | Versioned REQ/AC contract + evidence graph coverage |
| plans-decisions | Durable ExecPlans and design decision history | ACTIVE | Templates/policy exist | Risk-proportional plans + progress/decision logs |
| keel-spec-ledger | Delta-anchored per-change governance, REQ/AC evidence graph, phase gates, scope, risk/effects, verification and landed Git anchors | ACTIVE | KEEL filesystem/runtime scaffold exists; hook enforcement remains trust-dependent | `keel.py doctor` + baseline commit + reviewed/trusted hooks + acceptance coverage + verification/anchor evidence |
| architecture-boundaries | Architecture map, dependency direction and invariants | CONDITIONAL | Activate when components/code exist | Verified architecture + structural checks for durable invariants |
| build-toolchain | Build/package/tool commands and versions | CONDITIONAL | Activate when toolchain chosen | Reproducible commands + version/provenance |
| dependencies-supply-chain | Dependency provenance/update/vulnerability policy | CONDITIONAL | Activate on first third-party dependency | Lock/provenance + update/security checks |
| testing-evals | Unit/integration/e2e/simulation/eval strategy | CONDITIONAL | Activate on first executable behavior | Test taxonomy + deterministic commands + failure baseline |
| quality-static-analysis | Format/lint/type/static/architecture checks | CONDITIONAL | Activate when languages/tooling chosen | Fast checks with agent-actionable remediation |
| generated-artifacts | Source/generated boundaries and regeneration | ACTIVE | `.control-plane/bootstrap-manifest.json` has a repository-owned producer and deterministic drift check | Producer provenance + generator + freshness check |
| environments-worktrees | Reproducible dev env, isolated worktrees/instances | CONDITIONAL | Activate with Git/toolchain/runtime | Per-worktree bootability or documented equivalent |
| platform-compatibility | OS/CPU/runtime/browser/device compatibility | CONDITIONAL | Activate when supported platforms are chosen | Compatibility matrix + executable evidence |
| security | Threat boundaries, secrets, least privilege, secure defaults | ACTIVE | Baseline always applies | Threat model expands with architecture |
| privacy-data | Data classification, retention, access, sensitive data | CONDITIONAL | Activate when data/persistence exists | Classification + lifecycle + access evidence |
| api-contracts | API/schema/protocol/interface compatibility | CONDITIONAL | Activate when interfaces exist | Versioned contracts + compatibility validation |
| ui-browser-a11y-i18n | UI runtime legibility, browser/device, accessibility/i18n | CONDITIONAL | Activate on human-facing interface | Reproduction + visual/DOM/device/a11y evidence as relevant |
| performance-capacity-cost | Latency/throughput/resource/cost budgets | CONDITIONAL | Activate when measurable budgets matter | Benchmarks + budgets + regression evidence |
| observability | Logs, metrics, traces, diagnostics, runtime inspection | CONDITIONAL | Activate with a running system | Queryable local/runtime evidence proportional to system |
| reliability-slos | Reliability, fail-safe/degradation, SLOs/SLIs | CONDITIONAL | Activate for runtime/service/device obligations | Measurable targets + failure/recovery tests |
| ci-cd | Automated validation/integration pipeline | CONDITIONAL | Activate when VCS/provider/process chosen | CI mirrors trusted local checks; permissions explicit |
| release-deploy-rollback | Versioning, release, deployment and rollback | CONDITIONAL | Activate when artifacts ship/deploy | Repeatable release + rollback + authorization boundary |
| migrations-backup-dr | Migrations, backup/restore, disaster recovery | CONDITIONAL | Activate with persistent mutable state | Tested migration/restore/recovery evidence |
| incident-response | Detection, triage, containment, recovery, postmortem | CONDITIONAL | Activate for operated systems | Runbook + evidence capture + escalation |
| infra-iac | Infrastructure/platform/IaC lifecycle | CONDITIONAL | Activate when infra is managed | Declarative source + plan/apply/rollback + state security |
| ml-data-agent-evals | Data/model/prompt/agent provenance and evals | CONDITIONAL | Activate for ML/data/agentic product logic | Dataset/model/prompt versions + eval/regression loop |
| embedded-hardware-safety | Hardware/firmware/real-world safety and HIL evidence | CONDITIONAL | Activate for embedded/robotic/safety-critical work | Hazard/fail-safe + simulation/HIL/test evidence |
| codex-config-trust | Project config, sandbox, approvals, trust behavior | ACTIVE | `.codex/config.toml` exists | Trusted-state verified before claiming project config active |
| command-policy-rules | Destructive/privileged command policy | ACTIVE | Project rules shipped | Syntax/runtime tested when Codex available |
| hooks | Codex lifecycle/tool hooks | CONDITIONAL | KEEL hook definitions are present; runtime enforcement activates only after project + exact hook definition are trusted | `/hooks` trust review + hook smoke evidence; hooks remain guardrails, not the only control |
| subagents-skills | Narrow delegated roles and reusable workflows | ACTIVE | Baseline subagents + maintenance skill exist | Routing/boundary and tool/sandbox limits documented |
| external-integrations-mcp | MCP/plugins/CLIs/external systems | CONDITIONAL | Activate when a real integration is required | Least privilege + auth/secrets + failure behavior |
| orchestration | Ticket-driven unattended agent scheduling | DEFERRED | Tracker + agent runtime + workspace policy + demand exist | Containment, claim/reconcile, blockers, retries, observability |
| feedback-self-improvement | Production corrections/traces -> evals -> bounded tasks | DEFERRED | KEELBench harness exists; activate learning loop only after repeated reviewed production evidence exists | Provenance + clustered findings + target/regression evals + paired baseline evidence |
| entropy-doc-gardening | Recurring drift/documentation/quality maintenance | ACTIVE | Policy + maintenance skill exist | Scheduled/manual cadence once scheduler exists; quality trend |
| provenance-audit | Evidence/source/decision traceability | ACTIVE | Seed/manifest/source docs exist | Source dates/versions + manifest + evidence links |
| autonomy-permissions | Risk-scaled permission and side-effect boundaries | ACTIVE | Decision model exists | External/irreversible actions gated by authorization/evidence |
| domain-extension | Escape hatch for specialties not represented above | ACTIVE | Always available | New domain added with trigger, evidence, risks and owner |
