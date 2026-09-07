# Risk review

The mapper is derived and conservative. It reads paths and selected text metadata, never executes project commands, follows symlinks only as file entries, ignores configured vendor/build directories, and does not activate capabilities or rewrite authoritative docs. A write mode may only emit the fixed `.keel/knowledge/repository-map.json` artifact; stdout remains available for read-only inspection.

Not required for ordinary standard/trivial changes. Required before plan gate for high/control-plane/security/privacy/migration/release/high-blast-radius changes.
