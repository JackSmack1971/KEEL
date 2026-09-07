# Repository semantic map

## Objective

Extend the derived repository map with deterministic, provenance-bearing Python import relationships.

## Scope

- Parse Python source with the standard-library `ast` module only.
- Record local, external, unresolved, and parse-error outcomes.
- Preserve existing path classifications and read-only behavior.
- Update tests, command documentation, audit status, and manifest hashes.

## Non-goals

Dynamic execution, package installation, ownership inference, architecture conclusions, and parsers for languages not supported by the first slice.

## Verification

Focused map tests, strict control-plane validation, and the full configured KEEL verification.
