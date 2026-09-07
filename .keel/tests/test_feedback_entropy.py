import copy
import json
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import feedback_entropy as fe

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); (root / "evidence.txt").write_text("observed\n", encoding="utf-8")
    observation = {"schema_version": 1, "observation_id": "missing-check", "source": "review-1", "observed_at": "2026-09-07T00:00:00Z", "summary": "A reviewed failure", "failure_class": "verification-gap", "state": "REVIEWED", "reviewer": "human", "reviewed_at": "2026-09-07T01:00:00Z", "evidence": ["evidence.txt"]}
    assert fe.validate_observation(root, observation) == []
    assert fe.status(root, observation)["eligible_for_evaluation"] is True
    promoted = copy.deepcopy(observation); promoted["state"] = "PROMOTED"
    assert fe.validate_observation(root, promoted)
    (root / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    before = (root / "README.md").read_text(encoding="utf-8")
    first, second = fe.entropy_scan(root), fe.entropy_scan(root)
    assert first == second and first["read_only"] is True
    assert any(row["kind"] == "broken-link" for row in first["findings"])
    assert (root / "README.md").read_text(encoding="utf-8") == before
print(json.dumps({"status": "PASS", "checks": ["provenance", "review-gate", "deterministic-scan", "read-only"]}))
