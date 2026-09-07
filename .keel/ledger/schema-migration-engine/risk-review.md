# Risk review

Migration writes are limited to an explicit caller-provided artifact path and backup directory. The control-plane CLI remains inspection-only; live repository migration requires a separate authorized KEEL change. Tests verify atomic replacement, backup restoration, unsupported-version rejection, and no mutation during preflight.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
