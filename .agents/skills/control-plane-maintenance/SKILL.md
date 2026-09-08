---
name: control-plane-maintenance
metadata:
  version: "1"
description: Maintain this repository's Codex control plane when architecture, toolchain, CI, deployment, data, UI, runtime observability, tracker/orchestration, integrations, or recurring review feedback changes. Use to activate/deactivate capability-registry domains, synchronize durable docs, and promote stable recurring rules into mechanical checks. Do not use for ordinary feature implementation that does not change control-plane contracts.
---

# Control Plane Maintenance

Read root `AGENTS.md`, `CONTROL_PLANE.md`, and `docs/control-plane/CAPABILITY_REGISTRY.md`.

1. Identify the concrete project change/evidence that makes a control-plane domain stale or newly applicable.
2. Update the capability row status, trigger evidence, and definition-of-ready evidence. Never mark `ACTIVE` from intention alone.
3. Load only the affected domain document(s) from `docs/control-plane/` and update verified facts/contracts.
4. If the change introduces a durable consequential invariant, decide whether prose is sufficient or a deterministic lint/test/schema/generator/rule is justified.
5. If changing KEEL, Codex hooks/rules/MCP/subagents, treat them as runtime adapters: verify available Codex syntax/evidence, least privilege, project/hook trust behavior, failure handling, context cost, honest event/tool coverage, and permission boundaries. Put lifecycle/scope/evidence/authorization decisions in kernel modules. Static fixtures do not prove installed-runtime enforcement. A KEEL enforcement change is high-risk/control-plane work and must be independently reviewed.
6. Update `ARCHITECTURE.md`, `WORKFLOW.md`, design docs, plans, runbooks, or generated references only when they are materially affected.
7. Independently validate navigation/config/checks. State evidence and unresolved blockers.

Never invent provider/stack details, silently weaken safety settings, self-authorize `KEEL_BYPASS_REASON`, overwrite user work, or claim runtime enforcement is active without testing it.
