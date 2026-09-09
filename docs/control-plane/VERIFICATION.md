# Verification Model

A change is not complete because an edit or command succeeded. Verification authority follows:

`Requirement -> EvidenceRequirement -> EvidencePlan -> Verifier -> EvidenceReceipt`

A green command suite is insufficient while any required property is unestablished.

Scheduler changes additionally require deterministic simulated-adapter evidence
for frontier legality, dependency/resource/workspace isolation, bounded recovery,
stale/resume behavior, and duplicate-dispatch prevention, plus a repository-local
smoke path that exercises isolated WorkUnit progression without external effects.

## Authority model

Evidence strength is ordered: `ASSERTED < INSPECTED < TESTED < RUNTIME_OBSERVED < INDEPENDENTLY_REVIEWED < FORMALLY_VERIFIED`. A requirement declares `minimum_evidence_authority`. A verifier and its receipt cannot establish a stronger or unrelated property than its registry declaration permits. Unsupported, weak, stale, mismatched, or missing evidence is `INCONCLUSIVE`, never an optimistic pass.

## Verifier registry

`.keel/config.json.verifier_registry` declares every available Verifier with stable identity/version, provider type, evidence authority, supported requirement/provider classes, path/risk applicability, normalized command runtime contract, provenance, and whether it belongs to the mandatory kernel. Duplicate identities or invocations and malformed declarations fail closed.

The mandatory kernel is intentionally small: repository health, portable bootstrap contract, manifest producer, and compatibility inventory. Kernel success preserves self-integrity but does not satisfy unrelated EvidenceRequirements.

## EvidenceRequirement and EvidencePlan

Each requirement yields an `EvidenceRequirement` containing its exact requirement identity, minimum authority, type, impacted implementation surfaces, and acceptance-authorized verifier/provider choices. The EvidencePlanner combines these contracts with changed paths, risk, repository facts, and registry applicability. It deterministically chooses the least sufficient authority (then stable identity) for each requirement and adds mandatory kernel verifiers. Uncovered requirements make the plan `INCONCLUSIVE` before execution.

The selected `evidence-plan.json` replaces the flat run-every-command model. Checks are selected by requirement and impact; historical, irrelevant checks do not run forever.

## EvidenceReceipt

Every executed verifier emits a receipt in `evidence-receipts.json` containing:

- verifier identity, version, provider, declared authority, and provenance;
- exact Git/worktree subject including base/head, changed paths, and content digest;
- intent digest;
- environment/runtime fingerprint;
- normalized argv/cwd/timeout invocation without shell interpolation;
- literal `PASS`, `FAIL`, or `INCONCLUSIVE` result;
- bounded observations and artifact references;
- the EvidenceRequirements it is allowed to establish;
- start/end runtime metadata; and
- an immutable-content receipt digest.

Receipt evaluation rechecks integrity, exact subject, intent, result, declared authority, and planned establishment scope. A passing verifier cannot satisfy a requirement it was not selected and authorized to establish.

## Public lifecycle and KEEL write-change rule

The user-facing lifecycle reports `SEALED`, `LANDABLE`, `INTEGRATING`, and `LANDED`.
These are evidence states, not proof of behavioral correctness: `SEALED` binds a
verified candidate, `INTEGRATING` binds a landing transaction, and `LANDED` means the
resulting tree matched the landing attestation.

`python3 .keel/bin/keel.py verify` validates governance/scope/authorization, derives the plan, executes only selected verifiers, emits receipts, evaluates requirement coverage, and reaches `SHIP` only when every required property is established. Changed implementation or intent invalidates the exact subject and requires fresh receipts.

## Compatibility during migration

`verification.json`, `verification.md`, and `evidence-graph.json` remain generated compatibility projections for seal/anchor and existing views. They are not verification authority. `python3 .keel/bin/keel.py evidence` reads the receipt set. Historical ledgers remain readable and are not rewritten.

Candidate sealing semantics remain unchanged: sealing consumes the compatibility projection's exact content digest and independently checks the committed tree. Landed anchoring remains a distinct boundary.

## Completion blockers

Missing evidence, uncovered requirements, insufficient authority, `FAIL` or `INCONCLUSIVE` receipts, subject/intent drift, invalid registry/plan/receipt integrity, missing authorization, out-of-scope changes, or unauthorized effects block completion.

## Hosted CI evidence boundary

The Linux/Windows deterministic workflow is a clean-environment repository-behavior
proof surface. Its static Codex fixtures and hook wire-contract tests prove only
repository contracts. Its runtime smoke path is deliberately non-executing and
reports `UNVERIFIED_RUNTIME`; therefore hosted CI is not evidence of live Codex
availability, project/hook trust, hook delivery, enforcement, or model execution.
Those claims still require separate per-runtime observation under the runtime trust
contract.
