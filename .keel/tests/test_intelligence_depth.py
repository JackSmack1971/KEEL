import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import repository_map
import evidence_graph
import effect_inference

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / ".keel").mkdir()
    (root / ".keel" / "architecture.json").write_text(json.dumps({"facts": [{"from": "a", "to": "b"}]}), encoding="utf-8")
    (root / "architecture.json").write_text(json.dumps({"facts": [{"from": "a", "to": "c"}]}), encoding="utf-8")
    assert repository_map.build(root)["architecture"]["status"] == "CONFLICT"

    result = evidence_graph.oracle_integrity([".keel/config.json"], [])
    assert result["status"] == "REQUIRES_INDEPENDENT_VERIFICATION"
    assert effect_inference.infer_command(["not-a-provider", "run"])["authorization"] == "not evaluated or granted"

print(json.dumps({"status": "PASS", "checks": ["conflict-state", "oracle-integrity", "unknown-provider"]}))
