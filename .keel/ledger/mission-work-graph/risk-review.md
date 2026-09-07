# Risk review

This is control-plane work. The mission planner only reads a supplied contract, Git-backed child ledgers, and dependency metadata. It never mutates mission files, creates worktrees, transitions a change, runs commands from mission data, or authorizes effects. DAG validation rejects ambiguity and cycles before any frontier is reported.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
