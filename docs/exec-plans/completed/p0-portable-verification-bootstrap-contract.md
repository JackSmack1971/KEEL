# ExecPlan: P0 — Portable Verification and Bootstrap Contract

Status: `COMPLETE / LANDED`

## Authority and lifecycle boundary

This is the one authoritative active ExecPlan for P0. It is subordinate to [`docs/control-plane/UPGRADE_AUDIT.md`](../../control-plane/UPGRADE_AUDIT.md) for requirement identity, classification, evidence, and unresolved gaps, and subordinate to [`upgrade-remaining-plan.md`](upgrade-remaining-plan.md) for roadmap boundaries and dependency order.

KEEL change: `p0-portable-verification-bootstrap-contract`.

This plan authorized the bounded P0 implementation. Completion is proven only by the landed KEEL verification, seal, and anchor evidence below. P1 was not started. P4 remains `BLOCKED`; D1 remains `DEFERRED`; this plan authorized no runtime/provider, benchmark, evaluation, empirical, or external work.

## Objective and success evidence

Remove creator-machine dependencies and establish reliable portable verification, bootstrap-state classification, non-Git state handling, framework/consumer artifact boundaries, and version/compatibility contract foundations.

P0 is complete only when the implementation is verified on the committed tree with deterministic positive and negative evidence, the resolved canonical verification commands are recorded, generated dependents are closed through declared producers, only authorized P0 paths changed, runtime-unavailable evidence is classified, and the KEEL change is independently verified and lifecycle-complete. A plan, documentation claim, or lifecycle phase alone never proves completion.

## Requirement mapping — exactly once

| Audit identity | Classification | Strongest existing evidence | Residual P0 gap | Planned completion evidence |
|---|---|---|---|---|
| Rows 14–15 — Portable verification and extracted-package behavior | `PARTIAL`, owner `P0` | Local checks and KEEL verification configuration exist in `.keel/config.json`; `docs/control-plane/COMMANDS.md` requires repository-owned argv and forbids guessing. Current config contains creator-machine absolute paths under `C:/Users/click/...`. Existing lifecycle/runtime primitives and tests are repository-local but do not prove copied/extracted portability. | Canonical verification must resolve without creator-machine absolute paths; repository-owned, discovered, unsupported, ambiguous, unavailable, and unauthorized command states need deterministic outcomes; extracted/non-Git package behavior needs direct proof. | Focused P0 positive/negative tests, package/bootstrap checks, command-resolution report with provenance and exact argv, strict validation, KEEL verification, and copied/extracted-tree evidence. Absolute creator paths must be absent from the canonical portable contract. |
| Rows 16–17 — Installation, upgrade, and compatibility contract | `PARTIAL`, owner `P0` | `.keel/lib/lifecycle.py` reports `COMPATIBLE` or `MIGRATION_REQUIRED` and inventories framework/config/contract/ledger/skill/bootstrap schemas. `.keel/lib/schema_migrations.py` provides read-only preflight, apply, backup, rollback, and unsupported-schema rejection; `test_lifecycle_compatibility.py` and `test_schema_migrations.py` pass as existing foundations. | Foundational deterministic interpretation for compatible, incompatible, unsupported, missing metadata, and migration-required states is incomplete; full installer/live distribution orchestration is out of scope. | Focused compatibility/bootstrap tests cover each state and prove read-only inspection versus authorized migration boundaries; exact outputs/statuses and no silent migration are recorded. |
| Row 30 — Separate framework history from consumer-repository state | `PARTIAL`, owner `P0` | Historical plans are archived under `docs/exec-plans/completed/`; `.control-plane/bootstrap-manifest.json` and repository layout provide a control-plane package surface. No verified package manifest contract currently proves separation of framework, consumer, generated, machine-local, historical, and runtime state. | A distributable/bootstrap package must exclude creator-repository ledgers, consumer-specific/generated state, machine-local paths, and historical/runtime metadata unless explicitly classified as framework content. | Package-boundary inventory and tests over a clean extracted/bootstrap fixture, with deterministic prohibited-artifact findings and no creator-state leakage. |
| Rows 39–40 — Reproducible environment and supply-chain attestation | `PARTIAL`, owner `P0` | Worktree/environment primitives exist; `docs/control-plane/ENVIRONMENTS.md` requires declared setup/start/stop/isolation rather than inference. `docs/control-plane/TESTING_CI_GENERATED.md` requires named generated sources/producers/triggers/drift checks. Current capability discovery is advisory and reports unknown toolchain/generated-artifact evidence. | P0 needs portable environment/version provenance and bounded attestation foundations for verification/package outputs, with runtime/provider unavailability represented explicitly; it must not invent supply-chain proof or execute D1 evaluation. | Deterministic provenance/attestation artifact or report, generated-artifact closure evidence, clean-tree/reproducibility checks, and `VERIFIED`/`FAILED`/`BLOCKED`/`UNVERIFIED_RUNTIME` classification with direct evidence. |

