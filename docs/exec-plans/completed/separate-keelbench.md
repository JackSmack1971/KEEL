# Separate KEELBench

Status: `COMPLETE / LANDED IN CURRENT TREE — HISTORICAL LEDGER RETAINED`
Forward authority: [`KEEL_FORWARD_AUTHORITY.md`](../../control-plane/KEEL_FORWARD_AUTHORITY.md)

## Objective

Move KEELBench out of the mandatory `.keel` runtime into an optional,
dependency-free first-party package for empirical evaluation. Keep empirical
claims explicitly unvalidated until representative repeated paired trials exist.

## Scope

- Create `keelbench/` with the harness, contract, corpus, focused tests, and
  package documentation.
- Remove KEELBench files from the bootstrap manifest and core runtime discovery.
- Expand the telemetry contract to cover the requested outcome dimensions while
  retaining paired baseline/KEEL identity and fail-closed validation.
- Update control-plane documentation and capability evidence.

## Non-goals

No synthetic benchmark results, competitor claims, authority approval, corpus
promotion, or empirical superiority conclusion. No change to KEEL lifecycle
authorization or deterministic mechanism tests.

## Risks and controls

The primary risk is authority confusion: optional evaluation artifacts must not
look like runtime requirements, and valid-looking incomplete trials must not
produce comparison evidence. Controls are a generated-manifest check, core
portability tests, package tests, explicit `BLOCKED`/`UNVALIDATED` result state,
and independent review.

## Verification

Run the core configured verification, the optional package tests and validator,
then inspect the manifest and diff. Empirical superiority remains blocked unless
real representative repeated trials and an approved rubric/corpus are supplied.
