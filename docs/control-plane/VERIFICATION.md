# Verification Model

A change is not complete because an edit or command succeeded.

## Evidence loop
`goal -> action -> observation -> independent verification -> completion`

## KEEL write-change rule
`python3 .keel/bin/keel.py verify` is the deterministic gate for an active write change. It:
1. validates proposal/delta/scope/risk/effects/authorization state;
2. compares all Git-changed/untracked paths since the recorded base commit against `scope.txt`;
3. runs built-in structural checks and `git diff --check`;
4. runs configured canonical project commands from `.keel/config.json` without shell interpolation;
5. records literal exit codes, durations, redacted bounded excerpts, and a digest covering scoped changed content plus stable intent files;
6. reaches `SHIP` only if required checks pass and the evidence graph grants the change's required authority class.

Substantive source changes cannot pass with no configured project verification commands. Populate commands once the toolchain exists; never guess them.

## Selection rule
Use the narrowest high-signal checks first, then broaden proportional to coupling/blast radius. Add independent review for consequential changes. Runtime/UI/infra/hardware claims need direct evidence when available.

## Pre-existing failures
Capture a baseline before implementation. A pre-existing failure may be documented and isolated, but a newly introduced or unexplained failure blocks completion.

## Completion blockers
Missing evidence, missing required authorization, out-of-scope diffs, changed code or intent after verification, inconclusive checks, architecture/source-of-truth conflicts, unreviewed high-risk change, or unauthorized external effects block a success claim.

## Acceptance/evidence graph

A standard KEEL change must define `requirements.json` and `acceptance.json`. Verification evaluates each required AC through deterministic evidence providers and writes `evidence-graph.json`. A green command suite is insufficient when required acceptance edges remain unsatisfied. Because requirements/acceptance are included in the intent digest, changing them after verification invalidates the candidate. See [ACCEPTANCE_EVIDENCE.md](ACCEPTANCE_EVIDENCE.md).

### Evidence classes

Contracts use `PLAN_READINESS`, `IMPLEMENTATION_ACCEPTANCE`, and `LANDED_COMPLETION`. An implementation change defaults to `change_type: implementation`; a planning-only change must explicitly declare `change_type: planning_only`. Legacy criteria with only non-behavioral providers such as `changed_path`, `file_exists`, or control-plane `command` checks are recorded as `PLAN_READINESS`. Implementation criteria must name changed implementation paths and include a behavioral provider such as `unit_test`, `schema`, `runtime`, or an equivalent direct behavior provider. Readiness PASS is preserved in the evidence graph, but it cannot set implementation verification PASS, `SHIP`, seal eligibility, or completion authority. Landed anchoring is the `LANDED_COMPLETION` boundary.
