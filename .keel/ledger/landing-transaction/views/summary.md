# Change landing-transaction

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Close candidate-to-landed TOCTOU gap with explicit landing transaction

## Requirements
- `REQ-1` Landing observes and binds target T0, combines sealed candidate C with T0 in an isolated synthetic integration workspace, produces exact integration tree I, and derives an integration-specific EvidencePlan.
- `REQ-2` Candidate EvidenceReceipts are reused only when their subjects and assumptions remain valid; invalidated and integration-sensitive verifiers run against I.
- `REQ-3` LandingAttestation binds T0, CandidateAttestation C, I, intent digest, integration receipts, policy/runtime profile, and expected landing mechanism.
- `REQ-4` Integration uses compare-and-swap target protection, marks target drift stale, reconstructs and reverifies, and rejects conflicting or behavior-breaking integration.
- `REQ-5` Authorized merge, squash, and rebase strategies are accepted only when exact resulting-state equivalence is established, while existing candidate refs and CandidateAttestation semantics remain compatible.
- `REQ-6` After integration, the actual landed state is independently checked against the LandingAttestation before LANDED completion and anchor are recorded.
- `REQ-7` Durable control-plane documentation distinguishes candidate and landing attestation from proof of correctness and records the explicit transaction boundary.

## Non-goals
- Do not claim proof of correctness; attest only to properties established by exact evidence.
- Do not change CandidateAttestation semantics or remove existing candidate refs.
- Do not perform remote integration, push, release, deployment, or other external effects.
- Do not manually edit kernel-owned receipts, attestations, events, grants, or generated views.

## Scope
- `.keel/lib/**`
- `.keel/bin/keel.py`
- `.keel/tests/**`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `.keel/README.md`
- `ARCHITECTURE.md`
- `WORKFLOW.md`
- `CONTROL_PLANE.md`
- `docs/control-plane/**`
- `docs/exec-plans/active/**`

## Consequences
- This changes the authority boundary between sealed candidates and landed state for every future integration.
- Incorrect tree or evidence binding could record a false landed completion or reject a valid integration.
