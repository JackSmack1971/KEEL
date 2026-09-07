# ExecPlan: Plan 005 API and authorized integrations

## Objective

Deliver a versioned, provider-neutral domain contract that keeps authority in KEEL policy/effect/authorization handling.

## Implementation slices

1. Add shared response and lifecycle-event validation with deterministic error envelopes.
2. Add correlation context for mission/change/run/operation/evidence and emit it in append-only events.
3. Add explicit provider adapter declarations with redaction and disabled-by-default semantics.
4. Expose the contract through the CLI and test adversarial alternate-dispatch and forged-authority cases.

## Constraints

- No live external mutation or credentials.
- Existing schemas remain compatible unless an unsupported version is reported explicitly.
- One domain path owns authorization; transports only adapt input/output.

## Verification

- `api-contract-tests`
- existing provider/effect and lifecycle tests
- configured doctor, KEELBench, and strict control-plane validation
- `python .keel/bin/keel.py verify --change plan-005-api-authorized-integrations`
