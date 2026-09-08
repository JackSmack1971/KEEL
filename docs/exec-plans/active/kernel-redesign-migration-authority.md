# ExecPlan: KEEL kernel redesign migration authority

Status: `ACTIVE — PLANNING ONLY`

## Objective and success evidence
Publish one authoritative target-architecture and migration contract, freeze expansion above landed P2, classify the landed tree for migration, update navigation/roadmap authority, pass planning-readiness verification, and seal the exact candidate.

## Non-goals
No kernel, graph, planner, runtime profile, reconciler, landing transaction, compatibility tooling, CLI, hook, test, or runtime implementation. No P3-P7 feature execution.

## Verified context
The landed tree contains P0 portability/compatibility, P1 repository intelligence, P2 mission-v2 planning, the current ledger lifecycle, Git candidate/ledger refs and notes, Codex hook/agent configuration, and generated bootstrap provenance. Existing formats are active compatibility surfaces and cannot be removed by this plan.

## Assumptions to test
- The current audit and roadmap still direct future P3-P7 expansion.
- Primary documentation does not yet identify one kernel-redesign authority.
- The file-level inventory can classify all tracked component families without changing generated sources by hand.

## Risk / autonomy / permission boundaries
High/control-plane/migration-planning blast radius; no executable or external effect. Planning never authorizes implementation or integration. Later changes remain bounded by observed Codex/runtime trust and separate KEEL lifecycle records.

## Milestones
### M1 — Evidence inventory
- Action: inspect implementation, tests, docs, CLI/config, ledgers, Git refs/notes, bootstrap, and P0/P1/P2 surfaces.
- Observation: record landed facts and component families in the authority document.
- Verification: every tracked top-level/control-plane family has a matrix disposition.
- Exit criteria: no current-behavior claim relies on prior discussion.

### M2 — Normative transition contract
- Action: define ownership, primitives, orthogonal states, graph semantics, trust/evidence/authorization/integration invariants, compatibility, and staged gates.
- Observation: explicitly distinguish target requirements from landed facts.
- Verification: operator-required clauses are directly searchable in one document.
- Exit criteria: later changes can cite one stable authority section/ID.

### M3 — Authority and navigation reconciliation
- Action: freeze P3-P7 in the audit/roadmap and link primary navigation to the new authority.
- Observation: old plans become subordinate evidence, not a competing future authority.
- Verification: links resolve and canonical checks pass.
- Exit criteria: one unambiguous forward migration authority remains.

### M4 — Candidate handoff
- Action: run KEEL verification, inspect evidence/diff, commit, seal, and follow explicit integration authorization only.
- Observation: planning-only readiness is distinct from implementation acceptance.
- Verification: committed-tree seal matches the verified paths and intent.
- Exit criteria: sealed candidate exists; landing/anchor occurs only if repository and external authorization permit it.

## Baseline
Base commit: `810c40b4a3b8bd0acfb3d9fe49cf286f6348181f`. `keel doctor` passed before the change. Worktree began clean on branch `work`.

## Progress log
- 2026-09-08: inspected governing docs, repository inventory, canonical checks, Codex configuration, CLI surfaces, tests, P0/P1/P2 plans and ledgers, Git log/refs/notes, and bootstrap manifest.

## Decision log
- Use a new control-plane architecture document as sole forward authority; retain the audit and roadmap as subordinate landed-state/history maps.
- Treat the change as planning-only despite migration sensitivity; no executable artifact is in scope.

## Failure branches / blockers
Missing inventory evidence, unresolved authority conflicts, generated-manifest drift, or failed canonical checks require correction and re-verification. Missing remote integration authority stops work at a sealed local candidate.

## Final verification
Run `python3 .keel/bin/keel.py verify --change kernel-redesign-migration-authority`, inspect the evidence graph and diff scope, then commit and seal the exact commit.

## Completion / handoff
Later kernel work must cite `docs/control-plane/KERNEL_REDESIGN.md`, select a migration stage, preserve compatibility gates, and use a new KEEL change. This plan conveys no implementation authorization.
