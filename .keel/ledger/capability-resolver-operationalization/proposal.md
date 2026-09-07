# Proposal

## Problem / why
`keel discover` currently reports only status, confidence, and a truncated list of paths. It does not explain which rule matched each path, summarize source classification, or protect the resolver with deterministic regression tests. This makes discovery evidence harder to review and easy to regress.

## Objective
Make capability discovery deterministic and reviewable by adding rule-level evidence provenance, source-classification summaries, bounded unknown-path evidence, and focused resolver tests while preserving advisory-only policy behavior.

## Non-goals
Do not edit the capability registry automatically, activate domains from discovery, add provider-specific project configuration, scan ignored dependency/vendor trees, or build a semantic code graph.

## Success evidence
Resolver tests pass for detection, likelihood, unknowns, classifier conflicts, evidence bounds, and deterministic output; `keel discover` preserves advisory policy and writes the documented schema; all control-plane validation passes.

## Open decisions
The registry remains the policy source of truth; discovered evidence is generated state and remains ignored by Git.
