# Proposal

## Problem / why

KEEL documents environment isolation needs but has no machine-readable contract surface. Agents cannot distinguish an explicitly configured runtime contract from an unknown or intentionally unconfigured environment without inspecting prose.

## Objective

Add an optional schema-validated environment contract to `.keel/config.json` and a read-only `keel environment status` command. The command must report configured commands and isolation requirements without executing them or inventing defaults.

## Non-goals

- No service startup, shutdown, port allocation, database provisioning, or container orchestration.
- No stack detection or automatic contract generation.
- No external effects or environment mutation.

## Success evidence

- Focused tests prove unconfigured, configured, and invalid contracts are reported deterministically.
- The CLI is read-only and does not execute contract commands.
- Existing control-plane checks and KEELBench validation pass.

## Open decisions

None; command fields are optional argv arrays and isolation values are declarative strings only.
