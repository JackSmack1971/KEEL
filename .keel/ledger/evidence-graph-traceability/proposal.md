# Proposal

## Problem / why

The evidence graph evaluates acceptance criteria, but it currently permits a declared requirement to have no acceptance criterion. That creates a silent traceability gap: verification can pass while part of the intended behavior has no executable evidence edge.

## Objective

Require every declared requirement to be covered by at least one acceptance criterion and emit deterministic requirement coverage in the evaluated graph. Add focused tests for complete coverage and orphan-requirement rejection.

## Non-goals

- No new evidence provider types.
- No automatic inference of requirements or acceptance criteria.
- No change to command execution, authorization, scope, or Git sealing.

## Success evidence

- Focused evidence-graph tests prove orphan requirements fail validation and complete graphs emit coverage counts.
- Existing KEEL verification, KEELBench, doctor, and strict control-plane validation pass.
- Documentation defines the coverage invariant.

## Open decisions

None; an acceptance criterion may cover only one requirement under the existing contract, and every requirement must have at least one criterion.
