import json
import sys
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import developer_ux
init = developer_ux.init_check(ROOT)
assert init["status"] == "READY" and init["read_only"] is True and init["external"]["codex_version"] == "UNVERIFIED"
review = developer_ux.review(ROOT, "lifecycle-compatibility")
assert review["read_only"] is True and review["change_id"] == "lifecycle-compatibility"
import keel_core
with patch.object(keel_core, "current_verified", return_value=(True, "verified")), patch.object(keel_core, "run_git", return_value=SimpleNamespace(returncode=0)):
    ship = developer_ux.ship_eligibility(ROOT, "lifecycle-compatibility")
assert ship["status"] == "ELIGIBLE" and ship["permission"] == "NOT_GRANTED" and ship["integration"] == "NOT_PERFORMED"
assert "anchor" in ship["next"]
print(json.dumps({"status": "PASS", "checks": ["init", "review", "eligibility-boundary", "read-only"]}))
