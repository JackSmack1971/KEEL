# Risk review

This M2/M3 planning migration changes the authoritative interpretation of work
and dependencies while retaining legacy reads. Primary risks are semantic loss
during adaptation, accidental invention of authorization/runtime certainty,
multiple dependency authorities, nondeterministic canonical bytes, and CLI
compatibility regression. Mitigations are a single dependency-free graph API,
strict tagged records, edge-only dependencies, provenance-linked uncertainty,
golden compatibility tests, hostile graph tests, stable public CLI tests, and
the full repository verification suite. Resource conflicts are deliberately a
readiness concern rather than structural invalidity. No scheduling, dispatch,
effect execution, external effect, or irreversible operation is requested.
