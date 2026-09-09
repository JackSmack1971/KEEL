# Landing Transaction

Status: `COMPLETE / LANDED IN CURRENT TREE — HISTORICAL LEDGER RETAINED`
Forward authority: [`KEEL_FORWARD_AUTHORITY.md`](../../control-plane/KEEL_FORWARD_AUTHORITY.md)

Change: `landing-transaction`

## Objective

Close the candidate-to-landed time-of-check/time-of-use gap with an explicit,
local Landing Transaction. A sealed candidate remains a proof of candidate
material only; landing requires a newly observed target base, an isolated
synthetic integration result, integration-specific evidence, compare-and-swap
protection, and independent landed-state confirmation.

## Scope and non-goals

- Preserve `CandidateAttestation` fields and existing candidate refs.
- Add a serializable `LandingAttestation` and transaction lifecycle APIs/CLI.
- Keep remote integration and effect execution out of scope.
- Accept merge/squash/rebase only through exact resulting-state equivalence.
- Report attestations only for properties established by evidence; never claim
  proof of behavioral correctness from a tree digest alone.

## Implementation sequence

1. Add tree-level synthetic integration and strategy-equivalence primitives.
2. Add integration EvidencePlan/receipt subject construction and validity checks.
3. Add LandingAttestation serialization, stale handling, compare-and-swap
   integration, and post-land verification.
4. Preserve seal/candidate-status/anchor compatibility while routing landed
   completion through the transaction evidence.
5. Add hostile tests for drift, conflict, evidence reuse, strategy drift, and
   mismatched landed trees; update durable documentation.

## Verification

Focused Git proof and lifecycle tests must cover every requirement in the
canonical intent. Run KEEL verify, inspect exact-subject receipts, commit the
verified tree, seal the candidate, and stop before external integration unless
an authorized local integration scenario is explicitly supplied.
