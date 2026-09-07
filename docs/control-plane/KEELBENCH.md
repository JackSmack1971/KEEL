# KEELBench

KEELBench exists to answer the question the control plane cannot answer by inspection: **does KEEL materially outperform the same agent without KEEL?**

The shipped benchmark contract lives under `.keel/bench/` and includes:

- 12 representative engineering scenario archetypes;
- a telemetry/event schema;
- deterministic paired-trial manifests and run-record templates;
- deterministic corpus validation and scoring utilities.

Run:

```text
python3 .keel/bin/keelbench.py validate
python3 .keel/bin/keelbench.py new-trial --scenario KB-01-bugfix --replicates 3 --seed <seed> --start-state-id <id> --start-state-digest <digest> --out <trial-dir>
python3 .keel/bin/keelbench.py validate-trial <trial-dir>
python3 .keel/bin/keelbench.py score <trial-dir>
```

Required metrics cover task success, acceptance coverage, regressions, scope/authorization violations, human intervention, tokens, wall time, tool/command use, retries, merge conflicts, CI failures, and review findings.

Each trial requires one baseline and one KEEL run per replicate, with identical scenario, rubric, seed, and starting-state identity. Validation rejects missing, duplicate, incomplete, or mismatched records. Scoring reports paired deltas and aggregate condition summaries while retaining `empirical_claim: UNVALIDATED`. Deterministic KEEL self-tests validate mechanisms; they **do not** satisfy G5 empirical value. G5 requires repeated representative paired execution from equivalent starting states with a rubric fixed before outcomes.
