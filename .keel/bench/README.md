# KEELBench

KEELBench is the repository-local evaluation contract for testing whether KEEL materially improves engineering outcomes over a no-KEEL baseline. It is not a claim of superiority.

Use paired runs from equivalent starting states and a rubric fixed before execution. Repeat stochastic scenarios. Record success, acceptance coverage, regressions, scope/authorization violations, human interventions, tokens, time, tool/command counts, retries, conflicts, CI failures, and review findings.

Commands:

```text
python3 .keel/bin/keelbench.py validate
python3 .keel/bin/keelbench.py new-run --scenario KB-01-bugfix --condition baseline --out .keel/bench/runs/baseline-01.json
python3 .keel/bin/keelbench.py score <result-dir-or-json> [...]
```

Do not claim G5 empirical value until representative repeated baseline-vs-KEEL runs meet the project's predeclared material-value threshold.
