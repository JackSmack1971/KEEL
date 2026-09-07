# Proposal

## Problem / why
KEEL documents a conservative learning loop and entropy policy, but has no machine-readable reviewed observation contract or deterministic scan to surface repository decay.

## Objective
Add validation/listing for reviewed feedback observations and a read-only entropy scan for broken internal links, orphaned active plans, and stale derived map artifacts.

## Non-goals
No automatic instruction promotion, code edits, scheduling, external telemetry ingestion, arbitrary shell execution, or deletion of artifacts.

## Success evidence
Focused tests prove provenance and review-state validation, promotion remains gated, entropy findings are deterministic, and the full control-plane graph passes.

## Open decisions
Promotion and remediation remain separate KEEL changes after human review and target evaluation evidence.
