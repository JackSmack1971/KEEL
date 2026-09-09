# Change codex-app-server-adapter

> GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project.

Phase: `SHIP`

## Objective
Add a local Codex App Server stdio adapter with bounded lifecycle, safe compatibility handling, cost gating, tests, and docs

## Requirements
- `REQ-01` Implement the adapter as a distinct component through SchedulerAdapter injection without embedding Codex transport in scheduler or deterministic kernel modules.
- `REQ-02` Implement documented local stdio app-server launch/connect, initialize/initialized handshake, initialization observation, account/read inspection, and truthful live smoke reporting.
- `REQ-03` Implement documented thread/start and thread/resume operations.
- `REQ-04` Implement bounded turn/start submission and deterministic lifecycle/item event parsing.
- `REQ-05` Implement fail-safe timeout, malformed/partial frame, unexpected-exit, and clean shutdown handling.
- `REQ-06` Detect and surface protocol/method/capability mismatches without silent continuation or crash.
- `REQ-07` Preserve native KEEL behavior when App Server is unavailable.
- `REQ-08` Preserve ZERO_INCREMENTAL_COST and prohibit credential, API, billing, fallback, rotation, and evasion surfaces.
- `REQ-09` Keep experimental transport/process-control paths absent from the load-bearing baseline.
- `REQ-10` Gate every model-executing adapter action with runtime_authorization ZERO_INCREMENTAL_COST preflight.
- `REQ-11` Keep keel run bounded to its existing substrate and document the canonical adapter and superseded active plan state.

## Non-goals
- Do not implement an agent runtime, reasoning, tools, approvals, sandboxing, or thread storage inside KEEL.
- Do not add OpenAI Platform/API integration, API keys, billing, paid/provider fallback, credit purchase, account rotation, or rate-limit evasion.
- Do not use WebSocket, dynamic tools, experimental process-control, or external-token auth as the baseline path.
- Do not turn keel run into autonomous engineering or alter native behavior when App Server is absent.
- Do not manually edit kernel-owned receipts, grants, events, views, or attestations.

## Scope
- `.keel/lib/codex_app_server_adapter.py`
- `.keel/lib/scheduler.py`
- `.keel/tests/test_codex_app_server_adapter.py`
- `.keel/tests/smoke_codex_app_server.py`
- `.keel/config.json`
- `.keel/bootstrap-manifest.json`
- `ARCHITECTURE.md`
- `docs/control-plane/ORCHESTRATION.md`
- `docs/control-plane/CODEX_NATIVE.md`
- `docs/exec-plans/active/codex-app-server-adapter.md`
- `docs/exec-plans/completed/codex-app-server-adapter.md`

## Consequences
- A protocol adapter can mis-handle runtime state or accidentally trigger model execution if compatibility and cost gates are weak.
- Changes to the scheduler injection boundary and canonical architecture documentation can misdirect future execution if separation is not preserved.
