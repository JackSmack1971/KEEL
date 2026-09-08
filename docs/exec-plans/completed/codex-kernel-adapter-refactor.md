# Codex kernel adapter refactor

Authority: `KEEL-KERNEL-REDESIGN-v1`
Stage: `M4 — Runtime/evidence adapters`

## Objective and boundaries
Replace hook-local lifecycle/scope/evidence authority with a deterministic kernel query used by thin Codex adapters. Preserve legacy lifecycle reads and the existing entrypoint while broadening observable local/MCP function events. Do not implement M5 reconciliation/landing, an executor, scheduler, provider integration, or confinement.

## Canonical impact
- Primitives: `RuntimeProfile`, `EffectRequest`, `CapabilityGrant`, `Decision`, `EvidenceRequirement`, `EvidenceReceipt`, plus existing `WorkUnit`/`Requirement` subjects consumed by lifecycle compatibility readers.
- State: validity, knowledge, support, readiness, and lifecycle remain orthogonal; adapter output must not collapse them.
- Edges: existing requirement/evidence and work relationships are read only; no new independent graph is stored.
- Matrix rows: runtime authorization; hook/hooks.json; Codex rules/agents; repository skills; CLI/config documentation compatibility.

## Reader/writer and compatibility inventory
Readers: Codex hook stdin, `keel_core` lifecycle/status/scope/evidence/context APIs, `.keel/config.json`, active legacy ledger files, parent environment runtime observations. Writers: context cache/gate audit remain delegated to the existing lifecycle APIs; hook output is ephemeral JSON. Preserve current SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop payload compatibility and denial output while adding normalized tool families.

## Plan
1. Establish baseline tests and extract deterministic runtime authority/failure semantics.
2. Add `codex_adapter_kernel` normalized query/outcome contracts, bounded context, coverage facts, policy consultation, and compatibility lifecycle decisions.
3. Reduce the hook to repository discovery, input parsing, kernel invocation, and Codex wire rendering; update hooks.json matchers.
4. Remove phase agents; revise generic roles, rules, and skills to request context/evidence and select review dynamically.
5. Add pure and subprocess wire tests, structural authority checks, docs/smoke runbook, verifier entry, and an explicit producer-owned retirement mechanism before regenerating the manifest.
6. Run focused/full verification, independently review the high-risk diff, commit, seal, integrate only as authorized, and anchor the landed content.

## Exact subjects and evidence
Candidate subject is the committed tree plus this ledger's stable intent digest. `codex-adapter-tests` and `codex-hook-wire-tests` bind receipts to that verified subject; mandatory compatibility/doctor/manifest checks cover bootstrap and old readers. A live Codex `/hooks` smoke observation is intentionally not fabricated by tests and remains a separately reported runtime fact.

## Runtime and authorization prerequisites
Filesystem edits/local commit are reversible repository effects allowed by the task. No external effect is declared. RuntimeProfile observations are required before the adapter relies on enforcement; missing trusted state lowers autonomy and blocks enforcement events. Static config is never promoted to trust or authorization.

## No-second-authority / rollback proof
Structural tests reject lifecycle policy branches in the hook and phase-agent files, and ensure rules/skills defer to kernel operations. Existing P0/lifecycle suites prove reader compatibility. Git revert restores the previous adapter; no persisted canonical schema or writer changes require data rollback.
