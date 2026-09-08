## ADDED
- A versioned CandidateAttestation payload binds candidate/work identity, Git identities, intent/material/EvidencePlan digests, EvidenceReceipt identities and digests, and available policy/runtime profile digests.
- Deterministic Git-proof and attestation modules expose explicit interfaces and focused regression coverage.

## MODIFIED
- The generated bootstrap manifest records the updated verifier registry through its declared producer.
- Candidate sealing and landed anchoring delegate exact-Git proof and anchor behavior out of the lifecycle core while preserving CLI, ref, note, collision, and content-equivalence semantics.
- Durable architecture and lifecycle documentation identify attestation payloads as authority artifacts and refs/notes as mutable indexes/anchors.

## REMOVED
- Monolithic ownership of candidate/landing Git-proof calculations in keel_core.py.
