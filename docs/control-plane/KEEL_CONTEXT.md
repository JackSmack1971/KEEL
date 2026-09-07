# KEEL Context Architecture

Goal: keep the main decision thread high-signal while preserving inspectable evidence elsewhere.

1. Main thread keeps objective, constraints, decisions, current KEEL gate state, and final evidence summary.
2. `keel.py context` compiles a bounded packet from the current ledger, discovery evidence, changed paths, and relevant documentation pointers; `.keel/context/` is derived/ignored state, never authority.
3. Read-heavy exploration, test/log analysis, docs lookup, and large-file scans should use narrow subagents when doing so reduces noise. Each KEEL agent has a bounded summary contract.
4. Raw outputs belong in tool/evidence artifacts, not pasted wholesale into the main conversation.
5. `SessionStart` and `UserPromptSubmit` hooks invoke the context compiler and cap injected output. If compilation fails, hooks fall back to a minimal ledger-state warning rather than inventing context.
6. After compaction, current Codex may re-run SessionStart hooks; KEEL uses lifecycle restatement rather than asking the model to remember old gate state.
7. Binding state is Git-tracked. Codex memories may help recall preferences/history, but never substitute for `AGENTS.md`, ledger state, plans, acceptance criteria, or verification evidence.

See [CONTEXT_COMPILATION.md](CONTEXT_COMPILATION.md) for the compiler contract.
