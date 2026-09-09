from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
required = {
    "AGENTS.md": ["CONTROL_PLANE.md", "WORKFLOW.md", "ARCHITECTURE.md"],
    "ARCHITECTURE.md": ["KEEL", "canonical", "stack-neutral"],
    "docs/control-plane/COMMANDS.md": ["explain [subject]", "audit [subject]", "custom-ref"],
    "docs/control-plane/VERIFICATION.md": ["SEALED", "LANDED"],
    "docs/control-plane/CODEX_NATIVE.md": ["adapter"],
    "docs/control-plane/ORCHESTRATION.md": ["stack-neutral"],
}
for name, terms in required.items():
    text = (ROOT / name).read_text(encoding="utf-8").lower()
    for term in terms:
        assert term.lower() in text, (name, term)
print("Documentation contract tests PASS")
