# KEEL upgrade audit and runtime kernel

## Objective

Reconcile `docs/KEEL_UPGRADES.md` with executable repository evidence and implement a bounded first slice of the missing framework primitives.

## Order

1. Add read-only reconciliation and compatibility/version inspection.
2. Add provider-neutral evidence and effect capability contracts.
3. Replace source-extension-only decisions with explicit/detected/generic/unknown classification.
4. Add focused tests and update control-plane documentation.
5. Run the configured KEEL verification graph; do not activate policies or external integrations from detection alone.

## Safety boundaries

This slice does not mutate ledger state during inspection, execute evidence providers, authorize effects, schedule agents, create missions, or infer project policy. Later roadmap items remain explicitly deferred until their own change contracts exist.

## Verification

Focused kernel tests, `keel.py doctor`, strict control-plane validation, and KEELBench validation are required. The upgrade brief remains an input artifact and is not silently rewritten.
