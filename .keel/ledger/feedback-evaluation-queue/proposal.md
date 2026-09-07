# Proposal

## Problem / why

Feedback observations can be validated individually but have no repository-local queue projection for evaluation and promotion readiness.

## Objective

Add a deterministic read-only queue over observation JSON files that preserves provenance and separates evaluation eligibility from promotion eligibility.

## Non-goals

No automatic promotion, policy edits, scheduling daemon, external ingestion, or target execution.

## Success evidence

Focused tests prove queue ordering, invalid-observation handling, eligibility boundaries, and read-only behavior; full KEEL verification passes.

## Open decisions

Observation directory is caller-provided; absent directories produce an empty queue.
