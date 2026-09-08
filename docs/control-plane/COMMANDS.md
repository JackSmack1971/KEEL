# Canonical Commands and Tooling

Status: `CONDITIONAL` until the project chooses a toolchain.

Do not make agents rediscover routine commands every run. Once commands exist, record canonical forms here and mirror required verification commands into `.keel/config.json` as argv arrays (no shell interpolation).

| ID | Purpose | Command | Working directory | Preconditions | Side effects | Success evidence | Status |
|---|---|---|---|---|---|---|---|

KEEL navigation:

```text
python3 .keel/bin/keel.py next
```

`keel next` is a read-only advisor. It reports the active change phase, blockers, and the next legal command; it never advances a gate, records authorization, seals a candidate, or anchors a commit.

Portable bootstrap and generated-state checks:

```text
python .keel/bin/keel.py bootstrap status
python .keel/bin/keel.py manifest
python .keel/bin/keel.py manifest --write
```

`bootstrap status` works without Git and distinguishes a copied/extracted framework from a Git-backed repository. `manifest --write` is the repository-owned producer for `.control-plane/bootstrap-manifest.json`; `manifest` is its deterministic drift check. Neither command fabricates Git provenance.

Worktree isolation:

```text
python3 .keel/bin/keel.py worktree create <change-id> --path <explicit-path>
python3 .keel/bin/keel.py worktree status
python3 .keel/bin/keel.py worktree retire --path <registered-path> [--force]
```

Environment contract inspection:

```text
python3 .keel/bin/keel.py environment status
```

Canonical change-graph inspection:

```text
python3 .keel/bin/keel.py change-graph validate <plan.json>
python3 .keel/bin/keel.py change-graph normalize <plan.json>
python3 .keel/bin/keel.py change-graph serialize <plan.json>
python3 .keel/bin/keel.py change-graph frontier <plan.json> [--state <state.json>]
python3 .keel/bin/keel.py mission validate <mission.json>
python3 .keel/bin/keel.py mission frontier <mission.json>
```

These stable commands are read-only and normalize canonical, mission-v1, or
mission-v2 input into one `ChangeGraph`. Dependencies are typed edges only;
frontier uses those edges plus optional caller-supplied completion state. It
does not inspect lifecycle ledgers, resolve resource conflicts, schedule or
dispatch agents, execute effects, or grant authorization. `mission-v2`
remains a hidden temporary read-compatibility alias during migration.

Repository mapping:

```text
python3 .keel/bin/keel.py map --stdout
python3 .keel/bin/keel.py map
```

`map --stdout` is read-only. The default writes only the derived `.keel/knowledge/repository-map.json` artifact.

The map includes Python AST import facts when Python sources are present. It also parses a literal `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS` source when present; otherwise ownership is explicitly `UNAVAILABLE`. Facts carry analyzer/source provenance and are navigation evidence, not architecture or authorization decisions.

Read-only work-constraint projection:

```text
python3 .keel/bin/keel.py route <mission.json> [--change <change-id>]
```

The temporary `route` surface emits only canonical hard-dependency, resource,
effect-request, and evidence-requirement constraints. It makes no complexity,
effort, persona, model, schedule, or dispatch decision.

Lifecycle compatibility:

```text
python3 .keel/bin/keel.py version
python3 .keel/bin/keel.py compat
python3 .keel/bin/keel.py migrate --check
```

These commands inspect repository-owned versions and report migration actions. They do not query external Codex versions, download updates, or rewrite schemas.

`migrate --plan <artifact.json>` performs read-only preflight for a registered migration. Applying or rolling back a live control-plane artifact requires an explicitly authorized KEEL change; no CLI path performs that implicitly.

Developer UX projections:

```text
python3 .keel/bin/keel.py init --check
python3 .keel/bin/keel.py review [--change <change-id>]
python3 .keel/bin/keel.py ship [--change <change-id>]
```

All three commands are read-only. `ship` reports eligibility only; it never grants permission, integrates, releases, or anchors.

Effect inspection:

```text
python3 .keel/bin/keel.py effects [--change <change-id>]
```

This is read-only and advisory. It recognizes only explicit argv patterns, reports inferred capabilities and undeclared mismatches, and never executes or authorizes a command.

Lifecycle telemetry:

```text
python3 .keel/bin/keel.py telemetry --change <change-id>
```

This reports measured verification counts, exit outcomes, command count, and wall time. Token, cost, human-intervention, retry, and conflict metrics remain explicitly unavailable unless runtime instrumentation supplies them.

Cover setup/bootstrap, build, format, lint/static checks, type checks, unit/integration/e2e/evals, local run, generated-artifact refresh, security checks, benchmarks, release validation, and cleanup only when those commands actually exist.

Prefer repository scripts/task runners when they reduce cross-platform ambiguity. Any destructive or external command must state its authorization/recovery boundary. `keel verify` executes only commands explicitly configured in `.keel/config.json`; absence is a blocker for substantive source changes, not an invitation to guess.
