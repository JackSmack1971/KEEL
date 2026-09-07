# Risk review

Lifecycle inspection is read-only and fail-closed. It reads repository-owned metadata and ledger state JSON, never executes upgrade code, downloads dependencies, changes schemas, or treats a reported external Codex version as verified. Migration output is a plan requiring a separate authorized implementation.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
