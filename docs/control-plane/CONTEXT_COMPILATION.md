# Context Compilation

KEEL compiles task context instead of accumulating the whole repository control plane into every turn.

Run:

```text
python3 .keel/bin/keel.py context
python3 .keel/bin/keel.py context --stdout
```

The compiler combines current phase/base/mode, objective, delta, scope, risk/effects, acceptance contract, changed paths, capability-discovery evidence, and **pointers** to relevant authoritative docs. Generated packets live under `.keel/context/` and are ignored by Git.

## Invariants

- The packet is derived context, never a source of truth.
- Binding state remains the ledger, repository docs, configuration, and Git evidence.
- A hard character budget prevents the context compiler from becoming a new context-bloat mechanism.
- Capability-specific detail is represented primarily as load-next pointers; raw logs and long test output remain outside the main orchestration thread.
- Session/UserPrompt context hooks use this compiler and fall back to a minimal state summary if compilation fails.

The objective is **minimum sufficient decision context at the current consequential branch**, not maximum retrieval.
