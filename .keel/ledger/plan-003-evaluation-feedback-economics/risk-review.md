# Risk review

This changes control-plane evaluation and promotion boundaries. The implementation remains repository-local and read-only with respect to policy: scoring consumes complete paired records, unavailable runtime metrics remain explicitly unavailable, and feedback promotion emits a handoff contract rather than mutating configuration or authorization. Negative tests must reject incomplete pairs, adversarial critical violations, and BENCHMARKED claims without reproducible evidence. No external effects are declared.
