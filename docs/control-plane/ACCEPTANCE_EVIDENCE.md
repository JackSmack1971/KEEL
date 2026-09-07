# Acceptance and Evidence Graph

A KEEL standard change binds behavior to evidence through two intent artifacts:

```text
requirements.json
acceptance.json
```

`requirements.json` contains stable `REQ-*` statements. `acceptance.json` contains `AC-*` criteria, each linked to a requirement and one or more evidence edges. Both files are part of KEEL's intent digest, so changing acceptance after verification makes evidence stale.

Every declared requirement must be referenced by at least one acceptance criterion. An orphan requirement is a contract error and prevents verification; this keeps intent-to-evidence traceability explicit rather than treating an unreferenced requirement as implicitly satisfied.

Current deterministic providers:

- `command` — a configured verification check id must exit `0`;
- `changed_path` — the material Git diff must include a declared path/glob;
- `file_exists` — a repository-contained evidence artifact must exist.

The repository contract also defines adapter-backed providers (`unit_test`, `browser`, `visual`, `log_query`, `metric_query`, `trace_query`, `schema`, `security`, `benchmark`, `hardware`, `human_review`, and `external_ci`). These providers require a configured `check_id`; KEEL evaluates the adapter's literal exit status but does not invent or execute a provider implementation.

Unknown evidence providers do not silently pass. Extend provider support only when the new provider has a mechanically inspectable result contract.

During `keel verify`, KEEL evaluates every required criterion and writes `evidence-graph.json`. Verification cannot PASS while a required acceptance criterion is unsatisfied.

The evaluated graph also reports deterministic requirement coverage counts so reviewers can distinguish complete traceability from a merely green command check.

## Example

```json
{
  "id": "AC-004",
  "requirement_id": "REQ-002",
  "statement": "Expired refresh tokens are rejected",
  "required": true,
  "policy": "all",
  "evidence": [
    {"provider": "command", "check_id": "auth-integration-tests"}
  ]
}
```

This changes the completion question from "did tests run?" to "what explicit behavior does each piece of evidence establish?"
