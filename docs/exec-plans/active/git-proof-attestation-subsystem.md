# Git Proof and Candidate Attestation Subsystem

Status: active
Change: `git-proof-attestation-subsystem`

## Objective
Extract exact-Git candidate and landed proof behavior from `keel_core.py` into small,
deterministic modules and add a complete CandidateAttestation without implementing the
future Landing Transaction.

## Constraints
- Existing Git roots, baselines, paths, worktree metadata, diffs, digests, refs, notes,
  collision behavior, and content-equivalent landing are protected behavior.
- Existing CLI entry points and integration hooks remain compatible.
- Proof must come from committed Git trees and authoritative EvidencePlan/Receipts.
- Refs and notes remain mutable indexes/anchors, not the sole payload.

## Execution
1. Capture focused lifecycle baselines and trace all current helper dependencies.
2. Add dependency-free Git-proof primitives and CandidateAttestation validation.
3. Delegate core seal/status/anchor paths while retaining compatibility interfaces.
4. Add hostile temporary-repository tests for every protected negative and equivalence case.
5. Synchronize architecture/lifecycle documentation and verifier registry.
6. Run focused tests, full selected KEEL verification, independent review, commit, and seal.
7. Create the requested PR; anchor only if an authorized landed commit is actually available.

## Verification and rollback
The new focused verifier is receipt-selected by the change contract. Existing lifecycle
and worktree suites remain regression oracles. Revert the implementation commit to
restore the prior monolith; no remote ref, release, migration, or Landing Transaction is
part of implementation.
