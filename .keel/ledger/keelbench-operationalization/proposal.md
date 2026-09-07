# Proposal

## Problem / why
KEELBench currently accepts loose run files and aggregates baseline/KEEL results without proving that replicates share an equivalent starting state, rubric, or scenario. That makes empirical comparisons easy to misinterpret.

## Objective
Make KEELBench produce and validate reproducible paired trial manifests, require complete paired evidence before comparison, and report conservative per-replicate and aggregate results without claiming empirical superiority.

## Non-goals
No Codex orchestration, external tracker integration, model invocation, remote repository changes, or automatic policy activation. This slice defines the local benchmark contract and deterministic harness only.

## Success evidence
Deterministic KEELBench tests pass; malformed, incomplete, and mismatched trials fail closed; valid paired trials produce reproducible comparison output; existing corpus validation remains green.

## Open decisions
The agent-execution adapter remains external to this slice and supplies recorded run metrics/events under the new manifest contract.
