# Proposal

## Problem / why

The repository already has a context compiler, but its behavior is not covered by focused executable tests and its packet metadata does not preserve enough provenance to make derived context independently inspectable. The next roadmap milestone needs a small, deterministic proof surface before adding broader repository knowledge extraction.

## Objective

Operationalize the existing compiler so a bounded change context is deterministic, budgeted, provenance-aware, and safe when discovery evidence or referenced documents are missing.

## Non-goals

- No repository-wide knowledge graph or semantic code indexing.
- No automatic policy activation from compiled context.
- No external providers, model routing, or agent orchestration.
- No change to KEEL authorization or verification semantics.

## Success evidence

- Focused tests prove deterministic output, hard character bounds, safe fallback when discovery is malformed, and provenance for selected documents/evidence.
- The canonical KEEL verification suite and strict manifest validation pass.
- Documentation states the derived-context schema and authority boundaries.

## Open decisions

- Whether document provenance should include content hashes or only repository-relative pointers. This milestone resolves it in favor of SHA-256 hashes for included documents, while keeping the packet derived and non-authoritative.
