# Proposal

## Problem / why
KEEL can validate and order work but does not yet express how problem complexity should influence delegation, review depth, or verification breadth.

## Objective
Add a deterministic, model-independent routing report for mission work items that recommends complexity, effort capability, roles, and verification breadth from declared risk and dependency structure.

## Non-goals
No model names, token budgets, agent launches, permission changes, automatic delegation, or replacement of human risk decisions.

## Success evidence
Focused tests prove stable routing across trivial/standard/complex/critical cases and prove mission input is not mutated. Existing control-plane checks pass.

## Open decisions
Runtime consumers may map capabilities to available models; KEEL only emits capability labels.
