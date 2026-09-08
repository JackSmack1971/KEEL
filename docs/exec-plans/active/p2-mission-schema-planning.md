# P2 mission schema and planning

## Objective

Add a deterministic, provenance-bearing `keel.mission/v2` schema and advisory planner while preserving the existing `keel.mission/v1` input/compatibility contract. P2 ends at planning projections; it does not execute or dispatch.

## Design

- `.keel/lib/mission_v2.py` owns v2 validation, canonicalization, v1 normalization, graph/resource/capability/effect semantics, decomposition, and frontier projection.
- P1 evidence is accepted as supplied evidence and classified conservatively. Conflicting/ambiguous/unsupported/stale/runtime-only facts are never promoted to verified readiness.
- `keel mission-v2 validate|frontier|normalize-v1` is an explicit CLI surface. Existing `keel mission ...` remains v1.
- Fixtures and expected outputs are authored independently from implementation and contain no identity-bearing local values.

## Non-goals and generated closure

No dispatch, runtime/provider call, worktree/lock allocation, execution, authorization grant, seal, merge, external effect, P3–P7, or D1. No generated artifact is modified; P2 files are authored contracts/modules/tests.

## Verification

`python .keel/bin/keel.py doctor`, `python .keel/bin/keel.py contracts`, `python .keel/bin/keel.py manifest`, `python .keel/bin/keel.py compat`, focused P2/P1 tests, `git diff --check`, and `keel verify`.
