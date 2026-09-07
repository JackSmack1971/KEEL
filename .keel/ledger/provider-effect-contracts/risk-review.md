# Risk review

This changes contract validation at a safety boundary. Unknown evidence providers and effect capabilities fail closed. A supported non-command provider is only evidence when its declared `check_id` maps to a configured verification check that exits zero; no provider is executed implicitly. External/irreversible effects continue to require explicit authorization, and capability declarations do not grant permission.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
