## ADDED
- A deterministic Codex-adapter kernel query boundary normalizes supported runtime events/tool invocations, establishes conservative RuntimeProfile state, compiles bounded context, and returns explicit allow/deny/context/observe outcomes.
- Realistic subprocess wire-contract fixtures cover context, local write tools, Bash, additional local tools, MCP functions, invalid/untrusted state, outside-repository behavior, and post-effect limitations.
- Installed-runtime smoke instructions distinguish live hook observations from static fixture evidence.

## MODIFIED
- Codex hooks become thin wire/input-output adapters over the kernel query and advertise broader supported event coverage without claiming confinement.
- Runtime authorization owns adapter enforcement expectations, outside-authority classification, and fail-open/fail-closed semantics.
- Codex rules and KEEL skills describe runtime guardrails/adapters rather than independent lifecycle or authorization policy.
- Generic explorer/reviewer/risk-reviewer roles are selected dynamically from kernel evidence/risk context rather than phase names.
- Architecture, workflow, control-plane documentation, verifier configuration, and generated bootstrap provenance reflect the M4 adapter boundary.
- The bootstrap manifest producer supports an explicit, tested retirement list so removed generated-source entries are pruned by provenance rather than hand editing.

## REMOVED
- Hard-coded `keel-discuss`, `keel-plan`, `keel-verify`, and `keel-ship` agent definitions and documentation references.
- Semantic lifecycle, scope, evidence, and integration policy logic from the hook adapter.
