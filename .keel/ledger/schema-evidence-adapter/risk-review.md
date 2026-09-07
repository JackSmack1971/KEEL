# Risk review

The adapter reads only repository-contained JSON and performs no execution or external access. It validates a narrow declared contract and fails closed on malformed or out-of-root paths.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
