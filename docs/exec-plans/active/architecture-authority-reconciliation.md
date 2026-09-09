# KEEL architecture authority reconciliation

Status: `ACTIVE`
Change: `architecture-authority-reconciliation`

## Objective

Establish one forward architecture/product-contract/roadmap authority that
describes landed KEEL reality, the Codex/KEEL boundary, cost invariant, stable
integration policy, and the NS0–NS11 sequence. Preserve conflicting documents as
historical evidence while explicitly superseding them, and reconcile stale plan
status without changing implementation behavior.

## Non-goals

- No NS1–NS11 feature implementation.
- No runtime, dependency, refactor, API, billing, provider, or cleanup change.
- No remote push, merge, PR close, or published-history rewrite.

## Affected surfaces

- `docs/control-plane/` authority and index documents.
- Root architecture/control-plane/workflow navigation.
- Forward-looking research and execution-plan status markers.

## Risk and controls

This is high-risk control-plane documentation because future work will rely on
the authority. Controls are the canonical intent, direct inventory of conflicting
documents, explicit landed-versus-aspirational wording, documentation-only diff
inspection, `keel verify`, and independent review before sealing.

## Ordered work

1. Inventory current authorities, forward-looking documents, active plans, and
   landed implementation evidence.
2. Create the single forward authority with fixed decisions, scheduler
   clarification, verification distinction, and NS0–NS11 sequence.
3. Add supersession pointers to conflicting historical documents and update
   navigation to the new authority.
4. Reconcile active plans that describe landed work; preserve their history.
5. Inspect all acceptance criteria, run repository validation, verify the exact
   documentation/plan-only scope, commit, seal, and stop before remote landing.

## Completion criteria

All AC-01–AC-12 in the canonical intent have direct inspection or command
evidence. The resulting diff contains only documentation and plan metadata; no
implementation behavior changes.

## Failure exits

If a conflicting authority cannot be classified, a plan's lifecycle cannot be
reconciled without rewriting evidence, or any non-documentation path changes,
stop and re-plan rather than weakening the requirement.

## Progress and blocker

- The forward authority, supersession map, and landed-plan archive reconciliation
  are present in the declared documentation scope.
- Documentation contract tests pass. The amended goal explicitly authorizes the
  existing declared producer to regenerate `.keel/bootstrap-manifest.json` as a
  mechanical consequence of changed manifest-listed documentation.
- The manifest was regenerated only through `python3 .keel/bin/keel.py manifest
  --write`; the producer and verifier scope were not changed.
