# P1 — Repository Intelligence Foundation

Status: `IMPLEMENTATION IN PROGRESS`

## Authority and lifecycle boundary

This workstream is subordinate to the authoritative program documents:

1. [`docs/control-plane/UPGRADE_AUDIT.md`](../../control-plane/UPGRADE_AUDIT.md) is requirement and status authority.
2. [`upgrade-remaining-plan.md`](upgrade-remaining-plan.md) is program-roadmap and dependency authority.
3. This document is subordinate P1 execution authority.

This document never supersedes, replaces, archives, or relocates the global roadmap. The existing KEEL change is `p1-repository-intelligence-foundation`. Implementation, verification, sealing, landing, and anchoring remain governed by the KEEL ledger; P2 is not eligible from plan text alone.

## Requirement map

| Audit identity | Source | Status | P1 planning/implementation boundary |
|---|---|---|---|
| Section 8 | `docs/KEEL_UPGRADES.md` §8 | PARTIAL / P1 | Evidence-only repository graph and codebase mapping. |
| Section 12 | §12 | PARTIAL / P1 | Evidence-backed domain/adapter intelligence; no policy activation. |
| Section 13 | §13 | PARTIAL / P1 | Provenance-bearing repository command registry; no command execution. |
| Section 41 | §41 | PARTIAL / P1 | Read-only brownfield profile over repository evidence. |
| Sections 47–49 | §§47–49 | PARTIAL / P1 | Dependency, architecture, changed-path impact, and bounded history evidence. |

Each required identity is mapped exactly once. P0 is the evidenced prerequisite. P2 remains not instantiated; P3 is future; P4 is `BLOCKED`; P5, P6, and P7 remain future/unavailable through dependency shortcuts; D1 remains `DEFERRED`.

## Program dependency state

The global roadmap retains:

```text
P0 → P1 → P2 → P3 → P4
P1 → P5
P2 → P5
P3 → P5
P1 + P2 + P5 → P6
P6 → P7
```

D1 is not an active prerequisite. P1 completion cannot activate P2 without independent completion evidence and the roadmap’s established reconciliation.

## Canonical repository-intelligence contract

### Schema identity, location, ownership, and compatibility

The future canonical contract identity is `keel.repository-intelligence/v1` (serialized as `schema_id: "keel.repository-intelligence"` and integer `schema_version: 1`; this identity/version pair is the fallback when no more specific repository convention exists). The canonical contract is owned by the repository module `.keel/lib/repository_intelligence.py` and its versioned UTF-8 JSON output. The producer is the P1 read-only repository-intelligence collector in that module. Consumers are the repository-map projection, command/ownership/architecture/dependency/impact projections, generated-provenance checks, focused tests, and later read-only planning consumers. No consumer may treat an implementation-local model as a second authority.

The future validation interface is `repository_intelligence.validate(document, *, expected_schema="keel.repository-intelligence/v1") -> ValidationResult`, where `ValidationResult` reports structural, semantic, determinism, provenance, and unknown/conflict-state findings without mutation. The repository-native validation entry point must expose that interface through the declared P1 test/check command; no current command is claimed by this planning change.

The serialized format is UTF-8 JSON with an explicit `schema_version` and contract identifier. Version changes require an explicit compatibility classification (`compatible`, `migration-required`, or `unsupported`) and a migration decision before consumers change. The schema is validated by the repository-native JSON/schema validation used by P0 and focused P1 tests. Serialization is deterministic: UTF-8, LF line endings, canonical paths, lexicographically sorted object keys, arrays sorted by their defined keys, and no identity-bearing timestamps, hostnames, environment values, absolute paths, or process IDs.

### Nodes, facts, and relationships

Node identity is repository-relative and typed. Supported node classes are `repository`, `directory`, `file`, `module`, `symbol`, `package`, `service`, `test`, `command`, `configuration`, `dependency`, `ownership-source`, `architecture-source`, `generated-artifact`, and `runtime-surface` only when statically evidenced. A node contains `id`, `type`, `status`, and provenance; unavailable optional attributes are omitted or set to `UNKNOWN` according to the field contract, never guessed.

Canonical relationship classes are: `contains`/`member-of`, `declares`, `depends-on`, `generated-from`, `produced-by`, `owned-by`, `governed-by`, `architecture-source-for`, `command-declared-by`, and `references`. `impacts` and `impacted-by` are derived projections, not source facts. Edges have stable typed endpoints, relation, status, provenance, and derivation fields. Cycles are valid and represented; edges are never removed merely to force a DAG.

