# Risk review

All new commands are read-only. `ship` is an eligibility projection only and cannot seal, anchor, merge, push, release, or authorize. `review` reads current ledger/evidence files and `init --check` reports readiness without installing or rewriting anything.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
