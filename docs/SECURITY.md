# Security

Baseline security policy is active even before a stack exists:
- never commit secrets or credentials;
- least privilege for tools, agents, CI, integrations, and runtime identities;
- explicit trust boundaries and untrusted-input parsing when data flows exist;
- dependency/supply-chain provenance once dependencies exist;
- high-blast-radius actions require authorization and stronger evidence;
- do not weaken sandbox/approval controls just to complete a task.

Create a project-specific threat model when architecture introduces assets, identities, external inputs, persistence, network surfaces, privileged operations, or regulated/sensitive data.

See [control-plane/SECURITY_DATA_SUPPLY_CHAIN.md](control-plane/SECURITY_DATA_SUPPLY_CHAIN.md).
