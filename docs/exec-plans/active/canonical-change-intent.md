# Canonical change-intent migration

Authority: `KEEL-KERNEL-REDESIGN-v1`
Stages: M2 read compatibility, M3 canonical kernel, M4 evidence/runtime adapters limited to ledger consumers.

## Purpose
Replace independently editable per-change authorities with one canonical intent aggregate and causal/script-owned operational records while retaining deterministic legacy audit compatibility.

## Affected primitives and state
Requirements, WorkUnits/Edges references, EffectRequests, EvidenceRequirements, CapabilityGrants, EvidenceReceipts, Decisions/events, Candidate/Landed Attestations; validity, knowledge, support, readiness, and lifecycle remain orthogonal.

## Inventory and sequence
1. Characterize all legacy shapes and every reader/writer with fixtures.
2. Add schema/version validation and a read-only semantic loader for canonical and legacy data.
3. Add deterministic migration with source/target digests, preserved unknown fields, explicit ABSENT uncertainty, atomic output, and no invented grants or receipts.
4. Switch default start/transitions and canonical consumers, retaining legacy historical readers and templates.
5. Project human-readable/generated compatibility views from canonical semantics and mechanically reject manual authority.
6. Update docs, regenerate declared provenance artifacts, and run focused/full/hostile tests.
7. Independently review authority duplication, authorization inflation, tamper behavior, historical audit, and exact-subject Git proof.

## Recovery
Legacy inputs are append-preserved and the reader remains versioned. Remove incomplete staged migration output, correct the implementation, and deterministically regenerate. Default migration never deletes source files.

## Non-goals
No M5 landing transaction, scheduler, provider effect executor, remote integration, legacy template deletion, or assertion that hash chaining/Git refs are immutable.
