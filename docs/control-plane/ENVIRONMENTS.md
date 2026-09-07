# Environments and Worktrees

Status: `CONDITIONAL`.

When Git and a runtime/toolchain exist:
- make setup reproducible from documented commands;
- isolate concurrent agent work with worktrees or an equivalent workspace mechanism;
- prefer per-worktree bootable runtime instances when a running system exists;
- isolate ports, temp directories, caches, databases, logs and observability state as necessary;
- document ignored-but-required local files and a safe worktree transfer mechanism if needed;
- never assume a branch can be checked out in multiple worktrees simultaneously.

Record platform-specific deviations rather than hiding them in shell history.
