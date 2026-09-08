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

## Canonical semantic and planning boundary

A dependency-free semantic model defines the kernel's eleven canonical primitive records, orthogonal state dimensions, strict identity/provenance/resource rules, and deterministic serialization/content digests in `.keel/lib/semantic_kernel.py`. Canonical planning now composes those records into one authoritative `ChangeGraph`: work dependencies exist only as typed edges, effects remain requests rather than grants, resource overlap affects later scheduling rather than validity, and frontier is a pure projection over supplied state. Mission v1/v2 documents remain read-compatible only through explicit normalization adapters. Repository-intelligence, evidence, runtime, lifecycle-ledger, seal, and anchor subsystems retain their existing behavior until separately migrated under `KEEL-KERNEL-REDESIGN-v1`.
