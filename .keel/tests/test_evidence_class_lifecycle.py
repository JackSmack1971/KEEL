from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _contracts(root: Path, *, change_type: str = "implementation", criterion: dict | None = None) -> tuple[Path, Path]:
    requirements = root / "requirements.json"
    acceptance = root / "acceptance.json"
    requirements.write_text(json.dumps({
        "schema_version": 1,
        "change_type": change_type,
        "requirements": [{"id": "REQ-001", "statement": "The behavior is explicit."}],
    }), encoding="utf-8")
    acceptance.write_text(json.dumps({"schema_version": 1, "criteria": [criterion or {
        "id": "AC-001", "requirement_id": "REQ-001", "statement": "The behavior has evidence.",
        "required": True, "policy": "all", "evidence": [{"provider": "changed_path", "path": "docs/**"}],
    }]}), encoding="utf-8")
    return requirements, acceptance


def main() -> None:
    graph = _load("evidence_graph_under_test", ROOT / ".keel/lib/evidence_graph.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contracts, acceptance = _contracts(root)
        readiness = graph.evaluate(root, contracts, acceptance, [], ["docs/plan.md"])
        assert readiness["status"] == "PASS"
        assert readiness["verification_class"] == "PLAN_READINESS"
        assert readiness["implementation_status"] == "NOT_VERIFIED"
        assert readiness["criteria"][0]["evidence_class"] == "PLAN_READINESS"

        behavioral = {
            "id": "AC-001", "requirement_id": "REQ-001", "statement": "The behavior has a passing test.",
            "evidence_class": "IMPLEMENTATION_ACCEPTANCE", "evidence_type": "automated-test",
            "implementation_paths": ["src/**"], "required": True, "policy": "all",
            "evidence": [{"provider": "unit_test", "check_id": "behavior-test", "fixture": "fixture-1", "expected": "exit 0"}],
        }
        contracts, acceptance = _contracts(root, criterion=behavioral)
        implemented = graph.evaluate(root, contracts, acceptance, [{"id": "behavior-test", "exit_code": 0}], ["src/main.py"])
        assert implemented["status"] == "PASS"
        assert implemented["verification_class"] == "IMPLEMENTATION_ACCEPTANCE"
        assert implemented["implementation_status"] == "PASS"
        assert implemented["criteria"][0]["evidence"][0]["fixture"] == "fixture-1"

        planning_only = {
            "id": "AC-001", "requirement_id": "REQ-001", "statement": "The plan has evidence.",
            "evidence_class": "PLAN_READINESS", "evidence_type": "changed-path", "required": True,
            "policy": "all", "implementation_paths": ["docs/**"],
            "evidence": [{"provider": "changed_path", "path": "docs/**"}],
        }
        contracts, acceptance = _contracts(root, change_type="planning_only", criterion=planning_only)
        plan_change = graph.evaluate(root, contracts, acceptance, [], ["docs/plan.md"])
        assert plan_change["status"] == "PASS"
        assert plan_change["implementation_status"] == "NOT_APPLICABLE"

        invalid = dict(behavioral, evidence=[{"provider": "changed_path", "path": "docs/**"}])
        contracts, acceptance = _contracts(root, criterion=invalid)
        assert any("behavioral evidence provider" in error for error in graph.validate_contract(contracts, acceptance))

        contracts, acceptance = _contracts(root, criterion=behavioral)
        failed = graph.evaluate(root, contracts, acceptance, [{"id": "behavior-test", "exit_code": 1}], ["src/main.py"])
        assert failed["status"] == "FAIL"
        assert failed["implementation_status"] == "FAIL"

    sys.path.insert(0, str(ROOT / ".keel/lib"))
    core = _load("keel_core_under_test", ROOT / ".keel/lib/keel_core.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        ledger = root / ".keel/ledger/change-1"
        ledger.mkdir(parents=True)
        (ledger / "state.json").write_text(json.dumps({"change_id": "change-1", "phase": "SHIP", "mode": "standard", "base_commit": "abc"}), encoding="utf-8")
        (ledger / "verification.json").write_text(json.dumps({"status": "PASS", "change_type": "implementation", "implementation_status": "NOT_VERIFIED"}), encoding="utf-8")
        (root / ".keel/active-change").write_text("change-1\n", encoding="utf-8")
        with patch.object(core, "content_digest", return_value="digest"):
            explicit = core.next_action(root, "change-1")
            implicit = core.next_action(root)
            assert explicit["recommended_action"]["id"] == "implement"
            assert implicit["recommended_action"] == explicit["recommended_action"]

    print("Evidence-class lifecycle tests PASS")


if __name__ == "__main__":
    main()
