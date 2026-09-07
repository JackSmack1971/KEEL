# Plan 005: Stabilize the CLI/API before external integrations and product surfaces

> HISTORICAL / SUPERSEDED. Preserved for audit provenance only; its TODOs,
> steps, gates, and prior sequencing/dependency language do not authorize
> implementation or external integration. Current authority is only
> `docs/control-plane/UPGRADE_AUDIT.md` and
> `docs/exec-plans/active/upgrade-remaining-plan.md`.

## Status

- **Finding ID**: PROD-001
- **Type**: direction-spike
- **Priority**: P2
- **Leverage**: not ranked as a defect
- **Effort**: L
- **Implementation risk**: HIGH
- **Historical dependencies**: `docs/exec-plans/completed/legacy-plan-001-source-and-plan-reconciliation.md`, `docs/exec-plans/completed/legacy-plan-004-portability-and-mission-runtime.md`, `docs/exec-plans/completed/legacy-plan-002-intelligence-and-verification-depth.md`
- **Planned at**: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
- **State**: TODO

## Outcome

KEEL has a versioned structured CLI/API contract, correlation identifiers across mission/change/run/operation/evidence, and separately authorized tracker/PR and provider adapters. A dashboard is considered only after these contracts are stable.

## Evidence and current behavior

- `.keel/bin/keel.py:22-57` — JSON command surfaces exist, but no versioned API contract, `run`, correlation IDs, or tracker adapter.
- `.keel/lib/keel_core.py:110-118` — lifecycle events are ledger-local; no cross-tool event/correlation model.
- `docs/control-plane/UPGRADE_AUDIT.md:35-45` — tracker/PR integration is deferred for missing authorization/runtime prerequisites.
- `docs/KEEL_UPGRADES.md:2211-2235` — dashboard is explicitly deferred until an orchestration API exists.

## Scope

**In scope**

- `.keel/bin/keel.py`
- `.keel/lib/keel_core.py`
- `.keel/lib/evidence_graph.py`
- `.keel/tests/`

## Stable requirements

| ID | Source evidence | Current state | Target invariant | Implementation surface | Verification | Dependencies |
|---|---|---|---|---|---|---|
| KEEL-API-001 | `.keel/bin/keel.py:22-57` | JSON commands lack versioned API contract | Runtime output is stable and machine-readable | CLI schemas | compatibility fixtures | KEEL-RUNTIME-003 |
| KEEL-API-002 | `.keel/lib/keel_core.py:110-118` | Events are ledger-local | Mission/change/run/operation/evidence IDs correlate across tools | lifecycle event model | replay/correlation tests | KEEL-RUNTIME-003 |
| KEEL-API-003 | `.keel/lib/evidence_graph.py:9-140` | Provider vocabulary exists without live adapters | Provider effects/auth/redaction are explicit | adapter contracts | mock/sandbox tests | KEEL-INTEL-004 |
| KEEL-API-004 | `docs/KEEL_UPGRADES.md:2211-2235` | Dashboard intentionally deferred | Product UI cannot bypass stable API/evidence policy | decision record only | architecture review | KEEL-API-001, KEEL-API-002 |

No live external mutation is in scope.

## Steps and gates

1. Define stable JSON schemas, exit/error semantics, compatibility policy, and IDs: mission, change, run, operation, evidence.
2. Emit and validate append-only lifecycle events across CLI/runtime boundaries.
3. Define browser/log/metric/trace/device and tracker/PR provider contracts with effects, authorization, redaction, and sandbox tests.
4. Reassess dashboard value against the stable API; do not build it solely from current internal Python structures.

**Verify**: schema fixtures; replay/correlation tests; redaction tests; mock provider contract tests; explicitly authorized sandbox operation only after a separate effects contract.

## STOP conditions

- External identity, credentials, API policy, or sandbox is not authorized.
- The API contract depends on unresolved runtime semantics from Plan 004.
- A dashboard would expose unstable internal state or bypass existing authorization/evidence rules.

## Rollback or containment

Keep adapters behind disabled-by-default contracts and use mock/sandbox providers; no live write adapter is enabled by this plan.

## Deferred work

Product positioning and the VEY metric remain strategy until empirical evidence from Plan 003 exists.

## Assumptions

- [TODO] External identities, credentials, API policies, and sandbox providers must be authorized before adapter execution.

## Implementation constraints

- Keep adapters disabled by default and provider-neutral.
- Preserve redaction, effects, authorization, and evidence boundaries.

## Steps

### Step 1: Define the stable API

Specify JSON schemas, errors, compatibility, and mission/change/run/operation/evidence IDs.
**Verify**: schema fixtures and compatibility tests.
**Expected**: stable versioned output.

### Step 2: Add lifecycle correlation

Emit and validate append-only cross-tool events.
**Verify**: replay and correlation tests.
**Expected**: provenance survives process boundaries.

### Step 3: Define provider contracts

Specify provider effects, authorization, redaction, and sandbox behavior.
**Verify**: mock provider tests.
**Expected**: live writes remain disabled.

## Test plan

- Test schema compatibility, event replay, correlation propagation, redaction, and mock provider contracts.

## Verification matrix

| Gate | Command | Expected | Required |
|---|---|---|---|
| CLI | direct CLI contract tests | exit 0 | yes |
| Events | event/correlation tests | exit 0 | yes |
| Providers | mock adapter tests | exit 0 | yes |
| External | authorized sandbox only | no unauthorized writes | yes |
| Scope | `git diff --name-only` | only listed paths | yes |

## Done criteria

- [ ] CLI/API schemas and compatibility are tested.
- [ ] Correlation IDs and replay evidence cross lifecycle boundaries.
- [ ] Provider contracts pass redaction and authorization tests.

## Review focus

Review API stability, redaction, effect declarations, cross-process provenance, and authorization boundaries.

## Exact in-scope paths

- `.keel/bin/keel.py`
- `.keel/lib/keel_core.py`
- `.keel/lib/evidence_graph.py`
- `.keel/tests/`
