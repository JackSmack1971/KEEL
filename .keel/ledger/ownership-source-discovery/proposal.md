# Proposal

## Problem / why

Repository mapping has no ownership signal and must not invent one from path names.

## Objective

Discover standard CODEOWNERS locations and include parsed ownership rules or an explicit unavailable status in the derived map.

## Non-goals

No owner inference, identity validation, architecture judgment, or creation of a CODEOWNERS policy.

## Success evidence

Tests prove deterministic parsing, source provenance, unavailable behavior, and unchanged repository state.

## Open decisions

The repository must provide the authoritative CODEOWNERS file; this slice does not choose owners.
