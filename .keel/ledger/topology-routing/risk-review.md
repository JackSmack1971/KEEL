# Risk review

The router is advisory and deterministic. It reads mission declarations only, emits capability labels rather than provider/model choices, and cannot launch agents, change permissions, alter ledgers, or skip required checks. Invalid mission input fails closed.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
