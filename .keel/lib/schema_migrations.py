from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _config_1_to_2(document: dict) -> dict:
    migrated = dict(document)
    migrated.setdefault("verification_commands", [])
    migrated["schema_version"] = 2
    return migrated


MIGRATIONS = {("config", 1, 2): _config_1_to_2}


def _kind(path: Path) -> str:
    if path.name == "config.json" and path.parent.name == ".keel":
        return "config"
    raise ValueError(f"unsupported migration artifact: {path.as_posix()}")


def preflight(path: Path, target: int = 2) -> dict:
    raw = path.read_bytes()
    document = json.loads(raw.decode("utf-8"))
    kind = _kind(path)
    current = document.get("schema_version")
    if current == target:
        return {"status": "CURRENT", "read_only": True, "kind": kind, "path": path.as_posix(), "from": current, "to": target, "before_digest": _digest(raw), "after_digest": _digest(raw)}
    key = (kind, current, target)
    if key not in MIGRATIONS:
        raise ValueError(f"no migration registered for {kind} schema {current} -> {target}")
    candidate = MIGRATIONS[key](document)
    return {"status": "READY", "read_only": True, "kind": kind, "path": path.as_posix(), "from": current, "to": target, "before_digest": _digest(raw), "after_digest": _digest((json.dumps(candidate, indent=2, sort_keys=True) + "\n").encode("utf-8"))}


def _atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(path: Path, backup_dir: Path, target: int = 2) -> dict:
    plan = preflight(path, target)
    original = path.read_bytes()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"{path.name}.{plan['before_digest']}.bak"
    backup.write_bytes(original)
    document = json.loads(original.decode("utf-8"))
    migrated = MIGRATIONS[(plan["kind"], plan["from"], plan["to"])](document)
    encoded = (json.dumps(migrated, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_write(path, encoded)
    return {**plan, "status": "APPLIED", "backup": backup.as_posix(), "backup_digest": _digest(original), "result_digest": _digest(encoded)}


def rollback(path: Path, backup: Path) -> dict:
    original = backup.read_bytes()
    _atomic_write(path, original)
    return {"status": "ROLLED_BACK", "path": path.as_posix(), "backup": backup.as_posix(), "restored_digest": _digest(original)}