No contextual, complete, superseded, P1–P7, P4-blocked, or D1-deferred row is implementation work in this plan.

## Dependencies and prerequisites

- P0 has no prior upgrade-workstream dependency. It does not depend on P1, P2, P3, P4, P5, P6, P7, or D1.
- Required starting evidence: clean or explicitly baselined Git worktree, initial commit, passing `python3 .keel/bin/keel.py doctor`, authoritative audit/roadmap documents unchanged except by an explicitly re-planned authority change, and one active KEEL change owner/worktree.
- The current creator-machine absolute paths in `.keel/config.json` are a known P0 target, not a prerequisite to be silently accepted.
- If implementation discovers a concrete prerequisite that contradicts the roadmap or requires another workstream, stop and report the contradiction; do not widen P0 silently.

## Repository-relative implementation scope

Expected future P0 implementation surfaces, subject to the KEEL change `scope.txt` and re-plan before implementation:

- `.keel/bin/keel.py`, `.keel/lib/` modules owning command resolution, bootstrap/Git classification, package boundaries, version/compatibility, and provenance; no unrelated P1 intelligence or P4 dispatch.
- `.keel/config.json` and repository-owned command/compatibility metadata needed to remove absolute creator paths; exact changed files must be declared before execution.
- Focused P0 tests under `.keel/tests/` for positive, negative, extracted-package, non-Git, compatibility, artifact-boundary, and reproducibility behavior.
- A bounded package/bootstrap fixture or test data path only if required by the implementation and declared before execution.
- Documentation surfaces only where the implemented contract is authoritative, principally `docs/control-plane/COMMANDS.md`, `ENVIRONMENTS.md`, `RELEASE_OPERATIONS.md`, `TESTING_CI_GENERATED.md`, and the relevant active P0 plan/ledger.

Expected generated-artifact surface:

- `.control-plane/bootstrap-manifest.json` is a potential deterministic dependent of bootstrap/package source changes and is included in the future closure only if a declared producer or deterministic producer-discovery rule proves that relationship. The current repository contains no producer declaration for it; implementation must not hand-edit it or claim regeneration until provenance is established.
- `.keel/knowledge/repository-map.json` is a derived navigation artifact produced by `python3 .keel/bin/keel.py map`; it is not automatically authorized for P0 and may be included only if a changed P0 source/configuration deterministically requires regeneration and the scope is re-planned.
- No generated artifact may be hand-edited. Each included dependent must record artifact path, producer, triggering source/configuration relationship, regeneration command or deterministic producer discovery, and drift/integrity verification.

Explicitly excluded from this change and from P0 implementation: `.keel/bench/`, `keelbench` execution/corpus/evaluation/scoring, P1 repository intelligence, P2 mission schema/planning, P3 runtime handshake, P4 mission execution/provider/authorization, P5 adaptive workflow/context, P6 broader verification/lifecycle strengthening, P7 observability/feedback, application/runtime implementation, hooks, remote/external operations, installer/distribution orchestration beyond foundational contract behavior, and any path not authorized by the active KEEL scope.

## Required implementation behavior

### Portable verification and command resolution

