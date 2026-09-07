# Risk review

Dispatch output is advisory data only. It cannot create worktrees, start agents, change ledgers, retry failures, or integrate changes. Tests verify deterministic ordering and unchanged mission input.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
