# Proposal

## Problem / why
KEEL has landed canonical planning and evidence primitives, but runtime trust and authorization remain compatibility-stage concepts. Legacy effects and authorization records collapse permission into a boolean, while configured hooks/tools can be mistaken for observed enforcement. This prevents the autonomy ceiling from being evaluated conservatively against what the current Codex/runtime can actually enforce.

## Objective
Implement the `KEEL-KERNEL-REDESIGN-v1` M4 runtime/authorization boundary: a first-class observed `RuntimeProfile`; intent-bound, scoped `CapabilityGrant` authorization; independent `EffectRequest` and effect adapter/receipt contracts; and a deterministic autonomy policy that accounts for consequence, reversibility, uncertainty, observability, evidence, enforcement, authorization, and recovery cost.

## Non-goals
- No scheduler, agent framework, provider orchestration, deployment integration, or external effect execution.
- No claim that hooks, configuration, adapters, or receipts provide total confinement.
- No optimistic inference of unavailable runtime facts and no compatibility migration that invents permission.
- No retirement of legacy effects/authorization readers or change to the existing landing transaction boundary.
- No implementation of M5 or M6.

## Success evidence
- Deterministic unit fixtures cover fully observed and partially/unobserved runtimes, stale/conflicting observations, hook/tool coverage gaps, mediated/observed/unconfined effects, and all autonomy outcomes.
- Hostile authorization fixtures reject subject/action/resource/constraint/intent mismatches, expiry, exhaustion, unsupported capability, and legacy `authorized=true` as an implicit grant.
- Compatibility adapters read existing effects/authorization shapes losslessly enough to produce conservative requests/grant candidates without changing planning validity or silently authorizing execution.
- Existing canonical semantic, planning, lifecycle, provider-effect, and repository test suites remain green; `keel verify` supplies receipt-authoritative acceptance coverage.
- The exact committed candidate is sealed; integration and landing anchor occur only if the current authorization boundary permits them.

## Open decisions
None. The authoritative semantics and migration stage are fixed by `KEEL-KERNEL-REDESIGN-v1`; implementation details must preserve one canonical semantic authority and explicit negative/unknown states.
