# Capability Resolution

KEEL discovery turns repository facts into **advisory evidence**, not silent policy changes.

Run:

```text
python3 .keel/bin/keel.py discover
```

The resolver writes `.keel/knowledge/capabilities.json` (ignored generated state) with schema version `2`, rules version `1`, and `DETECTED`, `LIKELY`, or `UNKNOWN` evidence. Each capability retains compatible path evidence plus bounded `evidence_details` records containing the matched path, rule pattern, and evidence kind. The control-plane capability registry remains authoritative; discovery suggests what deserves review/activation.

Resolution precedence for classifying substantive files is:

1. explicit project `source_classification` globs in `.keel/config.json`;
2. evidence-backed ecosystem/source patterns;
3. obvious non-source documentation patterns;
4. `UNKNOWN`, treated conservatively by verification rather than assumed harmless.

This prevents KEEL from pretending its built-in extension list defines every language, DSL, build system, shader, notebook, infrastructure format, or future engineering artifact.

The output also includes `source_classification.counts` and a bounded `unknown_paths` list. Explicit source/non-source disagreements are emitted as `CONFLICT` records with the path and competing globs; the conflict is visible even though classification precedence remains deterministic. Evidence is bounded by `capability_resolver.max_evidence_per_capability` and paths are sorted before matching, so repeated discovery is reproducible.

## Safety rules

- Discovery never edits `CAPABILITY_REGISTRY.md` automatically.
- File and rule evidence is retained so an agent/human can inspect why a capability was suggested.
- Conflicting explicit classifiers are surfaced rather than resolved by precedence.
- A project may extend explicit source/non-source globs without modifying KEEL code.
