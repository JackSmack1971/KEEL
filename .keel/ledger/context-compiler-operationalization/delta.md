## ADDED
- Focused deterministic tests for context compilation and provenance metadata.
- SHA-256 provenance metadata for referenced documents in compiled context packets.

## MODIFIED
- Context packets remain derived and bounded while exposing their schema, selected documents, and evidence provenance.
- Malformed or unavailable discovery data falls back to resolver-derived evidence without failing compilation.

## REMOVED
