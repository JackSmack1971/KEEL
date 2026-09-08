# Desired-state reconciler and bounded scheduler

## Objective

Add a repository-local, deterministic scheduler for canonical ChangeGraph
WorkUnits. The scheduler observes desired and actual state, computes a legal
frontier, reserves compatible resources, dispatches through an injected
Codex/runtime adapter, records outcomes, and supports idempotent reconciliation.

## Design boundary

- `ChangeGraph` and canonical intent remain the authority for work and policy.
- The scheduler is a bounded projection/execution coordinator, not a second
  agent runtime or an authorization/grant engine.
- Adapter calls are injected; tests use simulated adapters. No network, merge,
  push, release, deployment, or automatic final landing is performed.
- Persistent scheduler state is explicit and portable, with stable WorkUnit and
  workspace identities. A dispatch key prevents duplicate active dispatch.

## Work slices

1. Define validated scheduler state, resource claims, dependency readiness,
   failure classifications, bounded recovery, stale detection, and deterministic
   frontier selection.
2. Implement reconcile/dispatch/resume through an adapter protocol with
   workspace ownership and shared/exclusive resource reservations.
3. Add simulated-adapter tests for all material constraints and a local smoke
   path using a temporary isolated workspace with no external effects.
4. Expose a read-only CLI scheduler command if it fits the existing command
   contract; update architecture and control-plane documentation.

## Risk controls

- Fail closed on malformed desired or persisted state.
- Never infer authorization from desired effects or successful dispatch.
- Never dispatch a work unit twice while an equivalent dispatch is active or
  already has a terminal result.
- Retry only when the classification policy permits it and the evidence/strategy
  fingerprint changes; otherwise escalate.
- Treat stale work as recoverable only through explicit, bounded reclamation.
- Verify focused tests, smoke, full regression, KEEL verification, committed
  tree, seal, and (only if separately authorized) integration/anchor.

## Evidence

The scheduler test suite is the primary deterministic evidence. The smoke path
proves isolated progression and persistence locally. Existing graph, lifecycle,
authorization, worktree, and repository checks provide regression evidence.