Facts are classified as `DIRECT` when observed from a named repository artifact or supported parser, `NORMALIZED` when canonicalized without changing meaning, and `DERIVED` when produced by an explicit rule over other facts. A derived edge must list its input fact identifiers and derivation rule. No semantic edge is emitted without repository evidence.

### Provenance and status

Every authoritative fact and edge includes `source_artifact`, `source_type`, `adapter`, `derivation_rule` (or `null` for direct facts), `fact_kind` (`DIRECT`, `NORMALIZED`, or `DERIVED`), and a stable source digest or location where available. Status vocabulary is `VERIFIED`, `UNKNOWN`, `UNSUPPORTED`, `UNAVAILABLE`, `UNVERIFIED_RUNTIME`, `AMBIGUOUS`, `CONFLICTING`, `FAILED`, `BLOCKED`, `STALE`, `PARTIAL`, or `HISTORICAL/SUPERSEDED` where applicable. Direct evidence remains distinguishable from normalized and derived output.

### Path normalization

All authoritative repository paths are repository-relative UTF-8 paths using `/`, with redundant `.` segments removed and `..` rejected after normalization if it would escape the repository root. Machine-local absolute paths are never identities; an absolute path is accepted only as an input that can be proven inside the current root and is immediately converted to a relative path, otherwise it is rejected/classified `UNKNOWN` or `FAILED` according to the input contract. Case is preserved and comparisons follow the repository/platform contract; case-colliding identities are `CONFLICTING` rather than silently merged. Symlinks are not followed into external roots; if supported, the link and resolved target are separate evidenced facts. Ignored/excluded paths may be reported as excluded evidence but cannot silently become authoritative graph members. Generated paths are ordinary relative paths plus generated provenance. Outputs are portable across machines and do not contain creator-machine prefixes.

### Deterministic serialization

Nodes sort by `(type, id)`, edges by `(relation, from, to, status, source_artifact, derivation_rule)`, and all maps use lexicographic key order. Duplicate facts are coalesced only when their canonical identity and provenance are identical; otherwise all conflict evidence is retained. Missing optional fields are omitted consistently or explicitly classified `UNKNOWN` as defined by the schema. Line endings, path separators, and Unicode encoding are normalized before serialization. Timestamps/environment values are excluded from identity-bearing output. Equal relevant repository state, configuration, and adapter versions produce byte-identical authoritative output.

## Source precedence and conflict semantics

### Commands

Command source classes are, in descending authority: `REPOSITORY_DECLARED`, `KEEL_CONFIG_DECLARED`, `PROJECT_METADATA_DERIVED`, and `DISCOVERED_CANDIDATE`. Every command record independently carries `exists`, `source_class`, `provenance`, `support`, `runtime_availability`, and `authorization`; none may be inferred from another field. Precedence applies only when sources describe the same command identity and do not conflict; conflicting authorities remain `CONFLICTING` unless an explicit repository contract resolves them. A present command can be unavailable; an available command can be unauthorized; a discovered candidate remains `UNVERIFIED_RUNTIME` until repository evidence proves it. Zero commands is an explicit empty registry with `UNKNOWN` availability, not an invented command. Machine-local absolute commands are non-portable/rejected. Unsupported metadata is `UNSUPPORTED`; ambiguous candidates are `AMBIGUOUS`; unavailable and unauthorized are preserved as exact independent outcomes rather than conflated with absence or unsupported status.

### Ownership

Ownership sources are repository-authoritative ownership contracts (for example, a valid repository ownership file), KEEL/config ownership declarations, supported project metadata, and descriptive/inferred evidence. Only explicitly authoritative sources govern decisions. Valid overlapping rules must be represented deterministically; unresolved overlap is `AMBIGUOUS`. Conflicting owners are `CONFLICTING`; malformed sources are `FAILED`; absence of a legitimate source is `UNKNOWN`. Ownership is never invented from author names, directory proximity, or current operator identity.

### Architecture

Architecture sources are (1) an explicitly authoritative architecture contract, (2) current descriptive architecture documentation, (3) implementation-derived structure, (4) generated architecture views, and (5) historical/superseded documents. Only (1) is governing authority by declaration. (2)–(4) are evidence unless explicitly promoted by a repository contract; implementation-derived structure never silently overrides explicit authority. Historical/superseded material is not current authority and is classified `HISTORICAL/SUPERSEDED`. Conflicting current authorities remain `CONFLICTING`; descriptive documentation cannot override explicit authority.

### Freshness

