# KEEL Parallelism and Worktrees

## Write invariant
**One change-id, one worktree, one primary write owner.** Never run multiple write-heavy agents against the same working tree.

Parallelize across independent changes by creating independent Git/Codex worktrees. Keep each change's `.keel/ledger/<id>/` on its branch/worktree. After Verify reaches SHIP, commit and `keel.py seal` the exact candidate; the shared Git ref `refs/keel/candidates/<id>` is the integration handoff. Merge/squash/rebase remains repository policy, but final `anchor` must prove the landed tree is content-equivalent to the sealed candidate for every verified path and intent artifact.

Codex-managed worktrees commonly begin detached at the selected starting commit. That is compatible with KEEL: the candidate ref is independent of whether the worktree later receives a branch. Do not rely on the same branch being checked out in multiple worktrees; Git intentionally prevents that.

## Read-heavy fan-out
Parallel subagents are appropriate for bounded read-only exploration, review, test/log triage, documentation verification, or independent per-item analysis. Require distilled outputs and an explicit stopping/output contract.

## Cross-cutting changes
For repeated changes across many files:
1. create one parent KEEL change with the behavioral delta;
2. inventory rows (path/owner/risk/dependency) into `batch-plan.csv`;
3. if a runtime batch-agent facility exists, use it for read-only per-row analysis or give every writing row an isolated worktree/branch;
4. never treat an undocumented/experimental tool as a hard dependency;
5. consolidate result rows into `batch-results.csv` and verify aggregate completeness plus regression checks.

If edits are tightly coupled or likely to conflict, one sequential primary writer is safer than artificial parallelism.
