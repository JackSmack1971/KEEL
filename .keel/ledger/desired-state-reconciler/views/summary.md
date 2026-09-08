# Change desired-state-reconciler

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Implement desired-state reconciliation and bounded WorkUnit scheduling

## Requirements
- `REQ-1` Implement a desired-state control loop that observes actual state, compares it with desired state, derives unmet conditions, computes a legal/runnable frontier, dispatches bounded actions through adapters, observes/classifies results, and can reconcile again without fixed lifecycle choreography.
- `REQ-2` Support hard dependency edges, supported ordering-only constraints, artifact/data dependencies, review/verification dependencies, resource claims, shared versus exclusive resources, bounded concurrency, one primary writer per write worktree, and safe read-heavy concurrency.
- `REQ-3` Persist isolated WorkUnit/workspace identity and enforce workspace ownership so work can resume idempotently and write worktrees have one primary writer.
- `REQ-4` Detect stale work and prevent duplicate dispatch, including when resuming persisted scheduler state.
- `REQ-5` Classify failures using the requested explicit classifications and apply bounded recovery; unchanged evidence and strategy must not cause infinite retries, and policy blockers must escalate.
- `REQ-6` Keep Codex as the worker harness and do not implement automatic final landing beyond existing safe integration semantics.
- `REQ-7` Provide deterministic simulated-adapter scheduler tests and at least one repository-local smoke path proving isolated WorkUnit progression without external effects.
- `REQ-8` Use existing KEEL governance and preserve canonical semantic, repository, evidence, runtime authorization, ledger, verification, commit, seal, integration, and anchor boundaries.
- `REQ-9` Provide repository-local smoke evidence that isolated WorkUnits progress and resume without external effects.

## Non-goals
- Do not implement a second generic agent runtime; Codex/runtime adapters remain the worker harness boundary.
- Do not automatically land, merge, push, release, deploy, or perform external effects.
- Do not replace canonical intent, ChangeGraph, evidence receipts, RuntimeProfile, CapabilityGrants, or existing safe integration semantics.
- Do not add unbounded retries, speculative providers, or a fixed lifecycle choreography as orchestration authority.

## Scope
- `.keel/lib/scheduler.py`
- `.keel/lib/change_graph.py`
- `.keel/tests/test_scheduler.py`
- `.keel/tests/test_p0_contract.py`
- `.keel/tests/smoke_scheduler.py`
- `.keel/bin/keel.py`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `ARCHITECTURE.md`
- `docs/control-plane/ORCHESTRATION.md`
- `docs/control-plane/COMMANDS.md`
- `docs/control-plane/VERIFICATION.md`
- `docs/exec-plans/active/desired-state-reconciler.md`

## Consequences
- Scheduler mistakes could duplicate work, violate write isolation, or suppress runnable work.
- Incorrect recovery classification could repeat failed actions or conceal authorization and specification blockers.
- The control-plane boundary must remain compatible with existing canonical lifecycle, evidence, and worktree guarantees.
