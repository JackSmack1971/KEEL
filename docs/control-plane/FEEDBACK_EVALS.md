# Production Feedback and Self-Improvement

Status: `DEFERRED` until real repeated production/field evidence exists.

Do not turn every correction into an autonomous code change.

Activation loop:
1. capture expert/user correction plus system proposal and final ground truth;
2. preserve full provenance/trace through intermediate transformations;
3. group related failures and separate systemic patterns from expected noise;
4. promote only reviewed, repeated patterns into bounded eval targets;
5. create a writable task worktree plus read-only evidence context;
6. investigate root cause, implement targeted fix, run target and broad regression evals;
7. route ambiguous/unsafe cases back to human/domain judgment.

A self-improvement loop must improve measurable outcomes, not merely produce more activity.

The repository provides conservative local inspection:

```text
python3 .keel/maintenance/keel_maintenance.py feedback validate <observation.json>
python3 .keel/maintenance/keel_maintenance.py feedback status <observation.json>
python3 .keel/maintenance/keel_maintenance.py feedback queue <observation-directory>
python3 .keel/maintenance/keel_maintenance.py entropy
```

These optional maintenance commands are read-only and outside the kernel/runtime path. An observation must retain provenance, repository-contained evidence, review state, and a failure class. Promotion to a permanent invariant requires a separate evaluated and authorized KEEL change; inspection never promotes or rewrites policy.

`feedback queue` deterministically reports evaluation and promotion candidates, target plans, and blocked observations; it does not schedule, evaluate, or promote them. Target plans retain evidence inputs and explicitly require deferred execution or an authorized KEEL change.

Entropy scanning treats an explicitly headed `# Long-horizon goal:` record as a durable goal plan rather than an orphaned execution plan. Ordinary active plans still require a matching KEEL ledger.

## KEELBench baseline gate

The repository ships optional first-party KEELBench tooling under `keelbench/`.
Use paired repeated runs from equivalent starting states to measure autonomous
completion, requirements, defects, authorization outcomes, interventions,
recovery, regressions, reproducibility, time, observable usage, context, and
portability. Deterministic KEEL self-tests demonstrate mechanism behavior only;
KEEL's superiority remains a hypothesis and empirical claims are blocked until
approved representative repeated trials demonstrate material value. See
[KEELBENCH.md](KEELBENCH.md).
