# Risk review

This is a control-plane schema/planning change. It is confined to authored Python, JSON fixtures, tests, the explicit v2 CLI route, and roadmap/audit text. It has no external, irreversible, runtime, provider, worktree, lock, authorization, generated-artifact, migration, or deployment effect. The primary risks are v1 compatibility drift, accidental readiness/authorization claims, and nondeterministic output; independent fixtures, preserved v1 tests, conservative classifications, byte-repeat checks, and KEEL scope verification mitigate them.

The change remains planning-only and cannot make P4 executable.
