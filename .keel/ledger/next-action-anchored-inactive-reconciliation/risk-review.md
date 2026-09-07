# Risk review

This is a localized control-plane behavior repair in next-action computation. The change does not mutate ledger state or anchor evidence; it adds a read-only validation path and focused tests. Existing anchor checks remain authoritative. Risk is limited to lifecycle guidance, with regression coverage for valid, missing, and inconsistent evidence.
