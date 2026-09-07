# Plan 003: Establish empirical evaluation, feedback promotion, and economics evidence

## Status

- **Finding ID**: TEST-001
- **Type**: corrective
- **Priority**: P1
- **Leverage**: 25.0
- **Effort**: L
- **Implementation risk**: MED
- **Depends on**: `plans/001-source-and-plan-reconciliation.md`, `plans/004-portability-and-mission-runtime.md`, `plans/002-intelligence-and-verification-depth.md`, `plans/005-api-and-authorized-integrations.md`
- **Planned at**: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
- **State**: TODO

## Outcome

KEEL can report reproducible no-skill versus KEEL results for an approved corpus, retain available timing/tool/retry/cost data with explicit missingness, and move reviewed observations through evaluation to separately authorized promotion.

## Evidence and current behavior

- `.keel/bench/README.md` and `.keel/bench/telemetry-schema.json` — harness/schema exist, but no empirical superiority result is present.
- `.keel/lib/feedback_entropy.py:68-96` — queue and target-plan projection exist; scheduling, target execution, and promotion do not.
- `.keel/lib/telemetry.py:27-31` — tokens, cost, human intervention, retries, and merge conflicts are `UNAVAILABLE` without instrumentation.

## Scope

**In scope**

- `.keel/bench/`
- `.keel/lib/feedback_entropy.py`
- `.keel/lib/telemetry.py`
- `.keel/config.json`
- `.keel/tests/test_feedback_entropy.py`
- `.keel/tests/test_telemetry.py`

## Stable requirements

| ID | Source evidence | Current state | Target invariant | Implementation surface | Verification | Dependencies |
|---|---|---|---|---|---|---|
| KEEL-EVAL-001 | `.keel/bench/README.md` | Harness exists; no paired result | Approved baseline/corpus produces reproducible trials | `.keel/bench/**` | repeated paired runs | KEEL-API-001 |
| KEEL-EVAL-002 | `.keel/lib/telemetry.py:27-31` | Runtime cost/retry/human metrics unavailable | Metrics are measured or explicitly unavailable | telemetry/runtime hooks | schema/completeness tests | KEEL-API-002 |
| KEEL-EVAL-003 | `.keel/lib/feedback_entropy.py:68-96` | Queue/target projection only | Reviewed observations flow to evaluation without auto-promotion | feedback contracts | promotion-boundary tests | KEEL-API-002 |
| KEEL-EVAL-004 | attachment recommendation | Evaluation has no adversarial penalty contract | Results penalize regressions, unauthorized effects, and scope violations | benchmark rubric | adversarial cases | KEEL-INTEL-003, KEEL-RUNTIME-004 |
| KEEL-EVAL-005 | requirement lifecycle contract | No benchmark maturity state is tracked separately | A requirement reaches `BENCHMARKED` only from reproducible improvement evidence | benchmark result/requirement record | lifecycle transition test and paired trial | KEEL-RECON-005, KEEL-API-002 |

## Lifecycle transition adversarial cases

| Transition | Attempted invalid operation | Required rejection evidence |
|---|---|---|
| `IMPLEMENTED → VERIFIED` | Submit a transition with no verification evidence, stale evidence, or a failed acceptance edge | Transition validator rejects it and leaves state `IMPLEMENTED` |
| `VERIFIED → BENCHMARKED` | Submit a benchmark label with no reproducible trial, mismatched requirement ID, or incomplete baseline | Transition validator rejects it and leaves state `VERIFIED` |
| `SUPERSEDED` | Submit supersession with neither `replaced_by` nor explicit rationale | Transition validator rejects it and leaves the prior state unchanged |

## Steps and gates

1. Obtain evaluation authority, define representative tasks, fixed rubric, equivalent starts, repetition count, and no-skill baseline.
2. Add deterministic trial lifecycle/telemetry records with provenance and explicit unavailable metrics.
3. Add queue eligibility, scheduler contract, target-evaluation result contract, and promotion handoff that requires a new KEEL change.
4. Run repeated paired trials and publish only bounded results with failure/recovery evidence.

**Verify**: corpus validation; repeated paired trial artifacts; schema validation; tests proving inspection never promotes or authorizes a change.

## STOP conditions

- No authorized corpus or evaluation authority.
- Runtime does not expose a metric; record `UNAVAILABLE` rather than fabricate it.
- A promotion path would mutate policy without a separate reviewed change.

## Rollback or containment

Keep trials and queue projections read-only; delete no evidence; disable scheduling if provenance or baseline equivalence cannot be established.

## Deferred work

Provider runtime instrumentation and external target execution remain blocked until Plan 004 establishes the runtime boundary.

## Assumptions

- [ASSUMPTION] Evaluation authority and corpus are selected before execution; this is an explicit prerequisite.

## Implementation constraints

- Preserve explicit `UNAVAILABLE` metrics.
- Promotion must create a separate authorized KEEL change.

## Steps

### Step 1: Establish the evaluation contract

Obtain authority and define corpus, rubric, equivalent starts, repetitions, and baseline.
**Verify**: corpus and rubric validation.
**Expected**: deterministic approved inputs exist.

### Step 2: Record trial telemetry

Add provenance-bearing trial records and explicit missingness.
**Verify**: bench schema and telemetry tests.
**Expected**: no fabricated metrics.

### Step 3: Complete feedback handoff contracts

Define queue, target result, and separate promotion change boundaries.
**Verify**: feedback tests.
**Expected**: inspection cannot promote.

## Test plan

- Validate corpus and telemetry schemas.
- Test reviewed/unreviewed, evaluated/unevaluated, and promoted/unpromoted observations.

## Verification matrix

| Gate | Command | Expected | Required |
|---|---|---|---|
| Bench | `python .keel/bin/keelbench.py validate` | exit 0 | yes |
| Feedback | `python -B .keel/tests/test_feedback_entropy.py` | exit 0 | yes |
| Telemetry | `python -B .keel/tests/test_telemetry.py` | exit 0 | yes |
| Trials | approved trial runner | reproducible artifacts | yes |
| Scope | `git diff --name-only` | only listed paths | yes |

## Done criteria

- [ ] Approved corpus and rubric are recorded.
- [ ] Repeated paired results are reproducible and bounded.
- [ ] Feedback promotion remains a separate authorized change.

## Review focus

Review baseline equivalence, metric provenance, statistical claims, and promotion isolation.

## Exact in-scope paths

- `.keel/bench/`
- `.keel/lib/feedback_entropy.py`
- `.keel/lib/telemetry.py`
- `.keel/config.json`
- `.keel/tests/test_feedback_entropy.py`
- `.keel/tests/test_telemetry.py`
