# Domain Specialties

Activate these surfaces only when the project needs them.

## UI / browser / mobile / game / rendered output
Directly reproduce user flows. Capture DOM/visual/console/network/device evidence as appropriate. Add accessibility, localization, input-mode and visual-regression policy according to supported users/platforms.

## APIs / protocols / libraries
Version contracts and compatibility guarantees. Add contract tests, schema generation, semver/deprecation policy, and consumer compatibility as relevant.

## Data / ML / agents
Version datasets/features/prompts/models/evals where they affect behavior. Preserve provenance from source through output. Separate target evals from broader regressions.

## Infrastructure
Keep infrastructure declarative when possible. Plan before apply, protect state/secrets, define drift and rollback, and require authorization for external changes.

## Embedded / hardware / robotics / safety-critical
Document physical hazards, fail-safe states, timing/resource constraints, hardware compatibility, simulation/HIL evidence, and stricter permission/review requirements. Do not apply software-only assumptions to irreversible physical effects.

## Scientific / research / numerical engineering
Record datasets, units, numerical tolerances, seeds, environment versions, reference results and reproducibility criteria. Distinguish exploratory findings from validated claims.
