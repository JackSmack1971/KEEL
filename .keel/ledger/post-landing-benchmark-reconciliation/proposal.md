# Proposal

## Problem / why
Post-landing validation identified two compatibility gaps: the validator expects the existing relative-error-reduction benchmark marker, and bootstrap provenance must be refreshed for the intentionally changed KEELBench files.

## Objective
Restore the benchmark compatibility marker and update generated-file provenance hashes without changing the paired-trial contract.

## Non-goals
No new benchmark behavior, external effects, empirical claim, or runtime policy change.

## Success evidence
Strict control-plane validation passes with zero findings; KEELBench tests and corpus validation pass; the corrected tree is sealed and anchored.

## Open decisions
None.
