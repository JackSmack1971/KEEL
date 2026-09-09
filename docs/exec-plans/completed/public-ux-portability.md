# ExecPlan: public UX and portability

Status: `COMPLETE / LANDED IN CURRENT TREE — HISTORICAL LEDGER RETAINED`
Forward authority: [`KEEL_FORWARD_AUTHORITY.md`](../../control-plane/KEEL_FORWARD_AUTHORITY.md)

## Objective

Refactor KEEL's public command surface, documentation, packaging, and portability
around the canonical kernel. Preserve historical ledgers and compatibility readers
while making internal schema and subsystem details implementation-only.

## Work

1. Inspect the current CLI and kernel projections; define one stable JSON envelope
   and public lifecycle vocabulary.
2. Add public `init`, `doctor`, `start`, `status`, `next`, `run`, `verify`, `land`,
   `explain`, and `audit` projections over existing kernel behavior. Keep detailed
   subsystem commands available only through an explicit compatibility path where
   existing automation requires them.
3. Add contract tests for help visibility, JSON shape, explain/audit provenance,
   and SEALED/LANDABLE/INTEGRATING/LANDED status distinctions.
4. Verify or minimally extend deterministic bootstrap, ownership classification,
   safe migration/upgrade behavior, and disposable-repository stack neutrality.
5. Rewrite the public documentation and indexes, including custom-ref replication,
   artifact ownership, policy-pack boundaries, and current lifecycle terminology.
6. Run focused and full verification, inspect scope, commit, seal, and stop before
   remote integration unless separately authorized.

## Risks and controls

- Public CLI changes can break callers: preserve compatibility commands and test
  both normal help and explicit compatibility behavior.
- Migration and packaging changes can lose user data: keep operations additive,
  deterministic, source-digesting, and backed by disposable and historical fixtures.
- Documentation can overclaim runtime enforcement: describe only observed or tested
  behavior and retain the kernel's fail-closed boundaries.

## Evidence

- `public-cli-contract-tests`
- `portability-installation-tests`
- `documentation-contract-tests`
- `python3 .keel/bin/keel.py verify --change public-ux-portability`
