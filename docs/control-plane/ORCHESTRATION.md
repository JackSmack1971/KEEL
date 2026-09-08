# Orchestration boundary

KEEL is not an agent, model, ticket, or deployment scheduler. The canonical
`ChangeGraph` supplies typed work dependencies, constraints, effects, and a pure
frontier projection. Runtime orchestration may consume those facts but cannot replace
canonical intent, lifecycle gates, CapabilityGrants, evidence receipts, worktree
isolation, or external authorization.

Generic explorer, reviewer, and risk-reviewer roles remain available for bounded
read-only work selected from unresolved facts and risk. There is no mission runtime or
topology router in the product.
