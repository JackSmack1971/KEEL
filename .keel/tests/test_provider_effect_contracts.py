import importlib.util
import json
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(module); return module

graph = load("graph_under_test", ROOT / ".keel/lib/evidence_graph.py")
core = load("core_under_test", ROOT / ".keel/lib/keel_core.py")

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); (root / ".keel").mkdir(); (root / ".keel/contracts.json").write_text(json.dumps({"evidence_providers": ["browser"], "effect_capabilities": ["cloud.deploy"]}), encoding="utf-8")
    req = root / "requirements.json"; acc = root / "acceptance.json"
    req.write_text(json.dumps({"requirements": [{"id": "REQ-001", "statement": "Browser evidence is required."}]}), encoding="utf-8")
    acc.write_text(json.dumps({"criteria": [{"id": "AC-001", "requirement_id": "REQ-001", "statement": "Browser check passes.", "evidence": [{"provider": "browser", "check_id": "browser-check"}]}]}), encoding="utf-8")
    contracts = root / ".keel/contracts.json"
    assert graph.validate_contract(req, acc, contracts_path=contracts) == []
    assert graph.evaluate(root, req, acc, [{"id": "browser-check", "exit_code": 0}], [], contracts_path=contracts)["status"] == "PASS"
    assert graph.evaluate(root, req, acc, [{"id": "browser-check", "exit_code": 1}], [], contracts_path=contracts)["status"] == "FAIL"
    effects = root / ".keel/ledger/change/effects.json"; effects.parent.mkdir(parents=True)
    effects.write_text(json.dumps({"external_effects": ["deploy"], "effect_capabilities": ["cloud.deploy"], "irreversible": False, "authorization_required": True}), encoding="utf-8")
    assert core.effects_valid(effects)[0] is True
    effects.write_text(json.dumps({"external_effects": ["deploy"], "effect_capabilities": ["unknown"], "irreversible": False, "authorization_required": True}), encoding="utf-8")
    assert core.effects_valid(effects)[0] is False
print(json.dumps({"status": "PASS", "checks": ["provider-binding", "provider-failure", "effect-vocabulary", "authorization-preserved"]}))
