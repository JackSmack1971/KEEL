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

Mission dependency inspection:

```text
python3 .keel/bin/keel.py mission validate <mission.json>
python3 .keel/bin/keel.py mission frontier <mission.json>
python3 .keel/bin/keel.py mission status <mission.json>
```

These commands are read-only. A mission planner validates a dependency DAG and projects child KEEL ledger phases; it does not dispatch agents, create worktrees, or transition changes.

Repository mapping:

```text
python3 .keel/bin/keel.py map --stdout
python3 .keel/bin/keel.py map
```

`map --stdout` is read-only. The default writes only the derived `.keel/knowledge/repository-map.json` artifact.

The map includes Python AST import facts when Python sources are present. It also parses a literal `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS` source when present; otherwise ownership is explicitly `UNAVAILABLE`. Facts carry analyzer/source provenance and are navigation evidence, not architecture or authorization decisions.

Advisory topology routing:

```text
python3 .keel/bin/keel.py route <mission.json> [--change <change-id>]
```

This emits model-independent complexity, effort capability, role, and verification recommendations; it does not launch agents or select models.

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

Cover setup/bootstrap, build, format, lint/static checks, type checks, unit/integration/e2e/evals, local run, generated-artifact refresh, security checks, benchmarks, release validation, and cleanup only when those commands actually exist.

Prefer repository scripts/task runners when they reduce cross-platform ambiguity. Any destructive or external command must state its authorization/recovery boundary. `keel verify` executes only commands explicitly configured in `.keel/config.json`; absence is a blocker for substantive source changes, not an invitation to guess.
