# Architecture

Forward authority: [KEEL forward architecture, product contract, and roadmap](docs/control-plane/KEEL_FORWARD_AUTHORITY.md).
This file records verified current implementation boundaries; it is not a
separate forward roadmap authority.

Status: `VERIFIED — CANONICAL KEEL KERNEL`

KEEL is a dependency-free, repository-local change-governance kernel. Its public
contract is a small JSON CLI projection over one canonical change ledger; schema
versions and subsystem history are compatibility implementation details. Historical
v1 *ledgers* are inputs to a versioned migration reader; there is no v1 mission/runtime
product path.

## Canonical components

- `.keel/lib/semantic_kernel.py` defines canonical primitive identity, provenance,
  normalization, serialization, and explicit unknown states.
- `.keel/lib/change_graph.py` owns requirement/work/effect planning and typed edges.
- `.keel/lib/fact_graph.py` owns repository facts, dependency/ownership projections,
  capability candidates, impact, and freshness. `keel.py facts` is its direct CLI view.
- `.keel/lib/evidence_system.py` owns EvidencePlans and exact-subject receipts.
- `.keel/lib/runtime_authorization.py` owns RuntimeProfile observations and
  CapabilityGrant evaluation without claiming confinement or executing effects.
- `.keel/lib/git_proof.py` and `.keel/lib/candidate_attestation.py` own repository,
  worktree, tree, commit, candidate, landing, landed, ref, note, and attestation proof.
- `.keel/lib/canonical_ledger.py` owns intent/events/grants/receipts/attestations and
  the narrow `keel.legacy-ledger/v1` migration reader.
- `.keel/lib/keel_core.py` orchestrates lifecycle transitions. The Codex hook is a
  thin adapter through `.keel/lib/codex_adapter_kernel.py`.
- `.keel/lib/scheduler.py` reconciles desired ChangeGraph WorkUnits with persisted
  actual state and computes/dispatches a bounded legal frontier through injected
  Codex/runtime adapters.

## Boundaries

The public UX is intentionally stack-neutral: KEEL governs intent, authorization,
evidence, and Git state but never invents a consumer build/test/runtime architecture.
KEEL-owned runtime and ledger files, project-owned policy/configuration, generated
cache/state, and durable historical ledger/ref/note data have separate ownership and
retention rules. Policy packs under `policies/templates/` are opt-in consumer
scaffolding, not KEEL runtime policy.

Facts and generated views do not become policy. Plans and EffectRequests do not grant
permission. Hooks are not confinement. SHIP is eligibility rather than integration
permission. Malformed canonical or legacy state fails closed; absence and uncertainty
remain explicit. Repository-relative path normalization and one-writer-per-worktree
isolation are enforced mechanically. A sealed candidate attests only to its own
verified material. A LandingAttestation separately binds target base T0, synthetic
integration tree I, integration evidence, and the expected landing mechanism;
landing completion is recorded only after the actual landed tree matches I.

Optional maintenance lives under `.keel/maintenance/`. Reusable consumer-project
policy templates live under `policies/templates/`. Historical bootstrap research
lives under `docs/references/research/`; neither surface is product authority.
