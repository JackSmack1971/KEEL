from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
plan_file = ROOT / "docs/exec-plans/active/p1-repository-intelligence-foundation.md"
if not plan_file.is_file():
    plan_file = ROOT / "docs/exec-plans/completed/p1-repository-intelligence-foundation.md"
plan = plan_file.read_text(encoding="utf-8")
roadmap = (ROOT / "docs/exec-plans/active/upgrade-remaining-plan.md").read_text(encoding="utf-8")
audit = (ROOT / "docs/control-plane/UPGRADE_AUDIT.md").read_text(encoding="utf-8")
for phrase in ("keel.repository-intelligence/v1", "DIRECT", "NORMALIZED", "DERIVED", "CONFLICTING", "UNSUPPORTED", "STALE", "generated-artifact", "read-only"):
    assert phrase in plan
for phrase in ("P1 → **VERIFIED COMPLETE / LANDED**", "P2 → **VERIFIED COMPLETE / LANDED**", "P4 → **BLOCKED**", "D1 → **DEFERRED**"):
    assert phrase in roadmap
assert "Repository intelligence and codebase mapping" in audit
print({"status": "PASS", "checks": ["authority", "schema", "negative-matrix", "downstream-locks"]})
