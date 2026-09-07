# Acceptance and Evidence Graph

A KEEL standard change binds behavior to evidence through two intent artifacts:

```text
requirements.json
acceptance.json
```

`requirements.json` contains stable `REQ-*` statements. `acceptance.json` contains `AC-*` criteria, each linked to a requirement and one or more evidence edges. Both files are part of KEEL's intent digest, so changing acceptance after verification makes evidence stale.

Current deterministic providers:

- `command` — a configured verification check id must exit `0`;
- `changed_path` — the material Git diff must include a declared path/glob;
- `file_exists` — a repository-contained evidence artifact must exist.

Unknown evidence providers do not silently pass. Extend provider support only when the new provider has a mechanically inspectable result contract.

During `keel verify`, KEEL evaluates every required criterion and writes `evidence-graph.json`. Verification cannot PASS while a required acceptance criterion is unsatisfied.

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
