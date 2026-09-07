# KEEL Emergency Bypass

Emergency process exists because forcing normal ceremony during a production incident can increase harm. Bypass creates process debt; it does not erase governance.

## Operator activation
Launch Codex from a shell where the **parent process** contains a concrete reason:

POSIX:
```sh
KEEL_BYPASS_REASON="P0 incident: restore service availability" codex
```

PowerShell:
```powershell
$env:KEEL_BYPASS_REASON = "P0 incident: restore service availability"
codex
```

Do not place the variable only inside an agent-proposed command; KEEL hooks read their parent environment before the tool runs.

## What bypass does
- KEEL hook blocks become audit-only.
- First observed bypass per session/change/reason is recorded under `.keel/audit/` and in the change gate log.
- A `retro-<change-id>` ledger entry is created for post-incident reconstruction/verification; when no change was active, a deterministic `retro-emergency-*` entry is created from the session/reason so process debt is still durable.

## What bypass does NOT do
- does not set `--yolo` or `danger-full-access`;
- does not disable Codex hook trust, sandboxing, approvals, execpolicy rules, secrets controls, or admin policy;
- does not grant GitHub/cloud/deployment/database/hardware authorization;
- does not waive domain-specific rollback, blast-radius, or safety constraints.

## After stabilization
Reconstruct the actual delta/effects, run the missing verification/regression work, record incident evidence/decisions, close or convert the retro ledger into normal follow-up work, and promote repeated failure patterns into tests/invariants.
