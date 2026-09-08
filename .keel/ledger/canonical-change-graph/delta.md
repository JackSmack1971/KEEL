## ADDED
- Add a canonical ChangeGraph planning API composed only from canonical semantic-kernel records and typed edges, with pure deterministic validation, serialization, and read-only frontier projection.
- Add explicit mission v1 and v2 compatibility adapters that preserve source provenance and unknown legacy meaning without inventing authority, runtime facts, or scheduler state.

## MODIFIED
- Make stable `change-graph` and `mission` CLI commands consume canonical graphs; retain `mission-v2` only as a temporary compatibility alias and remove dispatch exposure.
- Rebase planning tests and documentation on the canonical graph while retaining minimal legacy migration fixtures.

## REMOVED
- Remove node-level dependency authority, embedded authorization/runtime/lifecycle/scheduler/persona fields, and resource-conflict invalidation from authoritative planning semantics.
