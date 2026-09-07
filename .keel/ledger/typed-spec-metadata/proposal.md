# Proposal

## Problem / why

Requirements and acceptance criteria are linked, but their behavioral kind, priority, and implementation surface are not schema-checked.

## Objective

Add optional typed metadata and implementation-surface paths while preserving existing contracts.

## Non-goals

No inference of implementation paths, automatic requirement generation, or replacement of delta prose.

## Success evidence

Evidence-graph tests prove valid metadata, invalid enum/path rejection, and unchanged legacy contracts.

## Open decisions

Metadata remains optional until a future versioned contract makes a field mandatory.
