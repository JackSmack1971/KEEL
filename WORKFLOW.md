# Development Workflow — KEEL-governed

KEEL is the default write lifecycle. Repository evidence and canonical records, not chat memory or generated views, determine state.

## Modes
Read-only work creates no ledger. Localized reversible low-risk writes may use `trivial`; all other writes use `standard`. Control-plane, security/privacy, migration/release, external-effect, and high-blast-radius work cannot use trivial mode. Emergency bypass requires an operator-provided `KEEL_BYPASS_REASON` and creates auditable process debt without bypassing runtime/application authorization.

## Canonical ledger
`keel.py start <id>` creates `.keel/ledger/<id>/intent.json`, `events.jsonl`, and `grants/`, `receipts/`, `attestations/`, and `views/`. `intent.json` is the sole editable authority for objective, requirements, non-goals, scope, work/graph references, risk/consequences, EffectRequests, and EvidenceRequirements. Edit it only in the legal DISCUSS/PLAN phases. Markdown and JSON under `views/` are generated, non-authoritative projections.

Events record significant transitions/decisions with stable content identity and a previous-event digest. This detects local discontinuity; it does **not** make the ledger immutable. Committed Git history and independently verified Git subjects remain the durable integrity substrate. Grants, receipts, attestations, events, and views are kernel-owned records and must not be manually edited.

## Standard lifecycle
1. **Discuss:** write the objective and non-goals in `intent.json`; run `python3 .keel/bin/keel.py gate discuss`.
2. **Plan:** complete canonical requirements, scope, work references, risk/consequences, effect requests, and evidence requirements. High-risk work includes `risk.review` and an ExecPlan. Run `keel.py gate plan`.
3. **Execute:** edit only canonical scope. Use `replan` when intent changes and `reopen` after verification when implementation changes. Replanning invalidates prior effect grants.
4. **Verify:** `keel.py verify` selects verifiers from EvidenceRequirements and writes exact-subject immutable-content records under `receipts/`; generated compatibility reports go under `views/`. A green unrelated command cannot establish a requirement.
5. **Commit and seal:** commit the verified tree, then `keel.py seal --change <id> --commit HEAD`. Seal independently recomputes committed material and canonical intent digests and creates a Git-bound candidate attestation/ref.
6. **Integrate and anchor:** SHIP is eligibility, not authorization. After separately authorized integration, `keel.py anchor --change <id> --commit <landed-sha>` independently checks landed equivalence and records the landed Git anchor.

## Authorization
An EffectRequest is not permission. Only a valid, issuer-attributed, intent/effect/subject-bound CapabilityGrant can authorize an attempt, and effective autonomy is also limited by observed RuntimeProfile and external controls. Hooks are adapters, not confinement. Pushes, merges, releases, deployments, migrations, communications, and other external effects need explicit authorization.

## Compatibility and migration
`keel.py ledger migrate --change <id> [--output <dir>]` deterministically reads supported v1 ledgers. Migration preserves source bytes/digests and unknown fields, represents missing data as absent/unknown, never creates grants or receipts from absence, and does not delete source files. Existing historical ledgers remain readable through `keel.legacy-ledger/v1`. Legacy templates/readers remain until fixtures prove all supported states and a later removal decision passes its gate.

## Parallel work and context
One change-id has one primary writer in one worktree. Read-heavy agents may fan out; parallel writers need separate worktrees/change IDs. `keel.py context` is a bounded generated projection of canonical intent, repository facts, and relevant docs—not authority.
