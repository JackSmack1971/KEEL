# Proposal

## Problem / why
Repository intelligence is currently a small derived map, evidence is mostly exit-code based, and effect inference is limited to argv pattern matching. That leaves dependency/impact uncertainty, verification quality, and proof-mechanism changes under-specified.

## Objective
Implement Plan 002 in bounded repository-local slices: establish provenance-bearing intelligence facts, advisory impact and uncertainty reporting, typed evidence assertions, semantic diff and oracle-integrity warnings, and provider-aware effect analysis without granting authorization.

## Non-goals
Mission scheduling/execution, external provider adapters, external integrations, automatic policy changes, and any path by which derived intelligence can authorize effects.

## Success evidence
Focused positive and negative tests prove missing/conflicting/stale intelligence remains explicit, typed assertions are evaluated rather than treated as exit-code aliases, proof-mechanism changes require independent verification, semantic high-consequence changes are classified, and advisory results never authorize an effect. The full configured verification set must pass.

## Open decisions
The repository-owned source formats for architecture relations and semantic verification metadata must remain minimal and explicit; unsupported formats must report uncertainty rather than being guessed.
