# Proposal

## Problem / why
Current KEEL commands return individually shaped JSON and lifecycle events are local to a ledger. That makes clients couple to internal Python structures and leaves no durable correlation contract for cross-tool evidence. Provider vocabulary exists, but there is no explicit adapter boundary that prevents a provider from becoming an authorization path.

## Objective
Introduce a small, versioned domain response/event contract, propagate correlation identifiers through lifecycle operations, and define provider adapter declarations that remain disabled and authorization-neutral.

## Non-goals
No live GitHub, MCP, cloud, database, tracker, package-registry, or other external mutation; no dashboard; no transport-specific authorization; no migration of existing public schemas beyond an explicit compatibility failure.

## Success evidence
Contract tests assert deterministic response envelopes, version rejection, correlation propagation, append-only event records, redaction, and provider declarations that cannot grant authorization. Existing canonical checks and adversarial boundary tests remain green.

## Open decisions
Provider-specific transport implementations and external identity/credential policy remain deferred until a separately authorized integration change.
