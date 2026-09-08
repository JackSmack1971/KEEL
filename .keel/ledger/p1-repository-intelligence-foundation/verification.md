# Verification

Status: `PASS`
Base: `881531c21abff5b7cbce06d154534f1628837d6e`
Content digest: `ef14d5dd48eb0f14306aa2932364697b470ec5b833f0c0194bd0ec64bd2165bb`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (471 ms)
- `p0-contract-tests` exit `0` (863 ms)
- `manifest-producer-check` exit `0` (302 ms)
- `canonical-config-portability` exit `0` (287 ms)
- `remediation-diff-check` exit `0` (94 ms)
- `capability-resolver-tests` exit `0` (173 ms)
- `context-compiler-tests` exit `0` (214 ms)
- `evidence-graph-tests` exit `0` (144 ms)
- `next-action-tests` exit `0` (1915 ms)
- `worktree-lifecycle-tests` exit `0` (921 ms)
- `environment-contract-tests` exit `0` (180 ms)
- `upgrade-kernel-tests` exit `0` (1366 ms)
- `mission-work-graph-tests` exit `0` (156 ms)
- `repository-map-tests` exit `0` (1096 ms)
- `topology-routing-tests` exit `0` (101 ms)
- `provider-effect-contract-tests` exit `0` (196 ms)
- `feedback-entropy-tests` exit `0` (139 ms)
- `lifecycle-compatibility-tests` exit `0` (145 ms)
- `developer-ux-tests` exit `0` (4390 ms)
- `effect-inference-tests` exit `0` (115 ms)
- `schema-migration-tests` exit `0` (151 ms)
- `lifecycle-telemetry-tests` exit `0` (106 ms)
- `hook-event-compatibility-tests` exit `0` (111 ms)
- `evidence-class-tests` exit `0` (355 ms)
- `evidence-class-lifecycle-tests` exit `0` (380 ms)
- `p1-repository-intelligence-tests` exit `0` (155 ms)
- `p1-plan-contract-check` exit `0` (77 ms)

## Acceptance evidence
- `AC-P1-001` `PASS` — Graph/schema serialization, path normalization, provenance, determinism, validation, cycles, and graph negative states pass independent P1 tests.
- `AC-P1-002` `PASS` — Command intelligence proves independent fields, source precedence, zero commands, ambiguous candidates, unsupported metadata, unverified runtime, unavailable, unauthorized, conflict, and nonportable command outcomes.
- `AC-P1-003` `PASS` — Ownership, architecture, freshness, authority precedence, overlap, conflict, no-source, descriptive-vs-explicit, historical, and stale outcomes pass independent tests.
- `AC-P1-004` `PASS` — Bounded dependency adapters prove direct, parsed, derived, unresolved, external, generated, unsupported, malformed, incomplete, and cyclic dependency outcomes.
- `AC-P1-005` `PASS` — Changed-path normalization and advisory impact preserve direct relationships, uncertainty, conflict, ownership, architecture, dependency, generated provenance, unknown paths, and unsupported subsystems without mutation.
- `AC-P1-006` `PASS` — Generated-artifact provenance and drift tests prove verified, stale, missing/blocked, conflicting, and rejected hand-maintained classifications without mutation.
- `AC-P1-007` `PASS` — The authority hierarchy, roadmap state, P1 scope/effects boundary, and downstream locks remain documented and strict control-plane/doctor checks pass.
- `AC-P1-008` `PASS` — The focused P1 suite uses independent fixtures/oracles and all required regressions, drift checks, strict validation, and diff checks pass.
