# Proposal: Implement portable runtime and governed mission execution

## Problem

KEEL exposes mission validation and advisory dispatch contracts, but no supported capability handshake or executable runtime. Portability is also limited to repository-local compatibility inspection and config migration primitives.

## Objective

Add an explicit, fail-closed runtime capability contract and a local mission execution boundary that schedules only ordinary child Changes, preserves per-change verification/sealing, bounds retries, and never grants authorization or integrates unverified material.

## Non-goals

- No external tracker, PR, provider, Codex, browser, or deployment integration.
- No automatic authorization or remote/production effect.
- No parallel mission policy or evidence model separate from KEEL Changes.

## Success evidence

- `version`, adoption/upgrade inspection, and migration compatibility are explicit and portable.
- Mission execution is available through the CLI and runtime module, with isolated child worktrees and bounded retry state.
- Boundary fixtures reject scope/effects/authorization/evidence/sealing/tree-substitution bypasses.
- Existing compatibility, migration, mission, and full configured checks pass.

## Unresolved decisions

- External agent/provider execution remains a capability supplied by a configured adapter; absent capability must return a structured blocked result rather than being inferred from files.
