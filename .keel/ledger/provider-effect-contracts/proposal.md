# Proposal

## Problem / why
KEEL documents multimodal evidence providers and effect capabilities, but validation currently rejects provider types beyond three built-ins and does not validate declared effect capability names.

## Objective
Make the provider/effect contract executable: accept the declared provider vocabulary only through configured check evidence, validate effect capabilities against repository-owned contracts, and preserve existing authorization gates.

## Non-goals
Implementing browser, telemetry, hardware, cloud, or tracker adapters; inferring capabilities from shell commands; granting authorization; or weakening command/effect safety boundaries.

## Success evidence
Focused tests prove provider validation/evaluation and effect capability validation, including unknown and unauthorized cases. Existing full verification remains passing.

## Open decisions
Provider adapters remain project-specific configured checks until a separate runtime provider contract is implemented.
