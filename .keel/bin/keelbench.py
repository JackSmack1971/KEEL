#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, statistics, sys
sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT_DEFAULT = HERE.parents[2]

REQUIRED_SCENARIOS = {
    "bugfix","feature","refactor","dependency-upgrade","migration","security-remediation",
    "frontend-change","performance-regression","brownfield-investigation","multi-service-change","release","failure-recovery"
}
REQUIRED_METRICS = {
    "task_success","acceptance_coverage","introduced_regressions","scope_violations","unauthorized_effects",
    "human_interventions","tokens","wall_time_sec","tool_calls","commands","retries","merge_conflicts","ci_failures","review_findings"
}


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))

def validate(root: Path) -> list[str]:
    errors=[]; corpus=root/".keel/bench/corpus.json"; schema=root/".keel/bench/telemetry-schema.json"
    try: c=load(corpus)
    except Exception as e: return [f"corpus invalid: {e}"]
    try: s=load(schema)
    except Exception as e: return [f"telemetry schema invalid: {e}"]
    kinds={x.get("type") for x in c.get("scenarios",[]) if isinstance(x,dict)}
    missing=sorted(REQUIRED_SCENARIOS-kinds)
    if missing: errors.append("missing benchmark scenario types: "+", ".join(missing))
    ids=[x.get("id") for x in c.get("scenarios",[]) if isinstance(x,dict)]
    if len(ids)!=len(set(ids)): errors.append("duplicate benchmark scenario ids")
    metrics=set(s.get("run_metrics",[])); mm=sorted(REQUIRED_METRICS-metrics)
    if mm: errors.append("telemetry schema missing metrics: "+", ".join(mm))
    return errors

def new_run(root: Path, scenario: str, condition: str, out: Path) -> None:
    c=load(root/".keel/bench/corpus.json")
    row=next((x for x in c["scenarios"] if x.get("id")==scenario),None)
    if row is None: raise RuntimeError(f"unknown scenario id: {scenario}")
    payload={"schema_version":1,"scenario_id":scenario,"scenario_type":row["type"],"condition":condition,"replicate":None,"start_state_id":"","rubric_version":row.get("rubric_version","1"),"metrics":{k:None for k in sorted(REQUIRED_METRICS)},"critical_violation":False,"notes":""}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def score(paths: list[Path]) -> dict:
    rows=[]
    for p in paths:
        if p.is_dir(): files=sorted(p.glob("*.json"))
        else: files=[p]
        for f in files:
            try: rows.append(load(f))
            except Exception: pass
    groups={}
    for r in rows:
        cond=r.get("condition"); m=r.get("metrics") or {}
        if cond not in {"baseline","keel"}: continue
        groups.setdefault(cond,[]).append(m)
    out={"schema_version":1,"runs":{k:len(v) for k,v in groups.items()},"conditions":{}}
    for cond, vals in groups.items():
        success=[1.0 if x.get("task_success") is True else 0.0 for x in vals if x.get("task_success") is not None]
        out["conditions"][cond]={"task_success_rate":None if not success else sum(success)/len(success)}
        for metric in ("tokens","wall_time_sec","tool_calls","commands","human_interventions"):
            nums=[x.get(metric) for x in vals if isinstance(x.get(metric),(int,float))]
            out["conditions"][cond][f"median_{metric}"]=None if not nums else statistics.median(nums)
    if "baseline" in out["conditions"] and "keel" in out["conditions"]:
        b=out["conditions"]["baseline"].get("task_success_rate"); k=out["conditions"]["keel"].get("task_success_rate")
        out["comparison"]={"absolute_task_success_uplift":None if b is None or k is None else k-b}
        if b is not None and k is not None and b < 1:
            out["comparison"]["relative_error_reduction"]=( (1-b)-(1-k) )/(1-b)
        else: out["comparison"]["relative_error_reduction"]=None
    return out

def main()->int:
    ap=argparse.ArgumentParser(description="KEELBench corpus/paired-run harness")
    ap.add_argument("--root",type=Path,default=ROOT_DEFAULT)
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("validate")
    p=sub.add_parser("new-run"); p.add_argument("--scenario",required=True); p.add_argument("--condition",choices=["baseline","keel"],required=True); p.add_argument("--out",type=Path,required=True)
    p=sub.add_parser("score"); p.add_argument("paths",nargs="+",type=Path)
    a=ap.parse_args(); root=a.root.resolve()
    try:
        if a.cmd=="validate":
            e=validate(root); print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e},indent=2)); return 0 if not e else 1
        if a.cmd=="new-run": new_run(root,a.scenario,a.condition,a.out); print(a.out); return 0
        if a.cmd=="score": print(json.dumps(score(a.paths),indent=2)); return 0
    except Exception as e:
        print(f"KEELBENCH ERROR: {e}",file=sys.stderr); return 2
    return 2
if __name__=="__main__": raise SystemExit(main())