- Canonical commands must use repository-relative argv and portable runtime resolution; creator-machine absolute paths are rejected as non-portable findings.
- Resolution precedence is deterministic: an explicit repository-owned declaration wins; if absent, a repository-owned command discovered with provenance may be selected only when exactly one candidate is valid and executable; otherwise the result is `UNSUPPORTED`, `AMBIGUOUS`, `UNAVAILABLE`, or `UNAUTHORIZED` as applicable.
- A discovered command is valid only when its source is inside the repository or an explicitly declared portable runtime contract, its argv is literal/no shell interpolation, its purpose matches the verification surface, and its executable/runtime is available.
- Missing commands/runtimes and unsupported surfaces produce a non-passing status with actionable evidence. No guessed command, fallback success, or silent skip is permitted.
- The configured absolute paths currently present in `.keel/config.json` must be replaced or classified by the implemented portable contract; P0 completion requires proof that the canonical contract no longer depends on creator-machine paths.

### Repository-owned validator/discovery contract

The contract must distinguish declared commands, discovered commands, unsupported states, ambiguous states, execution availability, and authorization. It must remain foundational and repository-local; semantic repository intelligence and broad change-aware selection belong to P1/P6.

### Bootstrap and non-Git state

The implementation must deterministically classify valid Git, non-Git, incomplete bootstrap, malformed bootstrap, copied/extracted KEEL package, and Git-required operation without Git authority. `NOT_A_GIT_REPOSITORY` must be distinct from ordinary Git command failure, corruption, or an unavailable Git executable. Git-independent inspection/bootstrap operations must remain usable without Git; Git-required operations must return an explicit blocked/not-authorized state rather than a generic verification failure.

### Framework/consumer boundary

The package contract must classify framework-owned/distributable artifacts, consumer state, generated consumer artifacts, machine-local state, historical/runtime metadata, and prohibited leakage. A clean package/bootstrap fixture must not inherit creator-repository ledgers, absolute paths, consumer output, local caches, runtime traces, or historical artifacts unless explicitly declared framework content.

### Version and compatibility foundations

The contract must deterministically report `COMPATIBLE`, `INCOMPATIBLE`, `UNSUPPORTED`, `MISSING_METADATA`, or `MIGRATION_REQUIRED` as applicable. Compatibility inspection is read-only; migration requires an explicitly authorized KEEL change and must preserve backup/rollback behavior. Full installer, registry, live upgrade orchestration, and distribution publishing remain excluded.

## Exact verification commands and discovery rule

Commands currently knowable from repository evidence:

- `python3 .keel/bin/keel.py gate plan` — validates this standard change’s planning contract and keeps the change in `PLAN` until implementation is authorized separately.
- `python3 .keel/bin/keel.py doctor` — must exit `0` with `{"status":"PASS","errors":[]}`.
- `python3 C:/Users/click/.agents/skills/codex-control-plane-bootstrapper/scripts/validate_control_plane.py --root . --strict-manifest --require-keel-runtime` — current strict control-plane validation command; it must exit `0` with no errors. Its creator-machine path is a current portability finding to remediate in P0’s implementation; it is not a portable future canonical command.
- `python3 .keel/bin/keel.py next` and `python3 .keel/bin/keel.py status` — read-only lifecycle truth checks; after this planning turn they must identify this change, its `PLAN` phase, and no implementation/verification claim.
- `python3 -B .keel/tests/test_lifecycle_compatibility.py` — existing partial-foundation compatibility tests; expected exit `0` on the current tree.
- `python3 -B .keel/tests/test_schema_migrations.py` — existing partial-foundation migration tests; expected exit `0` on the current tree.
- `git diff --check` — expected exit `0`.
- `git status --short --branch` and `git diff --name-only <base-commit>` — changed-path truth checks; this planning turn may contain only the active P0 plan plus KEEL-owned lifecycle metadata, and no P0 implementation-bearing file.

