# ExecPlan: Canonical ChangeGraph planning model

Status: `ACTIVE`
Authority: `KEEL-KERNEL-REDESIGN-v1`, stages `M2 — Read compatibility` and bounded `M3 — Canonical kernel`

## Objective and success evidence
Replace mission-specific planning authority with one deterministic ChangeGraph
of canonical semantic records. Focused hostile tests, legacy equivalence tests,
CLI contract tests, and the complete KEEL verification suite must pass.

## Non-goals
No scheduling, dispatch, agent/persona selection, effect execution, grant
issuance, runtime observation, lifecycle-ledger migration, or compatibility
retirement.

## Verified context
M1 landed the canonical primitive contracts in `semantic_kernel.py`. Mission v1
stores dependencies on work nodes; mission v2 stores them both on nodes and in
a top-level array and embeds authorization/runtime/planning fields. Both current
CLI routes interpret those legacy structures directly.

## Assumptions to test
- A ChangeGraph envelope can compose existing strict primitive records without
  adding a second record schema or dependency representation.
- Legacy omissions can be represented as explicit uncertainty in provenance and
  requirement statements rather than optimistic defaults.
- Frontier readiness can use only hard edges plus caller-supplied completion.

## Risk / autonomy / permission boundaries
High control-plane and migration risk. All operations are pure reads or local,
reversible repository writes. Planning may request effects but cannot grant or
execute them. Resource overlap is reported, not scheduled or invalidated. No
external or irreversible effect is authorized.

## Milestones
### M1 — Canonical graph
- Action: implement the graph envelope, validation, canonical serialization,
  edge-only dependency policy, resource claims, and read-only frontier.
- Observation: malformed graph forms fail deterministically and equal graphs
  serialize byte-identically.
- Verification: `change-graph-tests`.
- Exit criteria: every requested invariant has a hostile test.

### M2 — Compatibility readers
- Action: replace direct v1/v2 planning with explicit adapters that emit the
  canonical graph and provenance-linked uncertainty.
- Observation: minimal legacy fixtures normalize deterministically without
  grants, runtime facts, scheduler state, personas, or lifecycle state.
- Verification: compatibility suites plus canonical validation.
- Exit criteria: old supported inputs remain readable only through adapters.

### M3 — Stable interface and governance evidence
- Action: route stable CLI commands to the graph API, retain the needed v2 alias,
  update durable docs/check registration, and regenerate declared provenance.
- Observation: no normal CLI dispatch or mission-v2-specific planning concept.
- Verification: full `keel verify`, independent review, exact commit seal.
- Exit criteria: verified committed tree is sealed, integrated only if authorized,
  anchored after landing, and handed off through the requested pull request.

## Baseline
Base `de7e4b0b84a2275c55b4946434b47bc6cfdf4a68`; clean branch `work`. Focused
semantic, mission-v2, mission-v1, and doctor checks passed before the change.

## Progress log
- 2026-09-08: established baseline, started standard change, passed Discuss.
- 2026-09-08: focused tests exposed the legacy topology route's direct mission
  interpretation and persona/scheduler projection; re-planned its conversion to
  a constraint-only canonical graph projection rather than preserving a second
  planning authority.

## Decision log
- Reuse canonical semantic primitive decoders; keep ChangeGraph as their sole
  planning aggregate rather than introducing mission-specific record classes.
- Preserve legacy source documents in adapter provenance/uncertainty rather than
  projecting their embedded authorization or runtime state as facts.

## Failure branches / blockers
Any semantic loss, invented certainty, second dependency authority, unstable
bytes, dispatch exposure, legacy-read regression, out-of-scope diff, or missing
acceptance evidence blocks completion and requires re-plan where appropriate.

## Final verification
Run focused suites, full KEEL verification, scope/diff inspection, independent
review, commit, seal, authorized integration if available, landed anchor, and PR.

## Completion / handoff
Move this plan to completed only in a separately scoped follow-up if required;
this change preserves it as resumable migration evidence.
