from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("capability_resolver", ROOT / ".keel/lib/capability_resolver.py")
RESOLVER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(RESOLVER)


def touch(root: Path, relative: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("evidence\n", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="keel-resolver-test-") as raw:
        root = Path(raw)
        for path in ("package.json", "package-lock.json", "tests/check.py", "src/known.py", "notes/custom.dsl"):
            touch(root, path)
        config = {
            "capability_resolver": {"max_evidence_per_capability": 1},
            "source_classification": {
                "explicit_source_globs": ["src/**"],
                "explicit_non_source_globs": ["src/**"],
            },
        }
        first = RESOLVER.resolve(root, config)
        second = RESOLVER.resolve(root, config)
        assert first == second, "resolver output must be deterministic"
        assert first["schema_version"] == 2
        assert first["policy"] == "advisory-evidence-only"
        assert first["capabilities"]["build-toolchain"]["status"] == "DETECTED"
        assert first["capabilities"]["build-toolchain"]["evidence"] == ["package.json"]
        detail = first["capabilities"]["build-toolchain"]["evidence_details"][0]
        assert detail["kind"] == "detected" and "package.json" in detail["patterns"]
        assert first["capabilities"]["dependencies-supply-chain"]["status"] == "DETECTED"
        assert first["source_classification"]["unknown_paths"] == ["notes/custom.dsl"]
        assert first["source_classification"]["unknown_paths_truncated"]
        assert first["conflicts"] == [{
            "status": "CONFLICT",
            "path": "src/known.py",
            "reason": "matches explicit source and non-source classifiers",
            "source_globs": ["src/**"],
            "non_source_globs": ["src/**"],
        }]
        assert "capability-registry" not in first
    print("Capability resolver tests PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
