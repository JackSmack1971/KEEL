from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))


def _load_context_compiler():
    path = ROOT / ".keel" / "lib" / "context_compiler.py"
    spec = importlib.util.spec_from_file_location("context_compiler_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    compiler = _load_context_compiler()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "docs").mkdir()
        (root / "docs" / "guide.md").write_text("# Guide\nAuthoritative guidance.\n", encoding="utf-8")
        ledger = root / "ledger"
        ledger.mkdir()
        (ledger / "scope.txt").write_text("src/**\n", encoding="utf-8")
        (ledger / "proposal.md").write_text("# Proposal\n\n## Objective\nCompile safe context.\n", encoding="utf-8")
        (ledger / "delta.md").write_text("## ADDED\n- Provenance.\n", encoding="utf-8")
        (ledger / "risk.json").write_text("{}", encoding="utf-8")
        (ledger / "effects.json").write_text("{}", encoding="utf-8")
        (ledger / "acceptance.json").write_text("{}", encoding="utf-8")
        (root / ".keel" / "knowledge").mkdir(parents=True)
        (root / ".keel" / "knowledge" / "capabilities.json").write_text(
            '{"capabilities": {"testing-evals": {"status": "DETECTED", "evidence": ["injected"]}}',
            encoding="utf-8",
        )
        config = {
            "context_compiler": {
                "always_docs": ["docs/guide.md", "missing.md", "../outside.md"],
                "max_chars": 420,
            }
        }
        state = {"phase": "EXECUTE", "base_commit": "abc", "mode": "standard"}
        first_text, first_meta = compiler.compile_packet(root, "test-change", state, config, ledger)
        second_text, second_meta = compiler.compile_packet(root, "test-change", state, config, ledger)

        assert first_text == second_text
        assert first_meta == second_meta
        assert len(first_text) <= 420
        assert first_meta["schema_version"] == 2
        assert first_meta["discovery"]["source"] == "resolver"
        provenance = first_meta["document_provenance"]
        assert provenance[0]["status"] == "PRESENT"
        assert len(provenance[0]["sha256"]) == 64
        assert provenance[1] == {"path": "missing.md", "status": "MISSING"}
        assert provenance[2] == {"path": "../outside.md", "status": "OUTSIDE_REPOSITORY"}
        assert "injected" not in first_text
        v2_config = {"context_compiler": {**config["context_compiler"], "max_chars": 2000}}
        v2_text, v2_meta = compiler.compile_packet_v2(root, "test-change", state, v2_config, ledger, ["src/auth/policy.py"], role="verifier", query=["testing"])
        selection = v2_meta["selection"]
        assert v2_meta["schema_version"] == 3
        assert selection["role"] == "verifier"
        assert selection["monotonicity"]["mandatory_documents_retained"] is True
        assert any(row["path"] == "docs/guide.md" for row in selection["documents"])
        assert selection["graph"]["status"] == "UNAVAILABLE"
        assert any(row["code"] == "graph-uncertain" for row in selection["warnings"])
        assert "derived navigation evidence only" in v2_text
        print("Context compiler tests PASS")


if __name__ == "__main__":
    main()
