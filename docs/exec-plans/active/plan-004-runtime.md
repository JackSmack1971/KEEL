# Plan 004: Define portable installation and authorized mission execution

## Status

- **Finding ID**: PORT-001
- **Type**: corrective
- **Priority**: P1
- **Leverage**: 20.0
- **Effort**: L
- **Implementation risk**: HIGH
- **Depends on**: `plans/001-source-and-plan-reconciliation.md`
- **Planned at**: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
- **State**: TODO

## Outcome

KEEL has a supported install/version/upgrade contract, runtime capability handshake, reproducible environment/candidate metadata, and an isolated mission runner whose retries, verification, sealing, and integration boundaries are explicit and authorization-aware. A mechanical validator/test family prevents Mission from crossing the Change governance boundary.

## Evidence and current behavior

- `.keel/bin/keel.py:29-57` — mission dispatch exists but `run` is absent.
- `.keel/lib/mission_graph.py:105-114` — dispatch returns advisory contracts only.
- `.keel/lib/lifecycle.py:39` — Codex version and hooks are `UNVERIFIED`.
- `.keel/lib/schema_migrations.py:30-70` — local preflight/apply/rollback exists; installer/live orchestration does not.

## Scope

**In scope**

- `.keel/bin/keel.py`
- `.keel/lib/mission_graph.py`
- `.keel/lib/lifecycle.py`
- `.keel/lib/schema_migrations.py`
- `.keel/tests/`
- `docs/control-plane/RELEASE_OPERATIONS.md`

## Steps and gates

1. Specify supported framework/config/contract versions, package layout, install/upgrade/rollback behavior, and external Codex compatibility probes.
2. Define runtime capability handshake and reproducible environment/candidate manifest; fail closed on unknown capabilities.
3. Implement dry-run mission scheduling over isolated worktrees, then bounded execution/retry/review/seal handoffs.
4. Add explicit integration authorization and mission-level verification without bypassing per-change ledgers.

**Verify**: clean extracted-package install; legacy migration fixtures and rollback; isolated dry-run; injected failure/retry test; no unauthorized integration; full configured checks.

## STOP conditions

- Supported provider/runtime versions, credentials, or operator authorization are unspecified.
- Execution would require broad filesystem/network effects outside the declared contract.
- A retry or integration operation cannot be proven idempotent and recoverable.

## Rollback or containment

Default to dry-run and isolated worktrees. Use migration backups and candidate refs; never auto-integrate or mutate external systems without recorded authorization.

## Deferred work

Browser/log/metric/trace/device adapters and tracker/PR integrations require this runtime contract and remain in Plan 005.

## Assumptions

- [ASSUMPTION] Supported provider/runtime versions and operator authority are selected before implementation.

## Implementation constraints

- Default to dry-run and isolated worktrees.
- Do not bypass per-change ledgers or external authorization.

## Steps

### Step 1: Specify portability contracts

Define supported versions, package layout, install/upgrade/rollback, and compatibility probes.
**Verify**: extracted-package and legacy fixture checks.
**Expected**: clean install and reversible migration.

### Step 2: Define runtime handshake

Record capabilities and reproducible environment/candidate metadata; fail closed on unknowns.
**Verify**: compatibility tests.
**Expected**: unknown runtime is not treated as active.

### Step 3: Add isolated mission execution

Implement dry-run scheduling, retry, review, and seal handoffs over worktrees.
**Verify**: injected-failure and isolation tests.
**Expected**: retry is bounded/idempotent and no integration occurs.

### Step 4: Add the Mission/Change boundary validator family

Test Mission scheduling, observation, and integration against explicit negative cases: scope bypass, effects bypass, authorization grant, fabricated evidence, weakened verification, sealing unverified material, and substitution of a different Git state for the verified state.

**Verify**: dedicated boundary validator/tests plus all existing ledger, scope, effects, evidence, seal, and anchor tests.
**Expected**: every prohibited operation is rejected or remains impossible through the Mission surface.

## Test plan

- Test extracted-package install, migration/rollback fixtures, unknown capabilities, dry-run isolation, failure recovery, unauthorized integration, and all seven adversarial boundary fixtures.

## Verification matrix

| Gate | Command | Expected | Required |
|---|---|---|---|
| Migration | `python -B .keel/tests/test_schema_migrations.py` | exit 0 | yes |
| Mission | `python -B .keel/tests/test_mission_work_graph.py` | exit 0 | yes |
| Compat | `python -B .keel/tests/test_lifecycle_compatibility.py` | exit 0 | yes |
| Boundary | dedicated Mission/Change boundary tests | all prohibited operations rejected | yes |
| Full | configured direct checks | all exit 0 | yes |
| Scope | `git diff --name-only` | only listed paths | yes |

## Done criteria

- [ ] Install and migration are reproducible and reversible.
- [ ] Mission dry-run and failure recovery are isolated and tested.
- [ ] Integration requires explicit authorization and evidence.
- [ ] Mission boundary tests reject all seven prohibited behaviors.

## Review focus

