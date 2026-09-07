# KEELBench

KEELBench exists to answer the question the control plane cannot answer by inspection: **does KEEL materially outperform the same agent without KEEL?**

The shipped benchmark contract lives under `.keel/bench/` and includes:

- 12 representative engineering scenario archetypes;
- a telemetry/event schema;
- paired-run result templates;
- deterministic corpus validation and scoring utilities.

Run:

```text
python3 .keel/bin/keelbench.py validate
python3 .keel/bin/keelbench.py new-run --scenario KB-01-bugfix --condition baseline --out <path>
python3 .keel/bin/keelbench.py new-run --scenario KB-01-bugfix --condition keel --out <path>
python3 .keel/bin/keelbench.py score <results>
```

Required metrics cover task success, acceptance coverage, regressions, scope/authorization violations, human intervention, tokens, wall time, tool/command use, retries, merge conflicts, CI failures, and review findings.

Deterministic KEEL self-tests validate mechanisms. They **do not** satisfy G5 empirical value. G5 requires repeated representative paired execution from equivalent starting states with a rubric fixed before outcomes.
