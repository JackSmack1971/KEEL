# Risk review

This change modifies the control-plane intelligence and evidence boundary. The primary risk is false authority: a derived fact, inferred effect, or implementation-controlled proof could weaken mandatory requirements or authorize an effect. The implementation must therefore keep all analyzers read-only, preserve explicit `UNAVAILABLE` and `CONFLICT` states, and make uncertainty widen warnings/verification rather than suppressing checks.

Containment:

- No external or irreversible effects are declared.
- New providers and source formats are explicit contracts; unsupported inputs remain unknown.
- Existing authorization, scope, and required-check paths remain policy-owned.
- Negative tests must demonstrate that advisory output cannot grant permission and that proof-surface changes trigger independent verification.

Review focus: monotonicity, oracle independence, semantic classification completeness, stale/conflicting provenance, and compatibility with existing evidence evaluation.
