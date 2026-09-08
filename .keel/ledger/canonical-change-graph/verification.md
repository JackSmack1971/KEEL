# Verification

Status: `PASS`
Base: `de7e4b0b84a2275c55b4946434b47bc6cfdf4a68`
Content digest: `f8e8b653769864a0e4a007aaff6415c16e811e2c85fb3516e26f02cf794fbf6e`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (557 ms)
- `p0-contract-tests` exit `0` (628 ms)
- `manifest-producer-check` exit `0` (482 ms)
- `canonical-config-portability` exit `0` (467 ms)
- `remediation-diff-check` exit `0` (65 ms)
- `capability-resolver-tests` exit `0` (225 ms)
- `context-compiler-tests` exit `0` (274 ms)
- `evidence-graph-tests` exit `0` (251 ms)
- `next-action-tests` exit `0` (1298 ms)
- `worktree-lifecycle-tests` exit `0` (733 ms)
- `environment-contract-tests` exit `0` (381 ms)
- `upgrade-kernel-tests` exit `0` (627 ms)
- `mission-work-graph-tests` exit `0` (310 ms)
- `repository-map-tests` exit `0` (1789 ms)
- `topology-routing-tests` exit `0` (243 ms)
- `provider-effect-contract-tests` exit `0` (336 ms)
- `feedback-entropy-tests` exit `0` (217 ms)
- `lifecycle-compatibility-tests` exit `0` (161 ms)
- `developer-ux-tests` exit `0` (574 ms)
- `effect-inference-tests` exit `0` (249 ms)
- `schema-migration-tests` exit `0` (218 ms)
- `lifecycle-telemetry-tests` exit `0` (171 ms)
- `hook-event-compatibility-tests` exit `0` (219 ms)
- `evidence-class-tests` exit `0` (583 ms)
- `evidence-class-lifecycle-tests` exit `0` (673 ms)
- `p1-repository-intelligence-tests` exit `0` (371 ms)
- `p1-plan-contract-check` exit `0` (108 ms)
- `change-graph-tests` exit `0` (2196 ms)
- `p2-mission-v2-tests` exit `0` (293 ms)
- `semantic-kernel-tests` exit `0` (567 ms)

## Acceptance evidence
- `AC-GRAPH-001` `PASS` — Canonical graph tests prove WorkUnit locality and edge-only dependency authority.
- `AC-GRAPH-002` `PASS` — Hostile validation and deterministic round-trip tests cover every requested graph invariant including non-invalidating resource conflicts.
- `AC-GRAPH-003` `PASS` — Minimal v1/v2 fixtures normalize deterministically with provenance and uncertainty and contain no invented grants, observations, dispatch, personas, or lifecycle state.
- `AC-GRAPH-004` `PASS` — CLI contract tests prove stable canonical surfaces, compatibility aliases, and absence of dispatch, scheduler, or persona projection while the full canonical suite passes.
