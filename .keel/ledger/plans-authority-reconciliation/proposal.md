# Proposal

## Problem / why

The legacy top-level `plans/` corpus contains useful audit reasoning but still
looks like an executable upgrade program: it has TODO states, a cross-plan
ordering, a P0 reconciliation plan, and deferred benchmark work. That creates
competing planning authority with the current control-plane matrix and
roadmap.

## Objective

Preserve the five legacy plan documents as historical evidence in the
repository's completed-plan archive, and make the remaining `plans/` index and
findings explicitly historical and non-authoritative. Redirect current humans
and agents to `docs/control-plane/UPGRADE_AUDIT.md` and
`docs/exec-plans/active/upgrade-remaining-plan.md`.

## Non-goals

Do not instantiate or implement P0; do not modify runtime/framework code,
tests, hooks, configuration, benchmark implementation, or the authoritative
audit/roadmap; do not activate D1 or change P4's blocked status.

## Success evidence

- Every legacy plan is archived without loss of content or provenance.
- `/plans` contains no current execution order or actionable TODO authority.
- Archived plans explicitly state that their instructions are historical and
  superseded, including the stale sections-1–28 claim.
- Benchmark/evaluation material is historical/deferred only.
- Strict control-plane validation, KEEL doctor, scope verification, and
  targeted negative authority searches pass.

## Open decisions

None: `docs/exec-plans/completed/` is the established repository archive for
completed planning evidence.
