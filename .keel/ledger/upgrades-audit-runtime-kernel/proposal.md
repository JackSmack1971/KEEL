# Proposal

## Problem / why
The upgrade brief identifies missing runtime/productization capabilities, but current repository state must be distinguished from aspirational documentation before implementation.

## Objective
Record an evidence-backed audit and add a small, read-only kernel slice that exposes reconciliation, provider-neutral evidence/effect declarations, layered source classification, and compatibility/version inspection without weakening existing gates.

## Non-goals
Mission scheduling, external tracker integrations, autonomous effect execution, and automatic policy activation are deferred.

## Success evidence
The audit maps upgrade items to repository evidence; focused tests cover every new primitive; doctor, strict control-plane validation, and configured checks pass.

## Open decisions
Provider execution remains adapter-owned; this change defines contracts and safe inspection only.
