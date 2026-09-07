## ADDED
- A versioned runtime capability handshake and structured mission execution result.
- A governed mission runtime with isolated child-change scheduling and bounded retry state.
- Adversarial Mission/Change boundary fixtures for scope, effects, authorization, evidence, sealing, tree identity, and alternate dispatch paths.
- Bootstrap manifest hashes for the changed canonical runtime/doc artifacts are regenerated from their exact bytes.

## MODIFIED
- The CLI exposes explicit mission execution and portability/compatibility semantics.
- Lifecycle and migration reporting distinguish supported local capabilities from unknown external runtime capabilities.

## REMOVED
- Advisory-only mission execution status is replaced by an executable local boundary with fail-closed provider handling.
