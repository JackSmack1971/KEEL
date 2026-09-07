# Proposal

## Problem / why

KEEL exposes phase and verification state, but an operator or agent still has to infer the next legal transition from lifecycle documentation and ledger files. That creates avoidable friction and makes blocked work less legible.

## Objective

Add `keel.py next` as a deterministic, read-only advisor that reports the active change phase, blockers, legal next action, and exact command where the lifecycle contract permits one.

## Non-goals

- No automatic phase transitions or writes.
- No mission scheduler, dependency DAG, worktree manager, or external tracker integration.
- No authorization grant or bypass of existing gates.

## Success evidence

- Focused tests cover idle state, each lifecycle phase, and stale verification guidance.
- The CLI emits stable JSON with explicit legal actions and blockers.
- Existing control-plane checks and KEELBench validation pass.

## Open decisions

None; `keel next` remains advisory and cannot mutate ledger state.
