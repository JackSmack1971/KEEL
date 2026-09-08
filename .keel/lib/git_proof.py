"""Deterministic, dependency-free Git proofs used by KEEL lifecycle boundaries."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

OID_RE = re.compile(r"^[0-9a-f]{40,64}$")


def run(root: Path, args: list[str], *, check: bool = True, binary: bool = False):
    return subprocess.run(["git", *args], cwd=root, text=not binary, capture_output=True, check=check)


def repository_root(cwd: Path | None = None) -> Path:
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("KEEL requires a Git repository")
    return Path(result.stdout.strip()).resolve()


def resolve_commit(root: Path, revision: str) -> str:
    result = run(root, ["rev-parse", f"{revision}^{{commit}}"], check=False)
    if result.returncode or not OID_RE.fullmatch(result.stdout.strip()):
        raise RuntimeError(f"invalid commit: {revision}")
    return result.stdout.strip()


def head_commit(root: Path) -> str:
    result = run(root, ["rev-parse", "HEAD"], check=False)
    if result.returncode:
        raise RuntimeError("KEEL requires an initial baseline commit before the first write change")
    return result.stdout.strip()


def normalize_repo_path(value: str) -> str:
    value = value.replace("\\", "/")
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or value in {".git", "."} or value.startswith(".git/"):
        raise ValueError(f"unsafe repository-relative path: {value}")
    return path.as_posix()


@dataclass(frozen=True)
class RepositoryIdentity:
    root: str
    common_dir: str
    git_dir: str
    worktree: str
    baseline_commit: str

    def as_dict(self) -> dict:
        return {"root": self.root, "common_dir": self.common_dir, "git_dir": self.git_dir,
                "worktree": self.worktree, "baseline_commit": self.baseline_commit}


def repository_identity(root: Path, baseline: str) -> RepositoryIdentity:
    root = repository_root(root)
    baseline = resolve_commit(root, baseline)
    common = run(root, ["rev-parse", "--git-common-dir"]).stdout.strip()
    git_dir = run(root, ["rev-parse", "--git-dir"]).stdout.strip()
    common_path = (root / common).resolve() if not Path(common).is_absolute() else Path(common).resolve()
    git_path = (root / git_dir).resolve() if not Path(git_dir).is_absolute() else Path(git_dir).resolve()
    return RepositoryIdentity(str(root), str(common_path), str(git_path), str(root), baseline)


def changed_paths(root: Path, base: str, commit: str | None = None) -> list[str]:
    args = ["diff", "--name-only", "--diff-filter=ACMRDTUXB", resolve_commit(root, base)]
    if commit is not None:
        args.append(resolve_commit(root, commit))
    args.append("--")
    result = run(root, args, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    names = {normalize_repo_path(x) for x in result.stdout.splitlines() if x}
    if commit is None:
        untracked = run(root, ["ls-files", "--others", "--exclude-standard"], check=False)
        if untracked.returncode:
            raise RuntimeError(untracked.stderr.strip() or "git ls-files failed")
        names.update(normalize_repo_path(x) for x in untracked.stdout.splitlines() if x)
    return sorted(names)


def worktree_entry(root: Path, rel: str) -> tuple[str, bytes]:
    rel = normalize_repo_path(rel); path = root / rel
    if path.is_symlink():
        return "120000", os.readlink(path).encode("utf-8", errors="surrogateescape")
    if path.is_file():
        executable = os.name != "nt" and bool(path.stat().st_mode & 0o111)
        data = path.read_bytes().replace(b"\r\n", b"\n") if os.name == "nt" else path.read_bytes()
        return ("100755" if executable else "100644"), data
    if path.is_dir():
        sub = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, text=True, capture_output=True)
        if sub.returncode == 0 and OID_RE.fullmatch(sub.stdout.strip().lower()):
            return "160000", sub.stdout.strip().lower().encode("ascii")
    return "000000", b"<missing>"


def tree_entry(root: Path, commit: str, rel: str) -> tuple[str, bytes]:
    rel = normalize_repo_path(rel); commit = resolve_commit(root, commit)
    result = run(root, ["ls-tree", "-z", commit, "--", rel], check=False, binary=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace").strip() or f"git ls-tree failed for {rel}")
    if not result.stdout:
        return "000000", b"<missing>"
    meta, separator, path_bytes = result.stdout.rstrip(b"\0").partition(b"\t")
    parts = meta.split()
    if not separator or len(parts) != 3 or not path_bytes:
        raise RuntimeError(f"unexpected git ls-tree result for {rel}")
    mode, kind, oid = (part.decode("ascii") for part in parts)
    if kind == "commit" and mode == "160000":
        return mode, oid.lower().encode("ascii")
    if kind != "blob":
        raise RuntimeError(f"unsupported Git tree entry type for {rel}: {mode} {kind}")
    blob = run(root, ["cat-file", "blob", oid], check=False, binary=True)
    if blob.returncode:
        raise RuntimeError(blob.stderr.decode(errors="replace").strip() or f"git cat-file failed for {rel}")
    return mode, blob.stdout.replace(b"\r\n", b"\n") if os.name == "nt" else blob.stdout


def digest_entries(entries: Iterable[tuple[str, str, tuple[str, bytes]]]) -> str:
    digest = hashlib.sha256()
    for boundary, rel, (mode, data) in entries:
        digest.update(f"{boundary}:{rel}".encode()); digest.update(b"\0")
        digest.update(mode.encode()); digest.update(b"\0"); digest.update(data); digest.update(b"\0")
    return digest.hexdigest()


def commit_tree(root: Path, commit: str) -> str:
    return run(root, ["rev-parse", f"{resolve_commit(root, commit)}^{{tree}}"]).stdout.strip()


def tree_changed_paths(root: Path, left: str, right: str) -> list[str]:
    """Return the exact repository paths changed between two Git tree-ish values."""
    result = run(root, ["diff", "--name-only", "--diff-filter=ACMRDTUXB", resolve_commit(root, left), resolve_commit(root, right), "--"], check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git tree diff failed")
    return sorted({normalize_repo_path(x) for x in result.stdout.splitlines() if x})


def synthetic_integration_tree(root: Path, target: str, candidate: str, strategy: str = "merge") -> tuple[str, list[str]]:
    """Construct an isolated merge result without changing the caller's index/worktree."""
    if strategy not in {"merge", "squash", "rebase"}:
        raise ValueError("unsupported landing strategy")
    target_sha = resolve_commit(root, target)
    candidate_sha = resolve_commit(root, candidate)
    # Git's tree merger is deterministic and reports conflicts without writing an
    # index or changing HEAD. Squash/rebase still require the same final tree
    # equivalence proof; the landing mechanism is recorded separately.
    result = run(root, ["merge-tree", "--write-tree", target_sha, candidate_sha], check=False)
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError("synthetic integration has conflicts" + (f": {detail[:4000]}" if detail else ""))
    tree = result.stdout.splitlines()[0].strip()
    if not OID_RE.fullmatch(tree):
        raise RuntimeError("synthetic integration did not produce a valid tree")
    return tree, tree_changed_paths(root, target_sha, candidate_sha)


def materialize_tree(root: Path, tree: str, destination: Path) -> None:
    """Materialize a Git tree in a disposable directory for integration verifiers."""
    import tarfile
    destination.mkdir(parents=True, exist_ok=False)
    archive = run(root, ["archive", "--format=tar", tree], binary=True)
    import io
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as tar:
        tar.extractall(destination, filter="data")


def show_json(root: Path, commit: str, rel: str) -> dict:
    rel = normalize_repo_path(rel)
    raw = run(root, ["show", f"{resolve_commit(root, commit)}:{rel}"], check=False, binary=True)
    if raw.returncode:
        raise RuntimeError(f"commit does not contain {rel}")
    try:
        return json.loads(raw.stdout.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"committed {Path(rel).name} is invalid JSON: {exc}") from exc
