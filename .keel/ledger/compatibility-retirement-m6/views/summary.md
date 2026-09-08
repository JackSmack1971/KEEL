# Change compatibility-retirement-m6

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Complete KEEL-KERNEL-REDESIGN-v1 M6 by proving and removing superseded v1/core/bootstrap product paths, retaining only versioned ledger migration compatibility and protected Git lifecycle guarantees, relocating generic policy and optional maintenance material, and leaving one canonical kernel vocabulary and CLI.

## Requirements
- `REQ-1` Remove the normal v1 mission runtime, mission-v2 compatibility product path, topology router, duplicate repository-map and developer-UX wrappers, and temporary upgrade kernel after all active consumers use ChangeGraph, FactGraph, EvidencePlanner, RuntimeProfile, canonical ledger, and kernel CLI semantics.
- `REQ-2` Retain deterministic, fail-closed historical v1 ledger migration through a narrow versioned reader and minimal frozen fixtures, preserving source bytes, digests, unknown fields, absence, and explicit uncertainty without inventing grants or evidence.
- `REQ-3` Move useful feedback and entropy inspection out of kernel core into explicitly optional maintenance tooling and move generic target-project frontend, reliability, security, and release guidance into an explicit policy-pack/template location.
- `REQ-4` Replace .control-plane as an active runtime namespace with canonical .keel distribution metadata, archive bootstrap research away from product authority, and remove reconciled planning residue, stale verification configuration, obsolete phase-agent configuration, and obsolete architecture documentation.
- `REQ-5` Preserve candidate and landed refs, Git notes indexing, candidate/landed attestations, exact committed-tree verification, worktree isolation, repository-relative normalization, fail-closed malformed-state handling, explicit uncertainty, and generic explorer/reviewer/risk-reviewer capabilities.
- `REQ-6` Prove retirement safety by repository reference search, deterministic tests, migration round-trip and idempotence, CLI behavior, documentation validation, runtime entry-point inspection, and a mechanical no-dual-path regression check.
- `REQ-7` Update the active architecture and governance documentation to describe one canonical architecture, one semantic vocabulary, one normal CLI, and no dual v1/v2 product path.

## Non-goals
- Do not remove candidate or landed refs, Git notes indexing, attestations, exact committed-tree verification, worktree isolation, repository-relative normalization, fail-closed malformed-state handling, explicit uncertainty, or useful generic explorer/reviewer/risk-reviewer roles.
- Do not delete historical ledgers or the minimal frozen fixtures required to prove deterministic v1 ledger migration.
- Do not claim hooks or Git refs are immutable confinement, and do not push, merge, release, deploy, or perform another external effect without separate authorization.

## Scope
- `.keel/**`
- `.codex/**`
- `.agents/**`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `WORKFLOW.md`
- `docs/**`
- `policies/**`
- `archive/**`
- `plans/**`
- `control-plane-engineering-bible.md`
- `control-plane-kb.md`
- `.control-plane/**`

## Consequences
- Removing a still-used entry point could break lifecycle or migration behavior.
- Moving generated distribution metadata could create stale bootstrap or package contracts.
- Overbroad cleanup could erase audit history or weaken Git, worktree, malformed-state, or uncertainty guarantees.
