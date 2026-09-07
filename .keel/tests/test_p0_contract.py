import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import p0_contract as p

assert p.resolve_command(ROOT, {"argv": ["C:/Users/click/.agents/skills/codex-control-plane-bootstrapper/scripts/validate_control_plane.py"], "provenance": "bad"})["status"] == "FAILED"
assert p.resolve_command(ROOT, {"argv": ["definitely-not-installed-keel-command"], "provenance": "repo"})["status"] == "UNAVAILABLE"
assert p.resolve_command(ROOT, {"argv": ["python", "./missing-p0-command.py"], "provenance": "repo"})["status"] == "UNAVAILABLE"
assert p.resolve_command(ROOT, candidates=[])["status"] == "UNSUPPORTED"
candidate = {"argv": ["python"], "repository_owned": True, "provenance": ".keel/config.json"}
assert p.resolve_command(ROOT, candidates=[candidate, candidate])["status"] == "AMBIGUOUS"
assert p.resolve_command(ROOT, candidates=[{"argv": ["python"], "repository_owned": True}])["status"] == "UNSUPPORTED"
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
    (root / ".control-plane/bootstrap-manifest.json").write_text(json.dumps({"schema_version": 2, "files": {}}), encoding="utf-8")
    assert p.generated_artifact_status(root)["status"] == "BLOCKED"
print(json.dumps({"status": "PASS", "checks": ["portable-resolution", "git-bootstrap", "artifact-boundary", "compatibility", "attestation", "negative-cases"]}))
