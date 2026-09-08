# Verification

Status: `FAIL`
Base: `810c40b4a3b8bd0acfb3d9fe49cf286f6348181f`
Content digest: `1a607acea6b5fa9dd340578a1614191a0682be8b567abde5726aef5ca856abbe`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (343 ms)
- `p0-contract-tests` exit `1` (245 ms)
- `manifest-producer-check` exit `0` (321 ms)
- `canonical-config-portability` exit `0` (330 ms)
- `remediation-diff-check` exit `0` (35 ms)
- `capability-resolver-tests` exit `0` (170 ms)
- `context-compiler-tests` exit `0` (164 ms)
- `evidence-graph-tests` exit `0` (128 ms)
- `next-action-tests` exit `0` (693 ms)
- `worktree-lifecycle-tests` exit `0` (443 ms)
- `environment-contract-tests` exit `0` (202 ms)
- `upgrade-kernel-tests` exit `0` (334 ms)
- `mission-work-graph-tests` exit `0` (199 ms)
- `repository-map-tests` exit `0` (1118 ms)
- `topology-routing-tests` exit `0` (95 ms)
- `provider-effect-contract-tests` exit `0` (224 ms)
- `feedback-entropy-tests` exit `0` (125 ms)
- `lifecycle-compatibility-tests` exit `0` (113 ms)
- `developer-ux-tests` exit `0` (377 ms)
- `effect-inference-tests` exit `0` (115 ms)
- `schema-migration-tests` exit `0` (125 ms)
- `lifecycle-telemetry-tests` exit `0` (114 ms)
- `hook-event-compatibility-tests` exit `0` (137 ms)
- `evidence-class-tests` exit `0` (375 ms)
- `evidence-class-lifecycle-tests` exit `0` (417 ms)
- `p1-repository-intelligence-tests` exit `0` (219 ms)
- `p1-plan-contract-check` exit `0` (83 ms)
- `p2-mission-v2-tests` exit `0` (147 ms)

## Acceptance evidence
- `AC-KR-001` `PASS` — The authoritative contract contains all named ownership, primitive, state, graph, authorization, resource, identity, verification, hook, trust, compatibility, and single-authority invariants.
- `AC-KR-002` `PASS` — The contract contains a repository-evidenced file-level migration matrix and explicit staged migration/compatibility gates while making no kernel implementation change.
- `AC-KR-003` `PASS` — The audit and active roadmap freeze P3-P7 feature expansion and defer to the redesign authority.
- `AC-KR-004` `PASS` — Primary navigation and architecture surfaces link to the sole migration authority and a subordinate ExecPlan records the handoff.
- `AC-KR-005` `FAIL` — Canonical control-plane checks validate documentation/bootstrap integrity after the planning change.

## Blockers
- verification command failed: p0-contract-tests exit=1
- acceptance criterion failed: AC-KR-005
