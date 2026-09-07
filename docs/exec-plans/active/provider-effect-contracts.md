# Provider and effect capability contracts

## Boundary

The contract vocabulary is provider-neutral, but execution is not implicit. A criterion using `browser`, `log_query`, `metric_query`, `trace_query`, `schema`, `security`, `benchmark`, `hardware`, `human_review`, or `external_ci` must name a configured verification `check_id`; the check is the project-specific adapter and its literal exit status is the evidence.

Effects declare capability names from `.keel/contracts.json`. Names describe the requested effect and are included in the effects digest. They never grant permission; external or irreversible effects still require the existing operator authorization record.
