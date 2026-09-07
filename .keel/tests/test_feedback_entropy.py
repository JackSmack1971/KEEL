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
    evaluated = copy.deepcopy(observation); evaluated.update({"state": "EVALUATED", "evaluation_reference": "eval-1", "evaluation_result": {"status": "PASS", "reproducible_improvement": True}})
    assert fe.validate_observation(root, evaluated) == []
    not_improved = copy.deepcopy(evaluated); not_improved["evaluation_result"]["reproducible_improvement"] = False
    assert fe.validate_observation(root, not_improved)
    (root / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    before = (root / "README.md").read_text(encoding="utf-8")
    first, second = fe.entropy_scan(root), fe.entropy_scan(root)
    assert first == second and first["read_only"] is True
    assert any(row["kind"] == "broken-link" for row in first["findings"])
    assert (root / "README.md").read_text(encoding="utf-8") == before
    (root / "docs/exec-plans/active").mkdir(parents=True)
    (root / "docs/exec-plans/active/goal.md").write_text("# Long-horizon goal: durable objective\n", encoding="utf-8")
    (root / "docs/exec-plans/active/orphan.md").write_text("# Ordinary plan\n", encoding="utf-8")
    findings = fe.entropy_scan(root)["findings"]
    assert not any(row["path"].endswith("goal.md") for row in findings)
    assert any(row["path"].endswith("orphan.md") for row in findings)
    observations = root / "observations"; observations.mkdir()
    (root / "evidence.txt").write_text("observed\n", encoding="utf-8")
    reviewed = {"schema_version": 1, "observation_id": "reviewed-one", "source": "test", "observed_at": "2026-09-07T00:00:00Z", "summary": "reviewed", "failure_class": "gap", "state": "REVIEWED", "reviewer": "human", "reviewed_at": "2026-09-07T01:00:00Z", "evidence": ["evidence.txt"]}
    (observations / "reviewed.json").write_text(json.dumps(reviewed), encoding="utf-8")
    (observations / "invalid.json").write_text("{bad", encoding="utf-8")
    queued = fe.queue(root, observations)
    assert queued["evaluation_candidates"] == ["reviewed-one"] and queued["promotion_candidates"] == []
    assert queued["target_plans"][0]["kind"] == "evaluation" and queued["target_plans"][0]["execution"] == "DEFERRED"
    assert len(queued["blocked"]) == 1 and queued["read_only"] is True
print(json.dumps({"status": "PASS", "checks": ["provenance", "review-gate", "goal-record", "deterministic-scan", "read-only"]}))