Freshness is explicit: current evidence is `VERIFIED`/`CURRENT`, generated evidence whose inputs changed is `STALE`, superseded documents are `HISTORICAL/SUPERSEDED`, outdated metadata is `STALE`, and unverifiable freshness is `UNKNOWN`. Stale evidence cannot be used as current authority without an explicit reconciliation result.

## Dependency, changed-path, and impact contracts

Dependency facts distinguish `DIRECT_DECLARED`, `DIRECT_PARSED`, `DERIVED`, `UNRESOLVED`, `EXTERNAL`, `GENERATED`, and `UNSUPPORTED_SOURCE`. Initial adapters are explicitly bounded to the evidenced Python semantic/import adapter in `.keel/lib/repository_map.py`, the JSON KEEL/config/bootstrap-manifest adapter in `.keel/lib/p0_contract.py`, the repository command-file/config adapter already used by `repository_map.py`, and the capability metadata adapter in `.keel/lib/capability_resolver.py`; a CODEOWNERS/ownership adapter is limited to the existing parser evidence in `repository_map.py`. No universal package-ecosystem parser is promised. Unsupported ecosystems or formats yield `UNSUPPORTED`/`UNKNOWN`, never fabricated edges. Malformed metadata is `FAILED`; incomplete evidence is `PARTIAL`/`UNKNOWN`; cycles are valid graph structure.

Changed-path input is a set of normalized repository-relative paths, optionally carrying `ADDED`, `MODIFIED`, `DELETED`, or `RENAMED` classification and the source of that classification. Outside-root, malformed, or unnormalizable paths are rejected and classified `UNKNOWN`/`FAILED`; they are not mapped to a nearby file.

An impact result is read-only and includes the changed path, direct graph relationships, dependency evidence, ownership evidence, architecture evidence, generated-artifact relationships, derivation rule, input fact IDs, and uncertainty/conflict statuses. A generated path with known provenance yields a derived impact with that provenance. Unknown paths and unsupported subsystems remain `UNKNOWN`/`UNSUPPORTED`; conflicting evidence remains visible. Impact never authorizes mutation, integration, mission execution, or external effects.

## Explicit negative acceptance matrix

| Area / adversarial case | Expected classification/result |
|---|---|
| Graph: unsupported ecosystem | `UNSUPPORTED` (or `UNKNOWN` when no classifier can identify it), no fabricated edge |
| Graph: malformed metadata | `FAILED` with malformed-evidence provenance |
| Graph: conflicting source facts | `CONFLICTING`, all source evidence retained |
| Graph: missing optional metadata | `UNKNOWN` where the field is applicable |
| Graph: repeated identical input | byte-identical canonical output |
| Commands: zero commands | explicit empty registry; availability `UNKNOWN` |
| Commands: ambiguous candidates | `AMBIGUOUS` |
| Commands: present but unproven | `UNVERIFIED_RUNTIME` (or `BLOCKED` where the trust contract requires proof) |
| Commands: unsupported metadata | `UNSUPPORTED` |
| Commands: machine-local absolute command | rejected/non-portable; not authoritative |
| Commands: conflicting authorities | `CONFLICTING` unless declared precedence legitimately resolves it |
| Ownership: no source | `UNKNOWN` |
| Ownership: conflicting owners | `CONFLICTING` |
| Ownership: malformed source | `FAILED`/invalid source |
| Ownership: unresolved overlap | `AMBIGUOUS` or `CONFLICTING` per source conflict |
| Architecture: no authority | `UNKNOWN` |
| Architecture: conflicting current authorities | `CONFLICTING` |
| Architecture: historical document | ignored as current authority; `HISTORICAL/SUPERSEDED` |
| Architecture: descriptive doc vs explicit authority | explicit authority remains governing; descriptive fact remains evidence |
| Dependencies: unsupported format | `UNSUPPORTED` |
| Dependencies: malformed metadata | `FAILED`/invalid dependency source |
| Dependencies: cycle | valid cycle representation; no arbitrary edge removal |
| Dependencies: incomplete evidence | `PARTIAL`/`UNKNOWN` |
| Dependencies: unresolved generated dependency | explicit `UNRESOLVED` |
| Impact: unknown changed path | `UNKNOWN` |
| Impact: generated path with provenance | derived impact with producer provenance |
| Impact: conflicting ownership | impact retains `CONFLICTING` ownership evidence |
| Impact: unsupported subsystem | `UNSUPPORTED`/`UNKNOWN` |
| Impact: conflicting dependency evidence | conflict remains visible |
| Generated: known producer | provenance `VERIFIED` |
| Generated: missing producer | `UNKNOWN`/`BLOCKED`; modification blocked |
| Generated: conflicting producer evidence | `CONFLICTING` |
| Generated: stale artifact | `STALE`; drift check is non-pass |
| Generated: hand-maintained file claimed generated | claim rejected; classification is not generated |

