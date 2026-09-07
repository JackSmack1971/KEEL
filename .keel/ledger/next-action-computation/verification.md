# Verification

Status: `PASS`
Base: `e413308dd12aed9ca8275d53f5104a0f29a5a94f`
Content digest: `da022fc8f8c7812ba968d7ca4dbeee98b9f171429be787960b38567454d22414`

## Checks
- `git-diff-check` exit `0` (0 ms)
- `control-plane-doctor` exit `0` (233 ms)
- `keelbench-tests` exit `0` (179 ms)
- `keelbench-validate` exit `0` (119 ms)
- `strict-control-plane-validation` exit `0` (668 ms)
- `capability-resolver-tests` exit `0` (109 ms)
- `context-compiler-tests` exit `0` (134 ms)
- `evidence-graph-tests` exit `0` (92 ms)
- `next-action-tests` exit `0` (142 ms)

## Acceptance evidence
- `AC-001` `PASS` — Focused tests prove stable guidance for idle, DISCUSS, PLAN, EXECUTE, and SHIP states without changing state files.
- `AC-002` `PASS` — Focused tests prove stale verification produces a blocker and reopen guidance instead of seal guidance.
- `AC-003` `PASS` — The strict control-plane validator and KEEL doctor pass after the next-action change.
