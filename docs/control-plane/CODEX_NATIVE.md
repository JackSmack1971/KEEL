# Codex-Native Adapter Surface

## Installed baseline
- `.codex/config.toml`: conservative Codex defaults, effective only when trusted.
- `.codex/hooks.json`: thin event-to-kernel adapter declarations; exact-definition trust is separate.
- `.codex/rules/control-plane.rules`: Codex-native prompts for selected destructive effects, not KEEL policy or grants.
- `.codex/agents/`: generic explorer/reviewer/risk-reviewer roles selected dynamically from missing facts, evidence requirements, impact, and risk.
- `.agents/skills/`: workflow adapters that call KEEL kernel/context/evidence operations.
- `.keel/`: deterministic lifecycle, policy, context, evidence, and authorization kernel.

## Trust and authority
File presence or fixture success does not prove activation. Verify project trust, hook trust, Python/Git runtime, delivered events, and actual allow/deny behavior before reporting KEEL hooks active. The hook, rule, skill, and agent surfaces do not independently decide lifecycle, scope, evidence sufficiency, or permission.

The public interaction remains the stable JSON CLI (`init`, `doctor`, `start`,
`status`, `next`, `run`, `verify`, `land`, `explain`, and `audit`). Codex hooks are
adapters over that contract; they do not expose schema-specific ledger commands as a
second authority.

## Declared hook and tool coverage
When an installed Codex runtime trusts and supports this definition, the project requests:
- `SessionStart` and `UserPromptSubmit`: bounded decision-relevant kernel context;
- `PreToolUse` with matcher `*`: normalize every delivered tool name into local-write, local-process, local-function, or MCP-function queries, then render the kernel allow/deny;
- `PostToolUse` with matcher `*`: observe every delivered tool event and independently inspect repository state after effects;
- `Stop`: query completion eligibility.

The wildcard expresses requested coverage, not observed coverage. Actual tool coverage is only the events the installed runtime delivers and is recorded in `RuntimeProfile`; missing local/MCP events remain unsupported or unobserved. `PostToolUse` cannot undo an effect. Hooks cannot cover alternate clients, direct processes, specialized paths the runtime does not emit, or configuration/trust drift, so they are never complete confinement. Sandbox, approvals, rules, CI, provider/application authorization, independent verification, and protected Git controls remain load-bearing.

## Installed-runtime smoke test
Static tests under `.keel/tests/` prove repository adapter wire contracts only. They **must not** be reported as proof that an installed Codex runtime loads, trusts, invokes, or enforces hooks.

For each installed Codex version/session:
1. Record `codex --version` (or equivalent runtime identity) and inspect `/hooks`; verify the trusted definition byte-for-byte matches `.codex/hooks.json`.
2. Start/resume a disposable standard change. Confirm SessionStart and UserPromptSubmit inject a bounded active-change summary rather than the full ledger.
3. In DISCUSS, request an allowed proposal edit and an out-of-phase source edit with a direct file tool. Observe the former allowed and the latter denied before execution.
4. Invoke one harmless local read function and, when configured, one harmless read-only MCP function. Confirm PreToolUse and PostToolUse delivery and record exact tool names. Absence is negative coverage evidence, never inferred away from `*`.
5. In a disposable branch/worktree, exercise a post-tool-only detected mutation. Confirm the output says the effect already occurred and must be reconciled; restore it reversibly.
6. Attempt Stop with an unverified disposable write and confirm the runtime honors the kernel denial. Verify normally and confirm Stop eligibility.
7. Record payload shapes, outcomes, missing events, project/hook trust, sandbox/approval state, and runtime version as a RuntimeProfile observation. Do not generalize to other clients or sessions.

## Generic subagents
Invoke explorer for unresolved facts, reviewer for requirement/evidence or impact concerns, and risk-reviewer for consequential effects or weak runtime trust. They consume bounded kernel context and never own phase transitions, scope, authorization, or evidence pass/fail. Parent permission can supersede child defaults, so read-only agent configuration is not a security boundary.

## Profiles and automation
Do not put `[profiles.*]` in project `.codex/config.toml`; current repository evidence says project-local profile selection is unavailable. Named user profiles belong outside the repo. KEEL emergency behavior requires parent-provided `KEEL_BYPASS_REASON` so repository files cannot self-authorize it.

For `codex exec`, default to read-only and grant workspace write only when required. A headless write still uses the same kernel lifecycle. A controlled runner that bypasses hooks must validate adapter sources and preserve equivalent independent verification rather than claiming hook enforcement.

## Local App Server adapter

`.keel/lib/codex_app_server_adapter.py` is a separate, dependency-free transport
adapter used through the scheduler's injected adapter boundary. Its load-bearing
path is local `codex app-server --listen stdio://` with newline-delimited JSON
messages and the documented stable `initialize`, `initialized`, `account/read`,
`thread/start`, `thread/resume`, and `turn/start` operations. It observes
`turn/*` and `item/*` notifications through bounded reads and closes process and
pipes on timeout, malformed frames, and crashes.

The published protocol documentation specifies initialization metadata and client
capability options, but does not specify a standalone protocol-version or
capability-discovery response. KEEL does not invent one: the adapter reports
`protocol_version: null`, labels its validated stable contract
`STABLE_DOCUMENTED_SURFACE`, and turns missing or unexpected documented fields
into an explicit compatibility failure. Fixture tests prove wire handling only;
the conditional smoke command is the installed-runtime evidence and reports
`UNVERIFIED_RUNTIME` when `codex` is absent or unreachable.

Before `turn/start`, the adapter calls the existing `runtime_authorization`
`ZERO_INCREMENTAL_COST` preflight. A blocked or incomplete observation prevents
model execution. No Platform/API client, credential input, paid continuation,
provider fallback, credit operation, account rotation, or experimental transport
or process-control dependency is introduced.