The implementation must first discover the final canonical command set by inspecting `.keel/config.json`, `docs/control-plane/COMMANDS.md`, repository-owned scripts/task definitions, and declared producers. Resolution must prefer an explicit repository-owned declaration, then one uniquely provenance-bearing repository-owned discovery; zero candidates is `UNSUPPORTED`/`UNAVAILABLE`, multiple valid candidates is `AMBIGUOUS`, and a candidate whose provenance or authorization cannot be proven is `UNVERIFIED_RUNTIME`/`BLOCKED`. The exact resolved argv, source/provenance, runtime availability, authorization requirement, and expected exit/status must be recorded in the P0 ledger/verification evidence before P0 can complete. Never guess and never convert unavailable verification to `PASS`.

Do not run `keel.py verify` for this planning-only turn if its current configured command set would execute `.keel/bench/` tests or validation: D1 execution is explicitly prohibited. The future P0 implementation must re-plan the canonical command set so required P0 checks are exact and D1 remains excluded.

## Acceptance criteria and expected behavior

1. Rows 14–15, 16–17, 30, and 39–40 appear exactly once in the P0 requirement map; no P1–P7 or D1 requirement is mapped.
2. The creator-machine absolute verification paths in `.keel/config.json` are detected as a negative case and are absent from the final portable canonical contract; any temporary compatibility/reporting behavior is explicit and non-passing until resolved.
3. Positive command resolution returns a repository-owned, provenance-bearing, executable argv and a `VERIFIED` finding with exit `0`.
4. Unsupported, unavailable, ambiguous, unproven, or unauthorized command resolution returns the named non-passing status and actionable finding; it never returns `VERIFIED`.
5. Git/bootstrap classification distinguishes valid Git, `NOT_A_GIT_REPOSITORY`, ordinary Git failure/corruption, incomplete bootstrap, malformed bootstrap, copied/extracted package, and Git-required operation without authority, with the expected operation-specific status.
6. Framework/consumer packaging checks reject consumer-specific state, generated consumer artifacts, machine-local paths/state, and historical/runtime metadata in a distributable package with explicit failure findings.
7. Compatibility checks distinguish compatible, incompatible, unsupported, missing metadata, and migration-required states; inspection is read-only and migration is authorization-bound.
8. Generated dependents are either regenerated by a declared producer and drift-checked, or the absence of a producer is recorded as `BLOCKED`/`UNVERIFIED_RUNTIME`; no hand-edited generated artifact passes.
9. Runtime/provider/environment unavailability uses only the established vocabulary: `VERIFIED`, `FAILED`, `BLOCKED`, or `UNVERIFIED_RUNTIME`, with direct evidence and no silent pass.
10. The final implementation diff is contained within the authorized P0 scope, and the committed/landed tree independently reproduces the verified path and intent digest.

## Required negative/failure acceptance cases

- Portable resolution: absolute creator path; unavailable configured command; multiple ambiguous candidates; discovered command whose repository provenance/appropriateness cannot be proven. Expected outcomes are explicit non-passing `FAILED`, `BLOCKED`, `UNSUPPORTED`, `AMBIGUOUS`, `UNAVAILABLE`, or `UNVERIFIED_RUNTIME` findings as applicable, never success.
- Bootstrap/Git: non-Git directory; Git present but command fails for a reason other than `NOT_A_GIT_REPOSITORY`; incomplete bootstrap; malformed bootstrap metadata. Expected outcomes distinguish `NOT_A_GIT_REPOSITORY`, `FAILED`, `BLOCKED`, and `UNSUPPORTED` rather than collapsing them into generic verification failure.
- Artifact boundary: framework package containing consumer state; generated consumer artifact classified as distributable framework content; machine-local path/state in package metadata; creator ledger/history/runtime metadata leakage. Expected outcome is a deterministic package-boundary failure naming the prohibited artifact.
- Compatibility: incompatible KEEL/version; unsupported compatibility metadata; missing required compatibility metadata; migration-required state. Expected outcomes are `INCOMPATIBLE`, `UNSUPPORTED`, `MISSING_METADATA`, and `MIGRATION_REQUIRED`; no silent migration or compatibility pass.
- Generated closure/runtime: known generated dependent without a declared producer, unavailable runtime/provider, and attempted D1/benchmark evidence. Expected outcomes are `BLOCKED` or `UNVERIFIED_RUNTIME`, and D1 remains `DEFERRED`.

