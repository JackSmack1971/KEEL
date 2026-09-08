# KEEL — Spec-Anchored Change Control Plane

Status: `INSTALLED`; runtime enforcement is `CONDITIONAL` until project trust + hook trust + Python/Git smoke tests are observed.

KEEL is the repository's per-change governance spine. It layers under the broader control plane: repository legibility tells an agent where truth lives; KEEL anchors each write change to a delta/scope/risk/evidence record; architecture/CI/security/release/operations supply domain checks; Symphony-style orchestration may later schedule isolated KEEL changes.

## Ledger
Each active change owns:

```text
.keel/ledger/<change-id>/
  state.json           # deterministic phase/mode/base commit
  proposal.md          # WHY / objective / non-goals / success evidence
  delta.md             # WHAT: ADDED / MODIFIED / REMOVED
  requirements.json    # machine-readable REQ-* behavioral obligations
  acceptance.json      # AC-* criteria -> deterministic evidence edges
  scope.txt            # machine-checkable repo-relative files/globs
  risk.json            # risk level + control-plane/sensitive flags
  effects.json         # declared external/irreversible side effects
  authorization.json   # script-owned, effects-bound record of permission already obtained when required
  gate-log.jsonl       # append-only-in-normal-use gate/audit events
  verification.json    # structured command/exit-code/digest evidence
  verification.md      # concise human/agent-readable summary
  evidence-plan.json  # requirement/impact-selected verifier plan
  evidence-receipts.json # exact-subject authoritative verifier receipts
  evidence-graph.json  # temporary compatibility projection
  evidence/            # bounded/redacted command excerpts when produced
  risk-review.md       # required for high/control-plane/sensitive changes
```

`gate-log.jsonl` is mechanically written by KEEL scripts/hooks in normal operation. Like any working-tree file it can be edited by a sufficiently privileged actor, so integrity ultimately comes from landed Git history + independent verification + remote protections where required.

## Delta format

```markdown
## ADDED
- ...

## MODIFIED
- ...

## REMOVED
- ...
```

At least one section must contain a real bullet. The prose delta states behavior; `scope.txt` exists separately because free-form Markdown is a poor enforcement interface.

## Gates

- `DISCUSS`: proposal is meaningful.
- `PLAN`: delta, requirements, acceptance criteria, scope, risk, and effects are structurally valid; KEEL synchronizes authorization shape without granting permission; high-risk work has a risk review and ExecPlan where required.
- `EXECUTE`: writes may occur only in declared scope; direct file tools are pre-checked and all Git diff paths are post/stop checked.
- `VERIFY`: scope and required authorization pass, canonical project checks run, every required property resolves through sufficient exact-subject receipts, literal exit status is recorded, and the verified digest covers both changed content and stable intent artifacts.
- `SHIP`: verified content is eligible for authorized integration only after implementation acceptance passes (or an explicit planning-only change completes through readiness); planning readiness alone never reaches this phase. It is not authorization itself.

After Plan passes, intent/scope changes require `keel.py replan`; re-plan invalidates prior effect authorization. After verification, implementation changes require `keel.py reopen`. This prevents silent spec drift.

Direct mutation permissions are phase-specific: DISCUSS permits only `proposal.md`; PLAN permits proposal/delta/requirements/acceptance/scope/risk/effects/risk-review plus the matching active ExecPlan; authorization/state/gate/verification records are script-owned; EXECUTE permits only declared implementation scope; VERIFY/SHIP permit no direct content writes without reopen/replan.

Hooks do not provide total confinement. Specialized tool paths may bypass hook coverage; therefore `keel verify` rechecks the Git diff independently and Codex sandbox/approval/rules/domain controls remain load-bearing.

