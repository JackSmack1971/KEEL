# Change canonical-change-intent

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
KEEL currently distributes change intent and authority across proposal, delta, requirements, acceptance, scope, risk, effects, authorization, state, and gate-log files. Independent editable authorities can diverge, obscure provenance, and complicate causal audit and migration.
Implement authority `KEEL-KERNEL-REDESIGN-v1` stages M2-M4 for change ledgers: one canonical versioned intent document; hash-chained causal lifecycle events; separate grants, receipts, and attestations; generated Markdown/compatibility views; deterministic loss-preserving legacy migration; and canonical consumers for lifecycle, context, evidence, candidate attestations, and status.
Do not claim append-only files or Git refs are immutable. Do not delete legacy readers, historical ledgers, templates, or implement the future landing transaction. Do not manufacture missing grants, requirements, acceptance criteria, receipts, or runtime observations during migration. Do not execute external effects or merge a pull request without separate authorization.
Automated fixtures prove canonical validation, stable identity and event-chain tamper detection, deterministic/idempotent legacy migration, uncertainty preservation, hostile-input rejection, generated-view provenance, legacy historical readability, canonical lifecycle transitions, context/evidence/status consumption, and exact-subject candidate attestation behavior. Full KEEL regression and repository verification pass.
None. The user supplied the target authority boundary; compatibility readers remain versioned and legacy authority files are accepted only as migration inputs for historical ledgers.

## Requirements
- `REQ-1` New changes have exactly one authoritative intent.json containing objective, requirements, non-goals, scope, work graph references, risk/consequences, EffectRequests, and EvidenceRequirements.
- `REQ-2` Significant transitions and decisions are causal events with stable identity and local previous-event digest tamper evidence without immutability claims.
- `REQ-3` Grants, exact-subject evidence receipts, and Git-bound attestations are distinct script-owned records; generated views are non-authoritative.
- `REQ-4` Migration from every supported legacy ledger is deterministic, idempotent, provenance-preserving, lossless for unknown data, and never invents missing authority or evidence.
- `REQ-5` Sealed and landed historical changes remain auditable through canonical migration or a versioned historical reader.
- `REQ-6` Lifecycle, scope enforcement, context, evidence planning, verification, candidate attestations, and status queries consume canonical ledger semantics.
- `REQ-7` Legacy readers and templates remain until migration and hostile fixtures prove all supported states, and durable control-plane documentation reflects the landed authority model.

## Non-goals
- No immutability claim for hash chains or Git refs.
- No deletion of legacy readers, historical ledgers, or templates.
- No future landing transaction, scheduler, provider effect executor, or unauthorized remote integration.
- No invented authorization, requirements, evidence, or runtime observations.

## Scope
- `.keel/bin/keel.py`
- `.keel/lib/**`
- `.keel/templates/**`
- `.keel/tests/**`
- `.keel/contracts.json`
- `.keel/config.json`
- `.keel/ledger/canonical-change-intent/**`
- `.control-plane/bootstrap-manifest.json`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `WORKFLOW.md`
- `docs/INDEX.md`
- `docs/control-plane/**`
- `docs/exec-plans/active/canonical-change-intent.md`
- `.agents/skills/keel-change-lifecycle/SKILL.md`

## Consequences
- Changes authority and audit semantics for every future KEEL write.
- Incorrect migration could lose obligations or inflate authorization.
- Candidate proof must continue to audit old and new ledgers.