Review effects, isolation, retry idempotency, migration rollback, and candidate/landed provenance.

## Exact in-scope paths

- `.keel/bin/keel.py`
- `.keel/lib/mission_graph.py`
- `.keel/lib/lifecycle.py`
- `.keel/lib/schema_migrations.py`
- `.keel/tests/test_mission_work_graph.py`
- `.keel/tests/test_lifecycle_compatibility.py`
- `.keel/tests/test_schema_migrations.py`

## Stable requirements

| ID | Source evidence | Current state | Target invariant | Implementation surface | Verification | Dependencies |
|---|---|---|---|---|---|---|
| KEEL-RUNTIME-001 | `.keel/lib/lifecycle.py:39` | External runtime is UNVERIFIED | Supported runtime capability handshake fails closed | `.keel/lib/lifecycle.py`, config | compatibility fixtures | KEEL-RECON-001 |
| KEEL-RUNTIME-002 | `.keel/lib/schema_migrations.py:30-70` | Local migration primitives only | Install/upgrade/rollback works from clean extraction | packaging, migration code | extracted-package and rollback tests | KEEL-RECON-002 |
| KEEL-RUNTIME-003 | `.keel/lib/mission_graph.py:105-114` | Dispatch is advisory | Mission schedules isolated Change ledgers with bounded retry | mission runtime/worktrees | dry-run and injected-failure tests | KEEL-RUNTIME-001 |
| KEEL-RUNTIME-004 | `WORKFLOW.md` | Change-level governance exists | Mission never bypasses Change verify/seal/anchor | mission integration boundary | unauthorized-integration test | KEEL-RUNTIME-003 |
| KEEL-BOUNDARY-001 | `docs/KEEL_UPGRADES.md` Mission/runtime sections | No mechanical Mission boundary family exists | Mission may schedule, observe, and integrate only verified Changes | mission dispatcher, ledger, hooks | boundary test family | KEEL-RUNTIME-003 |
| KEEL-BOUNDARY-002 | scope enforcement in `.keel/lib/keel_core.py` | Scope is enforced per Change | Mission cannot bypass scope | mission-to-change call path | scope-bypass negative test | KEEL-BOUNDARY-001 |
| KEEL-BOUNDARY-003 | effects/authorization in `.keel/lib/keel_core.py` | Authorization is Change-owned | Mission cannot bypass effects or grant authorization | effects/auth paths | effects/auth negative tests | KEEL-BOUNDARY-001 |
| KEEL-BOUNDARY-004 | evidence graph and verification in `.keel/lib/evidence_graph.py` | Evidence is recorded by verification | Mission cannot fabricate evidence or weaken verification | evidence/verify paths | forged/omitted evidence tests | KEEL-BOUNDARY-001 |
| KEEL-BOUNDARY-005 | seal/anchor in `.keel/lib/keel_core.py` | Seal binds verified material | Mission cannot seal unverified material | seal candidate path | unverified-seal rejection test | KEEL-BOUNDARY-004 |
| KEEL-BOUNDARY-006 | tree digest/seal in `.keel/lib/keel_core.py` | Git identifies verified material | Mission cannot substitute another Git state | candidate/anchor paths | tree-substitution negative test | KEEL-BOUNDARY-005 |
| KEEL-BOUNDARY-007 | `WORKFLOW.md` | Mission is orchestration, not policy | Every prohibited operation has a stable negative test | boundary test family | full boundary suite | KEEL-BOUNDARY-002, KEEL-BOUNDARY-003, KEEL-BOUNDARY-004, KEEL-BOUNDARY-005, KEEL-BOUNDARY-006 |

## Adversarial boundary fixtures

Each boundary requirement must include an attempted-bypass fixture. A positive validator alone is insufficient.

| ID | Attempted bypass fixture | Required result |
|---|---|---|
| `KEEL-BOUNDARY-001` | Mission dispatches a child Change through a path that omits the Change ledger | Dispatch is rejected; no child work begins outside a Change |
| `KEEL-BOUNDARY-002` | Mission asks a child operation to write outside its declared scope | Scope guard rejects the operation and records no authorized material change |
| `KEEL-BOUNDARY-003` | Mission manufactures or edits an authorization record, or requests an undeclared effect | Authorization/effects guard rejects it; no permission is granted |
| `KEEL-BOUNDARY-004` | Mission injects a fabricated evidence edge or suppresses a failed verification result | Evidence graph/verification rejects the transition |
| `KEEL-BOUNDARY-005` | Mission attempts to seal a child whose verification material no longer matches the current tree | Seal rejects the child and creates no candidate ref |
| `KEEL-BOUNDARY-006` | Mission substitutes another SHA after verification or presents a different tree as the verified state | Candidate/anchor digest comparison rejects the substitution |
| `KEEL-BOUNDARY-007` | Mission invokes each prohibited behavior through an alternate dispatch/API path | All seven rejection cases remain enforced at the boundary, not only in the primary CLI |

The fixtures must assert both the rejection and the unchanged durable state: no authorization, evidence, seal, candidate, anchor, or out-of-scope write is created.
