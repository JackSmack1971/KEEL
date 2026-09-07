import json
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import repository_map

first = repository_map.build(ROOT)
second = repository_map.build(ROOT)
assert first == second
assert first["policy"] == "derived-navigation-evidence-only"
assert all(not row["path"].startswith(".git") for row in first["topology"])
assert all(set(row) == {"path", "rule"} for key in ("topology", "modules", "entrypoints", "tests", "commands", "dependencies", "source") for row in first[key])
assert any(row["path"] == ".keel/config.json" for row in first["commands"])
assert all("node_modules" not in row["path"] for key in ("topology", "modules", "entrypoints", "tests", "commands", "dependencies", "source") for row in first[key])
assert first["analyzers"]["python"]["analyzer"] == "python-ast"
assert first["analyzers"]["python"]["files_analyzed"] > 0
assert all(row["analyzer"] == "python-ast" and row["source"] for row in first["semantic_imports"])
assert any(row["kind"] == "local" for row in first["semantic_imports"])
assert any(row["kind"] == "external" for row in first["semantic_imports"])
assert first["ownership"]["status"] == "UNAVAILABLE"
assert "command_intelligence" in first and all(row["provenance"] for row in first["command_intelligence"])
assert "symbols" in first and all(row["provenance"] for row in first["symbols"])
assert first["architecture"]["status"] == "UNAVAILABLE"
impact = repository_map.analyze_impact(first, [".keel/lib/repository_map.py", ".keel/config.json"])
assert impact["policy"] == "advisory-only" and impact["risk"] == "WIDEN_VERIFICATION"
before = json.dumps(first, sort_keys=True)
assert json.dumps(repository_map.build(ROOT), sort_keys=True) == before
with tempfile.TemporaryDirectory() as directory:
    temp_root = Path(directory); (temp_root / ".github").mkdir()
    (temp_root / ".github" / "CODEOWNERS").write_text("# owner rules\n/src/ @team\n", encoding="utf-8")
    ownership = repository_map.build(temp_root)["ownership"]
    assert ownership["status"] == "AVAILABLE" and ownership["source"] == ".github/CODEOWNERS"
    assert ownership["rules"][0]["owners"] == ["@team"]
print(json.dumps({"status": "PASS", "checks": ["deterministic", "provenance", "semantic-imports", "ownership-source", "ignored-directories", "derived-only"]}))
