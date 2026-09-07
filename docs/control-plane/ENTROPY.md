# Entropy and Documentation Gardening

Agent-generated repositories replicate existing patterns, including bad ones. Drift is expected and should be controlled continuously.

## Golden process principles
- shared durable abstractions over repeated one-off helpers when evidence supports reuse;
- parse/validate at trust boundaries rather than ad-hoc downstream shape probing;
- one source of truth for generated information;
- repository knowledge updated with code behavior;
- mechanical checks for repeated consequential mistakes;
- small, reviewable cleanup changes rather than periodic giant rewrites.

Use the repository skill `control-plane-maintenance` when tooling, architecture, workflow, or recurring feedback changes the control plane. Once a scheduler exists, consider a recurring small gardening task with explicit quality metrics and safe merge policy.
