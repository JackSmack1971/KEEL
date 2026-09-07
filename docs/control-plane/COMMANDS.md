# Canonical Commands and Tooling

Status: `CONDITIONAL` until the project chooses a toolchain.

Do not make agents rediscover routine commands every run. Once commands exist, record canonical forms here and mirror required verification commands into `.keel/config.json` as argv arrays (no shell interpolation).

| ID | Purpose | Command | Working directory | Preconditions | Side effects | Success evidence | Status |
|---|---|---|---|---|---|---|---|

Cover setup/bootstrap, build, format, lint/static checks, type checks, unit/integration/e2e/evals, local run, generated-artifact refresh, security checks, benchmarks, release validation, and cleanup only when those commands actually exist.

Prefer repository scripts/task runners when they reduce cross-platform ambiguity. Any destructive or external command must state its authorization/recovery boundary. `keel verify` executes only commands explicitly configured in `.keel/config.json`; absence is a blocker for substantive source changes, not an invitation to guess.
