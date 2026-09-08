# KEEL canonical change ledger

KEEL is the repository's per-change governance spine. The canonical layout for new changes is:

```text
.keel/ledger/<change-id>/
  intent.json       # sole editable change-intent authority
  events.jsonl      # kernel-owned causal transition/decision records
  grants/           # kernel-owned CapabilityGrant records
  receipts/         # kernel-owned exact-subject EvidenceReceipts
  attestations/     # kernel-owned candidate/landed attestations
  views/            # generated, non-authoritative Markdown/JSON projections
```

`intent.json` contains the canonical objective, Requirements, non-goals, scope, WorkUnits/edge or graph references as applicable, risk/consequence declarations, EffectRequests, EvidenceRequirements, Decisions, and source provenance. No proposal, delta, requirements, acceptance, scope, risk, effects, or authorization file is a separate editable authority.

## Causality and ownership
Each significant event has a stable digest identity and the previous event digest. Validation rejects changed identities and broken local chains. This is tamper-evidence, not immutability: privileged actors can rewrite files and refs; committed Git history plus independent exact-subject verification is the durable integrity substrate.

Humans edit intent during permitted phases. The kernel alone appends events and writes grants, receipts, attestations, and views. Generated views carry source digests and explicit non-authoritative markers. Adapters, hooks, dashboards, context packets, and CLI output consume this model and never become alternate authority.

## Lifecycle
DISCUSS validates a meaningful objective. PLAN validates canonical requirements, EvidenceRequirements, scope, risk/consequences, EffectRequests, and required review/ExecPlan. EXECUTE enforces canonical scope. VERIFY derives an EvidencePlan and exact-subject receipts from canonical EvidenceRequirements. SHIP means candidate eligibility only. Seal binds the candidate Git subject; the Landing Transaction observes target T0, produces synthetic integration tree I, derives integration evidence, uses compare-and-swap protection, and independently confirms the actual landed tree before recording the landed anchor. These attestations report only properties established by evidence and do not prove behavioral correctness.

Planning and effect declaration never grant authority. CapabilityGrants are separate issuer-attributed, subject/effect/scope/condition-bound records. Legacy authorization booleans migrate only as explicitly labelled historical evidence, never as CapabilityGrants.

## Historical compatibility
The versioned `keel.legacy-ledger/v1` reader continues to audit existing sealed/landed ledgers. `keel.py ledger migrate` is additive, deterministic, idempotent, source-digesting, and loss-preserving; missing requirements, authorization, acceptance, or evidence remain explicitly absent. Legacy source bytes are preserved in migration provenance and are never deleted by migration. M6 retired old split templates and product writers after corpus and hostile fixtures proved supported states. The narrow versioned reader remains for historical audit and migration only.

## Boundaries
Hash chains and Git refs are not immutable security controls. Hooks are not confinement. SHIP is not permission to push, merge, release, deploy, migrate, or mutate an external system. Candidate and landed verification remain distinct; landing integration requires explicit authorization and exact resulting-state equivalence for merge, squash, or rebase strategies.
