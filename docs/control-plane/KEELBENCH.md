# KEELBench

KEELBench exists to answer the question the control plane cannot answer by inspection: **does KEEL materially outperform the same agent without KEEL?**

The optional first-party package lives under `keelbench/` and includes:

- 12 representative engineering scenario archetypes;
- a telemetry/event schema;
- deterministic paired-trial manifests and run-record templates;
- deterministic corpus validation and scoring utilities.

Run:

```text
python3 keelbench/keelbench.py validate
python3 keelbench/keelbench.py new-trial --scenario KB-01-bugfix --replicates 3 --seed <seed> --start-state-id <id> --start-state-digest <digest> --environment-id <id> --environment-digest <digest> --stack-id <stack> --out <trial-dir>
python3 keelbench/keelbench.py validate-trial <trial-dir>
python3 keelbench/keelbench.py score <trial-dir>
```

Required metrics cover autonomous task completion, acceptance and requirement
outcomes, escaped defects, unauthorized-effect attempts and executions, false
governance blocks, recovery, integration regressions, attestation reproducibility,
human interventions, wall-clock time, observable token/tool/cost usage, context
volume, and cross-stack portability.

For ordinary lifecycle changes, `keel telemetry --change <change-id>` exposes the subset measurable from `verification.json` and marks runtime-dependent metrics unavailable. It is not a substitute for paired KEELBench trials.

Each trial requires one baseline and one KEEL run per replicate, with identical
scenario, rubric, seed, starting-state, environment, and stack metadata.
Validation rejects missing, duplicate, incomplete, or mismatched records before
scoring. Scoring reports paired deltas and aggregate condition summaries while
retaining `empirical_claim: BLOCKED_UNVALIDATED`. Deterministic KEEL self-tests
validate mechanisms; they do **not** satisfy empirical value. KEEL's superiority
remains a hypothesis until approved representative repeated paired execution
from equivalent starting states demonstrates material value.
