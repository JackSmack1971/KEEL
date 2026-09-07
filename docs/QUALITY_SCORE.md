# Quality Score

Quality is tracked by domain rather than by vague repository sentiment.

Initial state: no implementation exists, so product/code grades are `UNASSESSED`.

When code arrives, score at least:
- architecture/boundary integrity;
- test/eval evidence;
- static quality/type/lint health;
- security/supply-chain posture;
- reliability/operability;
- documentation freshness;
- generated-artifact provenance;
- developer/agent legibility;
- domain-specific quality signals.

Record evidence and trend. Do not convert missing evidence into a passing grade.
