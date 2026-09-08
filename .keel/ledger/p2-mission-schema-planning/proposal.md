# Proposal

## Problem / why
P1 provides repository intelligence and the existing mission_graph module provides a minimal keel.mission/v1 compatibility contract, but P2 lacks a typed, provenance-bearing v2 schema and deterministic planning semantics for dependencies, resources, capabilities, effects, decomposition, and advisory readiness.

## Objective
Implement keel.mission/v2 as a schema and read-only planning layer. Preserve mission_graph v1 unchanged, add independent fixtures and expected outputs, expose explicit v2 validation/planning behavior, and reconcile the P2 roadmap/audit state.

## Non-goals
No dispatch, worker/provider invocation, runtime handshake, worktree allocation, lock acquisition, execution, authorization grant, sealing, merge, deployment, external effect, P3–P7, or D1 implementation.

## Success evidence
Independent implementation-acceptance fixtures prove valid DAGs, graph/resource/capability/effect/decomposition/frontier/uncertainty cases, v1 normalization, deterministic repeated serialization, and prohibited execution. Required repository checks and KEEL verification pass.

## Open decisions
P2 consumes supplied P1 evidence only. Missing, conflicting, ambiguous, stale, unsupported, or runtime-only evidence is represented explicitly and never upgraded to readiness or authorization.
