# Proposal

## Problem / why

The repository map classifies paths but cannot show semantic relationships between source modules.

## Objective

Add deterministic Python AST import facts with source provenance to `keel map` output.

## Non-goals

No dynamic import execution, ownership inference, unsupported-language parser, or architecture judgment.

## Success evidence

Focused map tests prove deterministic local-import extraction, unresolved/external classification, provenance, and read-only build behavior; full configured verification remains green.

## Open decisions

Unsupported languages remain reported through an explicit analyzer-status field rather than inferred.
