# Verification

Status: `PASS`
Base: `1c0b25b8e20d09946b00bfea8345f322bbc31c5f`
Content digest: `207712318717fefb4b990bb272d50e611dcb7317f0e5a21225d5fd1dcd4ef138`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (281 ms)
- `keelbench-tests` exit `0` (217 ms)
- `keelbench-validate` exit `0` (160 ms)
- `strict-control-plane-validation` exit `0` (896 ms)
- `capability-resolver-tests` exit `0` (152 ms)
- `context-compiler-tests` exit `0` (165 ms)
- `evidence-graph-tests` exit `0` (120 ms)
- `next-action-tests` exit `0` (186 ms)
- `worktree-lifecycle-tests` exit `0` (734 ms)
- `environment-contract-tests` exit `0` (148 ms)
- `upgrade-kernel-tests` exit `0` (428 ms)

## Acceptance evidence
- `AC-001` `PASS` — reconcile reports ledger phase, Git state, scope, and next action without mutation
- `AC-002` `PASS` — provider and effect capability contracts validate known and unknown values deterministically
- `AC-003` `PASS` — source classification follows explicit, detected, generic, unknown precedence
- `AC-004` `PASS` — version and compatibility inspection returns repository metadata and schema status
- `AC-005` `PASS` — doctor, strict control-plane validation, and KEELBench remain passing
