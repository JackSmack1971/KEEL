# Change public-ux-portability

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Refactor KEEL public UX, documentation, packaging, portability, and installation around the redesigned kernel

## Requirements
- `REQ-1` The normal CLI converges on init, doctor, start, status, next, run, verify, land, explain, and audit; internal schema/versioned subsystem commands are compatibility-only or hidden from normal help.
- `REQ-2` Public commands emit stable machine-readable JSON contracts with explicit status and no schema-history-shaped normal interface.
- `REQ-3` keel explain exposes why an action is allowed, blocked, waiting, stale, or escalated, and keel audit reconstructs intended -> authorized -> executed -> verified -> integrated -> landed provenance.
- `REQ-4` Public lifecycle status clearly distinguishes SEALED, LANDABLE or INTEGRATING, and LANDED.
- `REQ-5` Installation is deterministic; ownership classes distinguish KEEL-owned files, project-owned policy/config, generated cache/state, and durable historical ledger data; upgrades and migrations are safe and loss-preserving.
- `REQ-6` Remote replication guidance documents KEEL custom refs, notes, and attestations where needed.
- `REQ-7` AGENTS.md remains a short navigational entry point; ARCHITECTURE.md describes KEEL itself; generic target-project policy scaffolding is explicit templates or policy packs.
- `REQ-8` CONTROL_PLANE.md, WORKFLOW.md, CODEX_NATIVE.md, VERIFICATION.md, ORCHESTRATION.md, and indexes match landed behavior and do not present obsolete Discuss/Plan/Execute/Verify/Ship terminology as the public user workflow.
- `REQ-9` Fresh installation is tested in representative disposable repositories and KEEL remains stack-neutral without inventing project commands or architecture.

## Non-goals
- Do not remove historical readers, ledgers, refs, notes, attestations, or migration provenance.
- Do not execute remote pushes, merges, releases, deployments, or migrations in consumer repositories.
- Do not invent project-language, framework, build, test, or deployment commands for stack-neutral repositories.
- Do not manually edit kernel-owned events, grants, receipts, attestations, or generated views.

## Scope
- `AGENTS.md`
- `ARCHITECTURE.md`
- `CONTROL_PLANE.md`
- `WORKFLOW.md`
- `.keel/bin/keel.py`
- `.keel/lib/**`
- `.keel/tests/**`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `.keel/README.md`
- `docs/INDEX.md`
- `docs/control-plane/**`
- `docs/exec-plans/active/**`
- `policies/**`

## Consequences
- Changes the public command contract, compatibility boundary, installation behavior, and durable control-plane documentation.
