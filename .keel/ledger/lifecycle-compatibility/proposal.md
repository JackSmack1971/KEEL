# Proposal

## Problem / why
`keel version` reports only a basic config/contract compatibility result; the upgrade brief calls for lifecycle awareness across Codex configuration, skills, KEEL schemas, ledgers, and bootstrap provenance.

## Objective
Add a read-only compatibility inventory and migration plan that identifies supported versions, unsupported/stale artifacts, and required operator-visible actions without rewriting repository state.

## Non-goals
No network installer, remote upgrade, automatic schema rewrite, rollback of user data, Codex version claim without evidence, or external integration.

## Success evidence
Focused tests cover compatible and stale ledger/skill/manifest cases, deterministic migration plans, and read-only behavior. Existing full validation passes.

## Open decisions
Actual schema migrations require separate versioned migration implementations and explicit change contracts; this slice detects and plans them.
