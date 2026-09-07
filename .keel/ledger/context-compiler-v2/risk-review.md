# Risk review

This changes the control-plane context selection boundary. The principal risk is that derived graph/query data could suppress mandatory context or create false authority. The v2 selector must retain configured always-loaded documents, preserve ledger/requirements/evidence obligations, report unavailable/conflicting intelligence, and remain read-only. Role profiles may widen context but cannot weaken policy.

No external effects are declared. Verification must cover deterministic selection, provenance, uncertainty, and backward compatibility with the v1 compiler.
