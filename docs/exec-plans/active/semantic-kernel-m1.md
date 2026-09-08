# ExecPlan: Canonical KEEL semantic kernel M1

Status: `ACTIVE`
Authority: `KEEL-KERNEL-REDESIGN-v1`, stage `M1 — Contract fixtures`

## Objective and success evidence
Implement an isolated, deterministic Python model layer for all canonical primitives and shared identity, provenance, serialization, digest, resource, schema, and orthogonal-state rules. Hostile tests and the unchanged canonical suite must independently disprove malformed acceptance, nondeterminism, host leakage, and compatibility drift.

## Non-goals
No default writer, graph store, reader migration, compatibility adapter, CLI route, mission_v2/repository-intelligence/evidence/runtime/ledger replacement, effect execution, authorization grant, or M2-M6 implementation.

## Verified context
The landed P0/P1/P2 implementations use separate legacy models and remain compatibility authority. The redesign contract requires the eleven primitive meanings, one future graph, exact subjects, orthogonal states, strict migration, and reader-before-writer sequencing. Python standard-library modules are the current KEEL implementation substrate.

## Assumptions to test
- A frozen dataclass model with a strict tagged-record decoder can express the full primitive minimum without coupling legacy subsystems.
- POSIX repository resource identity and explicit portable-value scanning can reject host-specific intent without filesystem inspection.
- Registering one focused test preserves every existing command and behavior.

## Risk / autonomy / permission boundaries
High control-plane/migration risk but local and reversible. Validation is pure and may not inspect filesystem, environment, clock, network, Git, or providers. The new module is not an authorization or execution surface. No external effect is requested.

## Milestones
### M1 — Model contract
- Action: define schema/identity/resource/provenance/value/state and eleven primitive dataclasses.
- Observation: each record has one canonical tagged representation and strict decoder.
- Verification: round-trip test for every kind.
- Exit criteria: no overloaded status field or missing primitive.

### M2 — Determinism and hostile validation
- Action: implement canonical JSON, digest, portable intent, reference, and collection validation.
- Observation: equal semantic mappings serialize and digest identically; malformed input blocks.
- Verification: hostile cases cover unknown fields, schema/version, paths, host values, provenance, duplicate/dangling IDs, and ordering.
- Exit criteria: focused test passes without filesystem/external effects.

### M3 — Compatibility and lifecycle evidence
- Action: add the focused test to canonical verification, regenerate only declared generated provenance, update the architecture fact, and run KEEL verification.
- Observation: existing modules and CLI are untouched.
- Verification: all canonical checks pass; scope/evidence graph pass.
- Exit criteria: exact committed tree is sealed, locally integrated as authorized, and anchored.

## Baseline
Base commit: `cd5974e5ab5a4b4b9bb37c9fb77101bcf448555b`. Worktree began clean on branch `work`; active change is `semantic-kernel-m1`.

## Progress log
- 2026-09-08: read the authoritative redesign, lifecycle, architecture, command, generated-artifact, and prior P2 contract evidence; established clean baseline and passed Discuss.

## Decision log
- Use an isolated standard-library module rather than changing `keel_core.py`, keeping the new layer independently testable and non-authoritative during M1.
- Represent references as canonical identity strings and resources as typed `repo:<path>` identities.
- Canonical serialization sorts object keys and semantically unordered set-like fields; ordered domain fields remain ordered.

## Failure branches / blockers
Any legacy regression, manifest drift, unknown-field acceptance, nondeterministic bytes, filesystem access in validation, host-specific portable intent, or missing evidence coverage blocks verification. Scope/intent changes require re-plan.

## Final verification
Run the focused test, canonical KEEL verify, inspect evidence and scope, commit the verified tree, seal the exact commit, integrate locally because the user explicitly requested it, and anchor the landed commit.

## Completion / handoff
The landed result is an M1 model/fixture surface only. M2 readers and all subsystem migrations require separate governed changes.
- 2026-09-08: implemented all eleven isolated record kinds, strict authoritative decoding, canonical encoding/digests, pure collection/reference validation, and hostile tests; registered the focused check and regenerated the bootstrap manifest through its producer.
- 2026-09-08: first full verification exposed a pre-existing POSIX failure in the P0 Windows absolute-path portability fixture; re-planned a narrow lexical compatibility correction rather than weakening acceptance.
