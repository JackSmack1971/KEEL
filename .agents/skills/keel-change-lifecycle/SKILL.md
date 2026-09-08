---
name: keel-change-lifecycle
metadata:
  version: "1"
description: Govern a repository write change with KEEL when implementation, refactoring, docs/control-plane edits, migrations, release preparation, infrastructure changes, or other engineering mutation is requested. Use standard mode by default, trivial fast path only for clearly low-risk localized writes, and operator-authorized emergency bypass only for time-critical incidents. Do not activate for purely read-only investigation/explanation.
---

# KEEL Change Lifecycle

Read root `AGENTS.md`, `WORKFLOW.md`, and `docs/control-plane/KEEL.md`.

## Mandatory
1. For a write change, ensure Git has a baseline commit and start/resume exactly one KEEL change-id.
2. Standard mode calls deterministic kernel operations in order: proposal -> discuss gate -> delta + requirements/acceptance + scope/risk/effects -> plan gate -> execute -> `keel verify` / `keel evidence` receipt coverage -> commit verified tree -> `keel seal` -> authorized integration -> landed `anchor`. This skill is routing knowledge, not lifecycle authority.
3. One primary writer per worktree. Dynamically use generic explorer/reviewer/risk-reviewer roles only when missing facts, evidence requirements, impact, or risk justify them. Delegate only read-heavy bounded work unless each writer has a separate worktree/change; agent output never grants permission or changes lifecycle state.
4. Never edit outside `scope.txt`; update/re-gate the plan if scope legitimately changes.
5. High/control-plane/security/privacy/migration/release/high-blast-radius work requires substantive risk review; require ExecPlan when `risk.json` says so.
6. Verification truth comes from `.keel/ledger/<id>/verification.json` plus `evidence-graph.json`, not model prose. Every required AC must resolve through deterministic evidence before PASS. Before integration, seal the exact committed tree; final anchor independently re-hashes the landed tree for the verified paths+intent.
7. `SHIP` is eligibility, not permission for external/irreversible operations.
8. `authorization.json`, `state.json`, gate logs, and verification records are script-owned. Never hand-edit them. Re-plan invalidates prior effect authorization.

## Trivial fast path
Use only when all are true: localized, reversible, low coupling, no control-plane/security/privacy/migration/release/external effect/high blast radius, and verification is straightforward. Start with `--mode trivial --summary ... --scope ...`; normal scope and verification still apply.

## Emergency bypass
Only the operator may provide `KEEL_BYPASS_REASON` in the Codex parent environment. Never self-set it to escape a gate. It bypasses KEEL blocking only and creates auditable retro process debt.

## Failure exits
- missing initial commit -> stop and request/establish local baseline without inventing identity;
- missing canonical verification commands for source change -> update project command contract from evidence, do not guess;
- missing/invalid REQ/AC contract or unsupported evidence provider -> re-plan; do not waive acceptance coverage;
- out-of-scope write -> stop, inspect, either revert safely or re-plan explicitly;
- stale verification -> `reopen`, change, re-verify;
- unsealed candidate -> commit the verified tree, run `keel.py seal`, then retry integration;
- landed-tree digest mismatch -> stop; inspect merge/squash/rebase/conflict resolution and re-verify/reseal rather than overriding the anchor;
- hook/project trust unavailable -> report filesystem KEEL installed but runtime enforcement unverified;
- external authorization missing -> stop at review/handoff.

## Adaptive helpers
- `keel.py discover` produces capability evidence without changing policy.
- `keel.py context` compiles a bounded current-change context packet; treat it as derived navigation, not authority.
- `keel.py evidence` reads the latest machine-evaluated acceptance graph.
- KEELBench is for empirical baseline comparison and does not replace per-change verification.
