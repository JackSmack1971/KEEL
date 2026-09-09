# KEEL forward architecture, product contract, and roadmap

Status: `AUTHORITATIVE — NS0 RECONCILIATION`

Authority ID: `KEEL-FORWARD-AUTHORITY-v1`

This document is the single forward authority for KEEL's architecture, product
contract, ownership boundary, operating surfaces, cost invariant, and roadmap.
It describes the current repository as landed only where repository evidence
supports that claim. Earlier forward-looking documents remain preserved as
historical evidence, but they do not authorize or sequence future work.

## North Star

KEEL is the portable, repository-native trust/control plane that makes
high-autonomy Codex engineering governable, evidence-backed, recoverable,
traceable, and delegable, operating strictly within the user's existing
Codex/ChatGPT entitlement.

Useful autonomy per unit of available Codex allowance is a design value.
Unnecessary agent calls are an architectural defect.

## Ownership boundary

Codex owns intelligence, coding, native tool execution, threads, model
execution, and Codex-native runtime facilities.

KEEL owns engineering intent/contracts, repository facts, WorkGraph semantics,
policy, authorization semantics, desired-state reconciliation, evidence
requirements/receipts, exact-state Git proof, recovery decisions, and landing
proof.

KEEL may schedule governed WorkUnits but must not become a second LLM runtime,
model provider, generic conversation engine, or sandbox implementation.

KEEL consumes observed Codex/runtime capabilities through narrow adapters. It
does not recreate Codex's intelligence, model execution, conversation engine,
tool runtime, or sandbox.

## Legitimate operating surfaces

KEEL has exactly two legitimate operating surfaces:

1. Native in-Codex governance: intent, policy, authorization semantics,
   WorkGraph reconciliation, evidence, Git proof, recovery decisions, and
   landing proof integrated with Codex-native work.
2. Stronger local controlled execution through documented Codex surfaces when
   available: a local governed WorkUnit may be scheduled and dispatched through
   observed Codex/runtime adapters without KEEL supplying an agent runtime.

No other KEEL operating surface is product authority. In particular, KEEL does
not expose an API-key model path, provider marketplace, generic chat surface,
paid fallback, or independent sandbox.

## Permanent cost invariant

`ZERO_INCREMENTAL_COST` is permanent and normative. KEEL MUST NOT create or
initiate any incremental AI cost path: no API keys, no API billing, no paid AI
fallback, no purchased-credit initiation, no rate-limit circumvention, and no
KEEL-created AI billing path of any kind.

KEEL operates within the user's existing Codex/ChatGPT entitlement. Account
rotation, purchased-credit flows, and provider substitution to evade an
allowance or rate limit are prohibited.

## Codex integration policy

Stable Codex integration paths are product dependencies only when their
capability is documented and observed. A stable path MUST degrade safely when a
capability is unsupported, unavailable, untrusted, or ambiguous; it MUST leave
the governed state explicit rather than silently guessing or broadening
authority.

Experimental Codex APIs are not load-bearing product dependencies. A specific
future goal may authorize an isolated experimental adapter, with an explicit
fallback and no effect on the stable path. This authority does not authorize
such an adapter.

Hooks, rules, skills, and subagents are Codex runtime adapters and guardrails.
They are not complete confinement, and their presence or configuration alone
does not prove runtime enforcement.

## Scheduler and runtime boundary

KEEL owns deterministic WorkGraph reconciliation and resource scheduling:
desired WorkUnits are compared with persisted actual state, legal readiness is
computed, compatible resources may be reserved, and bounded dispatch decisions
may be produced. Codex retains agent/runtime execution: the adapter invokes
Codex-native execution and reports observed outcomes back to KEEL.

This resolves the older wording that KEEL “must not implement a second
scheduler.” That wording remains useful only when it means KEEL must not create
a second agent/runtime scheduler. It is superseded for deterministic WorkGraph
reconciliation and resource scheduling, which are KEEL responsibilities. KEEL
still MUST NOT own agent execution, model routing, conversation scheduling, or
sandbox scheduling.

## Verification boundary

Exact candidate verification and exact landed-state verification are distinct.

- Candidate verification proves the declared requirements against the exact
  candidate subject/tree and canonical intent. A sealed candidate is not proof
  that it was landed.
- Landed-state verification independently observes the target and resulting
  landed tree, checks exact-state equivalence for the authorized landing
  mechanism, and records landing proof. A landing attestation does not replace
  candidate evidence, and a candidate attestation does not replace landed proof.

