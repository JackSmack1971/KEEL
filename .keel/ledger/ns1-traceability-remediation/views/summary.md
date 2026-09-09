# Change ns1-traceability-remediation

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Close NS1 traceability evidence gaps without changing behavior

## Requirements
- `REQ-01` Improve hostile-matrix and forbidden-operation traceability without weakening aggregate assertions.
- `REQ-02` Record and independently reproduce the cp1252 baseline failures at the main baseline.
- `REQ-03` Preserve preflight, RuntimeProfile, and public CLI behavior.
- `REQ-04` Produce KEEL verification evidence for the exact candidate and landing verification.

## Non-goals
- Do not change preflight decision logic, RuntimeProfile integration, or public CLI output.
- Do not modify the two cp1252-failing attestation tests or their implementation files.
- Do not merge to main without separate authorization.

## Scope
- `.keel/tests/test_codex_cost_preflight.py`
- `.keel/tests/test_public_cli_contract.py`
- `docs/exec-plans/active/ns1-traceability-remediation.md`

## Consequences
- Incorrect test traceability could create false audit confidence; documentation must accurately preserve baseline failure evidence.
