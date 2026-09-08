# Risk review

## Boundary and blast radius
This changes a repository-owned runtime guardrail. A false allow could permit an out-of-phase mutation; a false deny could halt normal Codex work. Hooks are not confinement, post-tool events cannot undo effects, and installed runtime activation remains unproven until a live smoke test.

## Safety controls
- Keep current hook entrypoint and legacy event compatibility during replacement.
- Centralize decisions in a dependency-free deterministic kernel API; the hook only discovers the repository, parses JSON, calls the API, and renders the returned contract.
- Treat repository discovery errors as unknown (fail closed for enforcement), with fail-open only for Git's conclusive not-a-repository result or an explicit kernel allow.
- Preserve Codex sandbox/approval defaults and destructive-command prompts; do not reinterpret them as KEEL grants.
- Exercise malformed input, missing kernel/config/state, unrecognized write wire shapes, Bash/integration cases, MCP/local function cases, and post-effect feedback through subprocess tests.

## Recovery
The change is local and reversible through Git. The preserved hook command path and conservative bootstrap query permit rollback to the baseline implementation. No external effects, reconciliation, deployment, migration, release, or remote integration are performed by the adapter.

## Independent review requirement
Review must focus on deny/allow polarity, trust establishment, scope normalization, context bounds, post-tool claims, coverage claims, and absence of alternate policy authority before sealing.
