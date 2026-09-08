# Proposal

## Problem / why
Candidate sealing and landed anchoring currently concentrate exact-Git proof logic in
the lifecycle core and encode the proof primarily through refs, notes, verification
documents, and audit rows. The protected behavior needs a cohesive deterministic
boundary and a formal candidate attestation without weakening compatibility.

## Objective
Extract Git identity, normalized path/diff, committed-tree proof, candidate
attestation, sealing, and landed anchoring logic into explicit modules. Preserve the
existing CLI and refs/notes semantics while adding a versioned CandidateAttestation
that binds work/candidate identity, material and intent digests, the EvidencePlan,
supporting EvidenceReceipts, and relevant policy/runtime profile information.

## Non-goals
- Do not implement the future Landing Transaction.
- Do not change integration authorization or make refs/notes immutable.
- Do not remove content-equivalent squash/rebase support or compatibility readers.
- Do not expand application/runtime capabilities.

## Success evidence
- Focused deterministic tests independently exercise Git root/baseline identity,
  repository-relative normalization, worktree isolation metadata, scoped material
  diffs, all attestation digests/identities, committed-tree verification, collisions,
  landed equivalence, drift rejection, and unrelated-mainline tolerance.
- Existing lifecycle compatibility/worktree tests and repository verification pass.
- Architecture and lifecycle documentation identify the new authority boundary.

## Open decisions
None. Existing exact-Git behavior is the compatibility oracle; new payload storage is
Git-tracked with the candidate ledger, while refs and notes remain indexes/anchors.
