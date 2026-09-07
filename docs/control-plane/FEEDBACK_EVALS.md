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

## KEELBench baseline gate

The repository ships a benchmark contract under `.keel/bench/`. Use paired repeated runs from equivalent starting states to measure task success, acceptance coverage, regressions, scope/authorization violations, human intervention and execution cost. Deterministic KEEL self-tests demonstrate mechanism behavior only; G5 empirical value remains unvalidated until KEELBench or an equivalent representative baseline comparison demonstrates material uplift. See [KEELBENCH.md](KEELBENCH.md).
