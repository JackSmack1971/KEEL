# Verification

Status: `FAIL`
Base: `4532bb43780cb45a025574403a8b4ae4ac7304ab`
Content digest: `e8410231246a018c3e15c763a991e441864d6f21fb43d1c2a5c9087774fb8563`

## Checks
- `git-diff-check` exit `2` (0 ms)
- `control-plane-doctor` exit `0` (293 ms)
- `keelbench-tests` exit `0` (221 ms)
- `keelbench-validate` exit `0` (151 ms)
- `strict-control-plane-validation` exit `0` (881 ms)
- `capability-resolver-tests` exit `0` (148 ms)
- `context-compiler-tests` exit `0` (174 ms)
- `evidence-graph-tests` exit `0` (136 ms)
- `next-action-tests` exit `0` (186 ms)
- `worktree-lifecycle-tests` exit `0` (802 ms)
- `environment-contract-tests` exit `0` (169 ms)
- `upgrade-kernel-tests` exit `0` (529 ms)
- `mission-work-graph-tests` exit `0` (144 ms)
- `repository-map-tests` exit `0` (635 ms)
- `topology-routing-tests` exit `0` (121 ms)
- `provider-effect-contract-tests` exit `0` (205 ms)
- `engineering-protocols-skill-check` exit `0` (85 ms)
- `feedback-entropy-tests` exit `0` (112 ms)
- `lifecycle-compatibility-tests` exit `0` (124 ms)
- `developer-ux-tests` exit `0` (2024 ms)
- `effect-inference-tests` exit `0` (90 ms)
- `schema-migration-tests` exit `0` (117 ms)
- `lifecycle-telemetry-tests` exit `0` (93 ms)
- `api-contract-tests` exit `0` (162 ms)

## Acceptance evidence
- `AC-API-001` `PASS` — API contract tests prove deterministic versioned envelopes and predictable unknown-version failure.
- `AC-API-002` `PASS` — Correlation tests prove identifiers survive lifecycle event creation and caller cannot forge authorization fields.
- `AC-API-003` `PASS` — Provider contract tests prove disabled-by-default, redaction, and no-authority behavior.
- `AC-API-004` `PASS` — Canonical doctor, strict control-plane validation, KEELBench, and existing provider/effect tests pass.

## Blockers
- git diff --check failed
