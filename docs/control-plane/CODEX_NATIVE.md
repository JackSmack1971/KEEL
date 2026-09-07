# Codex-Native Control Surface

## Installed baseline
- `.codex/config.toml`: conservative project defaults; effective only when the project layer is trusted.
- `.codex/hooks.json`: KEEL lifecycle/context guards; non-managed definitions require separate exact-definition trust.
- `.codex/rules/control-plane.rules`: approval escalation for selected destructive Git operations outside the sandbox.
- `.codex/agents/`: general explorer/reviewer/risk reviewer plus KEEL discuss/plan/verify/ship roles.
- `.agents/skills/`: control-plane maintenance + KEEL change lifecycle skills.
- `.keel/`: deterministic ledger/gate/verification runtime.

## Trust is evidence
File presence does not prove activation. Verify project trust, hook trust, Python runtime, Git baseline, and actual blocking/context behavior before reporting KEEL hooks active. Changed hook definitions require re-review.

## Hooks
Current Codex hooks are enabled by default unless configuration/admin policy disables them. This project uses:
- `SessionStart` / `UserPromptSubmit` for concise active-ledger context;
- `PreToolUse` for direct-write phase/scope checks and pre-integration gate checks;
- `PostToolUse` for independent Git diff-scope/content-digest feedback after tool side effects;
- `Stop` to prevent premature completion while an active source change is unverified.

Hooks are not a complete security boundary. Keep sandboxing, approvals, rules, CI, application authorization, and domain checks intact.

## Profiles
Do not put `[profiles.*]` in project `.codex/config.toml`; current Codex ignores project-local profile selection. If an organization wants named user profiles, maintain `$CODEX_HOME/<name>.config.toml` outside the repo. KEEL emergency behavior uses `KEEL_BYPASS_REASON` specifically so the repository does not pretend it can install a user profile.

## Subagents
Read-only KEEL agents are intended for bounded evidence/plan/review work. Live parent permission overrides can supersede child defaults; do not treat custom-agent sandbox settings as the sole security barrier.

## Automation
For `codex exec`, default to read-only and grant `workspace-write` only for tasks that must edit. Prefer JSONL/output schemas. A headless KEEL write task still requires the same ledger/scope/verification rules; if hook trust is intentionally bypassed in a controlled CI runner, validate hook sources outside Codex and preserve equivalent evidence.
