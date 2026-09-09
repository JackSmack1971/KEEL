# Change governed-delegation-boundary

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Redesign the Codex delegation boundary so transport completion is recorded only as an execution observation and exact-subject KEEL evidence alone can complete governed engineering work.

## Requirements
- `REQ-01` Define an immutable canonical DispatchEnvelope binding change, WorkUnit, Git subject/base, validated workspace, intent/graph/authority/runtime/context/evidence identities, objective, requirements, scope/resource claims, and stop/completion protocol.
- `REQ-02` Resolve every dispatch workspace to the exact registered KEEL Git worktree and subject, fail closed on unresolved or mismatched identity, and pass its validated path as Codex thread/start cwd.
- `REQ-03` Define and persist a bounded ExecutionObservation with Codex thread/turn/runtime/workspace/subject identities, outcome, artifacts/events, and timestamps.
- `REQ-04` Treat successful Codex turn/completed solely as execution observation and transition the WorkUnit to AWAITING_VERIFICATION, never COMPLETE.
- `REQ-05` Allow COMPLETE only after KEEL accepts successful evidence evaluation bound to the exact WorkUnit and all governed dispatch identities; reject stale or mismatched identity.
- `REQ-06` Preserve fail-closed ZERO_INCREMENTAL_COST preflight before any model execution.
- `REQ-07` Persist enough dispatch, workspace, thread, turn, and observation identity to support deterministic recovery without confusing transport and engineering state.
- `REQ-08` Update architecture, orchestration, Codex-native, and verification documentation and remove stale turn-completion language.
- `REQ-09` Preserve stack-neutral KEEL governance, Codex intelligence/runtime ownership, and the bounded non-autonomous keel run surface.

## Non-goals
- Do not expose broad autonomous execution through keel run.
- Do not add a model runtime, provider, sandbox, or conversation engine to KEEL.
- Do not weaken ZERO_INCREMENTAL_COST or exact-subject verification.

## Scope
- `.keel/lib/scheduler.py`
- `.keel/lib/codex_app_server_adapter.py`
- `.keel/tests/test_scheduler.py`
- `.keel/tests/test_codex_app_server_adapter.py`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `docs/control-plane/ORCHESTRATION.md`
- `docs/control-plane/CODEX_NATIVE.md`
- `docs/control-plane/VERIFICATION.md`
- `docs/control-plane/KEEL_FORWARD_AUTHORITY.md`
- `docs/exec-plans/active/governed-delegation-boundary.md`
- `docs/exec-plans/completed/governed-delegation-boundary.md`
- `.keel/tests/smoke_scheduler.py`

## Consequences
- A loose identity binding could let observations from the wrong intent, graph, authority, runtime, workspace, or evidence plan establish completion.
- Workspace confusion could execute Codex in the wrong checkout.
- A transport outcome could be incorrectly promoted into engineering truth.
