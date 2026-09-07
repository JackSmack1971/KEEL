# ExecPlan: P0 remediation — portability, provenance, hygiene, and plan archival

Status: `COMPLETE / LANDED`

This remediation is a child of the anchored KEEL change `p0-portable-verification-bootstrap-contract` because the original candidate and landed refs are collision-protected. It addresses only the four defects recorded by the independent P0 completion audit. It does not reimplement passed compatibility/migration behavior, instantiate P1, execute D1, or unblock P4.

## Required outcomes

1. Missing manifest-listed inputs produce explicit drift/failure; changed and unrelated drift are detected; matching regeneration verifies.
2. Present-but-unproven discovered commands are distinct from zero candidates while existing command-resolution statuses remain stable.
3. Newly produced remediation ledger artifacts and the final parent-to-child commit pass unsuppressed `git diff --check`.
4. After all implementation acceptance passes, the completed original P0 ExecPlan moves to `docs/exec-plans/completed/`, references remain truthful, and P1 remains unstarted.

## Verification

Run focused P0 remediation tests first, then lifecycle compatibility, schema migration, next-action, upgrade-kernel, hook compatibility, manifest drift, doctor, change-scoped KEEL verification, unsuppressed committed-diff hygiene, candidate status, seal, anchor, and explicit/implicit `keel next`. Do not run KEELBench or other D1 evaluation.

## Completion boundary

Completion requires the four outcomes above, fresh evidence on the child change, a sealed child candidate, an independently matching landed-tree anchor, a clean worktree, and no P1 implementation or D1 execution. The original P0 anchor remains preserved; this plan is historical remediation evidence for its four corrected defects.
