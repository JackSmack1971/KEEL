# Canonical commands

Run commands from the repository root with `python3 .keel/bin/keel.py`.

## Lifecycle

- `start`, `gate discuss`, `gate plan`, `replan`, `reopen`
- `status`, `next`, `context`, `evidence`
- `verify`, `seal`, `candidate-status`, `anchor`
- `worktree create|status|retire`, `environment status`

These commands query or transition the canonical ledger. `verify` writes exact-subject
receipts. `seal` binds the committed candidate; `anchor` independently checks the
landed tree. SHIP eligibility is not external permission.

## Canonical model queries

- `change-graph validate|frontier|status|normalize|serialize <path> [--state <path>]`
- `facts` — serialize the read-only canonical FactGraph.
- `discover` — evidence-backed capability candidates.
- `effects`, `telemetry` — read-only boundary/evidence queries.

There are no mission, mission-v2, topology route, repository-map, or developer-UX
aliases. Historical compatibility applies only to ledgers.

## Compatibility and distribution

- `ledger migrate|project|validate --change <id> [--output <dir>]`
- `compat`, `version`, `contracts`, `reconcile [--change <id>]`
- `bootstrap status [--requires-git]`
- `manifest [--write]`
- `doctor`

`manifest --write` is the sole producer for `.keel/bootstrap-manifest.json`; plain
`manifest` verifies deterministic freshness. `ledger migrate` is additive and uses the
versioned `keel.legacy-ledger/v1` reader. It never deletes historical input or creates
missing authority.

Optional gardening is intentionally separate: run
`python3 .keel/maintenance/keel_maintenance.py --help`.
