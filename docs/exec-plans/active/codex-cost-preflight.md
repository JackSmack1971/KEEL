# Codex ZERO_INCREMENTAL_COST preflight

Status: active
Owner / resumption note: primary writer in `codex/codex-cost-preflight-impl`; resume from the KEEL ledger and this plan.

## Goal and stopping conditions

Before autonomous Codex execution, classify the observed runtime as `SUPPORTED`
only with complete managed ChatGPT/Codex entitlement evidence. Every other
state is `BLOCKED`, with no fallback or limit-bypass operation. Stop only after
AC-01 through AC-12 have exact test or inspection evidence and the candidate is
verified and sealed.

## Constraints and non-goals

Use only documented local Codex observations. Never request, read, persist, or
pass API keys, email, account identifiers, or credentials. Never purchase,
nudge, consume reset credits, rotate identity, or call a secondary provider.
Keep human-directed governance usable and preserve resumable blocked state.

## Acceptance/evidence index

The canonical acceptance matrix is `.keel/ledger/codex-cost-preflight/intent.json`.
The focused hostile matrix is `.keel/tests/test_codex_cost_preflight.py`;
regression evidence uses the repository's configured verifier registry.

## Baseline

- Revision: `1473ea005c633fc0f99f5b8b631ba4825856b1fc`
- Pre-existing active state: none in this worktree.
- Runtime observation fact: repository has no documented account/billing API
  adapter; absent evidence therefore must remain blocked.

## Facts, assumptions, and unknowns

Facts are limited to repository source and the fixed decisions in the request.
The implementation may model documented observations supplied by a Codex adapter,
but it must not invent an upstream billing surface. Whether a future installed
Codex runtime exposes a stable entitlement observation remains unknown; that
unknown is a blocking condition, not an allow condition.

## Progress log

Iteration / timestamp: 2026-09-08
Hypothesis or acceptance criterion: lifecycle and acceptance contract can be established without broadening scope.
Action: inspected NS0 authority, RuntimeProfile, adapter, CLI, scheduler, and tests; created standard ledger in isolated worktree.
Observation: existing runtime profile has no cost eligibility; `run` is already blocked without an adapter; public surfaces are centralized in `keel_core.py`.
Verification (distinct from action): source inspection and clean worktree status confirmed the integration points and no documented account/billing surface.
Decision: continue
Blocker / failure classification: none
Next uncertainty: exact autonomous dispatch seam and conservative observation schema.
