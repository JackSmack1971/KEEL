# ExecPlan: Context Compiler v2

## Objective

Consume the Plan 002 repository graph and impact facts to select bounded, role-specific context without weakening mandatory context or evidence obligations.

## Design

- Keep compile_packet as the compatibility-preserving v1 API.
- Add a v2 API with explicit role, query, graph, and impact inputs.
- Always retain configured mandatory documents.
- Add role/profile and impact/query matches with provenance and confidence.
- Emit UNAVAILABLE/CONFLICT uncertainty and widen warnings/context conservatively.
- Expose v2 through the existing context CLI using explicit options.

## Verification

Run focused context tests, full configured KEEL checks, and inspect the evidence graph for all requirements.
