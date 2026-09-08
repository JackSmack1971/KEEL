# Context Compilation

KEEL compiles task context instead of accumulating the whole repository control plane into every turn.

Capability inputs are derived from the canonical FactGraph through the compatibility
resolver. The packet remains a bounded navigation projection; it is not repository,
policy, command, or authorization authority.

Run:

```text
python3 .keel/bin/keel.py context
python3 .keel/bin/keel.py context --stdout
```

The compiler combines current phase/base/mode, objective, delta, scope, risk/effects, acceptance contract, changed paths, capability-discovery evidence, and **pointers** to relevant authoritative docs. Its metadata schema is version `2` and records whether discovery came from cached generated state or resolver fallback, plus repository-relative document provenance (`PRESENT` with SHA-256, `MISSING`, or `OUTSIDE_REPOSITORY`). Generated packets live under `.keel/context/` and are ignored by Git.

## Invariants

- The packet is derived context, never a source of truth.
- Binding state remains the ledger, repository docs, configuration, and Git evidence.
- A hard character budget prevents the context compiler from becoming a new context-bloat mechanism.
- Malformed cached discovery is discarded and replaced with fresh resolver evidence; cached content never becomes an authorization or policy source.
- Capability-specific detail is represented primarily as load-next pointers; raw logs and long test output remain outside the main orchestration thread.
- Session/UserPrompt context hooks use this compiler and fall back to a minimal state summary if compilation fails.

The objective is **minimum sufficient decision context at the current consequential branch**, not maximum retrieval.
