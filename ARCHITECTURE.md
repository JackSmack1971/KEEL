# Architecture

Status: `GREENFIELD / NOT YET CHOSEN`

This file is the durable map of verified system structure. At bootstrap there is intentionally no invented stack.

## Verified facts
- Project root: `KEEL-v2`.
- Control-plane doctrine sources: `control-plane-engineering-bible.md` and `control-plane-kb.md`.
- Repository-owned control-plane scaffold exists.
- Application/runtime architecture is not yet established.

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
