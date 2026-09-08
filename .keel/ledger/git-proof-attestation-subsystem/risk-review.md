# Risk review

## Protected assets and trust boundaries
The protected assets are exact candidate/landed Git identity, verified intent and
material bytes, receipt evidence, collision-free local refs/notes, and isolation of a
change to its recorded worktree and baseline. Git metadata remains mutable absent
external protection and is not upgraded to an immutability claim.

## Principal failure modes
- Extraction changes path, diff, digest, ancestry, collision, or squash/rebase behavior.
- An attestation omits or ambiguously identifies evidence/policy inputs.
- Compatibility callers silently consume a weaker proof.
- A post-verification working-tree or committed-tree mutation is accepted.

## Controls and rollback
Existing behavior is treated as an oracle and retained behind compatibility wrappers.
New modules are dependency-free and deterministic. Focused temporary-repository tests
cover negative paths and content-equivalent landing independently from the lifecycle
suite. The change is reversible by reverting one commit; it performs no remote or
irreversible effect. Integration remains outside this implementation.

## Independent review requirement
A separate review must inspect dependency direction, proof completeness, fail-closed
behavior, collision handling, and exact preservation of ref/note semantics before seal.
