# Proposal

## Problem / why

Evidence contracts permit schema providers but currently require an external command for every schema claim.

## Objective

Add a repository-local JSON schema evidence adapter for path containment, parseability, schema version, and required keys.

## Non-goals

No general JSON Schema implementation, external provider access, or claims about runtime schemas.

## Success evidence

Focused provider tests prove valid/invalid local schema evidence and path-boundary rejection.

## Open decisions

Broader schema dialect support requires a separate dependency and contract decision.
