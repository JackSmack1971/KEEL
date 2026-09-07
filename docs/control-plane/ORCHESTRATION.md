# Orchestration

Status: `DEFERRED` until issue tracker, unattended runtime, demand, and trust/workspace policy exist.

KEEL is **not** the ticket scheduler. It is the per-change execution/governance contract that a future Symphony-style scheduler dispatches into isolated workspaces. The repository now also provides a read-only mission DAG/frontier planner; this is planning evidence, not unattended orchestration.

Mission contracts use `python3 .keel/bin/keel.py mission validate|frontier|status <mission.json>`. They preserve one normal KEEL change per work item and never mutate child ledgers.

When orchestration activates, preserve:
1. each task/change-id gets an isolated persistent workspace/worktree;
2. one primary write owner per worktree;
3. agent cwd equals assigned workspace;
4. normalized workspace path is a strict child of the configured root;
5. untrusted task IDs become sanitized collision-safe workspace/change keys;
6. blocker-aware deterministic dispatch and reconciliation prevent duplicate/obsolete work;
7. stalls and hard failures have distinct retry paths; safe persistent state survives retry;
8. bounded concurrency is explicit;
9. scheduler primarily reads tracker state; task-side writes follow the repository `WORKFLOW.md` and authorization contract;
10. the scheduler may dispatch read-only investigation that never opens a KEEL write change;
11. a write ticket creates/resumes a KEEL ledger and cannot report completed merely because the agent stopped;
12. successful work may stop at review/handoff rather than merge/deploy.

Do not build a second orchestration daemon merely to reproduce Codex-native subagents/worktrees. Use external scheduling only when ticket-driven unattended dispatch is actually needed.
