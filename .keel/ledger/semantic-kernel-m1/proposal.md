# Proposal

## Problem / why

The landed redesign contract defines canonical primitives and orthogonal state dimensions, but no small pure model layer currently implements them. Future migrations need deterministic, strict, portable identities and serialization without changing the behavior of current P0/P1/P2 subsystems.

## Objective

Implement migration stage M1 under `KEEL-KERNEL-REDESIGN-v1`: a dependency-free Python semantic model for all eleven canonical primitive kinds, shared identity/provenance/resource/schema rules, canonical serialization and SHA-256 content digests, strict authoritative decoding, collection validation, and hostile tests.

## Non-goals

Do not replace, modify, or migrate mission_v2, repository intelligence, evidence_graph, runtime/hooks, lifecycle ledgers, seal/anchor logic, or existing public CLI behavior. Do not make the new model a default writer or persistent graph authority. Do not implement M2-M6 early. Do not perform external effects.

## Success evidence

A focused independent test suite proves round-trip decoding for every primitive, stable canonical bytes/digests under input map ordering, strict rejection of unknown fields and malformed schemas/identities/resources/provenance, duplicate-ID rejection, portable intent rules, and pure validation. All existing canonical KEEL checks remain passing.

## Open decisions

None. The contract's exact primitive set and orthogonal dimensions are binding; implementation details remain deliberately small and dependency-free.
