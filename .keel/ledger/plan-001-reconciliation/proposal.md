# Proposal: Reconcile upgrade traceability and plan lifecycle state

## Problem

The current upgrade audit maps only the first 28 numbered recommendations, while the authoritative brief contains 70 numbered sections. Active execution plans also do not distinguish completed slices from genuinely resumable work.

## Objective

Extend the audit to sections 1–70, classify contextual sections without inventing runtime requirements, and make active/completed plan state explicit while preserving plan history.

## Non-goals

- Do not edit the authoritative upgrade brief.
- Do not change `.keel/**` or implement runtime features.
- Do not claim Plan 004 runtime behavior is implemented.

## Success evidence

- A source-section matrix covers sections 1–70 exactly once.
- Active and completed plan indexes state lifecycle semantics and retain historical artifacts.
- No implementation-complete plan remains active without an explicit partial boundary.
- `git diff --check`, strict control-plane validation, and configured checks pass.

## Unresolved decisions

- Plans whose remaining work is explicitly prerequisite-dependent remain active as partial handoffs; completed slices move to the completed index.
