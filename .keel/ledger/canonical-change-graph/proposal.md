# Proposal

## Problem / why

The landed mission v1/v2 planners persist overlapping dependency and planning
authority in mission nodes, top-level dependency arrays, authorization-shaped
fields, runtime observations, and dispatch projections.  This conflicts with
the canonical semantic-kernel boundary and makes equivalent inputs capable of
divergent interpretation.

## Objective

Make a canonical ChangeGraph of WorkUnit, Requirement, Edge, EffectRequest, and
EvidenceRequirement records the authoritative planning representation.  Add
deterministic structural and canonical-serialization validation, explicit
legacy v1/v2 adapters that preserve uncertainty, and a stable mission/change-
graph CLI whose frontier is a read-only projection from the graph plus supplied
state.

## Non-goals

- Scheduling, agent selection, dispatch, effect execution, or authorization.
- Removing the ability to ingest previously supported mission v1/v2 documents.
- Migrating lifecycle ledgers or other later kernel-redesign stages.
- Treating resource-claim conflicts as graph invalidity.

## Success evidence

- Canonical tests prove identity, endpoint, duplicate-edge, self-dependency,
  hard-cycle, resource, requirement/evidence, provenance, and serialization
  invariants.
- Compatibility tests prove deterministic v1/v2 normalization, uncertainty
  retention, and the absence of invented grants/runtime facts.
- CLI tests prove the stable `mission` and `change-graph` surfaces consume the
  canonical graph and that compatibility aliases remain read-only adapters.
- Repository canonical checks and an independent control-plane review pass.

## Open decisions

None.  The operator request and `KEEL-KERNEL-REDESIGN-v1` define the semantic
boundary; implementation details must remain dependency-free and deterministic.
