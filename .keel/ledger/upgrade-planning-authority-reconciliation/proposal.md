# Proposal

## Problem

KEEL upgrade planning is represented by multiple active-looking ExecPlans, while the upgrade audit does not consistently distinguish executable requirements from contextual strategy. This creates competing planning authority and leaves benchmark/evaluation work insufficiently separated from the corrected P0–P7 roadmap.

## Objective

Repair the preceding readiness-gate defects in the upgrade audit and roadmap contract: partition every relevant `docs/KEEL_UPGRADES.md` section exactly once, explicitly classify reconciliation and mutation testing, and require complete future ExecPlan evidence fields before P0 can be instantiated.

## Non-goals

- No runtime, framework, hook, policy, test, CLI, configuration, or product implementation.
- No benchmark execution, corpus work, scoring, paired trials, or empirical promotion.
- No deletion of historical evidence.

## Success evidence

- `docs/control-plane/UPGRADE_AUDIT.md` contains the authoritative once-only requirement matrix and corrected classifications.
- `docs/exec-plans/active/upgrade-remaining-plan.md` is the sole active top-level roadmap and contains P0–P7 plus deferred D1 with the reviewed dependencies and safety contract.
- Completed historical plans and competing top-level plans are archived/closed/superseded under the repository convention and no longer appear as active authority.
- Cross-references identify the audit and roadmap as authoritative and do not make archived or deferred plans active.
- Repository-native verification confirms only documentation/planning files changed and the stated reconciliation properties hold.
