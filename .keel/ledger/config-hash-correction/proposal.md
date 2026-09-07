# Proposal

## Problem / why
The bootstrap manifest must record the current hash of the canonical KEEL configuration.

## Objective
Update the manifest entry for `.keel/config.json` to its current repository hash.

## Non-goals
No runtime behavior, project policy, or external integration changes.

## Success evidence
Strict control-plane validation and `keel.py doctor` pass with no manifest drift.

## Open decisions
None.
