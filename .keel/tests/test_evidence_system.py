from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("evidence_system_under_test", ROOT / ".keel/lib/evidence_system.py")
evidence = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(evidence)


def verifier(identity="test", authority="TESTED", paths=None, mandatory=False):
    return {"id":identity,"version":"1","provider":"unit_test","authority":authority,"supports":{"requirement_types":["behavior","architecture","security","quality","documentation"],"evidence_providers":["unit_test"]},"applicability":{"paths":paths or ["src/**"],"risk_levels":["low","standard","high"]},"runtime":{"kind":"command","argv":["python","test.py"],"cwd":".","timeout_sec":10},"provenance":"test fixture","mandatory_kernel":mandatory}


def main():
    assert evidence.AUTHORITY[0] == "ASSERTED" and evidence.AUTHORITY[-1] == "FORMALLY_VERIFIED"
    assert evidence.authority_at_least("RUNTIME_OBSERVED", "TESTED")
    assert not evidence.authority_at_least("INSPECTED", "TESTED")
    assert evidence.validate_registry([verifier(), verifier()]) == ["duplicate verifier identity: test", "duplicate verifier invocation: test"]
    malformed=verifier(); malformed["authority"]="MAGIC"; assert any("authority" in x for x in evidence.validate_registry([malformed]))
    er={"id":"ER-REQ-1","requirement_id":"REQ-1","minimum_authority":"TESTED","requirement_type":"behavior","implementation_paths":["src/**"],"acceptable_verifiers":["test"],"acceptable_providers":["unit_test"]}
    weak=evidence.plan([verifier(authority="INSPECTED")],[er],["src/a.py"],"high",{})
    assert weak["status"] == "INCONCLUSIVE"
    unrelated=evidence.plan([verifier(paths=["docs/**"])],[er],["src/a.py"],"high",{})
    assert unrelated["status"] == "INCONCLUSIVE"
    registry=[verifier(),verifier("kernel",paths=["**"],mandatory=True)]
    # Give distinct invocation to the mandatory verifier.
    registry[1]["runtime"]["argv"]=["python","kernel.py"]
    plan=evidence.plan(registry,[er],["src/a.py"],"high",{"fact":"observed"})
    assert plan["status"] == "PASS" and [x["verifier_id"] for x in plan["steps"]] == ["kernel","test"]
    assert evidence.plan(registry,[er],["src/a.py"],"high",{"fact":"observed"}) == plan
    subject={"kind":"git-worktree","content_digest":"tree"}; intent="intent"
    step=next(x for x in plan["steps"] if x["verifier_id"]=="test")
    receipt=evidence.receipt(registry[0],step,subject,intent,"PASS",[{"exit_code":0}],"start","end")
    # A green mandatory command is unrelated and cannot satisfy ER-REQ-1.
    kernel_step=next(x for x in plan["steps"] if x["verifier_id"]=="kernel")
    green_unrelated=evidence.receipt(registry[1],kernel_step,subject,intent,"PASS",[{"exit_code":0}],"start","end")
    assert evidence.evaluate(plan,[green_unrelated],[er],subject,intent)["status"] == "INCONCLUSIVE"
    assert evidence.evaluate(plan,[receipt,green_unrelated],[er],subject,intent)["status"] == "PASS"
    assert evidence.evaluate(plan,[receipt],[er],{"kind":"git-worktree","content_digest":"drift"},intent)["status"] == "INCONCLUSIVE"
    tampered=dict(receipt); tampered["result"]="FAIL"
    assert evidence.evaluate(plan,[tampered],[er],subject,intent)["status"] == "FAIL"
    cfg=json.loads((ROOT/".keel/config.json").read_text()); reg=cfg["verifier_registry"]
    assert evidence.validate_registry(reg) == []
    invocations=[(tuple(x["runtime"]["argv"]),x["runtime"].get("cwd",".")) for x in reg]
    assert len(invocations)==len(set(invocations))
    assert not any(any(len(a) >= 40 and all(c in "0123456789abcdef" for c in a.lower()) for a in x["runtime"]["argv"]) for x in reg)
    docs=(ROOT/"docs/control-plane/VERIFICATION.md").read_text()
    for word in ("EvidenceRequirement","EvidencePlan","Verifier","EvidenceReceipt","INCONCLUSIVE"): assert word in docs
    print(json.dumps({"status":"PASS","hostile_checks":["duplicates","authority","applicability","determinism","unrelated-green","subject-drift","tamper","config"]}))


if __name__ == "__main__": main()
