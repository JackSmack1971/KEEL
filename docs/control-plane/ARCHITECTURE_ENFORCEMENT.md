# Architecture Enforcement

Status: `CONDITIONAL until architecture exists`.

When durable boundaries emerge, prefer mechanical checks over repeated prose. Candidate invariant classes:
- dependency/layer direction and forbidden imports;
- parse/validate once at trust boundaries;
- generated-source ownership;
- API/schema compatibility;
- structured logging/telemetry shape;
- naming/layout rules with real correctness or legibility value;
- limits that prevent known pathological architecture.

Each lint/test error should say what is wrong and how to remediate it. Do not mechanize personal taste without recurrence/evidence.
