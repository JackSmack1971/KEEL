# Verification Model

A change is not complete because an edit or command succeeded. Verification authority follows:

`Requirement -> EvidenceRequirement -> EvidencePlan -> Verifier -> EvidenceReceipt`

A green command suite is insufficient while any required property is unestablished.

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

## KEEL write-change rule

`python3 .keel/bin/keel.py verify` validates governance/scope/authorization, derives the plan, executes only selected verifiers, emits receipts, evaluates requirement coverage, and reaches `SHIP` only when every required property is established. Changed implementation or intent invalidates the exact subject and requires fresh receipts.

## Compatibility during migration

`verification.json`, `verification.md`, and `evidence-graph.json` remain generated compatibility projections for seal/anchor and existing views. They are not verification authority. `python3 .keel/bin/keel.py evidence` reads the receipt set. Historical ledgers remain readable and are not rewritten.

Candidate sealing semantics remain unchanged: sealing consumes the compatibility projection's exact content digest and independently checks the committed tree. Landed anchoring remains a distinct boundary.

## Completion blockers

Missing evidence, uncovered requirements, insufficient authority, `FAIL` or `INCONCLUSIVE` receipts, subject/intent drift, invalid registry/plan/receipt integrity, missing authorization, out-of-scope changes, or unauthorized effects block completion.
