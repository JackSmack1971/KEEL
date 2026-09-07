# Ownership source discovery

Parse only standard repository-owned CODEOWNERS locations for literal rules. If none exists, emit an explicit `UNAVAILABLE` analyzer status. Do not infer or assign owners.

Verification: repository-map tests, strict control-plane validation, and full KEEL verification.