## Modes
- `standard`: full lifecycle.
- `trivial`: only for localized, reversible, low-risk writes. `start --mode trivial --summary ... --scope ...` creates/passes Discuss+Plan deterministically, then normal Execute/Verify/Ship still applies.
- read-only: no ledger needed because no mutation occurs.
- emergency: operator exports `KEEL_BYPASS_REASON` before launching Codex. Hooks stop blocking but append a bypass event and create `retro-<change-id>` process debt; if no change-id was active, KEEL creates a deterministic `retro-emergency-*` debt entry instead. The variable must come from the parent process; putting it inside a proposed shell command does not authorize the parent hook runtime.

## Emergency safety invariant
KEEL bypass never changes Codex permission mode, sandbox, rules, hook trust, host authorization, secrets policy, deployment permissions, or application authorization. It bypasses only KEEL's phase/scope stop behavior. See [KEEL_EMERGENCY.md](KEEL_EMERGENCY.md).

## Sealed candidates and Git anchors
After verification, commit the candidate in its worktree and run `seal`. KEEL recomputes the content+intent digest from the **commit tree**, requires the committed material diff to match the verified changed-path set, and creates:

- `refs/keel/candidates/<change-id>` -> exact verified candidate commit.
- `refs/keel/attestations/candidates/<change-id>` -> canonical
  `CandidateAttestation` blob binding work/base and candidate commit/tree identity,
  independent material and intent digests, combined content digest, EvidencePlan
  digest, supporting EvidenceReceipt identities/digests, and available policy/runtime
  profile digest.

An integration checkout can then merge that exact ref. After landing, use `anchor` to create:
- `refs/keel/ledger/<change-id>` -> landed commit;
- `refs/notes/keel` note on the landed commit.

Anchoring requires the sealed candidate, re-reads the landed ledger, and recomputes the candidate's verified changed-path + intent digest from the landed Git tree. This permits unrelated mainline changes and supports either candidate ancestry or content-equivalent squash/rebase landing while refusing candidate-content drift. The operation refuses collisions to a different commit/note. Refs/notes are mutable Git metadata, not an immutable ledger; protected remote history/audit systems are required when stronger tamper resistance matters.

The Git blob is the payload and refs/notes are mutable indexes/anchors; none is claimed
immutable. Existing anchor behavior continues unchanged at the integration boundary.
The future Landing Transaction is not implemented by this subsystem.

## Definition of KEEL-ready
1. Git repository exists with an initial baseline commit.
2. `python3 .keel/bin/keel.py doctor` passes.
3. Project `.codex/` layer is trusted.
4. `.codex/hooks.json` exact definition has been reviewed/trusted through Codex `/hooks` (or managed policy supplies equivalent enforcement).
5. A runtime smoke test demonstrates SessionStart/UserPrompt context and a blocked out-of-phase write/Stop gate.
6. Once substantive source exists, `.keel/config.json` contains real canonical verification commands.

Until those are observed, report KEEL as installed but not fully runtime-validated.

## Adaptive intelligence primitives

- `keel.py discover` emits evidence-backed capability suggestions without silently activating policy. See [CAPABILITY_RESOLUTION.md](CAPABILITY_RESOLUTION.md).
- `keel.py context` compiles a bounded derived context packet for the current decision surface. See [CONTEXT_COMPILATION.md](CONTEXT_COMPILATION.md).
- `keel.py next` reports the next legal action and blockers for the active change; it is read-only guidance and never advances lifecycle state.
- Required `REQ-*`/`AC-*` contracts derive EvidenceRequirements, a selected EvidencePlan, and authoritative EvidenceReceipts. `evidence-graph.json` is a compatibility projection. See [ACCEPTANCE_EVIDENCE.md](ACCEPTANCE_EVIDENCE.md).
- `.keel/bench/` provides KEELBench paired-run schemas and scoring. See [KEELBENCH.md](KEELBENCH.md).
- `keel change-graph` and the stable `keel mission` alias validate or normalize canonical planning graphs and report a read-only frontier from typed hard-dependency edges plus explicitly supplied state. Mission v1/v2 reads pass through compatibility adapters; the hidden `mission-v2` alias is temporary. Planning does not schedule, dispatch, observe runtime state, or grant requested effects.
