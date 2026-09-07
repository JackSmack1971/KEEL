# Proposal

## Problem / why

The anchored P0 implementation has four independently observed completion defects: missing manifest inputs can be treated as valid, present-but-unproven discovered commands are misclassified, repository-wide diff hygiene fails on P0 ledger artifacts, and the completed P0 ExecPlan remains in the active plan directory.

## Objective

Remediate those four defects under a child KEEL change linked to `p0-portable-verification-bootstrap-contract`, then produce fresh focused, lifecycle, generated-artifact, hygiene, and committed-tree evidence without instantiating P1.

## Non-goals

No P1–P7 implementation, D1 benchmark/evaluation work, P4 runtime/provider authorization, installer/distribution orchestration, migration behavior changes, or rewriting of the original P0 anchor.

## Success evidence

The manifest producer rejects missing and changed listed inputs and detects unrelated drift; command resolution distinguishes absent from present-but-unproven candidates; newly generated lifecycle artifacts pass unsuppressed repository-wide `git diff --check`; the completed P0 ExecPlan is archived with history preserved; focused and regression checks pass; the remediation is committed, sealed, and anchored with independently matching landed-tree evidence.

## Open decisions

The original P0 change is already anchored, so this child remediation change is required to preserve the original ref/note and provide a new collision-free sealed candidate.
