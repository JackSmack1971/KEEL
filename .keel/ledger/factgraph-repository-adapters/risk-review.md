# Risk review

## Classification

High-risk control-plane migration at `KEEL-KERNEL-REDESIGN-v1` stages M2/M3. It
changes the repository-understanding authority used by discovery, context, and impact
projections, while retaining compatibility readers and output shapes.

## Principal risks and controls

- **Semantic regression:** legacy outputs could drift. Existing P1/map/resolver/context
  suites remain mandatory and gain equivalence assertions against the graph projection.
- **Optimistic activation:** adapter heuristics could be mistaken for policy or command
  authority. Facts encode candidate versus declaration and negative knowledge/support;
  discovery remains read-only and no adapter executes commands.
- **Evidence loss:** precedence could hide contradictions. All observations remain in the
  graph, conflicts are explicit derived facts, and precedence affects projections only.
- **Non-determinism/staleness:** filesystem/Git ordering or mutable inputs could vary.
  Portable normalized paths, stable sorting/identities, content digests, and freshness
  comparison receive hostile fixtures.
- **Premature later-stage work:** no reconciler, EvidencePlanner, authorization, runtime,
  evidence, seal, or anchor redesign is in scope.

## Recovery

The change is locally reversible as a single Git commit. Compatibility schemas remain
readable; no data migration or external state mutation occurs. Revert restores the
previous collectors without converting persisted user data.
