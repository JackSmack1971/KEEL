# AGENTS.md

## Mission
Build and maintain **KEEL-v2** as a legible, verifiable engineering repository. Humans specify intent and consequential policy; agents execute reversible work inside documented boundaries.

## Read first
1. [CONTROL_PLANE.md](CONTROL_PLANE.md) — operating model and capability state.
2. [WORKFLOW.md](WORKFLOW.md) — KEEL change lifecycle and evidence rules.
3. [ARCHITECTURE.md](ARCHITECTURE.md) — verified architecture facts and boundaries.
4. [docs/INDEX.md](docs/INDEX.md) — progressive-disclosure map.
5. [docs/control-plane/KEEL.md](docs/control-plane/KEEL.md) — spec ledger, gates, fast path, bypass, worktrees.

## Persistent invariants
- Repository evidence beats assumption; never invent project facts or commands.
- Binding decisions/spec state live in Git-tracked repository artifacts, not chat memory.
- Any write change uses KEEL: `standard` by default, `trivial` only for low-risk localized work, emergency bypass only when operator-authorized.
- One change-id has one primary write owner in one worktree. Parallel writes require separate worktrees.
- Do not manually edit declared generated artifacts; follow provenance/regeneration contracts.
- Establish a baseline before attributing failures to a change.
- Completion requires observable verification capable of disproving success.
- Preserve unrelated work; destructive reset/cleanup is never a convenience mechanism.
- Do not weaken security, sandbox, approvals, hooks, or rules merely to get work through a gate.
- External, irreversible, privileged, security/privacy-sensitive, migration, release, or high-blast-radius effects require explicit authorization and stronger evidence.
- Repeated consequential mistakes should become tested mechanical invariants, not repeated prose reminders.

## Change entry points
- Read-only investigation: no KEEL ledger required; return concise evidence.
- Trivial write: `python3 .keel/bin/keel.py start <id> --mode trivial --summary "..." --scope <path-or-glob>`.
- Standard write: start a change, produce proposal + delta + requirements/acceptance + scope + risk/effects state, pass discuss/plan gates, execute, verify the acceptance/evidence graph, commit the verified tree, `keel.py seal`, then authorized integration/handoff and landed `anchor`. Re-plan if intent/scope/acceptance changes; do not hand-edit authorization/state/gate/verification records.
- Emergency: operator launches Codex with `KEEL_BYPASS_REASON`; KEEL gates become audit-only and create retro process debt. This never bypasses Codex/runtime/application authorization.

## Adaptive helpers
- `python3 .keel/bin/keel.py discover` — evidence-backed capability detection; never silent policy activation.
- `python3 .keel/bin/keel.py context` — compile a bounded current-change context packet.
- `python3 .keel/bin/keel.py evidence` — inspect the latest acceptance/evidence graph.
- `python3 .keel/bin/keelbench.py validate` — validate the paired-evaluation corpus; benchmark results are separate from deterministic self-tests.

## Before declaring done
- Inspect KEEL status and diff scope.
- Run `python3 .keel/bin/keel.py verify` for an active write change.
- Before integration, require a sealed candidate that independently matches committed-tree verification evidence.
- Independently review consequential changes.
- Update affected docs/plan/decision records.
- State verified evidence, pre-existing failures, unresolved blockers, and external actions taken/not taken.
