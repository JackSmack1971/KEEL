# Requirement and receipt evidence

Canonical `intent.json` contains both `REQ-*` Requirements and corresponding
EvidenceRequirements. `.keel/lib/evidence_system.py` derives an EvidencePlan from
impact and declared verifiers, then records immutable-content, exact-subject receipts
under the kernel-owned `receipts/` directory. Generated views are navigation only.

A required acceptance property passes only when its declared provider/check receipts
match the current subject, intent digest, and verifier declaration. Missing,
unsupported, malformed, stale, or unrelated evidence does not pass. Editing intent
invalidates previous coverage and requires replanning.
