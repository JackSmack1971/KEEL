# Change separate-keelbench

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Separate KEELBench from the mandatory portable KEEL runtime and redesign it as an optional first-party empirical evaluation package

## Requirements
- `REQ-KB-001` KEELBench is an optional first-party empirical evaluation package outside the mandatory portable .keel runtime, and the core installation/manifest/runtime verification path does not require it.
- `REQ-KB-002` The evaluation contract represents autonomous completion, interventions, requirements satisfied or missed, escaped defects, unauthorized-effect attempts and executions, false governance blocks, injected-failure recovery, integration regressions, attestation reproducibility, wall-clock time, observable token/tool/cost usage, context volume, and cross-stack portability.
- `REQ-KB-003` Paired trials preserve equivalent starting state, task/scenario, rubric, seed/environment metadata, and repeated baseline/KEEL trials, with comparisons limited to reproducible conditions.
- `REQ-KB-004` Deterministic KEEL mechanism tests remain separate from empirical evaluation evidence, and missing evaluation authority or repeated representative trial infrastructure leaves empirical superiority explicitly blocked/unvalidated.
- `REQ-KB-005` Incomplete, duplicated, or mismatched trial manifests and run records fail closed before scoring or comparison output is treated as valid.
- `REQ-KB-006` The separated package remains compatible and its contract, scoring integrity, documentation, and core-runtime independence are verified by focused tests and repository checks.

## Non-goals
- Do not claim empirical superiority or fabricate corpus authority, baseline runs, competitor results, or repeated-trial outcomes.
- Do not make KEELBench a dependency of the portable KEEL runtime or its mandatory installation and verification path.
- Do not change KEEL lifecycle authorization, deterministic mechanism verification, or unrelated historical ledger records.

## Scope
- `**`

## Consequences
- Moving the evaluation package changes documented commands and generated bootstrap-manifest membership.
- Scoring must remain fail-closed so incomplete or mismatched trials cannot support comparison claims.
- This is a control-plane/package-boundary change requiring independent review.
