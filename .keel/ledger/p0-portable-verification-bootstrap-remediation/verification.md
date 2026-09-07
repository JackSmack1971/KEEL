# Verification

Status: `FAIL`
Base: `6b0414d61395db0067d593dd5aa578efb74697d8`
Content digest: `d6a4e23ec832c7349895578ca90fae202adf87d574207802c1881b163d093e36`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (246 ms)
- `p0-contract-tests` exit `0` (576 ms)
- `manifest-producer-check` exit `0` (190 ms)
- `canonical-config-portability` exit `0` (187 ms)
- `remediation-diff-check` exit `0` (52 ms)
- `capability-resolver-tests` exit `0` (103 ms)
- `context-compiler-tests` exit `0` (138 ms)
- `evidence-graph-tests` exit `0` (112 ms)
- `next-action-tests` exit `0` (1126 ms)
- `worktree-lifecycle-tests` exit `0` (663 ms)
- `environment-contract-tests` exit `0` (111 ms)
- `upgrade-kernel-tests` exit `0` (450 ms)
- `mission-work-graph-tests` exit `0` (110 ms)
- `repository-map-tests` exit `0` (871 ms)
- `topology-routing-tests` exit `0` (75 ms)
- `provider-effect-contract-tests` exit `0` (137 ms)
- `feedback-entropy-tests` exit `0` (100 ms)
- `lifecycle-compatibility-tests` exit `0` (105 ms)
- `developer-ux-tests` exit `0` (3344 ms)
- `effect-inference-tests` exit `0` (91 ms)
- `schema-migration-tests` exit `0` (116 ms)
- `lifecycle-telemetry-tests` exit `0` (91 ms)
- `hook-event-compatibility-tests` exit `0` (76 ms)

## Acceptance evidence
- `AC-REM-001` `PASS` — Focused disposable manifest fixtures return VERIFIED only for matching inputs and after regeneration; changed, missing, and unrelated drift return explicit non-passing statuses.
- `AC-REM-002` `PASS` — Focused command-resolution tests show zero candidates as UNSUPPORTED and a present candidate without provenance as a distinct UNVERIFIED_RUNTIME or BLOCKED result, while preserving the other required distinctions.
- `AC-REM-003` `PASS` — The final parent-to-remediation commit git diff --check passes with no exclusions or whitespace suppression.
- `AC-REM-004` `FAIL` — The original P0 plan is present under docs/exec-plans/completed, absent from docs/exec-plans/active, and the authoritative roadmap preserves P1 as unstarted.

## Blockers
- acceptance criterion failed: AC-REM-004
