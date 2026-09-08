# FactGraph repository adapters execution plan

Authority: `KEEL-KERNEL-REDESIGN-v1`
Stages: M2 read compatibility and M3 canonical kernel
Change: `factgraph-repository-adapters`

## Boundary and inventory

The affected canonical primitives are `Fact` and `Edge`; knowledge/support/freshness
are the relevant state dimensions; dependency, containment, declaration, candidate,
ownership, and provenance are the affected edge semantics. Matrix rows are
`repository_intelligence.py`, `repository_map.py`, `capability_resolver.py`, and
`context_compiler.py`. Existing v1 intelligence/map/resolver/context readers and tests
are compatibility obligations. Exact repository-relative paths plus source content and
Git-tree digests identify discovery subjects.

## Work sequence

1. Define a dependency-free FactGraph value model, deterministic builder, adapter SPI,
   source digest/freshness API, conflict-aware precedence, and impact traversal.
2. Implement foundational filesystem/Git adapters and bounded adapters for current
   command/config/ownership/source/Python dependency behavior.
3. Route repository intelligence through the graph and make map/capability/context
   legacy surfaces consume graph-derived projections without changing public schemas.
4. Add cross-stack hostile fixtures for unsupported formats, conflicts, path
   portability, determinism, freshness, command safety, and Python semantic edges.
5. Update thin architecture documentation and canonical verification configuration,
   regenerate declared provenance, then run focused and full KEEL verification.

## Invariants and recovery

Facts never grant permission. Candidate evidence never becomes a declaration merely
because a filename exists. Adapters inspect bytes/Git metadata only and never execute
discovered commands. Conflicts survive projection. Unknown adapters remain conservative.
No reconciler, EvidencePlanner, RuntimeProfile, effect/grant, or landing implementation
is introduced. The commit is reversible and legacy serialized inputs remain readable.

## Verification boundaries

Candidate verification binds the changed paths and intent through the KEEL verification
digest, then the committed candidate is sealed. Integration verification/anchoring is
performed only if the local current-branch landing is authorized and exact. External
effects and runtime capability grants are not required because no remote operation,
release, deployment, or migration is requested.
