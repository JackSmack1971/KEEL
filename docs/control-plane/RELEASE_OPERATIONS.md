# Release, Deployment, Migration, Incident, and Recovery Operations

Status: `CONDITIONAL` until the project produces an operated or distributed artifact.

## Portable runtime contract

`keel mission run <mission.json>` executes only through the shared Mission runtime. The runtime records an explicit capability handshake, requires an ordinary child Change ledger, bounds retries, writes mission-local run evidence under `.keel/mission/`, and leaves integration as `NOT_PERFORMED`. Unknown provider, Codex, or hook capabilities are reported as `UNKNOWN`; generated files never activate them.

Mission execution cannot grant authorization, alter a child scope, fabricate verification evidence, seal an unverified tree, or integrate a candidate. Those operations remain owned by the child Change lifecycle and sealed-candidate boundary.

`keel adopt --check` classifies a clean, existing, or incomplete repository without mutation. `keel upgrade --check` reports whether repository-owned artifacts are current or which migrations/repairs are required; applying them remains a separately governed Change.

When activated, define:
- versioning/release artifact provenance;
- staging/production or equivalent environment promotion;
- deployment authorization and evidence;
- rollback/forward-fix criteria;
- schema/data migration expand-contract and compatibility strategy where applicable;
- backup/restore and recovery objectives for persistent state;
- incident detection, triage, containment, communication, recovery and postmortem;
- release/incident evidence retained for future agents.

Remote or production mutation is a consequential action and must not be inferred from local success alone.