## Generated-dependent closure

Hand-editing generated artifacts is prohibited. This table is the complete planning-time closure; an artifact may change during P1 only when its source relationship and producer are proven.

| Artifact | Purpose | Producer | Trigger/source relationship | Regeneration / discovery | Verification | Drift behavior | P1 modification |
|---|---|---|---|---|---|---|---|
| `.control-plane/bootstrap-manifest.json` | bootstrap source/provenance manifest | `.keel/lib/p0_contract.py` via `python .keel/bin/keel.py manifest --write` | tracked bootstrap inputs and manifest source set | run producer; inspect manifest producer metadata | `python .keel/bin/keel.py manifest` and strict control-plane validation | stale/drift is non-pass; producer must be rerun | only if P1 changes a proven listed source; otherwise not expected |
| `.keel/knowledge/repository-map.json` | derived repository map | `.keel/lib/repository_map.py` via `python .keel/bin/keel.py map` | repository evidence consumed by map producer | run `python .keel/bin/keel.py map`; no hand edit | repository-map checks and deterministic byte comparison | stale/drift is non-pass | not expected in this planning remediation; future P1 execution only through producer |
| `docs/generated/**` | generated references | no producer is declared in current repository evidence | no proven P1 source relationship | producer discovery required before any authorization | no modification permitted until producer/verification are known | `UNKNOWN PRODUCER — BLOCKS MODIFICATION` | not authorized |

## Tight implementation scope and effects boundary

P1 implementation may touch only implementation code/contracts, focused P1 tests, declared P1 intelligence artifacts, proven generated dependents, KEEL lifecycle metadata, and final authorized audit/roadmap/plan reconciliation. The global roadmap may be updated only at verified P1 completion under established reconciliation rules; it may not be superseded. Generated documentation is not an unrestricted wildcard. P1 may inspect static repository evidence describing runtime/deployment surfaces, but may not query live capabilities, execute providers, perform a runtime handshake, mutate deployment systems, or infer live activation from configuration alone. Live runtime capability belongs to P3.

P1 does not authorize external effects, arbitrary repository commands, deployment changes, Git integration outside KEEL, mission execution, runtime/provider calls, P2–P7 implementation, or D1 execution. Discovery and impact remain advisory/read-only.

## Implementation acceptance boundary

The behavioral criteria are exclusively `IMPLEMENTATION_ACCEPTANCE`; planning criteria remain exclusively `PLAN_READINESS`. Each criterion executes a focused P1 test against implementation-bearing paths and an independent fixture plus expected-output oracle that is not produced by the implementation under test. Planning files, control-plane checks, and generic KEEL tests may supplement these results but cannot substitute for them.

The required behavioral domains are graph/schema serialization and negative graph states; command classification with independent existence, source class, provenance, support, runtime availability, and authorization fields; ownership/architecture authority and freshness; dependency/changed-path/impact derivation; and generated-artifact producer provenance and drift. The suite must assert expected outputs and statuses for every matrix case, including `UNSUPPORTED`, `FAILED`, `CONFLICTING`, `UNKNOWN`, `AMBIGUOUS`, `UNVERIFIED_RUNTIME`, `STALE`, `UNRESOLVED`, `BLOCKED`, exact unavailable/unauthorized outcomes, valid cycles, rejected paths, and rejected hand-maintained generated claims. The current implementation surfaces are `.keel/lib/repository_intelligence.py`, `.keel/tests/test_repository_intelligence.py`, and `.keel/tests/fixtures/repository-intelligence/`.

## Execution milestones and completion evidence

1. Select only evidence-supported adapters and record their exact source/consumer boundaries.
2. Implement the contract without changing the effects boundary.
3. Verify deterministic serialization, provenance, status degradation, negative classifications, generated closure, and read-only behavior through focused tests and repository-native checks.
4. Independently review the evidence graph, commit the verified tree, seal, and later anchor only through KEEL after implementation acceptance passes.

P1 is complete only when every required acceptance edge is proven against the committed tree and KEEL reports `LANDED_COMPLETION`. The active roadmap remains in place throughout this execution.

## Failure and blocker rules

Unknown, unsupported, malformed, conflicting, stale, unavailable, or unproven evidence blocks a `VERIFIED` claim for that fact. Unknown producer provenance blocks modification. Scope, authority, acceptance, or effects changes require KEEL re-plan. P2 cannot start until independent P1 completion evidence exists; P4 remains blocked; D1 remains deferred.
