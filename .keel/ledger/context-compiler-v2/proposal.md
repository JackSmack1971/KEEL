# Proposal

## Problem / why
The current context compiler selects documents primarily from static capability mappings and always-loaded documents. Plan 002 now provides a derived repository graph and impact facts that can support query-driven, role-specific selection, but there is no bounded API that consumes those facts while preserving mandatory context and uncertainty.

## Objective
Add Context Compiler v2 selection that consumes repository intelligence and impact/query inputs, produces role-specific packets with provenance and confidence, and remains monotonic: it may add context and warnings but cannot remove policy-required documents or ledger obligations.

## Non-goals
Changing KEEL policy, authorizing effects, replacing the existing compiler contract, external retrieval, autonomous document mutation, or implementing provider-specific context sources.

## Success evidence
Focused tests prove deterministic role/query/impact selection, provenance for selected and unavailable sources, mandatory documents are retained, uncertainty widens warnings, and the CLI exposes the v2 surface. Full configured verification passes.

## Open decisions
Role profiles and graph input are repository-local configuration contracts; unsupported roles or unavailable graph data must remain explicit and conservative.
