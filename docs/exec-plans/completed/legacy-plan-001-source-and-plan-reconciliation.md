# Plan 001: Reconcile stale active plans against the authoritative upgrade brief

> HISTORICAL / SUPERSEDED. This document preserves the 2026-09-07 audit-era
> reasoning and is not current execution authority. Its P0 TODO, steps, gates,
> and requirements are retired. The old claim that `UPGRADE_AUDIT.md` stopped
> at sections 1–28 is superseded: the authoritative matrix now covers sections
> 1–70. Current authority is only `docs/control-plane/UPGRADE_AUDIT.md` and
> `docs/exec-plans/active/upgrade-remaining-plan.md`.

> Follow this plan in order. This is a documentation/control-plane reconciliation change; do not implement runtime features in the same change.

## Status

- **Finding ID**: DOC-001
- **Type**: corrective
- **Priority**: P0
- **Leverage**: 100.0
- **Effort**: S
- **Implementation risk**: LOW
- **Depends on**: none
- **Planned at**: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
- **State**: TODO

This is the governing plan for Plans 004, 002, 005, and 003.

## Outcome

The confirmed authoritative upgrade brief remains unchanged, its 1–70 sections have a durable status matrix, and active ExecPlans describe only unsatisfied work. Completed history remains recoverable.

## Evidence and current behavior

- `docs/KEEL_UPGRADES.md:1-5920` — user-confirmed authoritative upgrade brief for this audit.
- `docs/control-plane/UPGRADE_AUDIT.md:1-45` — historical snapshot claimed traceability stopped at sections 1–28; that claim is obsolete because the current authoritative matrix covers sections 1–70.
- `docs/exec-plans/active/` — multiple plan files remain active while recent commits indicate slices have landed; plan files lack a uniform lifecycle state.
- `git status --short` — the upgrade brief is user-modified and must remain untouched.

## Scope

**In scope**

- `docs/KEEL_UPGRADES.md`
- `docs/control-plane/UPGRADE_AUDIT.md`
- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `docs/exec-plans/README.md`

**Out of scope**: `.keel/**`, runtime features, external integrations, and rewriting the user’s uncommitted brief without first reconciling its two copies.

## Steps

### Step 1: Reconcile the upgrade brief

Treat the confirmed current brief as authoritative; do not rewrite or normalize its content.

**Verify**: `git status --short -- docs/KEEL_UPGRADES.md`
**Expected**: the document remains unchanged by reconciliation.

### Step 2: Complete source traceability

Extend `UPGRADE_AUDIT.md` to cover sections 1–70, distinguishing strategy/context from executable requirements.

**Verify**: section-count check.
**Expected**: every section has exactly one status and workstream.

### Step 3: Reconcile active plans

Compare active plans with anchored commits and tests; move, supersede, or split them without deleting history.

**Verify**: `rg -n "State:|Status:|SUPERSEDED|DONE|TODO" docs/exec-plans`
**Expected**: no completed implementation remains only in `active/`.

### Step 4: Update navigation

Make active, completed, superseded, and deferred state unambiguous.

**Verify**: strict control-plane validation.
**Expected**: exit 0.

**Verify**: `git diff --check`; strict control-plane validation; a script or table proving every section 1–70 has exactly one status and workstream.

## Done criteria

- [ ] The authoritative upgrade brief remains unchanged.
- [ ] Sections 1–70 are each classified with evidence or explicitly labeled strategy/context.
- [ ] No implementation-complete plan remains in `active/`.
- [ ] No stale plan is deleted; history is preserved in `completed/` or superseded records.

## STOP conditions

- The user changes the authoritative brief while reconciliation is in progress.
- A plan’s acceptance state cannot be proven from an anchored commit or deterministic test.
- Any unrelated user change would be overwritten.

## Rollback or containment

Use Git revert or restore the moved plan file from `completed/`; do not delete plan history.

## Deferred work

All runtime and empirical work is deferred to Plans 002–005.

## Assumptions

- [ASSUMPTION] The current upgrade brief is user-confirmed authoritative input and is not edited by this plan.

## Implementation constraints

- Preserve unique requirements and completed-plan history.
- Do not change `.keel/**` or implement runtime features.

## Test plan

- Run `git diff --check` and strict control-plane validation.
- Prove every section 1–70 appears exactly once in the status matrix.

## Verification matrix

| Gate | Command | Expected | Required |
|---|---|---|---|
| Formatting | `git diff --check` | exit 0 | yes |
| Traceability | section-count check | sections 1–70 mapped once | yes |
| Lifecycle | lifecycle transition tests | invalid transitions rejected; evidence required | yes |
| Control plane | strict validator | exit 0 | yes |
| Scope | `git diff --name-only` | only listed paths | yes |

## Review focus

Check for lost requirements, false completion claims, stale plan ownership, and accidental overwrite of user changes.

## Exact in-scope paths

- `docs/KEEL_UPGRADES.md`
- `docs/control-plane/UPGRADE_AUDIT.md`
- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `docs/exec-plans/README.md`

## Stable requirements

| ID | Source evidence | Current state | Target invariant | Implementation surface | Verification | Dependencies |
|---|---|---|---|---|---|---|
| KEEL-RECON-001 | `docs/KEEL_UPGRADES.md:1-5920` | User-confirmed authoritative brief | Downstream work references one unchanged source | `docs/KEEL_UPGRADES.md` | status/diff check | none |
| KEEL-RECON-002 | `docs/control-plane/UPGRADE_AUDIT.md:1-45` | Historical snapshot incorrectly said trace stopped at section 28 | Current authoritative matrix covers sections 1–70 exactly once | `docs/control-plane/UPGRADE_AUDIT.md` | section-count check | KEEL-RECON-001 |
| KEEL-RECON-003 | `docs/exec-plans/active/` | Lifecycle state is inconsistent | Active contains only unsatisfied work | `docs/exec-plans/**` | anchored commit review | KEEL-RECON-002 |
| KEEL-RECON-004 | attachment recommendation | Downstream plans lack shared IDs | Every requirement has the mandatory evidence/invariant contract | `plans/**` | plan validator and review | KEEL-RECON-002 |
| KEEL-RECON-005 | attachment requirement lifecycle | Implementation status is currently conflated with evidence maturity | Every requirement has exactly one lifecycle state from PROPOSED through SUPERSEDED | requirement records and plan metadata | schema/transition tests | KEEL-RECON-004 |

## Requirement lifecycle transitions

| State | Entry evidence | Exit condition |
|---|---|---|
| `PROPOSED` | Upgrade brief or approved direction | Source and current implementation are reconciled |
| `RECONCILED` | Evidence/current-state record | Human/operator acceptance recorded |
| `ACCEPTED` | Stable requirement and target invariant | Implementation changes land in declared surface |
| `IMPLEMENTED` | Material change exists | Required verification passes |
| `VERIFIED` | Acceptance/evidence graph passes | Approved reproducible benchmark result exists, if applicable |
| `BENCHMARKED` | Reproducible benchmark evidence tied to the requirement | Requirement is replaced or remains current |
| `SUPERSEDED` | Explicit replacement reference or rationale | Terminal state |

Lifecycle transitions are themselves validated. A transition record must name the requirement, prior state, next state, evidence IDs, and (for `SUPERSEDED`) either `replaced_by` or an explicit rationale. `IMPLEMENTED → VERIFIED` is invalid without verification evidence; `VERIFIED → BENCHMARKED` is invalid without reproducible benchmark evidence; `SUPERSEDED` is invalid without replacement/rationale evidence.
