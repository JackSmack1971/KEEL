# ExecPlan: Plan 002 — Intelligence and Verification Depth

## Objective

Add bounded, provenance-aware repository intelligence and verification-quality controls while preserving the rule that derived intelligence is advisory only.

## Implementation order

1. Repository intelligence substrate: files, modules/symbols where supported, dependencies, tests, configuration, generated surfaces, runtime surfaces, ownership, architecture relations, and explicit uncertainty.
2. Command intelligence: discover commands from repository evidence with provenance/confidence; do not hard-code a stack assumption.
3. Impact analysis: map changes to probable dependents, tests, interfaces, runtime surfaces, and risk indicators.
4. Verification selection: derive additional checks from scope/requirements/risk/impact, never remove policy-required checks.
5. Typed evidence assertions: evaluate provider-specific assertions beyond process exit status.
6. Oracle integrity: detect changes to assertions, thresholds, skipped tests, verification configuration, or similar proof surfaces and require independent verification.
7. Semantic diff classification: identify public API, schema, permissions, dependencies, security, deployment, and verification-surface changes.
8. Context Compiler v2 is explicitly deferred until the graph exists and is consumed by a later change.

## Invariants

Intelligence may add context, suspected impact, verification, risk, and warnings. It may not remove declared requirements, policy-required verification, authorization requirements, scope boundaries, or evidence obligations. Uncertainty makes the system more conservative.

## Verification

Run the configured KEEL verification set plus focused repository-map, evidence-graph, and effect-inference tests. Include negative fixtures for missing/conflicting/stale sources, scope laundering, weakened proof mechanisms, and advisory results attempting to authorize effects.

## Containment

No external effects. Provider adapters remain explicit and repository-local. Unsupported semantics remain unknown; no generated artifact is edited manually.
