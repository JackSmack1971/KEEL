# KEEL lifecycle compatibility

Compatibility inspection is evidence-backed inventory, not an installer. It reports repository-owned framework/config/contract/ledger/skill/manifest versions and produces explicit migration findings. It does not query or infer external Codex versions, download code, rewrite schemas, or mutate ledgers.

`keel migrate --check` is intentionally a planning command. Each actual migration must have a versioned implementation, backup/rollback evidence where relevant, and its own KEEL change contract.
