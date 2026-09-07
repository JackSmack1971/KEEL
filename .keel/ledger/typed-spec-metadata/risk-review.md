# Risk review

This is a contract-validation change with backward-compatible optional fields. Invalid metadata fails closed; no paths are inferred or written, and existing ledgers without the fields remain valid.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
