# ExecPlan: Runtime trust and authorization model

Status: `ACTIVE`
Authority: `KEEL-KERNEL-REDESIGN-v1`, stage `M4 — Runtime/evidence adapters`

## Objective and success evidence
Implement conservative runtime observation, intent-bound capability grants, independent effect requests and effect adapter/receipt contracts, and the six-outcome autonomy policy. Hostile deterministic tests and full KEEL verification must show that absent or adverse evidence only lowers authority.

## Non-goals
No scheduler, dispatch, provider executor, network action, deployment, external mutation, hook-confinement claim, M5 landing transaction, M6 retirement, or default-writer migration.

## Verified context
The canonical semantic kernel already declares skeletal `RuntimeProfile`, `CapabilityGrant`, and `EffectRequest` primitives. Existing lifecycle `effects.json` and script-owned `authorization.json` remain governing compatibility surfaces and use boolean authorization state. Hooks explicitly are not total confinement. Canonical planning can remain valid without runtime or grant records.

## Risk / autonomy / permission boundaries
High control-plane, security, and compatibility risk. All implementation operations are reversible local repository writes. No effect adapter performs an effect in this stage. Legacy authorization evidence is preserved but never becomes a grant. Runtime configuration is not observation, and UNCONFINED effects cannot be represented as preventable.

## Milestones
### M1 — Canonical contracts
- Expand the three existing semantic primitives without adding a second authority.
- Define effect boundary and receipt/value contracts in a dependency-free runtime module.
- Verify strict serialization, validation, and intent binding.

### M2 — Conservative observation and policy
- Build RuntimeProfile only from supplied observations with negative states preserved.
- Evaluate the complete policy factor set into six ordered decisions.
- Verify hostile missing, stale, conflicting, unsupported, and coverage-gap cases.

### M3 — Compatibility and documentation
- Adapt legacy effects/authorization shapes without grants or permission defaults.
- Keep plan validity independent from execution readiness.
- Register focused verification, regenerate declared provenance, and update durable current-state docs.

## Failure branches / blockers
Any optimistic default, boolean-to-grant conversion, intent-drift acceptance, unclassified effect confinement, scheduler/executor behavior, legacy-read regression, second authorization authority, out-of-scope diff, or uncovered acceptance criterion blocks completion.

## Final verification and handoff
Run focused hostile suites, existing semantic/provider/lifecycle regressions, full `keel verify`, scope/diff inspection, commit, seal, integrate only if authorized, anchor the landed commit, and create the requested pull request.
