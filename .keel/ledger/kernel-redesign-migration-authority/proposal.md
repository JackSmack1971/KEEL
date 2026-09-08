# Proposal

## Problem / why
The landed P0/P1/P2 implementation has accumulated multiple schemas, projections, lifecycle states, and planning surfaces. Continuing the prior P3-P7 feature roadmap before establishing a single semantic kernel risks duplicate authorities, conflated state, runtime-trust overclaims, and compatibility breakage. The repository needs an authoritative transition contract grounded in the landed tree.

## Objective
Freeze feature expansion above the landed P2 state and publish one authoritative architecture and file-level migration contract for a later KEEL kernel redesign. Define ownership between Codex and KEEL, canonical primitives and graph/state invariants, trust/authorization/evidence/integration boundaries, compatibility rules, migration sequencing, and explicit component dispositions.

## Non-goals
Do not implement or alter the kernel, ChangeGraph, FactGraph, EvidencePlanner, RuntimeProfile, reconciler, landing transaction, schemas, CLI behavior, hooks, tests, runtime configuration, or migration tooling. Do not begin P3-P7, dispatch agents, alter worktrees, grant authorization, integrate remotely, or perform any external/irreversible effect.

## Success evidence
A single indexed redesign document is the unambiguous forward migration authority; it contains every requested invariant, a complete file-level classification of landed component families, compatibility and sequencing gates, and mechanical-reference rules. A subordinate ExecPlan and risk review describe this planning-only change. Documentation navigation and deterministic repository checks pass, KEEL records planning-only readiness, and the exact committed candidate is sealed.

## Open decisions
Implementation details intentionally remain deferred. Later turns must resolve serialization/schema versions, module boundaries, migration tooling, runtime observation adapters, and landing mechanics within this document's invariants and through separate authorized KEEL changes.
