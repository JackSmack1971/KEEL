from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))

import fact_graph as fg


def write(root: Path, relative: str, content: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ConflictAdapter:
    name = "fixture-conflict"

    def collect(self, snapshot: fg.RepositorySnapshot) -> fg.AdapterEmission:
        source = "src/app.py"
        digest = snapshot.digests[source]
        return fg.AdapterEmission((
            fg.Fact("source-class", source, "SOURCE", fg.Provenance(self.name, source, digest, "explicit")),
            fg.Fact("source-class", source, "NON_SOURCE", fg.Provenance(self.name, source, digest, "explicit")),
        ))


with tempfile.TemporaryDirectory(prefix="keel-factgraph-") as raw:
    root = Path(raw)
    write(root, "src/app.py", "import src.lib\nfrom . import lib\n")
    write(root, "src/lib.py", "VALUE = 1\n")
    write(root, "package.json", "{}\n")
    write(root, "project.unknown.json", "{}\n")
    write(root, "Makefile", "danger:\n\t@touch command-was-executed\n")
    write(root, "docs/readme.md", "evidence\n")
    config = {"source_classification": {"explicit_source_globs": ["src/**"], "explicit_non_source_globs": ["src/**"]}}

    first = fg.build(root, config)
    second = fg.build(root, config)
    assert first.serialize() == second.serialize()
    assert json.loads(first.serialize())["schema"] == fg.SCHEMA
    assert all("\\" not in fact.subject for fact in first.facts)
    assert not (root / "command-was-executed").exists()

    candidates = first.select("command-candidate")
    assert any(fact.subject == "Makefile" for fact in candidates)
    assert first.select("command-declaration") == []
    assert first.resolution("command-declaration", "Makefile")["status"] == "UNKNOWN"

    assert first.select("capability-candidate", "build-toolchain")[0].value["status"] == "DETECTED"
    unsupported = first.select("ecosystem-support", "project.unknown.json")[0]
    assert unsupported.support == "UNSUPPORTED" and unsupported.knowledge == "UNKNOWN"

    python_edges = [edge for edge in first.edges if edge.relation == "depends-on"]
    assert any(edge.source == "src/app.py" and edge.target == "src/lib.py" for edge in python_edges)
    assert all(edge.inputs for edge in python_edges)
    impact = first.impact(["src/lib.py"])
    assert impact["read_only"] and "src/app.py" in impact["impacted"]

    conflict_graph = fg.build(root, config, adapters=(fg.FilesystemAdapter(), ConflictAdapter()))
    resolution = conflict_graph.resolution("source-class", "src/app.py")
    assert resolution["status"] == "CONFLICTING" and resolution["selected"] is None
    assert len(resolution["evidence"]) == 2

    tracked = first.select("resource", "src/lib.py")[0]
    assert first.freshness_against(root)[tracked.id] == "CURRENT"
    write(root, "src/lib.py", "VALUE = 2\n")
    assert first.freshness_against(root)[tracked.id] == "STALE"

    class CustomAdapter:
        name = "custom"
        def collect(self, snapshot: fg.RepositorySnapshot) -> fg.AdapterEmission:
            return fg.AdapterEmission((fg.Fact("custom", ".", True, fg.Provenance(self.name, None, snapshot.digests.get("src/app.py"))),))
    custom = fg.build(root, adapters=(CustomAdapter(),))
    assert custom.select("custom")[0].provenance.adapter == "custom"

print(json.dumps({"status": "PASS", "checks": ["adapter-spi", "determinism", "portable-paths", "read-only", "command-separation", "unsupported", "python-dependencies", "impact", "conflicts", "freshness"]}))
