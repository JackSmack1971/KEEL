# Proposal

## Problem / why

Typed implementation paths are validated syntactically but are not connected to the material diff during evidence evaluation.

## Objective

Require declared implementation surfaces to match changed paths for required acceptance criteria.

## Non-goals

No path inference, automatic scope expansion, or requirement that documentation-only criteria declare source paths.

## Success evidence

Evidence tests prove surface match passes and mismatch fails while legacy contracts remain valid.

## Open decisions

Globs remain repository-relative and use existing path matching semantics.
