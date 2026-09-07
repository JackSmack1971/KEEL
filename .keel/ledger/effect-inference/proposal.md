# Proposal

## Problem / why

Declared effect capabilities are validated, but configured argv commands are not analyzed for recognizable effect-bearing operations.

## Objective

Add a read-only, conservative argv analyzer and a `keel effects` projection that reports inferred capabilities separately from authorization.

## Non-goals

No command execution, authorization grant, provider-specific API calls, shell parsing, or inference for unknown commands.

## Success evidence

Focused tests prove deterministic inference, unknown-command neutrality, mismatch reporting, and read-only behavior; full KEEL verification passes.

## Open decisions

Inference is token-based and conservative; ambiguous commands produce no capability rather than a risky guess.
