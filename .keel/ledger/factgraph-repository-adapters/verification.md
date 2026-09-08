# Verification

Status: `PASS`
Base: `d574b9dd323cfde9a00fb92c2dd18cbde0b2243c`
Content digest: `322a31648647c282f9bd555da2f257d6aac8daf7070e4090c5f2d09afdf5e340`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (436 ms)
- `p0-contract-tests` exit `0` (519 ms)
- `manifest-producer-check` exit `0` (387 ms)
- `canonical-config-portability` exit `0` (368 ms)
- `remediation-diff-check` exit `0` (50 ms)
- `capability-resolver-tests` exit `0` (291 ms)
- `context-compiler-tests` exit `0` (269 ms)
- `evidence-graph-tests` exit `0` (151 ms)
- `next-action-tests` exit `0` (812 ms)
- `worktree-lifecycle-tests` exit `0` (584 ms)
- `environment-contract-tests` exit `0` (329 ms)
- `upgrade-kernel-tests` exit `0` (460 ms)
- `mission-work-graph-tests` exit `0` (223 ms)
- `repository-map-tests` exit `0` (2689 ms)
- `topology-routing-tests` exit `0` (193 ms)
- `provider-effect-contract-tests` exit `0` (338 ms)
- `feedback-entropy-tests` exit `0` (140 ms)
- `lifecycle-compatibility-tests` exit `0` (127 ms)
- `developer-ux-tests` exit `0` (413 ms)
- `effect-inference-tests` exit `0` (137 ms)
- `schema-migration-tests` exit `0` (142 ms)
- `lifecycle-telemetry-tests` exit `0` (153 ms)
- `hook-event-compatibility-tests` exit `0` (127 ms)
- `evidence-class-tests` exit `0` (421 ms)
- `evidence-class-lifecycle-tests` exit `0` (403 ms)
- `p1-repository-intelligence-tests` exit `0` (1080 ms)
- `p1-plan-contract-check` exit `0` (80 ms)
- `change-graph-tests` exit `0` (1737 ms)
- `p2-mission-v2-tests` exit `0` (209 ms)
- `fact-graph-tests` exit `0` (237 ms)
- `semantic-kernel-tests` exit `0` (295 ms)

## Acceptance evidence
- `AC-001` `PASS` — FactGraph tests prove generic adapter registration, normalized Fact/Edge identities/provenance, and byte-stable construction.
- `AC-002` `PASS` — Cross-stack fixtures prove filesystem/Git/Python support and conservative UNKNOWN/UNSUPPORTED results for unsupported ecosystems.
- `AC-003` `PASS` — FactGraph tests prove conflicts remain visible, precedence is explicit, and source digest changes produce stale observations.
- `AC-004` `PASS` — FactGraph and legacy suites prove impact/capabilities/context/map/intelligence are graph-derived compatibility projections.
- `AC-005` `PASS` — Tests prove candidates and declarations are separate and adapter discovery does not execute candidate commands or activate policy.
- `AC-006` `PASS` — Cross-stack and compatibility tests prove portable deterministic paths and legacy behavior without reconciler or EvidencePlanner surfaces.
- `AC-007` `PASS` — Doctor and manifest provenance checks pass for the governed tree.
