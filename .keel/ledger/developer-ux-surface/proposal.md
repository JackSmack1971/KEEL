# Proposal

## Problem / why
KEEL has strong inspection primitives but ordinary users must know their internal command names; the upgrade brief calls out `init`, `review`, and `ship` as missing product UX.

## Objective
Add safe developer-facing projections: `keel init --check`, `keel review`, and `keel ship` eligibility reporting, while keeping state transitions and external integration explicit.

## Non-goals
No automatic agent execution, commit/seal/anchor mutation, merge/push/release, authorization grant, or installer network access.

## Success evidence
Focused tests prove each command is read-only, review aggregates current evidence, ship distinguishes eligibility from permission, and init reports repository readiness. Full KEEL verification passes.

## Open decisions
`keel run` remains deferred until an authorized execution runtime is available; the UX surface must not pretend to dispatch work.
