# Risk review

This change only inspects repository-owned configuration and returns advisory findings. It never executes inferred commands, changes authorization, or treats inference as proof of an external effect. Unknown and ambiguous tokens remain unclassified. Tests cover recognized capability mappings, unknown-command neutrality, deterministic output, and unchanged input state; strict control-plane validation and full KEEL verification are required before sealing.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