## Baseline, risk, rollback, and recovery

Before implementation, record the clean-tree/base commit, current `doctor`, `next`, strict validation, compatibility/migration test, and configured-command baseline. Separate pre-existing absolute-path and runtime-trust findings from introduced failures.

The implementation must be local and reversible through the normal KEEL/Git lifecycle. If bootstrap/package compatibility regresses, stop before distribution, preserve the failing fixture/evidence, revert the implementation commit or restore the prior contract through a new authorized change, and re-run the full P0 acceptance matrix. Do not delete consumer data, rewrite published history, or apply migrations implicitly.

## Milestones

### M1 — Reconfirm authority and baseline

- Action: Re-read the audit and roadmap, confirm one P0 owner/change/worktree, and capture baseline commands.
- Verification: Audit rows and roadmap boundaries match this plan; no contradiction.
- Exit criteria: baseline evidence is durable and P0 scope is unchanged.

### M2 — Implement portable verification/bootstrap foundations

- Action: Modify only the re-planned P0 implementation surfaces; remove absolute creator dependencies and implement deterministic command/bootstrap/Git classification.
- Verification: focused positive/negative tests and resolved-command evidence.
- Exit criteria: portable and bootstrap acceptance criteria pass or are explicitly blocked with evidence.

### M3 — Implement artifact and compatibility foundations

- Action: Add only bounded package-boundary, provenance, version/compatibility, and migration-state behavior.
- Verification: clean extracted-package checks, compatibility/migration tests, generated closure, and runtime availability classification.
- Exit criteria: artifact/compatibility criteria pass; no installer/P1/P4/D1 scope expansion.

### M4 — Independent verification and lifecycle completion

- Action: Run exact P0 command set, strict validation, doctor, changed-path checks, committed-tree verification, and independent review.
- Verification: KEEL evidence graph resolves every required AC; seal/anchor only through authorized later lifecycle actions.
- Exit criteria: P0 is independently verified complete and lifecycle-complete before P1 becomes eligible.

## Completion evidence contract

Durable completion requires the P0 ledger’s `requirements.json`, `acceptance.json`, `scope.txt`, `verification.json`, `verification.md`, and `evidence-graph.json`; focused P0 test output including all required negative cases; baseline and final command-resolution/provenance reports; bootstrap/package fixture results; compatibility/migration results; generated-artifact producer/regeneration/drift evidence; runtime-unavailability classification; strict validation and doctor output; changed-path and committed-tree digest evidence; independent review; and final KEEL lifecycle evidence. `VERIFIED` requires direct evidence; `FAILED` records a reproducible defect; `BLOCKED` records a missing prerequisite/authorization; `UNVERIFIED_RUNTIME` records unavailable runtime/provider evidence. None may be converted to `PASS` by plan status.

The explicit completion gate is: all required P0 ACs resolve through deterministic evidence, no prohibited negative case passes, all changed paths are P0-authorized, generated closure is complete, no P1/P4/D1 work occurred, the exact committed tree matches verification evidence, and the P0 KEEL change is independently verified and lifecycle-complete. Only then may a separately authorized P1 change begin.

## Progress / decision / blocker log

- Instantiation: active KEEL change and this single active P0 ExecPlan are created by the authorized planning turn.
- Implementation: not started by this turn.
- P0 dependency status: no predecessor required.
- P4: remains `BLOCKED`.
- D1: remains `DEFERRED`.
- Any audit/roadmap contradiction, missing generated producer, unavailable runtime/provider, or out-of-scope dependency discovered during implementation is a blocker requiring evidence and re-planning, not an implicit scope expansion.

## Final handoff

P0 implementation, verification, sealing, landing, and anchoring are complete under the KEEL change `p0-portable-verification-bootstrap-contract`. See the ledger's `verification.json`, `evidence-graph.json`, seal evidence, and landed anchor for the authoritative completion record.
