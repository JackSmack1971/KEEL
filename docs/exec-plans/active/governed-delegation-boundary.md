# ExecPlan: governed Codex delegation completion boundary

Status: ACTIVE

## Objective and success evidence
Replace objective-only scheduler dispatch with a canonical governed envelope and a persisted execution observation. A Codex transport completion may reach only `AWAITING_VERIFICATION`; exact-subject KEEL evidence evaluation is the sole route to `COMPLETE`. Hostile tests must disprove workspace confusion and every stale identity class.

## Verified context and baseline
Baseline is clean `main` commit `766de783bb846957b7011a38a9b7ffbb71b8e038`. `python3 .keel/ci/verify.py` passed before implementation, including explicit `UNVERIFIED_RUNTIME` for the intentionally disabled live Codex branch. Current adapter dispatch calls `thread/start` without `cwd`, submits only `unit.objective`, and maps `turn/completed` directly to scheduler `COMPLETE`.

## Non-goals
No broad autonomous `keel run`, provider/API billing path, model runtime, conversation scheduler, sandbox, or stack-specific project semantics.

## Risk, autonomy, and permission boundaries
This is high-risk control-plane and security-sensitive work because identity confusion can execute in or verify the wrong subject. Dispatch must fail closed before thread creation. ZERO_INCREMENTAL_COST must remain before `turn/start`. Codex owns runtime execution; KEEL owns envelope construction, workspace proof, desired state, evidence evaluation, and completion. PR creation and merging are requested external effects, but actual grants and repository permissions remain authoritative.

## Milestones
1. Define immutable envelope, workspace proof, observation, verification decision, serialization, and state persistence.
2. Require scheduler governance context and make the adapter use full context plus validated `cwd`.
3. Add hostile tests for omitted context, workspace mismatch, stale identities, completion separation, recovery identity, and preflight ordering.
4. Reconcile architecture/orchestration/Codex/verification docs; run focused and full deterministic evidence; independently review; commit, seal, PR, merge, and anchor the landed tree.

## Failure branches
Any unresolved worktree, Git subject mismatch, incomplete envelope, stale identity, failed evidence decision, missing cost observation, or model execution before preflight blocks progress. Runtime unavailability is reported, not converted to success. Remote authorization/check failure blocks integration rather than being overridden.

## Progress log
- 2026-09-09: established clean baseline and full deterministic PASS; inspected current scheduler and App Server transport defect.

## Final verification
Pending implementation.
- 2026-09-09: implemented immutable governed envelopes, exact registered-worktree resolution, validated `cwd`, bounded execution observations, `AWAITING_VERIFICATION`, receipt-authoritative exact-identity completion, persistence, and hostile tests.
- 2026-09-09: independent review found incomplete observation/runtime/evidence identity validation, awaiting-verification resource release, unvalidated base ancestry, and event byte bounds. Remediation now validates every duplicated observation identity, actual RuntimeProfile identity/digest, canonical EvidencePlan/receipt evaluation, resource retention, canonical ancestor base, and total observation bytes.

## Final verification
Focused hostile scheduler, App Server, cost-preflight, smoke, and documentation tests passed. The full repository deterministic verifier passed with live Codex intentionally reported `UNVERIFIED_RUNTIME`; no model execution was required.

## Completion / handoff
Implementation and independent review remediation are complete. Candidate sealing, PR checks, authorized merge, landed-tree anchor, and exact landed-tree re-verification remain lifecycle delivery steps.
