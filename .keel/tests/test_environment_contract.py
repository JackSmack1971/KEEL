from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_core():
    lib = ROOT / ".keel" / "lib"
    sys.path.insert(0, str(lib))
    path = lib / "keel_core.py"
    spec = importlib.util.spec_from_file_location("keel_core_under_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_config(root: Path, contract) -> None:
    config_dir = root / ".keel"
    config_dir.mkdir(exist_ok=True)
    config = {} if contract is None else {"environment_contract": contract}
    (config_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")


def main() -> None:
    core = _load_core()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        _write_config(root, None)
        absent = core.environment_contract(root)
        assert absent == {"schema_version": 1, "status": "UNCONFIGURED", "contract": None, "errors": []}

        valid = {
            "schema_version": 1,
            "setup": ["tool", "setup"],
            "start": ["tool", "start"],
            "stop": ["tool", "stop"],
            "isolation": {"ports": "per-worktree", "database": "per-worktree"},
        }
        _write_config(root, valid)
        configured = core.environment_contract(root)
        assert configured["status"] == "CONFIGURED"
        assert configured["contract"] == valid
        assert configured["errors"] == []

        invalid = {"schema_version": 2, "setup": "tool setup", "isolation": {"ports": [8080]}}
        _write_config(root, invalid)
        rejected = core.environment_contract(root)
        assert rejected["status"] == "INVALID"
        assert rejected["errors"] == [
            "environment_contract.schema_version must be 1",
            "environment_contract.setup must be null or a non-empty argv list",
            "environment_contract.isolation must map non-empty string keys to non-empty string values",
        ]
        print("Environment contract tests PASS")


if __name__ == "__main__":
    main()
