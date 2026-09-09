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

## Hosted deterministic kernel proof

`.github/workflows/deterministic-kernel.yml` runs `python -B .keel/ci/verify.py all`
from fresh GitHub-hosted Ubuntu and Windows checkouts. The repository-owned command
runs every canonical `test_*.py` entry point, names the required contract categories
in machine-readable output, checks bootstrap-manifest/config drift, exercises the
explicit unavailable-runtime branch, and rejects cache, temporary producer, and
Python bytecode artifacts. Workflow YAML contains only checkout/runtime setup and
that command; validation logic remains in the repository.

The workflow has read-only repository permission, receives no provider credential,
and never starts Codex or makes a model/API call. `UNVERIFIED_RUNTIME` is the
expected hosted result of the disabled live-runtime smoke path, not a live-test
success. This preserves `ZERO_INCREMENTAL_COST`.

The CI trust boundary is exact: a green hosted job establishes only that the checked
out repository's deterministic behavior passed on that runner. It does **not**
establish that any installed Codex runtime loaded, trusted, invoked, or enforced
KEEL hooks, and it must never be described as live Codex hook/runtime activation.
macOS is excluded until the complete suite has direct, current, credential-free
hosted evidence there; Linux success alone is not portability evidence for macOS.
