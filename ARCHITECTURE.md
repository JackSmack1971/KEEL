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

Repository understanding now has one implementation authority: the dependency-free
FactGraph in `.keel/lib/fact_graph.py`. Read-only filesystem, Git, repository-structure,
ecosystem-candidate, Python-AST, and CODEOWNERS adapters emit normalized Facts and
Edges; repository intelligence, maps, capabilities, context inputs, and impact are
compatibility projections over that graph. Heuristic facts remain candidates and never
activate policy or authorize/execute a discovered command.

## Canonical semantic and planning boundary

A dependency-free semantic model defines the kernel's eleven canonical primitive records, orthogonal state dimensions, strict identity/provenance/resource rules, and deterministic serialization/content digests in `.keel/lib/semantic_kernel.py`. Canonical planning now composes those records into one authoritative `ChangeGraph`: work dependencies exist only as typed edges, effects remain requests rather than grants, resource overlap affects later scheduling rather than validity, and frontier is a pure projection over supplied state. Mission v1/v2 documents remain read-compatible only through explicit normalization adapters. Repository-intelligence and runtime remain compatibility-stage subsystems. Verification now uses `.keel/lib/evidence_system.py` as its primary authority for EvidenceRequirements, impact-selected EvidencePlans, declared Verifiers, and exact-subject EvidenceReceipts. `.keel/lib/evidence_graph.py` remains a legacy contract reader and new `evidence-graph.json` output is a compatibility projection. Lifecycle seal and anchor boundaries retain their existing semantics under `KEEL-KERNEL-REDESIGN-v1`.

## Git proof and attestation boundary

Exact repository, worktree, path, diff, tree-entry, and commit identity proofs are now
owned by the dependency-free `.keel/lib/git_proof.py`. The versioned
`CandidateAttestation` and the compatible candidate/landed boundary are owned by
`.keel/lib/candidate_attestation.py`; `keel_core.py` remains the lifecycle orchestrator
and compatibility facade. Candidate attestations are stored as canonical Git blobs
indexed by `refs/keel/attestations/candidates/<change-id>` and also recorded in local
audit output. Candidate, attestation, landed, and note refs are mutable indexes/anchors,
not immutable policy or the sole attestation payload. This boundary deliberately does
not implement the future Landing Transaction.

## Runtime trust and authorization boundary

The dependency-free `.keel/lib/runtime_authorization.py` implements the M4
runtime-policy boundary over canonical `RuntimeProfile`, `EffectRequest`, and
`CapabilityGrant` records. Profiles retain explicit negative observations rather
than deriving trust from configuration. Grants bind subject, work/change, action,
resource, constraints, intent digest, issuer evidence, validity, and use limits.
Effect adapters classify boundaries as `MEDIATED`, `OBSERVED`, or `UNCONFINED`;
none currently executes provider effects. Planning validity remains independent
from execution readiness. This does not implement a scheduler or hook confinement.
