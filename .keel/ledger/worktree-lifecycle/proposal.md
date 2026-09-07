# Proposal

## Problem / why

KEEL documents one-change/one-worktree isolation, but it does not provide a repository-native lifecycle command for creating, inspecting, and safely retiring those worktrees. Agents must currently compose raw Git commands and can accidentally reuse or remove the wrong workspace.

## Objective

Add `keel worktree create`, `status`, and `retire` commands backed by Git's worktree metadata, with exact path validation, dirty-worktree refusal, and explicit force required for destructive retirement.

## Non-goals

- No environment/service/port/database isolation automation.
- No mission scheduler, dependency graph, or external tracker integration.
- No automatic branch policy or remote push.

## Success evidence

- Focused tests create, inspect, and retire a temporary Git worktree and prove dirty retirement is refused unless explicitly forced.
- Commands return structured, deterministic metadata and do not alter the primary worktree.
- Existing control-plane checks and KEELBench validation pass.

## Open decisions

None; worktree paths are explicit to keep creation and retirement targets inspectable and avoid hidden destructive defaults.
