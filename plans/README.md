# KEEL upgrade audit plans

Generated from the current worktree at commit `4532bb43780cb45a025574403a8b4ae4ac7304ab` (2026-09-07). These are diagnosis and planning artifacts only; no implementation is authorized by this audit.

## Audit scope and baseline

- Compared the complete numbered brief in `docs/KEEL_UPGRADES.md` with executable `.keel` code, tests, configuration, control-plane docs, and active ExecPlans.
- Canonical checks: `python .keel/bin/keel.py doctor`, all direct `python -B` commands in `.keel/config.json`, KEELBench validation, and strict control-plane validation.
- All configured checks passed after removing only temporary `__pycache__` directories created by an exploratory pytest invocation. `python -m pytest` is not a valid suite runner here: it reports `no tests ran`.
- The user confirms the current working-tree `docs/KEEL_UPGRADES.md` is authoritative as of this audit. It is preserved unchanged and is the source for the matrix below.
- `docs/control-plane/UPGRADE_AUDIT.md` is incomplete as a source trace: it maps only sections 1–28, while the current brief has sections 1–70.

## Status matrix for sections 1–70

Status means executable evidence, not design intent.

| Sections | Current status | Planned treatment |
|---|---|---|
| 1–4 | Implemented foundation: ledger, candidate verification, scope, effects/authorization | Preserve; verify after source normalization |
| 5–10 | Partial-to-implemented: missions are read-only projections; repository map and context are bounded; typed evidence exists | Plan 002 for missing intelligence/verification depth |
| 11–13 | Partial: protocol routing and command discovery exist; adaptive workflow/domain intelligence are not a runtime | Plan 004 for runtime; Plan 003 for evaluation |
| 14–18 | Partial: local checks, migration primitives, compatibility inventory, capability resolver exist; portability/installer/external checks remain | Plan 001 and Plan 004 |
| 19–24 | Partial: topology, providers, typed assertions, and lifecycle projections exist; runtime routing/adapters/change-aware verification remain | Plan 004, Plan 002, Plan 005 |
| 25–30 | Partial or deferred: read-only UX exists, `run` and dashboard are absent, docs are oversized, framework/consumer separation is unresolved | Plan 001, Plan 004, Plan 005 |
| 31–36 | Harness/state primitives exist; empirical benchmark, adversarial/mutation/property tests, and formal lifecycle model are absent | Plan 003; Plan 002 for invariant tests |
| 37–40 | Partial effect vocabulary/inference and environment primitives; semantic tool inference, reproducibility proof, and attestation are absent | Plan 002 and Plan 004 |
| 41–44 | Partial repository discovery and feedback/entropy inspection; continuous refresh and evaluated self-improvement are absent | Plan 002 and Plan 003 |
| 45–51 | Mostly absent: policy compiler, invariant ownership, architecture dependency enforcement, impact/history learning, evidence-derived risk, and explicit uncertainty policy | Plan 002 |
| 52–57 | Partial reversible/worktree controls and ledger verification; experiment changes, semantic diff, oracle independence, verification-quality protection, and laundering detection are absent | Plan 002 |
| 58–61 | Partial JSON CLI and per-change event log; stable API contract, lifecycle event stream, and cross-tool correlation IDs are absent | Plan 005 |
| 62 | Explicitly deferred until stable orchestration API | Plan 005 only after Plans 004/002 |
| 63–70 | Positioning, competitor comparison, target architecture, roadmap, doctrine, and metric are strategy/context, not implemented runtime requirements | Keep as reviewed direction; no feature claim |

## Execution order

| Plan | Finding | Outcome | Priority | Effort | State |
|---|---|---|---|---|---|
| [001](001-source-and-plan-reconciliation.md) | DOC-001 | Truthful active/completed plan inventory against the authoritative upgrade brief | P0 | S | TODO |
| [004](004-portability-and-mission-runtime.md) | PORT-001 | Portable install/compatibility and authorized mission execution boundary | P1 | L | TODO |
| [002](002-intelligence-and-verification-depth.md) | ARCH-001 | Evidence-backed ownership, architecture/impact, effects, uncertainty, and verification-quality contracts | P1 | L | TODO |
| [005](005-api-and-authorized-integrations.md) | PROD-001 | Stable structured CLI/API and explicitly authorized tracker/PR/product-surface contracts | P2 | L | TODO |
| [003](003-evaluation-feedback-and-economics.md) | TEST-001 | Reproducible KEELBench/protocol/feedback evidence and available economics telemetry | P1 | L | TODO |

Plan 001 governs Plans 004, 002, 005, and 003. The implementation dependency order is `001 → 004 → 002 → 005 → 003`; instrumentation requirements are designed during the earlier plans and measured in 003.

## Mandatory requirement contract

Every downstream requirement has a stable ID (`KEEL-<AREA>-NNN`) and must declare: source evidence, current state, target invariant, implementation surface, verification, and dependencies. Plans must separate architecture changes from product/UX changes and state the concrete failure prevented by every mandatory control. Derived intelligence remains advisory; only policy authorizes. Mission orchestration uses ordinary Change ledgers as its atomic governed unit.

Requirement lifecycle is separate from implementation status:

```text
PROPOSED → RECONCILED → ACCEPTED → IMPLEMENTED → VERIFIED → BENCHMARKED
                                      └──────────────→ SUPERSEDED
```

Every requirement record must carry exactly one lifecycle state. `IMPLEMENTED` does not imply `VERIFIED`, and `VERIFIED` does not imply `BENCHMARKED`.

Core invariant:

```text
MISSION ORCHESTRATES
CHANGE GOVERNS
INTELLIGENCE ADVISES
POLICY AUTHORIZES
EVIDENCE PROVES
GIT IDENTIFIES THE MATERIAL STATE
```

The runtime plan must add a validator/test family proving that Mission operations cannot bypass scope or effects, grant authorization, fabricate evidence, weaken verification, seal unverified material, or substitute another Git state for the verified state.

## Rejected or contextual candidates

- Sections 63–70 are not independently missing features. They describe positioning, comparison, proposed architecture, sequencing, doctrine, or a metric; they remain direction/context until a separate product decision turns one into a contract.
- A dashboard is intentionally deferred by section 62 until the orchestration/state API is stable.
- External Codex checks, tracker/PR adapters, runtime browser/log/metric/trace/device providers, and empirical trials are planned as deferred prerequisites, not falsely marked incomplete local code that can be safely implemented without their authority.

## Stale-plan mitigation policy

After each implementation change, compare its acceptance evidence to every `docs/exec-plans/active/*.md` plan. Move only fully satisfied plans to `docs/exec-plans/completed/`; mark plans superseded when their scope is replaced; split remaining work into a new plan when only a slice landed. Preserve old plan text and commit history. Do not leave an implementation-complete plan in `active/` merely because it is useful history.
