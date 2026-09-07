---
name: engineering-protocols
metadata:
  version: "1"
description: Route recurring debugging, architecture, dependency, migration, security, performance, frontend-runtime, test-remediation, incident, and release work to evidence-producing protocols. Do not activate for ordinary implementation without one of these protocol concerns.
---

# Engineering Protocols

Use this skill when the task has a named protocol concern. Select the smallest applicable row; combine concerns only when the task actually spans them.

| Concern | Decision-changing evidence | Completion proof |
|---|---|---|
| Debugging / root cause | Reproduce or establish a baseline; record falsifiable hypotheses and narrow the trigger. | Regression proof plus the original failure no longer reproduces. |
| Architecture investigation | Trace actual dependencies and authority; distinguish verified facts from proposals; identify the narrowest invariant. | Updated boundary/decision artifact and structural or focused verification. |
| Dependency upgrade | Identify direct/transitive provenance, compatibility risk, lockfile impact, and security/license evidence. | Reproducible install/build/test evidence and reviewed diff. |
| Migration | Define preconditions, backup/restore or rollback, idempotency, compatibility window, and cutover evidence. | Dry-run or test migration plus rollback/restore proof. |
| Security review | Map assets, actors, trust boundaries, untrusted inputs, secrets, and least-privilege effects. | Targeted security evidence, with no unapproved external action. |
| Performance investigation | Establish a repeatable metric baseline, isolate one mutable variable, and control workload/environment. | Before/after measurements and regression-threshold evidence. |
| Frontend/runtime verification | Exercise the real runtime and collect relevant DOM, visual, console, network, accessibility, or device evidence. | Reproducible runtime artifact tied to acceptance. |
| Test remediation | Classify the uncovered behavior and add the narrowest meaningful test; prove it detects the target failure. | Test output plus red/green or perturbation evidence. |
| Incident response | Preserve timestamps/logs and impact, contain within authorization, separate mitigation from root cause, and define recovery. | Incident evidence, recovery check, and follow-up invariant/task. |
| Release | Verify version/artifact provenance, compatibility, migration/rollback, and explicit release authorization. | Reproducible release checks and rollback/handoff evidence. |

For every protocol:

1. Read current repository evidence and establish a baseline before attributing results to a change.
2. Keep hypotheses, observations, and decisions separate; do not turn unreviewed feedback into permanent policy.
3. Use the KEEL lifecycle for writes and respect scope, acceptance evidence, effects, authorization, and sealed-tree verification.
4. Stop at review/handoff when external, irreversible, privileged, or production effects lack explicit authorization.
5. Report pre-existing failures and unresolved uncertainty instead of treating an unrelated green check as proof.

This is routing and method guidance, not an agent roster, model router, permission grant, or replacement for domain-specific controls.
