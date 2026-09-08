# Decision and Autonomy Model

## Mandatory
- Establish project facts before specialization.
- Use KEEL for write changes; select standard unless trivial criteria are clearly met.
- Preserve user data/work and existing history.
- Baseline before diagnosing introduced failures when practical.
- Verify completion with observable evidence, scope checks, intent digest, and required authorization record.
- Record durable consequential decisions in-repo.
- Classify every control-plane domain explicitly.

## Prohibited
- Silent assumptions presented as facts.
- Multiple write agents concurrently editing one worktree.
- Trivial mode for control-plane, security/privacy, migration, release/deploy, external-effect, high-coupling, or high-blast-radius work.
- Destructive cleanup/reset to recover from an agent mistake.
- Secret disclosure or credential persistence.
- Approval/sandbox/hook bypass merely for convenience.
- Manual mutation of declared generated outputs contrary to provenance.
- Unapproved external/irreversible/high-blast-radius operations or fabricated authorization records.

## Judgment regions
Use agent judgment for implementation details, investigation order, refactoring shape, validation breadth beyond mandatory checks, and tool choice when multiple reasonable paths satisfy constraints.

Choose autonomy by reversibility, blast radius, authorization, external effects, privacy/security impact, recovery speed, observability, and uncertainty. Emergency KEEL bypass changes process timing only; it does not change those consequence controls.

## Runtime trust policy

The implemented policy evaluates consequence, reversibility, uncertainty,
observability, evidence strength, runtime enforcement, authorization, and recovery
cost. Its ordered outcomes are `ALLOW_AUTONOMOUS`,
`ALLOW_WITH_STRONGER_VERIFICATION`, `REQUIRE_CAPABILITY`,
`REQUIRE_INDEPENDENT_REVIEW`, `REQUIRE_HUMAN_DECISION`, and `PROHIBIT`.
Missing or invalid authority and unknown/unconfined runtime surfaces lower the
ceiling; unavailable observations never receive optimistic defaults.

A `CapabilityGrant` is valid only for its bound subject, work/change, effect
request, action, resource, constraints, intent digest, accepted issuer evidence,
validity window, and remaining use count. Changed intent invalidates an
incompatible grant. A plan, effect declaration, legacy `authorized=true`, adapter
availability, or receipt is not a grant.
