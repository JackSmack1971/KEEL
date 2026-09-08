# Proposal

## Problem / why

KEEL currently has overlapping repository truth and classification implementations in
`repository_map.py`, `repository_intelligence.py`, and `capability_resolver.py`. This
permits their dependency, source, command, and capability semantics to diverge and
conflicts with `KEEL-KERNEL-REDESIGN-v1`, stages M2/M3, which requires canonical
provenance-bearing Facts and Edges in one graph with compatibility projections.

## Objective

Introduce a deterministic canonical FactGraph fed by read-only repository adapters.
Move filesystem, Git, existing ecosystem/config/ownership, and practical Python
semantic dependency discovery behind that adapter SPI; derive capabilities, context,
impact, and temporary legacy outputs from graph Facts and Edges rather than separate
repository models.

## Non-goals

- Do not implement the reconciler or EvidencePlanner.
- Do not execute discovered commands or infer policy activation from filenames.
- Do not add optimistic parsers for unsupported ecosystems.
- Do not remove required legacy readers or compatibility output schemas.
- Do not alter authorization, runtime trust, lifecycle, evidence, seal, or anchor semantics.

## Success evidence

- Deterministic unit and compatibility tests demonstrate normalized Fact/Edge emission,
  source-digest freshness, visible conflicts, portable paths, conservative unsupported
  states, separated command declarations/candidates, Python dependency preservation,
  impact queries, and graph-derived legacy projections.
- Existing repository intelligence, repository map, capability resolver, and context
  compiler regression tests pass.
- Canonical repository verification passes with complete acceptance evidence coverage.

## Open decisions

None. Canonical authority, compatibility obligations, conservative negative-state
behavior, and excluded later-stage components are fixed by the user request and
`KEEL-KERNEL-REDESIGN-v1`.
