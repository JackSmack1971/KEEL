import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import upgrade_kernel
assert upgrade_kernel.contract_report(ROOT)["status"] == "PASS"
assert upgrade_kernel.version_report(ROOT)["compatibility"] == "COMPATIBLE"
first, second = upgrade_kernel.reconcile(ROOT), upgrade_kernel.reconcile(ROOT)
assert first["read_only"] is True and first["git"]["head"] == second["git"]["head"]
print(json.dumps({"status": "PASS", "checks": ["contracts", "version", "reconcile"]}))
