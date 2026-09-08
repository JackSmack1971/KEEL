# Proposal

## Problem / why
KEEL's flat verification command list and acceptance/evidence graph conflate command success with authority. They run every historical check, permit duplicate and SHA-pinned checks, and do not emit exact-subject receipts that constrain what a verifier can establish.

## Objective
Implement the M4 evidence-adapter portion of `KEEL-KERNEL-REDESIGN-v1`: a provenance-bearing verifier registry, authority-bearing evidence requirements, deterministic impact-aware minimal planning, immutable-content evidence receipts, and receipt-based requirement satisfaction as the primary verification authority.

## Non-goals
- Redesign candidate sealing or landed anchoring beyond consuming the new receipt-authoritative verification projection.
- Retire legacy compatibility views or historical ledgers.
- Add unevidenced remote/runtime providers.
- Change authorization, effect, or integration permission semantics.

## Success evidence
- Hostile fixtures reject unrelated passing checks, insufficient authority, subject drift, duplicate registrations, and unavailable verifiers.
- Planner fixtures prove deterministic minimal impact/requirement selection and a small mandatory kernel.
- Verification emits a plan and receipts and derives status from receipt coverage.
- Existing lifecycle tests pass; active config has no duplicates or historical SHA pins.

## Open decisions
None; authority and compatibility follow the user request and kernel redesign authority.
