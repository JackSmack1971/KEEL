# Plan 002: Close repository-intelligence and verification-quality gaps

> HISTORICAL / SUPERSEDED. Preserved for audit provenance only; its TODOs,
> steps, gates, and implementation scope do not authorize current work and do
> not supplement the active P0–P7 roadmap. Current authority is only
> `docs/control-plane/UPGRADE_AUDIT.md` and
> `docs/exec-plans/active/upgrade-remaining-plan.md`.

## Status

- **Finding ID**: ARCH-001
- **Type**: corrective
- **Priority**: P1
- **Leverage**: 40.0
- **Effort**: L
- **Implementation risk**: HIGH
- **Historical dependencies**: `docs/exec-plans/completed/legacy-plan-001-source-and-plan-reconciliation.md`, `docs/exec-plans/completed/legacy-plan-004-portability-and-mission-runtime.md`
- **Planned at**: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
- **State**: TODO

## Outcome

KEEL can report provenance-backed ownership and bounded architecture/impact relations, express uncertainty and typed assertions, and detect verification-quality risks without turning advisory analysis into permission.

## Evidence and current behavior

- `.keel/lib/repository_map.py:59-77` — only literal CODEOWNERS discovery exists; no ownership policy or architecture relation source.
- `.keel/lib/effect_inference.py:7-37` — argv-only advisory inference.
- `.keel/lib/evidence_graph.py:9-140` — provider vocabulary and path matching exist; semantic diff, oracle independence, and laundering controls are absent.
- `.keel/lib/mission_graph.py:105-114` — dispatch is contract projection only.

## Scope

**In scope**

- `.keel/lib/repository_map.py`
- `.keel/lib/evidence_graph.py`
- `.keel/lib/effect_inference.py`
- `.keel/lib/keel_core.py`
- `.keel/bin/keel.py`
- `.keel/tests/`
- `.keel/contracts.json`

## Stable requirements

| ID | Source evidence | Current state | Target invariant | Implementation surface | Verification | Dependencies |
|---|---|---|---|---|---|---|
| KEEL-INTEL-001 | `.keel/lib/repository_map.py:59-77` | CODEOWNERS-only discovery | Ownership/architecture facts are provenance-backed and conflict-aware | repository map | source fixtures | KEEL-RECON-002, KEEL-RUNTIME-001 |
| KEEL-INTEL-002 | `.keel/lib/repository_map.py`, `.keel/lib/topology_router.py` | Bounded map/routing | Impact and uncertainty remain advisory and explicit | map/router | impact fixtures | KEEL-RUNTIME-003 |
| KEEL-INTEL-003 | `.keel/lib/evidence_graph.py:9-140` | Typed providers/path matching | Evidence assertions are typed, change-aware, and oracle-independent | evidence graph | positive/negative evidence tests | KEEL-RUNTIME-004 |
| KEEL-INTEL-004 | `.keel/lib/effect_inference.py:7-37` | argv-only advisory inference | Tool semantics remain advisory; policy alone authorizes | effect/provider contracts | unknown-provider tests | KEEL-INTEL-001 |

## Steps and gates

1. Define explicit repository-owned sources for ownership and architecture relations; emit `UNAVAILABLE`/`CONFLICT` with provenance rather than infer authority.
2. Add bounded dependency/impact facts and explicit uncertainty/risk inputs; preserve advisory status.
3. Add typed evidence assertions, semantic-diff classification, scope-laundering detection, and independent-oracle requirements where executor and verifier overlap.
4. Extend effect analysis behind provider contracts for tool semantics; never grant authorization from inference.
5. Add contract tests for missing, conflicting, stale, and positive evidence.

**Verify**: all configured direct tests; strict control-plane validation; fixtures proving no advisory result authorizes an effect and no unavailable provider is reported as verified.

## STOP conditions

- A source of ownership or architecture authority is not explicitly approved.
- A proposed semantic adapter needs external credentials/provider behavior not present in the repository.
- The change would make advisory discovery mutate ledger state or grant permission.

## Rollback or containment

Keep new analyzers read-only and feature-gated by explicit contracts; revert the change if any existing verification path changes pass/fail semantics without an acceptance contract.

## Deferred work

Mission execution, provider runtime adapters, and external integrations remain in Plans 004–005.

## Assumptions

- [ASSUMPTION] New analyzers remain read-only and repository-local until a separate effects contract exists.

## Implementation constraints

- Preserve advisory versus authorization boundaries.
- Unknown or conflicting sources remain explicit.

## Steps

### Step 1: Define trusted source contracts

Add ownership/architecture source schemas and provenance states.

**Verify**: `python -B .keel/tests/test_repository_map.py`
**Expected**: missing/conflicting sources are explicit and non-authorizing.

### Step 2: Add bounded impact and uncertainty

Compute only source-backed dependency, impact, and risk facts.

**Verify**: repository-map and routing tests.
**Expected**: no inferred authority from filenames alone.

### Step 3: Strengthen evidence quality

Add typed assertions, semantic diff, laundering, and independent-oracle contracts.

**Verify**: evidence and effect tests.
**Expected**: invalid or non-independent evidence cannot satisfy acceptance.

## Test plan

- Cover missing, conflicting, stale, positive, and scope-laundering fixtures.
- Run all configured direct test commands.

## Verification matrix

| Gate | Command | Expected | Required |
|---|---|---|---|
| Map | `python -B .keel/tests/test_repository_map.py` | exit 0 | yes |
| Evidence | `python -B .keel/tests/test_evidence_graph.py` | exit 0 | yes |
| Effects | `python -B .keel/tests/test_effect_inference.py` | exit 0 | yes |
| Full | configured direct checks | all exit 0 | yes |
| Scope | `git diff --name-only` | only listed paths | yes |

## Done criteria

- [ ] Every new fact has provenance and explicit unknown/conflict handling.
- [ ] Verification-quality controls have positive and negative tests.
- [ ] Advisory analyzers cannot authorize effects.

## Review focus

Review trust boundaries, false-positive authority, oracle independence, and scope enforcement.

## Exact in-scope paths

- `.keel/lib/repository_map.py`
- `.keel/lib/evidence_graph.py`
- `.keel/lib/effect_inference.py`
- `.keel/lib/keel_core.py`
- `.keel/bin/keel.py`
- `.keel/tests/`
- `.keel/contracts.json`
