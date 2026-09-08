# Development Workflow — KEEL-governed

KEEL is the default write-change lifecycle. It is a thin governance spine around capable agent judgment, not a reason to force ceremony onto read-only exploration or genuine emergencies.

## Mode selection

| Mode | Use | Required control |
|---|---|---|
| Read-only | Investigation, explanation, evidence gathering | No ledger; no writes |
| Trivial | Localized, reversible, low-coupling write with no external/security/migration/release effect | One-command proposal/delta/scope fast path + normal scope/verification |
| Standard | Normal feature/fix/refactor/docs/control-plane changes | Discuss -> Plan -> Execute -> Verify -> Ship |
| Emergency bypass | Time-critical incident where normal gates materially increase harm | Operator-owned bypass reason; audit + retro ledger; all non-KEEL safety boundaries remain |

If uncertain between trivial and standard, use standard. High-risk/control-plane/external/migration/security changes cannot use trivial mode.

## Standard lifecycle

### 1. Start / Discuss
`python3 .keel/bin/keel.py start <change-id>` creates a ledger rooted at `.keel/ledger/<change-id>/` and records the current Git baseline commit. Use the `keel_discuss` read-only agent when useful. Write a concrete `proposal.md`: problem, objective, non-goals, success evidence, unresolved decisions.

Pass: `python3 .keel/bin/keel.py gate discuss`.

### 2. Plan
Use `keel_plan` for read-heavy planning. Maintain:
- `delta.md` — ADDED / MODIFIED / REMOVED behavior;
- `scope.txt` — exact repo-relative files/globs the implementation may touch;
- `risk.json` — risk level and consequential-change flags;
- `effects.json` — declared external/irreversible effects, if any;
- `authorization.json` — legacy KEEL-owned evidence record for permission reported as obtained when `effects.json` requires it. Do **not** hand-edit it; its boolean is not a canonical grant and cannot independently authorize an effect;
- durable ExecPlan when risk/cross-cutting criteria require one.

Pass: `python3 .keel/bin/keel.py gate plan`.

### 3. Execute
Trace the actual code/data/runtime path before editing. One primary write owner edits only declared scope inside the change's worktree. Read-heavy exploration/review/test-log analysis may fan out to subagents and should return distilled summaries rather than raw dumps.

If proposal/delta/scope/risk/effects intent must change after Plan passes, run `python3 .keel/bin/keel.py replan` and pass Plan again before continuing. Re-plan invalidates previously recorded effect authorization. After verification, use `keel.py reopen` for implementation edits or `replan` for intent changes.

### 4. Verify
Run `python3 .keel/bin/keel.py verify`. KEEL performs structural/scope checks, derives an impact- and requirement-selected EvidencePlan from the verifier registry, executes selected verifiers, and records exact-subject EvidenceReceipts. Compatibility projections remain in `verification.json` / `verification.md`; receipt coverage is authoritative and an unrelated green command cannot satisfy a requirement. Required external/irreversible authorization must be recorded before the legacy Verify path can pass; the record is effects-bound evidence, but its boolean is not a `CapabilityGrant`. Effect execution additionally requires a valid intent-bound grant and sufficient observed runtime enforcement. Within Codex, the pre-tool hook blocks agent-initiated `record-authorization` unless the parent session explicitly carries `KEEL_AUTHORIZATION_CHANGE=<exact-change-id>`; an operator may also run the recorder directly outside the agent session.

Use the `keel_verify` agent for independent interpretation/review of evidence, not as the source of pass/fail truth.

### 5. Seal / Ship / handoff
`SHIP` means the working content is verified and eligible to become a candidate; it does not itself grant permission to push, merge, release, deploy, migrate, or mutate external systems. A task may stop at review/handoff.

Commit the verified change in its write worktree, then seal the exact commit:

```text
python3 .keel/bin/keel.py seal --change <id> --commit HEAD
```

`seal` independently recomputes the verification digest from the committed Git tree, requires the candidate commit's material diff to equal `verification.json.changed_paths`, and creates collision-checked `refs/keel/candidates/<id>`. It does not modify the candidate commit after sealing.

Seal also creates a formal, canonical `CandidateAttestation` Git blob, indexed by
`refs/keel/attestations/candidates/<id>`. It binds the change/base identity, candidate
commit and tree, independent material and intent digests, combined content digest,
EvidencePlan digest, supporting EvidenceReceipt identities/digests, and the available
policy/runtime-profile digest. The candidate ref remains commit-compatible; neither ref
is an immutability guarantee or the sole attestation payload.

An integration checkout with no active change may merge only a simple sealed-candidate ref (`git merge ... refs/keel/candidates/<id>`) through the KEEL hook path. This makes the handoff exact without forcing one global merge strategy; normal repository review/branch rules still decide whether merge, squash, rebase, PR, or another authorized integration mechanism is used.

After landing, run `keel.py anchor --change <id> --commit <landed-sha>`. Anchoring requires the sealed candidate, re-reads the landed ledger, and independently recomputes the candidate's verified material+intent digest from the **landed Git tree**. Unrelated commits since the change's base are ignored; any changed candidate path or intent artifact must remain byte-equivalent. This supports ordinary merge ancestry and content-equivalent squash/rebase landing while detecting post-verification drift. Only then does KEEL create `refs/keel/ledger/<id>` plus the `refs/notes/keel` note.

This remains the existing anchor operation, not the future Landing Transaction.

Candidate/landed refs and notes are versioned Git anchors, not immutable security policy; protect remote history separately when required.

## Parallel work
One change-id = one worktree = one primary writer. Separate changes may run in separate worktrees. Do not use subagent concurrency for write-heavy edits in the same tree. Runtime-detected batch-agent facilities may be used for bounded read-heavy fan-out or worktree-isolated rows only.

## Context discipline
The main thread keeps requirements, decisions, gate state, and final evidence. Exploration/log/test detail belongs in bounded subagent/tool artifacts. KEEL session/prompt hooks inject a short active-ledger summary when trusted. Memories remain supplementary.

## Integration authorization
Local investigation/edits/commits are generally reversible. Remote pushes, PR transitions/merges, releases, deployments, migrations, issue changes, cloud/hardware operations, and other external effects follow explicit user/domain authorization and the active risk contract.

## Adaptive intelligence and evaluation

- Run `keel.py discover` after meaningful project structure appears; treat results as advisory evidence only.
- Run `keel.py context` to compile minimal current-change context before consequential decisions.
- Standard changes require requirement/acceptance contracts; `keel verify` must satisfy required evidence edges.
- Use KEELBench for repeated baseline-vs-KEEL evaluation; deterministic mechanism tests never substitute for empirical uplift.
