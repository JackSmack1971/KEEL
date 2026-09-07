# Effect inference

## Objective

Add conservative, read-only inference of effect capabilities from configured argv commands.

## Scope

- Match explicit token patterns to existing `.keel/contracts.json` capabilities.
- Report inferred capabilities, unknown commands, and undeclared-capability mismatches.
- Keep inference advisory and separate from authorization or command execution.
- Add focused tests, CLI documentation, audit evidence, and manifest hashes.

## Non-goals

Shell interpretation, dynamic tool/API analysis, authorization grants, and claims about commands that are not explicitly recognized.

## Verification

Focused effect-inference tests, strict control-plane validation, and full configured KEEL verification.
