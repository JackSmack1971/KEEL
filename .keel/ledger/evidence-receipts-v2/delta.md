## ADDED
- Canonical verifier registry contracts, evidence requirements, deterministic evidence plans, authority ordering, and exact-subject evidence receipts.
- Hostile tests for authority confusion, unrelated PASS results, drift, duplicates, inapplicability, and insufficient coverage.

## MODIFIED
- `keel verify` selects a minimal sufficient set of applicable verifiers plus a small self-integrity kernel, executes the plan, and derives authority from receipts.
- Legacy verification/evidence files become compatibility projections over receipt authority.
- Verification documentation and active configuration describe registry/planner/receipt semantics.

## REMOVED
- Duplicate active checks and the historical SHA-pinned remediation diff command.
- The flat run-every-command behavior as normal verification authority.
