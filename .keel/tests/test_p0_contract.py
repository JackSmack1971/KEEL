import json
import shutil
import sys
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import p0_contract as p
import keel_core as k

assert p.resolve_command(ROOT, {"argv": ["C:/Users/click/.agents/skills/codex-control-plane-bootstrapper/scripts/validate_control_plane.py"], "provenance": "bad"})["status"] == "FAILED"
assert p.resolve_command(ROOT, {"argv": ["definitely-not-installed-keel-command"], "provenance": "repo"})["status"] == "UNAVAILABLE"
assert p.resolve_command(ROOT, {"argv": ["python", "./missing-p0-command.py"], "provenance": "repo"})["status"] == "UNAVAILABLE"
assert p.resolve_command(ROOT, candidates=[])["status"] == "UNSUPPORTED"
candidate = {"argv": ["python"], "repository_owned": True, "provenance": ".keel/config.json"}
assert p.resolve_command(ROOT, candidates=[candidate, candidate])["status"] == "AMBIGUOUS"
assert p.resolve_command(ROOT, candidates=[{"argv": ["python"], "repository_owned": True}])["status"] == p.UNVERIFIED_RUNTIME
assert p.resolve_command(ROOT, candidates=[{"argv": ["definitely-not-installed-keel-command"], "repository_owned": True, "provenance": ".keel/config.json"}])["status"] == "UNAVAILABLE"
assert p.resolve_command(ROOT, {"argv": ["python"], "requires_authorization": True}, authorized=False)["status"] == "BLOCKED"

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    assert p.classify_git_state(root)["status"] == "NOT_A_GIT_REPOSITORY"
    assert p.classify_git_state(root, requires_git=True)["status"] == "BLOCKED"
    (root / ".control-plane").mkdir()
    (root / ".control-plane/bootstrap-manifest.json").write_text("{", encoding="utf-8")
    assert p.classify_bootstrap(root)["status"] == "MALFORMED_BOOTSTRAP"
    (root / ".control-plane/bootstrap-manifest.json").write_text(json.dumps({"schema_version": 2, "bootstrapper": "x", "files": {}}), encoding="utf-8")
    assert p.classify_bootstrap(root)["status"] == "COPIED_EXTRACTED_FRAMEWORK"

assert p.artifact_boundary([".keel/config.json"])["status"] == "VERIFIED"
assert p.artifact_boundary([".keel/ledger/x/state.json"])["status"] == "FAILED"
assert p.classify_compatibility({})["status"] == "MISSING_METADATA"
assert p.classify_compatibility({"version": "0.1.1"})["status"] == "INCOMPATIBLE"
assert p.classify_compatibility({"version": "2.0.0"})["status"] == "UNSUPPORTED"
assert p.classify_compatibility({"version": "0.0.1"}, migrations={"0.0.1"})["status"] == "MIGRATION_REQUIRED"
assert p.classify_compatibility({"version": "0.1.0"})["status"] == "COMPATIBLE"
assert p.attest(ROOT, [".keel/config.json"])["status"] == "VERIFIED"
assert p.attest(ROOT, [".keel/config.json"], runtime_available=False)["status"] == "UNVERIFIED_RUNTIME"
assert p.generated_artifact_status(ROOT)["status"] == "VERIFIED"
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); (root / ".control-plane").mkdir()
    (root / ".keel/lib").mkdir(parents=True)
    (root / ".keel/lib/p0_contract.py").write_text("producer", encoding="utf-8")
    source = root / "input.txt"; source.write_text("original", encoding="utf-8")
    manifest = root / ".control-plane/bootstrap-manifest.json"
    manifest.write_text(json.dumps({"schema_version": 2, "bootstrapper": "x", "files": {"input.txt": "stale"}}), encoding="utf-8")
    assert p.manifest_producer(root, write=False)["status"] == "FAILED"
    assert p.manifest_producer(root, write=True)["status"] == "WRITTEN"
    assert p.generated_artifact_status(root)["status"] == p.PASS
    source.write_text("changed", encoding="utf-8")
    assert p.generated_artifact_status(root)["status"] == "FAILED"
    source.unlink()
    assert p.generated_artifact_status(root)["status"] == "FAILED"
    (root / "unrelated.txt").write_text("unlisted", encoding="utf-8")
    manifest.write_text(manifest.read_text(encoding="utf-8").replace("input.txt", "unrelated.txt"), encoding="utf-8")
    assert p.generated_artifact_status(root)["status"] == "FAILED"
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory); (root / ".control-plane").mkdir()
    (root / ".control-plane/bootstrap-manifest.json").write_text(json.dumps({"schema_version": 2, "files": {}}), encoding="utf-8")
    assert p.generated_artifact_status(root)["status"] == "BLOCKED"

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / ".keel/templates").mkdir(parents=True)
    for template in (ROOT / ".keel/templates").iterdir():
        shutil.copyfile(template, root / ".keel/templates" / template.name)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", ".keel/templates"], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "baseline"], cwd=root, check=True)
    k.start_change(root, "line-ending-regression", "standard")
    for name in ("proposal.md", "delta.md", "requirements.json", "acceptance.json", "scope.txt", "risk.json", "effects.json", "authorization.json", "risk-review.md", "state.json", "gate-log.jsonl"):
        assert b"\r" not in (root / ".keel/ledger/line-ending-regression" / name).read_bytes()
print(json.dumps({"status": "PASS", "checks": ["portable-resolution", "git-bootstrap", "artifact-boundary", "compatibility", "attestation", "negative-cases"]}))
