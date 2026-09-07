import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import mission_runtime


MISSION = {
    "schema_version": 1,
    "mission_id": "runtime-fixture",
    "objective": "Verify a governed child",
    "success_criteria": ["child evidence is recorded"],
    "work": {"child": {"risk": "standard", "depends_on": []}},
}

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
    (root / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "config", "user.name", "KEEL Test"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "keel@example.invalid"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "baseline.txt"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True, capture_output=True)
    (root / ".keel/ledger/child").mkdir(parents=True)
    (root / ".keel/config.json").write_text(json.dumps({"runtime_capabilities": {"provider": "fixture"}}), encoding="utf-8")
    (root / ".keel/ledger/child/state.json").write_text(json.dumps({"schema_version": 1, "change_id": "child", "phase": "EXECUTE"}), encoding="utf-8")
    (root / ".keel/ledger/child/scope.txt").write_text("src/**\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", ".keel"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "child-ledger"], check=True, capture_output=True)

    seen = []
    def executor(_root, change_id, state):
        assert _root != root and (_root / ".git").exists()
        seen.append((change_id, state["phase"]))
        return {"status": "PASS", "evidence": "provider-claim-must-not-count"}

    authoritative = mission_runtime.keel_core.verify_change
    mission_runtime.keel_core.verify_change = lambda *_args: {"status": "PASS", "evidence": "authoritative"}
    result = mission_runtime.run(root, MISSION, executor=executor, max_retries=1)
    assert result["status"] == "PASS" and seen == [("child", "EXECUTE")]
    assert result["results"][0]["result"]["evidence"] == "authoritative"
    record = json.loads((root / ".keel/mission/runtime-fixture/runs/child.json").read_text())
    assert record["attempts"] == 1 and record["integration"] == "NOT_PERFORMED"
    assert mission_runtime.dispatch(root, MISSION)["dispatch_policy"] == "shared-mission-runtime"
    try:
        mission_runtime.integrate(root, "runtime-fixture", "child")
    except mission_runtime.BoundaryViolation as exc:
        assert "authorization" in str(exc)
    else:
        raise AssertionError("mission integration bypass was accepted")

    (root / ".keel/ledger/child/state.json").write_text(json.dumps({"schema_version": 1, "change_id": "other", "phase": "EXECUTE"}), encoding="utf-8")
    try:
        mission_runtime.run(root, MISSION, executor=executor)
    except mission_runtime.BoundaryViolation as exc:
        assert "identity" in str(exc)
    else:
        raise AssertionError("child ledger identity bypass was accepted")

    bad_results = [
        ({"changed_paths": ["outside.txt"]}, "scope"),
        ({"authorization_granted": True}, "Change-owned"),
        ({"fabricated_evidence": True}, "Change-owned"),
        ({"seal": True}, "Change-owned"),
        ({"verification_status": "FAIL"}, "verification"),
        ({"commit": "different-sha"}, "different Git"),
    ]
    for index, (extra, expected) in enumerate(bad_results):
        mission = dict(MISSION); mission["mission_id"] = f"boundary-{index}"
        (root / ".keel/ledger/child/state.json").write_text(json.dumps({"schema_version": 1, "change_id": "child", "phase": "EXECUTE"}), encoding="utf-8")
        result = mission_runtime.run(root, mission, executor=lambda *_args, extra=extra: {"status": "PASS", **extra})
        assert result["status"] == "FAILED" and expected in result["results"][0]["result"]["error"]
        assert not (root / ".keel/mission" / mission["mission_id"] / "runs/child.json").exists()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(MISSION, handle); mission_path = handle.name
    cli = subprocess.run([sys.executable, str(ROOT / ".keel/bin/keel.py"), "mission", "dispatch", mission_path], cwd=ROOT, text=True, capture_output=True)
    assert cli.returncode == 0 and "shared-mission-runtime" in cli.stdout
    mission_runtime.keel_core.verify_change = authoritative

print(json.dumps({"status": "PASS", "checks": ["capability-handshake", "child-ledger", "scope-boundary", "effects-boundary", "evidence-boundary", "seal-boundary", "tree-boundary", "alternate-dispatch", "bounded-retry", "integration-boundary", "identity-boundary"]}))
