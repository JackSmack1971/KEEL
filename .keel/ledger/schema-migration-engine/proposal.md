# Proposal

## Problem / why

Lifecycle compatibility can identify stale schemas but has no versioned repository-owned migration or rollback engine.

## Objective

Implement a conservative migration registry with preflight, atomic writes, backup creation, and rollback for supported fixtures.

## Non-goals

No automatic live-repository migration, installer, external Codex update, or bypass of KEEL authorization.

## Success evidence

Focused tests migrate a legacy config fixture, verify the backup and digest, roll it back exactly, reject unsupported versions, and prove live files are untouched by planning.

## Open decisions

Additional schema transitions require explicit migration functions and fixtures.
