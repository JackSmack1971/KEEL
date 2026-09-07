# Proposal

## Problem / why

The authoritative upgrade audit identifies four unresolved P0-owned requirement groups: portable verification and extracted-package behavior (rows 14–15), installation/upgrade/compatibility foundations (rows 16–17), framework-versus-consumer state separation (row 30), and reproducible environment/supply-chain foundations (rows 39–40). Existing lifecycle compatibility and schema-migration primitives are only partial foundations, and `.keel/config.json` still contains creator-machine absolute verification paths.

## Objective

Implement and land exactly one authoritative P0 — Portable Verification and Bootstrap Contract change. The implementation removes creator-machine verification assumptions, separates canonical verification from D1, classifies Git/bootstrap/package/version states deterministically, and establishes repository-owned provenance for generated bootstrap state.

## Non-goals

No P1–P7 work, P4 runtime/provider execution, D1 benchmark/evaluation execution, hooks, installer/distribution orchestration, or external integration.

## Success evidence

Portable verification/bootstrap/package/compatibility tests pass, canonical verification contains no D1 or creator-machine absolute path, generated state is produced through the repository-owned manifest command, the committed tree verifies, and the change is sealed and anchored.

## Open decisions

Future implementation must resolve newly discoverable verification commands only through the deterministic discovery contract in the ExecPlan and record the resolved commands before P0 completion. No command may be guessed, and no later workstream may be pulled into P0.
