# Observability, Reliability, Performance, Capacity, and Cost

Status: `CONDITIONAL` until a measurable runtime exists.

When active, make the system itself legible to agents:
- structured logs with stable fields;
- metrics tied to objective budgets;
- traces for cross-component behavior when useful;
- reproducible local diagnostics, preferably isolated per worktree;
- explicit SLO/latency/throughput/resource/cost budgets where consequential;
- failure injection/recovery evidence proportional to risk.

Do not install a universal observability vendor in an empty repository. Choose the lightest mechanism that makes the actual system directly inspectable.