Neither boundary proves more than its receipts establish. Hooks are guardrails,
not confinement; Git refs and attestations are evidence surfaces, not
immutability by themselves.

## Landed capability baseline

The current tree contains these landed capability areas, confirmed by the
corresponding implementation, tests, and repository records:

- canonical kernel migration and canonical intent/change ledger;
- `RuntimeProfile` and `CapabilityGrant` authorization semantics;
- desired-state WorkUnit scheduler with deterministic reconciliation;
- exact Git proof;
- distinct candidate and landing attestations;
- public lifecycle UX; and
- separated KEELBench as an optional evaluation package.

These are current capabilities, not roadmap items. Their historical plans and
ledgers remain evidence and are not future work queues.

## Post-migration roadmap

The following sequence is a forward planning order, not an implementation claim
or authorization. Each stage requires its own governed change, evidence, and
authorization. No stage authorizes incremental AI cost or a second runtime.

| Stage | Forward outcome and dependency |
|---|---|
| NS0 | This authority reconciliation: one boundary, cost invariant, verification distinction, supersession map, and landed baseline. |
| NS1 | Stable Codex-surface capability contract and safe degradation, building on the landed RuntimeProfile/CapabilityGrant boundary. |
| NS2 | Governed WorkGraph-to-Codex WorkUnit delegation, building on landed desired-state reconciliation while keeping execution in Codex. |
| NS3 | Bounded recovery and resource policy, building on WorkUnit lifecycle state and deterministic scheduling; no model or sandbox runtime. |
| NS4 | Requirement-to-receipt coverage for delegated work, building on the landed canonical ledger and evidence receipts. |
| NS5 | Candidate-to-landed proof continuity for governed delegation, building on the distinct exact candidate and landed attestations. |
| NS6 | Portable local controlled execution profiles, building on stable integration policy and existing stack-independent local tooling. |
| NS7 | Evidence-backed observability and operational recovery signals, only where a supported runtime surface supplies observable facts. |
| NS8 | Optional KEELBench feedback/evaluation loops, keeping empirical evaluation separate from deterministic correctness and authorization. |
| NS9 | Narrow, explicitly authorized external adapters, with KEEL retaining policy/evidence/landing authority and no provider or billing ownership. |
| NS10 | Distribution and upgrade hardening for repository portability, preserving dependency-light operation and historical evidence. |
| NS11 | Reassessment of the boundary from observed evidence; promote only stable, repeatedly justified invariants and leave unsupported ambitions deferred. |

Each stage is conditional on the preceding landed or NS0-produced contract.
“Planned” means eligible for a separately governed proposal; it does not mean
implemented, available, or authorized.

## Supersession and historical evidence

The following retained documents are historical evidence or execution history,
not competing forward authority. Where they conflict with this document, this
authority supersedes their forward architecture, product-contract, sequencing,
and “current roadmap” claims.

| Retained document | Disposition |
|---|---|
| `docs/control-plane/KERNEL_REDESIGN.md` | Superseded migration authority; landed kernel evidence retained. |
| `docs/references/research/KEEL_UPGRADES.md` | Superseded research and upgrade strategy. |
| `docs/references/research/UPGRADE_AUDIT.md` | Frozen landed-state evidence map; forward claims superseded. |
| `docs/exec-plans/completed/kernel-redesign-migration-authority.md` | Superseded planning evidence. |
| `docs/exec-plans/completed/upgrade-remaining-plan.md` | Historical roadmap copy. |
| `docs/exec-plans/completed/upgrade-planning-archive.md` | Historical plan archive. |
| `docs/exec-plans/completed/canonical-change-graph.md`, `runtime-trust-authorization-model.md`, `semantic-kernel-m1.md` | Completed landed implementation plans. |
| `docs/exec-plans/completed/compatibility-retirement-m6.md`, `desired-state-reconciler.md`, `landing-transaction.md`, `public-ux-portability.md`, `separate-keelbench.md` | Completed landed implementation plans moved from the stale active directory; historical ledgers retained. |

The plan archive records the same disposition for individual execution plans.

## Change control

Amending this authority requires a standard high-risk KEEL change with explicit
requirements, independent review, direct evidence, exact candidate verification,
exact landed-state verification, and authorized landing. This document never
authorizes implementation by itself.
