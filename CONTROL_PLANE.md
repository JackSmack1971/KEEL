# Codex Control Plane

State: `BOOTSTRAPPED_WITH_KEEL_ENFORCEMENT_PENDING_RUNTIME_TRUST_VALIDATION`

The control plane is the repository's information architecture, change-governance spine, and feedback system. It remains stack-neutral until project evidence activates specialized domains.

## Layer map
1. Repository legibility — thin entry points, indexed durable knowledge.
2. KEEL spec ledger — delta-native proposal/scope/risk/effects/evidence per write change.
3. Architectural enforcement — stable invariants become tested mechanical checks.
4. Capability extension — repo skills and narrow subagents.
5. Runtime legibility — logs/metrics/traces/browser/hardware evidence when relevant.
6. Work isolation — one write-owner per change/worktree; read-heavy subagent fan-out.
7. Orchestration — issue-driven scheduling only after tracker/runtime/workspace prerequisites exist.
8. Production feedback — reviewed traces/corrections -> findings -> evals -> bounded tasks.
9. Entropy control — recurring docs/quality gardening and promotion of repeated feedback into rules.

## Kernel transition freeze

Feature expansion above landed P2 is frozen. [`docs/control-plane/KERNEL_REDESIGN.md`](docs/control-plane/KERNEL_REDESIGN.md) is the sole forward architecture and migration authority; existing P0/P1/P2 surfaces remain governing current behavior until deterministic migration lands.

## Core maps
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
