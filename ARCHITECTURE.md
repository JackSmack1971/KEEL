# Architecture

Status: `VERIFIED — CANONICAL KEEL KERNEL`

KEEL is a dependency-free, repository-local change-governance kernel. It has one
normal CLI (`.keel/bin/keel.py`), one canonical change ledger, and one semantic
vocabulary. Historical v1 *ledgers* are inputs to a versioned migration reader; there
is no v1 mission/runtime product path.

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
