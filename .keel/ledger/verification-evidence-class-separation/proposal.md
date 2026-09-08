# Proposal

## Problem / why

KEEL currently evaluates planning/readiness evidence as ordinary implementation acceptance, allowing an implementation change with only changed planning paths and control-plane checks to reach `SHIP` and seal eligibility.

## Objective

Separate planning readiness, implementation acceptance, and landed completion evidence in the generic evidence graph and lifecycle consumers. Planning evidence must remain useful but cannot grant implementation authority.

## Non-goals

- Implement P1 repository intelligence or any P2–P7/D1/P4 behavior.
- Weaken canonical verification, scope, authorization, sealing, or anchoring checks.
- Rewrite the P1 ledger or erase its historical false verification.

## Success evidence

Focused evidence-graph, lifecycle, next-action, seal, and historical-anchor regressions prove that planning-only evidence remains labeled readiness, implementation changes cannot ship or seal without behavioral evidence, planning-only changes retain a legitimate path, and existing anchored behavior is unchanged. Broad control-plane validation, doctor, generated-artifact checks, and landed-tree anchoring pass.

## Open decisions

Use a generic change-level `change_type` with `implementation` as the compatible default and explicit `planning_only` support. Criteria preserve an explicit evidence class when present and otherwise classify non-behavioral legacy evidence as planning readiness and behavioral providers as implementation acceptance.
