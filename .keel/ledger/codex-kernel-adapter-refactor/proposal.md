# Proposal

## Problem / why
KEEL's Codex-facing hooks, rules, skills, and phase-specific agents currently duplicate lifecycle, scope, integration, and evidence decisions that belong to the deterministic kernel. The hook recognizes only a narrow tool set, combines wire parsing with semantic policy, and can overstate what post-tool observation or static hook fixtures prove about runtime enforcement.

## Objective
Implement migration stage M4 under `KEEL-KERNEL-REDESIGN-v1`: create a deterministic kernel query boundary for normalized Codex runtime events, bounded context, runtime-profile-aware policy, and explicit adapter outcomes; reduce the hook to wire normalization and outcome rendering; align Codex configuration, rules, skills, agents, tests, and documentation with that boundary.

## Non-goals
- Do not implement the reconciler, a scheduler, a tool executor, runtime confinement, or the future landing transaction.
- Do not claim installed Codex hook enforcement from repository fixtures or configuration.
- Do not weaken Codex sandbox, approval, host, provider, Git, or domain controls.
- Preserve legacy lifecycle behavior and a safe bootstrap path while the adapter changes.

## Success evidence
- Deterministic tests prove event/tool normalization, bounded context, RuntimeProfile/policy queries, fail-closed enforcement when trusted KEEL state is unavailable, narrowly proven outside-authority fail-open behavior, and honest pre/post-tool decisions.
- Realistic hook subprocess fixtures cover current Codex wire payloads, including additional local/MCP function events where supported, without labeling fixture success as installed-runtime enforcement.
- Architecture checks show semantic lifecycle/scope/evidence decisions live in kernel modules rather than the hook, rules, skills, or agents.
- Documentation provides an explicit installed-runtime smoke procedure and accurate hook/tool coverage and limitations.
- Phase-specific `keel-discuss`, `keel-plan`, `keel-verify`, and `keel-ship` agents are removed after their responsibilities are exposed through kernel context/evidence operations; generic explorer/reviewer/risk-reviewer roles remain dynamically selected by evidence and risk.

## Open decisions
None. Use the current observed repository contracts and conservative M4 authority; unsupported or ambiguous runtime surfaces remain explicit negative/unknown observations.
