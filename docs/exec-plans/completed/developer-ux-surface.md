# Developer UX surface

Add read-only command projections over existing KEEL evidence. `init --check` validates local readiness, `review` aggregates lifecycle/evidence/candidate state, and `ship` reports verified-and-sealed eligibility. None of these commands mutates state or grants integration permission. `run` remains outside this slice because no authorized execution runtime is present.
