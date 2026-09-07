# Proposal

## Problem / why

Lifecycle verification records command durations and exit codes but has no stable read-only economics/telemetry projection.

## Objective

Expose measured verification counts, wall time, failures, and explicitly unavailable runtime metrics.

## Non-goals

No token/cost invention, external telemetry ingestion, model selection, or instrumentation of unavailable runtimes.

## Success evidence

Focused tests prove aggregation, missing-metric representation, malformed input handling, and read-only behavior.

## Open decisions

Runtime token/cost sources remain provider-specific.
