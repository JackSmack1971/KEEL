# Schema migration engine

Implement a versioned migration registry for repository-owned JSON artifacts. The first supported transition is config schema 1 to 2: preserve existing keys, add the verification-command collection when absent, and update the schema marker.

Preflight is read-only. Apply requires an explicit artifact and backup directory, writes atomically, and records a digest. Rollback restores the backup byte-for-byte. The CLI continues to inspect live compatibility rather than mutating the active repository implicitly.

Verification: focused migration tests, strict control-plane validation, and full KEEL verification.
