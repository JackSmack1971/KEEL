# Proposal

## Problem / why

Explicit `keel next --change` evaluates a preserved `SHIP` ledger directly and currently recommends `integrate-anchor` whenever a sealed candidate exists, even when the candidate is already landed and the change is inactive. Implicit `keel next` correctly reports `IDLE` because anchoring removes the active marker.

## Objective

Make next-action computation derive anchored/inactive state from valid candidate, landed, note, and provenance evidence so an already anchored change is not actionable while unanchored or inconsistent evidence remains actionable or blocked.

## Non-goals

- Do not rewrite preserved ledger phase text.
- Do not change upgrade scope, requirement classifications, benchmark policy, P0/P4 state, or unrelated lifecycle behavior.
- Do not weaken anchor integrity checks or manually mutate ledger state.

## Success evidence

- Focused regression tests cover anchored, unanchored, incomplete, and provenance-mismatch `SHIP` states and explicit/implicit consistency.
- Explicit next for `upgrade-planning-authority-reconciliation` is inactive and does not recommend `integrate-anchor`.
- Implicit next remains `IDLE`; doctor and canonical lifecycle checks pass.

## Open decisions

None; the existing anchor contract in `keel_core.anchor` is authoritative for candidate/landed/note/provenance validation.
