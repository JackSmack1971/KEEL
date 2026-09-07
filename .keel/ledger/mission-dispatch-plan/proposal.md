# Proposal

## Problem / why

Mission planning identifies runnable work but does not express the isolation, roles, and verification contract a future dispatcher would need.

## Objective

Add a deterministic, read-only dispatch plan for runnable mission nodes.

## Non-goals

No agent launch, worktree creation, lifecycle transition, retry, integration, or external runtime selection.

## Success evidence

Focused tests prove dispatch order, dependency and risk metadata, read-only behavior, and blocked missions produce no dispatches.

## Open decisions

Runtime/provider selection remains an operator/runtime concern.
