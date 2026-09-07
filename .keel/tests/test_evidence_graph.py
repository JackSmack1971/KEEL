from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_graph():
    path = ROOT / ".keel" / "lib" / "evidence_graph.py"
    spec = importlib.util.spec_from_file_location("evidence_graph_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_contract(directory: Path, criteria: list[dict]) -> tuple[Path, Path]:
    requirements = directory / "requirements.json"
    acceptance = directory / "acceptance.json"
    requirements.write_text(json.dumps({
        "schema_version": 1,
        "requirements": [
            {"id": "REQ-001", "statement": "First behavior is explicit.", "source": "test"},
            {"id": "REQ-002", "statement": "Second behavior is explicit.", "source": "test"},
        ],
    }), encoding="utf-8")
    acceptance.write_text(json.dumps({"schema_version": 1, "criteria": criteria}), encoding="utf-8")
    return requirements, acceptance


def main() -> None:
    graph = _load_graph()
    assert graph.classify_semantic_paths(["src/auth/policy.py"])[0]["consequence"] == "HIGH"
    oracle = graph.oracle_integrity([".keel/tests/test_evidence_graph.py"], [".github/workflows/verify.yml"])
    assert oracle["status"] == "CLEAR"
    passed, _ = graph._assertion({"exit_code": 0, "excerpt": "PASS metric=9"}, {"type": "output_contains", "value": "PASS"})
    assert passed
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        orphan_requirements, orphan_acceptance = _write_contract(root, [{
            "id": "AC-001",
            "requirement_id": "REQ-001",
            "statement": "First behavior has evidence.",
            "required": True,
            "policy": "all",
            "evidence": [{"provider": "changed_path", "path": "src/**"}],
        }])
        errors = graph.validate_contract(orphan_requirements, orphan_acceptance)
        assert errors == ["requirement REQ-002 has no acceptance criterion"]

        requirements, acceptance = _write_contract(root, [
            {
                "id": "AC-001",
                "requirement_id": "REQ-001",
                "statement": "First behavior has evidence.",
                "required": True,
                "policy": "all",
                "evidence": [{"provider": "changed_path", "path": "src/**"}],
            },
            {
                "id": "AC-002",
                "requirement_id": "REQ-002",
                "statement": "Second behavior has evidence.",
                "required": True,
                "policy": "all",
                "evidence": [{"provider": "file_exists", "path": "evidence.txt"}],
            },
        ])
        (root / "evidence.txt").write_text("verified\n", encoding="utf-8")
        result = graph.evaluate(root, requirements, acceptance, [], ["src/main.py"])
        assert result["status"] == "PASS"
        assert result["summary"]["requirements_total"] == 2
        assert result["summary"]["requirements_covered"] == 2
        assert result["summary"]["requirements_passing"] == 2
        assert result["requirement_coverage"] == [
            {"requirement_id": "REQ-001", "type": "behavior", "priority": "must", "implementation_paths": [], "criterion_ids": ["AC-001"], "criterion_count": 1, "passed": True},
            {"requirement_id": "REQ-002", "type": "behavior", "priority": "must", "implementation_paths": [], "criterion_ids": ["AC-002"], "criterion_count": 1, "passed": True},
        ]
        typed = json.loads(requirements.read_text(encoding="utf-8")); typed["requirements"][0].update({"type": "security", "priority": "must", "implementation_paths": ["src/auth/**"]})
        acceptance_data = json.loads(acceptance.read_text(encoding="utf-8")); acceptance_data["criteria"][0].update({"evidence_type": "automated-test", "implementation_paths": ["src/auth/**"]})
        requirements.write_text(json.dumps(typed), encoding="utf-8"); acceptance.write_text(json.dumps(acceptance_data), encoding="utf-8")
        assert graph.validate_contract(requirements, acceptance) == []
        assert graph.evaluate(root, requirements, acceptance, [], ["src/auth/tokens.py"])["status"] == "PASS"
        assert graph.evaluate(root, requirements, acceptance, [], ["docs/README.md"])["status"] == "FAIL"
        typed["requirements"][0]["implementation_paths"] = ["../outside"]
        requirements.write_text(json.dumps(typed), encoding="utf-8")
        assert any("contains unsafe path" in error for error in graph.validate_contract(requirements, acceptance))
        print("Evidence graph tests PASS")


if __name__ == "__main__":
    main()
