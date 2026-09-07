# Risk review

The loop is fail-closed and non-destructive. Feedback validation requires source/evidence and an explicit reviewed state before a candidate invariant is considered eligible, but never promotes it. Entropy scanning reports findings only; it does not repair, delete, execute project commands, or treat generated views as authority.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
