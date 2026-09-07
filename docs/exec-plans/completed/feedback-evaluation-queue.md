# Feedback evaluation queue

Add a read-only queue projection over repository-local observation JSON files. It classifies invalid, evaluation-eligible, promotion-eligible, and already-promoted observations in deterministic order.

Non-goals: automatic promotion, external ingestion, scheduling, or target execution.

Verification: focused feedback tests, strict control-plane validation, and full KEEL verification.
