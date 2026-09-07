import json
import sys
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
assert all("node_modules" not in row["path"] for key in first if isinstance(first[key], list) for row in first[key])
before = json.dumps(first, sort_keys=True)
assert json.dumps(repository_map.build(ROOT), sort_keys=True) == before
print(json.dumps({"status": "PASS", "checks": ["deterministic", "provenance", "ignored-directories", "derived-only"]}))
