# Risk review

This is control-plane work. The implementation is intentionally read-only at runtime: reconciliation and compatibility inspection report discrepancies but do not repair ledger state, run external providers, or change authorization. Source classification is conservative and only informs inspection. Existing scope, phase, authorization, verification, seal, and anchor controls remain authoritative.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
