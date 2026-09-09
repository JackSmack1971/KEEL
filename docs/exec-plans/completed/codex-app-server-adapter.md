# Codex App Server stdio adapter

Status: completed in change `codex-app-server-adapter`.

The repository-local adapter at `.keel/lib/codex_app_server_adapter.py` uses the
documented local stdio JSONL surface for initialization/account inspection,
thread start/resume, and bounded turn/event observation. It remains a transport
adapter through the scheduler injection boundary, not an agent runtime.

Verification passed all 11 acceptance requirements. Fixture tests cover malformed,
truncated, timeout, cost-gated, and cleanup paths. The installed-runtime smoke
observed `codex-cli 0.153.4`, initialization metadata, account state, and thread
creation. The smoke records `protocol_version: null` because the published
protocol documentation does not define a standalone protocol-version or server
capability-discovery response; the adapter reports that unknown rather than
inferring it. `keel doctor` still reports ZERO_INCREMENTAL_COST as BLOCKED, so no
model turn was attempted during verification.
