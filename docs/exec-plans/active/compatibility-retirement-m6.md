# M6 compatibility retirement and repository cleanup

Status: `ACTIVE`
Authority: `KEEL-KERNEL-REDESIGN-v1`, M6

## Purpose

Retire the duplicate v1 product/runtime path after the canonical semantic kernel,
ChangeGraph, FactGraph, EvidencePlanner, RuntimeProfile/authorization boundary,
Codex adapter, Git proof/attestation layer, and canonical ledger migration have
landed. Preserve the narrow, versioned historical-ledger reader and every Git and
worktree safety invariant.

## Baseline and proof before deletion

1. Inventory imports, CLI registrations, configuration entries, documentation,
   generated-artifact producers, package/bootstrap inputs, fixtures, and tests for
   each retirement candidate.
2. Exercise the current deterministic tests and migration CLI before mutation.
   Record any pre-existing failure separately from introduced failures.
3. Classify retained behavior as canonical kernel behavior, historical ledger
   compatibility, or optional maintenance/tooling. Delete only duplicate product
   paths; relocate useful non-authoritative material.

## Execution

1. Consolidate repository projections on FactGraph and compatibility/version
   inventory on canonical modules; remove legacy module imports and CLI verbs.
2. Preserve only the minimal frozen v1 ledger migration corpus and tests. Remove
   normal mission/topology/runtime fixtures, old split-ledger templates, and stale
   verifier registrations.
3. Move feedback/entropy helpers outside kernel core as explicitly optional
   maintenance tooling. Move generic target-project guidance into policy packs.
4. Replace `.control-plane/` distribution metadata with a canonical `.keel/`
   manifest path and update the producer, package boundary, tests, and docs.
5. Archive bootstrap research sources under a clearly non-authoritative location;
   remove reconciled planning residue and obsolete architecture/configuration docs.
6. Add a structural retirement test that rejects reintroduction of removed paths,
   CLI verbs, stale config, and active-authority references.

## Risk controls

- Deletions are reversible through Git and limited to canonical intent scope.
- Migration compatibility is tested against frozen hostile and historical v1
  fixtures, including unknown/absent state and deterministic repeated output.
- Candidate refs, landed refs, Git notes, attestations, exact-tree proof, worktree
  isolation, path normalization, malformed-state rejection, uncertainty, and generic
  review roles remain protected by direct regression tests and structural assertions.
- Independent diff review checks for dangling imports, docs links, command names,
  generated provenance, and accidental loss of historical audit inputs.

## Verification

- Run all executable deterministic test files using the repository's declared
  Python entry-point convention.
- Run the migration/compatibility suite and migrate a frozen v1 fixture twice,
  comparing outputs byte-for-byte.
- Run `keel.py doctor`, manifest verification, compatibility inventory, strict
  ledger validation, reference scans, and `keel.py verify`.
- Commit the verified tree, seal the exact commit, and anchor only after authorized
  integration. A local commit on the already-landed working branch may be treated as
  the landed subject only when the lifecycle command accepts that topology.

## Rollback

Revert the implementation commit. Do not rewrite refs, notes, attestations, or
historical ledgers. If any external consumer of a removed normal-runtime path is
discovered, stop and retain or introduce an explicit versioned compatibility adapter
rather than recreating a second authority path.
