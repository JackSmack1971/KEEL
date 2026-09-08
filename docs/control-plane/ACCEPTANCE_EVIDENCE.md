# Requirements and receipt evidence

A standard change records normative `REQ-*` entries in `requirements.json` and acceptance mappings in `acceptance.json`. Each required property declares `minimum_evidence_authority`; acceptance identifies permitted verifier/provider evidence. Both files are portable intent and changing either invalidates prior receipts.

Verification derives one `EvidenceRequirement` per requirement and an impact-selected `EvidencePlan`. Registry Verifiers can be selected only when their declared provider, requirement type, authority, path/risk applicability, and runtime contract are sufficient. Every selected execution emits an exact-subject `EvidenceReceipt`; receipt coverage is the primary authority.

A literal command exit zero is only an observation. It establishes a requirement only when the receipt is intact, matches the exact subject and intent, has sufficient declared authority, and names the planned EvidenceRequirement. An unrelated green check cannot grant completion.

During migration, `evidence-graph.json` is a deterministic compatibility projection over receipt coverage. Historical graph records remain readable; new graph projections do not carry independent evidence-edge truth. See [VERIFICATION.md](VERIFICATION.md).
