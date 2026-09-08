# Architecture

Status: `APPLICATION GREENFIELD / KEEL KERNEL REDESIGN AUTHORIZED FOR PLANNING`

This file is the durable map of verified system structure. At bootstrap there is intentionally no invented stack.

## Verified facts
- Project root: `KEEL-v2`.
- Control-plane doctrine sources: `control-plane-engineering-bible.md` and `control-plane-kb.md`.
- Repository-owned control-plane scaffold exists.
- Application/runtime architecture is not yet established.

## KEEL target architecture

[`docs/control-plane/KERNEL_REDESIGN.md`](docs/control-plane/KERNEL_REDESIGN.md) is the sole authoritative target architecture and migration contract for the KEEL kernel. The landed implementation remains current behavior until separately migrated; this link does not implement or authorize the target.

## Architecture contract
When architecture is introduced, record:
- system purpose and users;
- major components and trust boundaries;
- dependency direction/layers;
- public interfaces/contracts;
- authoritative data stores and generated artifacts;
- runtime/deployment topology;
- cross-cutting concerns and their single entry points;
- forbidden dependencies/cycles;
- invariants that deserve structural tests or lints.

Every architecture claim must be either `VERIFIED`, `PROPOSED`, or `DEPRECATED`. Do not present proposals as current facts.

See [docs/control-plane/ARCHITECTURE_ENFORCEMENT.md](docs/control-plane/ARCHITECTURE_ENFORCEMENT.md).

## Control-plane intelligence boundary

Repository discovery and context compilation are derived views. They may summarize evidence and route agents toward relevant source-of-truth artifacts, but they never replace Git-tracked policy, KEEL ledger intent, architecture contracts, or verification evidence.

## Canonical semantic model boundary

A dependency-free M1 semantic model now defines the target kernel's eleven canonical primitive records, orthogonal state dimensions, strict identity/provenance/resource rules, and deterministic serialization/content digests in `.keel/lib/semantic_kernel.py`. It is an isolated contract layer, not yet a persistent authority or default reader/writer: the landed mission, repository-intelligence, evidence, runtime, lifecycle-ledger, seal, and anchor subsystems retain their existing behavior until separately migrated under `KEEL-KERNEL-REDESIGN-v1`.
