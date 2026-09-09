from __future__ import annotations
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("ci_verify",ROOT/".keel/ci/verify.py"); ci=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(ci)

def main():
    rows=ci.categorized_tests(); categories={c for c,_ in rows}; names={p.name for _,p in rows}
    required={"public-cli","ledger-kernel","scheduler","evidence","git-proof-candidate-landing","portability-bootstrap-install","documentation-contracts","hook-wire-contract","codex-app-server-fixtures"}
    assert required <= categories
    assert names == {p.name for p in (ROOT/".keel/tests").glob("test_*.py")} | {"smoke_scheduler.py"}
    workflow=(ROOT/".github/workflows/deterministic-kernel.yml").read_text()
    assert "ubuntu-latest" in workflow and "windows-latest" in workflow and "macos" not in workflow
    assert workflow.count(".keel/ci/verify.py all") == 1 and "secrets." not in workflow and "OPENAI_API_KEY" not in workflow
    smoke=subprocess.run([sys.executable,"-B",".keel/tests/smoke_codex_app_server.py","--no-live-runtime"],cwd=ROOT,text=True,capture_output=True)
    payload=json.loads(smoke.stdout); assert smoke.returncode==0 and payload["status"]=="UNVERIFIED_RUNTIME"
    with tempfile.TemporaryDirectory(dir=ROOT) as td:
        bad=Path(td)/"__pycache__"; bad.mkdir()
        assert not ci.hygiene()
    assert ci.hygiene()
    assert ci.run([sys.executable,"-c","raise SystemExit(7)"],"intentional-regression-probe") is False
    assert ci.run([sys.executable,"-B",".keel/bin/keel.py","manifest"],"manifest-drift-probe")
    print(json.dumps({"status":"PASS","checks":["category-coverage","linux-windows-matrix","thin-yaml","zero-credential-surface","runtime-unverified","hygiene-failure-probe","regression-failure-probe","manifest-drift-check"]},sort_keys=True))
if __name__=="__main__": main()
