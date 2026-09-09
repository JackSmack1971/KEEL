import json
import subprocess
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import p0_contract


with tempfile.TemporaryDirectory() as directory:
    repo = Path(directory)
    assert p0_contract.classify_git_state(repo)["status"] == "NOT_A_GIT_REPOSITORY"
    (repo / ".keel").mkdir()
    (repo / ".keel/bootstrap-manifest.json").write_text(json.dumps({"schema_version": 2, "bootstrapper": "test", "files": {}}), encoding="utf-8")
    first = p0_contract.classify_bootstrap(repo)
    second = p0_contract.classify_bootstrap(repo)
    assert first == second
    assert first["status"] == "COPIED_EXTRACTED_FRAMEWORK"
    assert p0_contract.artifact_boundary([".keel/config.json"])["status"] == "VERIFIED"
    assert p0_contract.artifact_boundary([".keel/ledger/change/intent.json"])["status"] == "FAILED"
print("Portability installation tests PASS")
