# Risk review

- Schema risk: low; add versioned fields without changing existing classifications.
- Parser risk: contained; parse failures become per-file findings, never execution.
- Trust risk: low; facts carry source paths and analyzer provenance and are not authorization evidence.
- Scope risk: bounded to map implementation, tests, docs, and manifest hashes.

## Control and verification

The analyzer uses only the standard-library AST parser and never imports or executes repository code. Parse errors are recorded as evidence, not hidden. The output is derived navigation data and cannot authorize effects, change lifecycle state, or replace acceptance verification. Tests cover deterministic output, explicit unsupported/failed analysis, and unchanged source state; strict control-plane validation and the full KEEL check set remain required before sealing.
