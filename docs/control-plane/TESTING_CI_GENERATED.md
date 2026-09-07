# Testing, CI, Static Quality, and Generated Artifacts

All are represented at bootstrap; concrete tools remain conditional.

## Testing/evals
Define layers appropriate to the project: unit/property/integration/e2e/simulation/HIL/evals/contract/performance/security. Keep commands deterministic and document known flake behavior rather than normalizing failure.

## CI/CD
Select a provider only after repository/organization evidence exists. CI should run trusted local checks, use least-privilege credentials, distinguish retryable infrastructure failures from product failures, and preserve machine-readable evidence.

## Static/architecture checks
Promote stable high-value invariants to format/lint/type/architecture checks. Error text should be agent-actionable.

## Generated outputs
A generated artifact needs a named source, generator, trigger, and drift check. Source/generated disagreement is a blocker until reconciled through the source or generator. The bootstrap manifest is produced by `python .keel/bin/keel.py manifest --write`; its producer and source are recorded in the manifest itself, and `python .keel/bin/keel.py manifest` is the drift check. Consumer, ledger, runtime, cache, and machine-local artifacts are not distributable framework content.
