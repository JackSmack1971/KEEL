# Public command surface

Run `python3 .keel/bin/keel.py` from a repository root. Public commands return
JSON with a stable `schema` identifier:

- `init [--check]` and `doctor` inspect local installation and Git readiness.
- `start <objective> [--id <change-id>]` begins a governed change.
- `status`, `next`, `explain [subject]`, and `audit [subject]` provide lifecycle,
  decision, and provenance projections.
- `run` reports the fail-closed execution boundary when no authorized executor is
  configured; KEEL does not invent project commands.
- `verify` establishes exact-subject evidence; `land prepare|integrate|verify`
  performs the authorized landing transaction.

The public lifecycle is `UNSEALED` (verified work has no candidate yet), `SEALED`
(candidate is verified and sealed), `LANDABLE`
(candidate is ready for a landing transaction), `INTEGRATING` (a landing
attestation exists), and `LANDED` (the resulting target was independently checked).

Detailed gates, ledger migration, graph, scheduler, and compatibility commands are
internal support surfaces. They remain available for automation and historical
compatibility but are intentionally absent from normal help.

## Distribution and ownership

`.keel/` is KEEL-owned runtime and canonical ledger data. Project-owned policy and
configuration are explicit under `policies/` and the project portions of config.
Generated cache/state belongs under ignored runtime directories; durable historical
ledger data, Git refs, notes, and attestations must be retained and replicated when
history is shared.

KEEL custom refs (custom-ref names under `refs/keel/candidates/*`, `refs/keel/attestations/*`,
`refs/keel/ledger/*`), and the
`keel` Git notes ref are not included by ordinary branch pushes. Replicate them with
explicit refspecs and notes configuration when remote auditability is required, for
example `git push origin refs/keel/candidates/* refs/keel/attestations/* refs/keel/ledger/*`
and `git push origin refs/notes/keel`.

Migration is additive and loss-preserving: use the internal `ledger migrate` reader
for historical v1 ledgers, retain the source, and verify the resulting provenance.
