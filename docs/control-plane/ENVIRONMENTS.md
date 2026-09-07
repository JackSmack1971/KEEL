# Environments and Worktrees

Status: `CONDITIONAL`.

KEEL may declare an optional `environment_contract` in `.keel/config.json`:

```json
{
  "environment_contract": {
    "schema_version": 1,
    "setup": ["tool", "setup"],
    "start": ["tool", "start"],
    "stop": ["tool", "stop"],
    "isolation": {
      "ports": "per-worktree",
      "database": "per-worktree"
    }
  }
}
```

Inspect it with `python3 .keel/bin/keel.py environment status`. This command is read-only: it validates and reports the contract but never executes its commands. Missing contracts remain `UNCONFIGURED`; KEEL does not infer setup, ports, databases, or service behavior.

When Git and a runtime/toolchain exist:
- make setup reproducible from documented commands;
- isolate concurrent agent work with worktrees or an equivalent workspace mechanism;
- prefer per-worktree bootable runtime instances when a running system exists;
- isolate ports, temp directories, caches, databases, logs and observability state as necessary;
- document ignored-but-required local files and a safe worktree transfer mechanism if needed;
- never assume a branch can be checked out in multiple worktrees simultaneously.

Record platform-specific deviations rather than hiding them in shell history.
