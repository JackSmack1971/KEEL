# Codex Control Plane

State: `CANONICAL_KERNEL_M6`; live Codex/hook enforcement remains pending per-session observation.

The control plane is the repository's information architecture, change-governance spine, and feedback system. It remains stack-neutral until project evidence activates specialized domains. Candidate and landing attestations report only properties established by exact evidence; they are not proof of behavioral correctness.

The forward architecture, product contract, and roadmap authority is
[KEEL_FORWARD_AUTHORITY.md](docs/control-plane/KEEL_FORWARD_AUTHORITY.md).
This document is an operating-model summary and must not introduce a competing
forward roadmap.

The stable public surface is the JSON CLI: `init`, `doctor`, `start`, `status`,
`next`, `run`, `verify`, `land`, `explain`, and `audit`. Internal schema and
subsystem commands are compatibility surfaces, not normal user workflow.

## Layer map
1. Repository legibility — thin entry points, indexed durable knowledge.
2. KEEL canonical ledger — one authoritative intent model plus causal events, grants, exact-subject receipts, attestations, and generated views.
3. Architectural enforcement — stable invariants become tested mechanical checks.
4. Capability extension — repo skills and narrow subagents.
5. Runtime legibility — logs/metrics/traces/browser/hardware evidence when relevant.
6. Work isolation — one write-owner per change/worktree; read-heavy subagent fan-out.
7. Orchestration — issue-driven scheduling only after tracker/runtime/workspace prerequisites exist.
8. Production feedback — reviewed traces/corrections -> findings -> evals -> bounded tasks.
9. Entropy control — recurring docs/quality gardening and promotion of repeated feedback into rules.

## Canonical kernel

The `KEEL-KERNEL-REDESIGN-v1` migration is complete through M6. Canonical semantics, ChangeGraph, FactGraph, receipt planning, runtime authorization, Codex adaptation, Git attestations, and the canonical ledger are the only active product path. Versioned v1 ledger reading exists solely for audit and migration.

## Core maps
- [KEEL forward architecture, product contract, and roadmap authority](docs/control-plane/KEEL_FORWARD_AUTHORITY.md)
- [KEEL kernel redesign and migration authority](docs/control-plane/KERNEL_REDESIGN.md)
- [KEEL control plane](docs/control-plane/KEEL.md)
- [Capability registry](docs/control-plane/CAPABILITY_REGISTRY.md)
- [Decision and autonomy model](docs/control-plane/DECISION_MODEL.md)
- [Verification model](docs/control-plane/VERIFICATION.md)
- [Codex-native configuration](docs/control-plane/CODEX_NATIVE.md)
- [Documentation index](docs/INDEX.md)

## Activation truth
Generated `.codex/` files do not prove runtime enforcement. Project trust, hook-definition trust, executable hook runtime, Git baseline, and current Codex behavior must be observed before KEEL hooks are called active. `python3 .keel/bin/keel.py doctor` reports filesystem/Git readiness; Codex `/hooks` and runtime smoke tests establish hook readiness.

## Doctrine
Universal coverage does not mean universal tooling. Every domain is represented, but provider/framework/runtime choices activate only when evidence justifies them. KEEL governs changes across all domains; it does not replace domain-specific architecture, safety, release, or operational controls.

## Adaptive intelligence kernel

Repository evidence flows through read-only adapters into the canonical FactGraph;
capability resolution (`DETECTED/LIKELY/UNKNOWN/CONFLICT` evidence only), bounded
context, repository maps, and impact are projections rather than parallel repository
models. Requirement-to-receipt verification is authoritative; legacy evidence-graph views are compatibility projections. KEELBench retains its separate evaluation behavior. These mechanisms increase decision quality without
silently changing project policy.

Runtime trust and authorization now have a canonical M4 policy boundary:
`RuntimeProfile` preserves observed and negative states, `CapabilityGrant`
replaces boolean permission semantics, and effect contracts distinguish mediated,
observed, and unconfined boundaries. This is not proof that a session is confined,
and it supplies neither an effect executor nor an agent/runtime scheduler.
Deterministic WorkGraph reconciliation, governed dispatch-envelope construction,
resource scheduling, and exact-subject completion decisions remain KEEL
responsibilities as defined by the forward authority. Codex turn completion is
recorded only as an execution observation and never as engineering completion.
Codex hook/rule/skill/agent surfaces are adapters over that boundary: the hook queries
the kernel, generic read-only roles are selected from evidence/risk, and no adapter is
an independent lifecycle, scope, evidence, or permission authority. Live hook trust and
coverage still require per-runtime observation.

## Hosted deterministic verification

GitHub-hosted Linux and Windows jobs continuously exercise the repository-owned
deterministic kernel suite. Their trust boundary ends at verified checkout behavior:
static hooks/fixtures and an explicit `UNVERIFIED_RUNTIME` smoke result do not prove
live Codex hook loading, trust, delivery, enforcement, or runtime activation. The
workflow carries no model credentials and performs no model execution, preserving
`ZERO_INCREMENTAL_COST`.
