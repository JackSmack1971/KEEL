# Historical KEEL audit plans

This directory is a historical evidence index, not an active planning surface.
The five numbered audit plans formerly stored here were superseded and moved
to [`docs/exec-plans/completed/`](../docs/exec-plans/completed/). Their original
reasoning, dates, findings, and obsolete instructions are retained there for
provenance, but none of their TODOs, steps, dependencies, or ordering authorizes
current work.

Current KEEL upgrade authority is deliberately centralized:

- Sole authoritative requirement/status matrix:
  [`docs/control-plane/UPGRADE_AUDIT.md`](../docs/control-plane/UPGRADE_AUDIT.md)
- Sole authoritative top-level upgrade roadmap:
  [`docs/exec-plans/active/upgrade-remaining-plan.md`](../docs/exec-plans/active/upgrade-remaining-plan.md)

The roadmap's P0–P7 dependency graph is the only current upgrade ordering. P0
is not instantiated here; P4 remains blocked; D1 remains deferred. No
benchmark, corpus, paired-trial, scoring, promotion, or telemetry experiment
is activated by this historical corpus.

`findings.json` is retained as historical audit output. It records observations
and fix sketches only; it is not a requirements ledger, authorization record,
or execution plan.
