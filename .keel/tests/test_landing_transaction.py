from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import candidate_attestation as ca
import git_proof
import keel_core as core


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "-c", "user.name=T", "-c", "user.email=t@x", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def repo() -> tuple[Path, str, str, str]:
    directory = Path(tempfile.mkdtemp(prefix="keel-landing-test-"))
    git(directory, "init", "-q")
    git(directory, "config", "user.name", "T")
    git(directory, "config", "user.email", "t@x")
    (directory / "base.txt").write_text("base\n")
    base = commit(directory, "base")
    (directory / "candidate.txt").write_text("candidate\n")
    candidate = commit(directory, "candidate")
    git(directory, "branch", "candidate", candidate)
    git(directory, "checkout", "-q", base)
    (directory / "target.txt").write_text("target\n")
    target = commit(directory, "target")
    git(directory, "branch", "target", target)
    return directory, base, candidate, target


def main() -> None:
    root, base, candidate, target = repo()
    tree, changed = git_proof.synthetic_integration_tree(root, target, candidate, "merge")
    assert git_proof.commit_tree(root, target) != tree
    assert changed == ["candidate.txt", "target.txt"]
    landing = ca.LandingAttestation(
        "landing-test", "refs/heads/target", target, "a" * 64, candidate, git_proof.commit_tree(root, candidate),
        tree, "b" * 64, "c" * 64, ({"receipt_id": "r", "receipt_digest": "d" * 64},), "e" * 64,
        "git-merge-tree", "merge")
    assert ca.LandingAttestation.from_dict(json.loads(json.dumps(landing.as_dict()))) == landing
    landed = git(root, "commit-tree", tree, "-p", target, "-p", candidate, "-m", "landing")
    verified = core.verify_landing(root, "landing-test", landed, landing)
    assert verified["status"] == "PASS"
    try:
        core.verify_landing(root, "landing-test", candidate, landing)
    except RuntimeError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched landed tree was accepted")
    try:
        git_proof.synthetic_integration_tree(root, target, candidate, "unsupported")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported strategy was accepted")
    print("Landing transaction tests PASS")


if __name__ == "__main__":
    main()
