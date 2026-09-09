# KEELBench (optional)

KEELBench is optional evaluation tooling, not part of the portable `.keel`
runtime or its mandatory verification path. It measures whether a KEEL-governed
workflow produces materially better outcomes than a comparable baseline. This
repository contains no authority-approved corpus or empirical superiority result.

Use `new-trial` to create a deterministic manifest. The caller must provide a
stable starting-state identifier and digest plus environment and stack metadata;
every replicate then receives exactly one baseline and one KEEL run with matching
scenario, rubric, seed, starting-state, and environment metadata.

Commands:

```text
python3 keelbench/keelbench.py validate
python3 keelbench/keelbench.py new-trial --scenario KB-01-bugfix --replicates 3 --seed run-1 --start-state-id commit-abc --start-state-digest sha256:... --environment-id env-1 --environment-digest sha256:... --stack-id python --out runs/trial-01
python3 keelbench/keelbench.py validate-trial runs/trial-01
python3 keelbench/keelbench.py score runs/trial-01
```

Incomplete, duplicated, or mismatched trials fail closed before paired scoring.
Legacy loose run fixtures remain readable for compatibility but are marked
`legacy_unpaired`. Scores always retain `empirical_claim:
BLOCKED_UNVALIDATED` until representative repeated baseline-vs-KEEL runs,
approved evaluation authority, and a predeclared material-value threshold exist.

