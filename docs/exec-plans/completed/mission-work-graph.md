# Mission work graph

## Objective

Provide objective-level dependency planning while keeping each leaf as a normal KEEL change.

## Contract

Mission JSON is explicit, versioned, and read-only to the planner. A mission contains an id, objective, success criteria, and a `work` object keyed by change id. Each work item has `risk` (`trivial`, `standard`, or `high`) and optional `depends_on` IDs. A child ledger phase is observed by `keel mission status`; it is never changed by the mission planner.

## Safety

Validation is required before frontier computation. Cycles, missing dependencies, duplicate dependencies, invalid IDs, and unsupported risk values fail closed. The planner does not dispatch agents, run mission-provided commands, create worktrees, authorize effects, or merge changes.

## Verification

Focused mission tests, the existing KEEL verification graph, strict control-plane validation, and KEELBench are required.
