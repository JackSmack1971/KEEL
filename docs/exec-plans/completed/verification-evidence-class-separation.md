# ExecPlan: Verification Evidence-Class Separation

## Objective

Prevent planning/readiness evidence from granting implementation completion authority in generic KEEL verification.

## Design

- Add a generic `change_type`: `implementation` (default for compatibility) or explicit `planning_only`.
- Preserve `PLAN_READINESS`, `IMPLEMENTATION_ACCEPTANCE`, and `LANDED_COMPLETION` in contracts and evidence records.
- Infer legacy non-behavioral criteria as planning readiness; require implementation criteria to declare implementation paths and include behavioral evidence providers.
- Make verification retain readiness PASS while withholding implementation authority, SHIP, seal eligibility, and completion recommendations for implementation work.
- Keep planning-only completion explicit and preserve anchored historical behavior.

## Verification

Focused graph/lifecycle/next-action/developer-UX tests, then configured control-plane regressions, strict validation, doctor, generated-manifest validation, and `git diff --check`. Seal and anchor the committed candidate only after the verified tree is stable.

## Non-goals

No P1 repository-intelligence implementation, P2–P7/D1 work, or P4 provider/runtime behavior.
