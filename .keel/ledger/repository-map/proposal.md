# Proposal

## Problem / why
Capability discovery identifies domains, but KEEL still lacks a compact, provenance-bearing map of repository structure that agents can query without repeatedly scanning the tree.

## Objective
Add a deterministic `keel map` report for topology, modules, entrypoints, tests, commands, and dependency manifests, with every fact tied to a repository path and mapping rule.

## Non-goals
No semantic import/dependency graph, ownership inference, code indexing, RAG store, policy activation, or external service integration.

## Success evidence
Focused tests prove deterministic output, ignored-directory handling, provenance on emitted facts, and safe write boundaries. Existing control-plane checks pass.

## Open decisions
The map is a derived navigation artifact; source documents, ledgers, and architecture contracts remain authoritative.
