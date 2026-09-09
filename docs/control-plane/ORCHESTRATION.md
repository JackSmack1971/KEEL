# Bounded WorkUnit orchestration

Orchestration remains optional and stack-neutral. It does not infer a consumer
project architecture or create commands that the repository has not declared.

`.keel/lib/scheduler.py` provides a repository-local desired-state reconciler and
bounded scheduler over canonical `ChangeGraph` WorkUnits. Each reconciliation
observes actual state, compares it with the desired graph, derives unmet
conditions, computes a deterministic legal frontier, reserves compatible
resources, dispatches selected units through an injected Codex/runtime adapter,
observes results, classifies failures, and can resume from persisted state.

The scheduler supports hard and ordering dependencies, artifact/data and
review/verification prerequisites, shared/exclusive resource claims, bounded
concurrency, read-heavy parallelism, persistent isolated WorkUnit workspaces,
one primary writer per write worktree, stale-work detection, idempotent resume,
and duplicate-dispatch prevention. Resource conflicts block/serialize work when
possible; they do not invalidate an otherwise valid mission.

Recovery is bounded and uses explicit classifications including implementation,
specification, environment, verifier, dependency-drift, resource-conflict,
authorization, integration, agent, and unknown failures. Repeating an unchanged
failure does not create an infinite retry loop; exhausted or policy-blocked work
escalates.

The adapter boundary is deliberate: Codex remains the worker harness. The
scheduler does not grant capabilities, execute external effects, merge/push,
or perform automatic final landing. Existing KEEL lifecycle gates, evidence
receipts, worktree proof, authorization, seal, integration, and anchor semantics
remain authoritative.
