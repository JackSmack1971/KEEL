# Change codex-cost-preflight

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Add fail-closed ZERO_INCREMENTAL_COST Codex runtime preflight

## Requirements
- `REQ-01` Implement a deterministic fail-closed ZERO_INCREMENTAL_COST preflight in RuntimeProfile/capability/authorization integration and autonomous Codex entry points, satisfying AC-01, AC-02, AC-03, AC-07, AC-08, and AC-11.
- `REQ-02` Surface blocked eligibility through existing doctor/status/explain and document proven versus unprovable billing boundaries, satisfying AC-04, AC-09, and AC-12.
- `REQ-03` Prove forbidden cost/auth continuation paths are absent and non-sensitive, satisfying AC-05, AC-06, and AC-10.

## Non-goals
- Do not add OpenAI API-key or provider authentication.
- Do not call billing, credit-purchase, nudge, reset, identity-rotation, or fallback-provider operations.
- Do not add a second runtime, scheduler, public reporting mechanism, or account API integration.
- Do not change WorkUnit scheduler internals, KEELBench, or unrelated behavior.
- Do not merge, push, or close a PR without separate authorization.

## Scope
- `.keel/bootstrap-manifest.json`
- `.keel/lib/**`
- `.keel/tests/**`
- `.keel/bin/keel.py`
- `.keel/hooks/**`
- `docs/control-plane/**`
- `docs/exec-plans/active/**`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `WORKFLOW.md`
- `docs/INDEX.md`

## Consequences
- Changes authorization semantics for autonomous Codex execution and must fail closed under opaque or changing runtime evidence.
- A false allow could create an incremental AI charge or bypass a limit; a false block must preserve resumable governance.
