from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_core():
    lib = ROOT / ".keel" / "lib"
    import sys
    sys.path.insert(0, str(lib))
    path = lib / "keel_core.py"
    spec = importlib.util.spec_from_file_location("keel_core_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def main() -> None:
    core = _load_core()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        _git(root, "init", "-q")
        (root / "README.md").write_text("baseline\n", encoding="utf-8")
        _git(root, "add", "README.md")
        _git(root, "-c", "user.name=KEEL Test", "-c", "user.email=keel@example.invalid", "commit", "-qm", "baseline")
        primary_head = _git(root, "rev-parse", "HEAD")
        target = Path(directory) / "change-1"

        created = core.worktree_create(root, "change-1", str(target))
        assert created["path"] == str(target.resolve())
        assert created["head"] == primary_head
        assert any(item["path"] == str(target.resolve()) for item in core.worktree_records(root))
        assert _git(root, "status", "--porcelain") == ""

        (target / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        try:
            core.worktree_retire(root, str(target))
        except RuntimeError as error:
            assert str(error) == "worktree is dirty; pass --force to retire it"
        else:
            raise AssertionError("dirty worktree retirement unexpectedly succeeded")
        assert target.exists()

        retired = core.worktree_retire(root, str(target), force=True)
        assert retired == {"path": str(target.resolve()), "retired": True, "dirty": True, "forced": True}
        assert not target.exists()
        assert all(item["path"] != str(target.resolve()) for item in core.worktree_records(root))
        assert _git(root, "rev-parse", "HEAD") == primary_head
        print("Worktree lifecycle tests PASS")


if __name__ == "__main__":
    main()
