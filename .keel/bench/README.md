# KEELBench

KEELBench is the repository-local evaluation contract for testing whether KEEL materially improves engineering outcomes over a no-KEEL baseline. It is not a claim of superiority.

Use `new-trial` to create a deterministic manifest. The caller must provide a stable starting-state identifier and digest; every replicate then receives exactly one baseline and one KEEL run with matching scenario, rubric, seed, and starting-state metadata. Run adapters complete the generated JSON records without changing the manifest.

Commands:

```text
python3 .keel/bin/keelbench.py validate
python3 .keel/bin/keelbench.py new-trial --scenario KB-01-bugfix --replicates 3 --seed run-1 --start-state-id commit-abc --start-state-digest sha256:... --out .keel/bench/runs/trial-01
python3 .keel/bin/keelbench.py validate-trial .keel/bench/runs/trial-01
python3 .keel/bin/keelbench.py score .keel/bench/runs/trial-01
```

Incomplete, duplicated, or mismatched trials fail closed before paired scoring. Legacy loose run fixtures remain readable for compatibility but are marked `legacy_unpaired` and `empirical_claim: UNVALIDATED`. Do not claim G5 empirical value until representative repeated baseline-vs-KEEL runs meet the project's predeclared material-value threshold.
