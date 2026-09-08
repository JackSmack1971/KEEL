# Verification

Status: `PASS`
Base: `cd5974e5ab5a4b4b9bb37c9fb77101bcf448555b`
Content digest: `e2baab7d7359aec64a87e74c20e4d606c098dbd6bf350a94a55b6ff3f15693f3`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (535 ms)
- `p0-contract-tests` exit `0` (647 ms)
- `manifest-producer-check` exit `0` (482 ms)
- `canonical-config-portability` exit `0` (426 ms)
- `remediation-diff-check` exit `0` (51 ms)
- `capability-resolver-tests` exit `0` (236 ms)
- `context-compiler-tests` exit `0` (257 ms)
- `evidence-graph-tests` exit `0` (186 ms)
- `next-action-tests` exit `0` (1030 ms)
- `worktree-lifecycle-tests` exit `0` (738 ms)
- `environment-contract-tests` exit `0` (315 ms)
- `upgrade-kernel-tests` exit `0` (497 ms)
- `mission-work-graph-tests` exit `0` (312 ms)
- `repository-map-tests` exit `0` (1717 ms)
- `topology-routing-tests` exit `0` (159 ms)
- `provider-effect-contract-tests` exit `0` (326 ms)
- `feedback-entropy-tests` exit `0` (208 ms)
- `lifecycle-compatibility-tests` exit `0` (235 ms)
- `developer-ux-tests` exit `0` (537 ms)
- `effect-inference-tests` exit `0` (165 ms)
- `schema-migration-tests` exit `0` (231 ms)
- `lifecycle-telemetry-tests` exit `0` (166 ms)
- `hook-event-compatibility-tests` exit `0` (197 ms)
- `evidence-class-tests` exit `0` (558 ms)
- `evidence-class-lifecycle-tests` exit `0` (517 ms)
- `p1-repository-intelligence-tests` exit `0` (252 ms)
- `p1-plan-contract-check` exit `0` (115 ms)
- `p2-mission-v2-tests` exit `0` (191 ms)
- `semantic-kernel-tests` exit `0` (416 ms)

## Acceptance evidence
- `AC-KERNEL-001` `PASS` — Independent tests instantiate, serialize, and decode every canonical primitive and prove all five state dimensions are separate enum types.
- `AC-KERNEL-002` `PASS` — Tests prove byte-identical canonical serialization and digests across reordered maps and strict rejection of unknown fields, wrong schemas, and unsupported versions.
- `AC-KERNEL-003` `PASS` — Hostile tests reject malformed and duplicate identities, invalid repository resources, host-specific portable intent values, dangling references, and defective provenance while validation performs no I/O.
- `AC-KERNEL-004` `PASS` — All configured legacy P0/P1/P2/lifecycle checks pass unchanged alongside the new isolated semantic-kernel check.
