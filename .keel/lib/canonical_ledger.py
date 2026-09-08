"""Canonical change ledger and deterministic legacy compatibility.

``intent.json`` is the sole editable authority. Events and records are kernel-owned
transactions. Hash chaining provides local tamper evidence, not immutability; Git is
the durable integrity substrate.
"""
from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone

SCHEMA="keel.change-intent/v2"; EVENT_SCHEMA="keel.change-event/v1"
LEGACY_NAMES=("proposal.md","delta.md","requirements.json","acceptance.json","scope.txt","risk.json","effects.json","authorization.json","risk-review.md","state.json","gate-log.jsonl","evidence-plan.json","evidence-receipts.json","verification.json","verification.md","evidence-graph.json")
HEX=re.compile(r"^[0-9a-f]{64}$")

def canonical_bytes(v): return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def digest(v): return hashlib.sha256(canonical_bytes(v)).hexdigest()
def file_digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def _atomic(p:Path,data:bytes):
 p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(p.name+".tmp-keel"); t.write_bytes(data); os.replace(t,p)
def write_json(p,v): _atomic(p,json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False).encode()+b"\n")
def safe_id(v):
 if not isinstance(v,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}",v) or ".." in v: raise ValueError(f"unsafe identity: {v!r}")
 return v

def blank_intent(change_id,base,mode="standard",summary=None,scopes=None):
 req=[]; ev=[]
 if mode=="trivial":
  req=[{"id":"REQ-TRIVIAL","statement":summary,"source":{"kind":"human","reference":"cli:start"},"knowledge":"KNOWN"}]
  ev=[{"id":"ER-REQ-TRIVIAL","requirement_id":"REQ-TRIVIAL","minimum_authority":"TESTED","requirement_type":"behavior","policy":"any","evidence":[{"provider":"changed_path","path":x} for x in scopes or []]}]
 return {"schema":SCHEMA,"change_id":change_id,"base_commit":base,"mode":mode,"objective":summary or "","requirements":req,"non_goals":[],"scope":scopes or [],"work":{"units":[],"edges":[],"graph_references":[]},"risk":{"level":"trivial" if mode=="trivial" else "standard","consequences":[],"control_plane_change":False,"security_privacy_sensitive":False,"migration_or_release_sensitive":False,"high_blast_radius":False,"requires_exec_plan":False,"review":""},"effect_requests":[],"evidence_requirements":ev,"decisions":[],"provenance":{"kind":"human-authored","authority_id":None}}

def validate_intent(v,require_planned=False):
 e=[]
 if not isinstance(v,dict) or v.get("schema")!=SCHEMA:return ["unsupported canonical intent schema"]
 for k in ("change_id","base_commit","mode","objective","requirements","non_goals","scope","work","risk","effect_requests","evidence_requirements","decisions","provenance"):
  if k not in v:e.append(f"intent missing {k}")
 try:safe_id(v.get("change_id"))
 except ValueError as x:e.append(str(x))
 if v.get("mode") not in {"standard","trivial"}:e.append("intent mode must be standard|trivial")
 if not isinstance(v.get("scope"),list):e.append("intent scope must be a list")
 else:
  for x in v["scope"]:
   p=PurePosixPath(str(x).replace("\\","/"))
   if not isinstance(x,str) or not x or p.is_absolute() or ".." in p.parts or x.startswith(".git"):e.append(f"unsafe scope pattern: {x}")
 for field in ("requirements","non_goals","effect_requests","evidence_requirements","decisions"):
  if not isinstance(v.get(field),list):e.append(f"intent {field} must be a list")
 ids=[]
 for field in ("requirements","effect_requests","evidence_requirements","decisions"):
  for row in v.get(field,[]) if isinstance(v.get(field),list) else []:
   if not isinstance(row,dict) or not row.get("id"):e.append(f"intent {field} record lacks id")
   else:ids.append(row["id"])
 if len(ids)!=len(set(ids)):e.append("canonical record identities must be unique")
 if require_planned:
  if len(str(v.get("objective","")).strip())<12:e.append("intent objective is too thin")
  if not v.get("scope"):e.append("intent scope has no paths/globs")
  if v.get("mode")!="trivial" and not v.get("requirements"):e.append("standard intent requires requirements")
  if v.get("mode")!="trivial" and not v.get("evidence_requirements"):e.append("standard intent requires evidence requirements")
 return e

def intent_digest(d): return digest(load_intent(d))
def load_intent(d):
 v=json.loads((d/"intent.json").read_text()); errs=validate_intent(v)
 if errs:raise RuntimeError("; ".join(errs))
 return v

def read_events(d,verify=True):
 p=d/"events.jsonl"; out=[]
 if not p.exists():return out
 previous=None
 for no,line in enumerate(p.read_text().splitlines(),1):
  try:r=json.loads(line)
  except Exception as x:raise RuntimeError(f"events.jsonl line {no} invalid: {x}")
  body={k:v for k,v in r.items() if k not in {"event_id","event_digest"}}
  expected=digest(body)
  if r.get("schema")!=EVENT_SCHEMA or r.get("event_id")!=expected or r.get("event_digest")!=expected:raise RuntimeError(f"event integrity failure at line {no}")
  if r.get("previous_event_digest")!=previous:raise RuntimeError(f"event chain failure at line {no}")
  previous=expected;out.append(r)
 return out

def append_event(d,kind,result,details=None,actor="keel-kernel",timestamp=None):
 events=read_events(d); prev=events[-1]["event_digest"] if events else None
 seq=len(events)+1; body={"schema":EVENT_SCHEMA,"sequence":seq,"previous_event_digest":prev,"timestamp":timestamp or now(),"kind":kind,"result":result,"actor":actor,"details":details or {}}
 eid=digest(body); row={**body,"event_id":eid,"event_digest":eid}
 p=d/"events.jsonl";p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("ab") as f:f.write(canonical_bytes(row));f.flush();os.fsync(f.fileno())
 return row

def phase(d):
 current=None
 mapping={"START":"DISCUSS","DISCUSS":"PLAN","PLAN":"EXECUTE","REPLAN":"PLAN","REOPEN":"EXECUTE","VERIFY_PASS":"SHIP","VERIFY_FAIL":"EXECUTE"}
 for e in read_events(d):
  if e["kind"] in mapping and (e["result"] in {"PASS","RECORDED"} or e["kind"] in {"START","REPLAN","REOPEN","VERIFY_PASS","VERIFY_FAIL"}):current=mapping[e["kind"]]
 return current

def create(d,intent):
 if d.exists() and any(d.iterdir()):raise RuntimeError("ledger already exists")
 errs=validate_intent(intent)
 if errs:raise ValueError("; ".join(errs))
 for x in ("grants","receipts","attestations","views"): (d/x).mkdir(parents=True,exist_ok=True)
 write_json(d/"intent.json",intent);append_event(d,"START","PASS",{"base_commit":intent["base_commit"],"mode":intent["mode"]});project_views(d)

def record(d,folder,value,identity_key):
 ident=safe_id(value.get(identity_key)); body={k:v for k,v in value.items() if k not in {"record_digest","generated_by"}}
 row={**body,"record_digest":digest(body),"generated_by":"keel-kernel"};p=d/folder/f"{ident}.json"
 if p.exists() and p.read_bytes()!=json.dumps(row,indent=2,sort_keys=True,ensure_ascii=False).encode()+b"\n":raise RuntimeError(f"record identity collision: {ident}")
 write_json(p,row);return row

def project_views(d):
 i=load_intent(d); ph=phase(d); marker="GENERATED PROJECTION — NON-AUTHORITATIVE; regenerate with keel ledger project."
 lines=[f"# Change {i['change_id']}","",f"> {marker}","",f"Phase: `{ph}`","","## Objective",i.get("objective") or "UNRESOLVED","","## Requirements"]
 lines += [f"- `{r.get('id')}` {r.get('statement','')}" for r in i.get("requirements",[])] or ["- None declared"]
 lines += ["","## Non-goals"]+[f"- {x if isinstance(x,str) else x.get('statement','')}" for x in i.get("non_goals",[])]
 lines += ["","## Scope"]+[f"- `{x}`" for x in i.get("scope",[])]
 lines += ["","## Consequences"]+[f"- {x}" for x in i.get("risk",{}).get("consequences",[])]
 _atomic(d/"views"/"summary.md",("\n".join(lines)+"\n").encode())
 write_json(d/"views"/"status.json",{"schema":"keel.change-status-view/v1","generated":True,"source":{"intent_digest":intent_digest(d),"last_event_digest":read_events(d)[-1]["event_digest"] if read_events(d) else None},"change_id":i["change_id"],"phase":ph,"mode":i["mode"],"base_commit":i["base_commit"]})

def legacy_snapshot(d):
 out={}
 for n in LEGACY_NAMES:
  p=d/n
  if p.is_file():out[n]={"sha256":file_digest(p),"encoding":"utf-8","content":p.read_text(encoding="utf-8",errors="surrogateescape")}
 return out

def _json_legacy(d,n,default):
 p=d/n
 if not p.is_file():return default, {"knowledge":"ABSENT","source":n}
 try:return json.loads(p.read_text()), {"knowledge":"KNOWN","source":n,"sha256":file_digest(p)}
 except Exception as x:raise RuntimeError(f"legacy {n} invalid: {x}")
def migrate_legacy(d,output=None):
 output=output or d
 snap=legacy_snapshot(d)
 if not snap:raise RuntimeError("no supported legacy ledger artifacts")
 state,sp=_json_legacy(d,"state.json",{}); req,rp=_json_legacy(d,"requirements.json",{});acc,ap=_json_legacy(d,"acceptance.json",{});risk,riskp=_json_legacy(d,"risk.json",{});effects,ep=_json_legacy(d,"effects.json",{});auth,aup=_json_legacy(d,"authorization.json",{})
 proposal=snap.get("proposal.md",{}).get("content",""); delta=snap.get("delta.md",{}).get("content","")
 objective="\n".join(x.strip() for x in proposal.splitlines() if x.strip() and not x.startswith("#"))
 ers=[]
 for c in acc.get("criteria",[]) if isinstance(acc,dict) else []:
  if isinstance(c,dict):ers.append({"id":"ER-"+str(c.get("id","UNKNOWN")),"requirement_id":c.get("requirement_id"),"statement":c.get("statement"),"required":c.get("required",True),"policy":c.get("policy","UNKNOWN"),"evidence":c.get("evidence",[]),"provenance":ap})
 intent={"schema":SCHEMA,"change_id":state.get("change_id") or d.name,"base_commit":state.get("base_commit"),"mode":state.get("mode","standard"),"objective":objective,"requirements":req.get("requirements",[]) if isinstance(req,dict) else [],"non_goals":[],"scope":[x.strip() for x in snap.get("scope.txt",{}).get("content","").splitlines() if x.strip() and not x.lstrip().startswith("#")],"work":{"units":[],"edges":[],"graph_references":[],"legacy_delta":{"knowledge":"KNOWN" if delta else "ABSENT","content":delta}},"risk":{"level":risk.get("risk_level","UNKNOWN"),"consequences":[],"control_plane_change":risk.get("control_plane_change"),"security_privacy_sensitive":risk.get("security_privacy_sensitive"),"migration_or_release_sensitive":risk.get("migration_or_release_sensitive"),"high_blast_radius":risk.get("high_blast_radius"),"requires_exec_plan":risk.get("requires_exec_plan"),"review":snap.get("risk-review.md",{}).get("content","")},"effect_requests":[{"id":f"EFFECT-{n+1}","description":x,"authorization_required":effects.get("authorization_required"),"irreversible":effects.get("irreversible"),"capabilities":effects.get("effect_capabilities",[]),"provenance":ep} for n,x in enumerate(effects.get("external_effects",[]) if isinstance(effects,dict) else [])],"evidence_requirements":ers,"decisions":[],"provenance":{"kind":"legacy-migration","reader":"keel.legacy-ledger/v1","source_digest":digest(snap),"sources":{"state":sp,"requirements":rp,"acceptance":ap,"risk":riskp,"effects":ep,"authorization":aup},"preserved_legacy":snap}}
 # Missing legacy authorization is absence, never a grant. Existing boolean authorization is evidence only.
 grants=[]
 if auth.get("authorized") is True:grants.append({"grant_id":"LEGACY-AUTHORIZATION-EVIDENCE","status":"LEGACY_EVIDENCE_NOT_CAPABILITY_GRANT","legacy":auth,"source_digest":aup.get("sha256")})
 errs=validate_intent(intent)
 if errs:raise RuntimeError("legacy migration invalid: "+"; ".join(errs))
 target=output
 if (target/"intent.json").exists():
  existing=load_intent(target)
  if canonical_bytes(existing)!=canonical_bytes(intent):raise RuntimeError("canonical migration target differs from deterministic result")
  return {"status":"UNCHANGED","source_digest":digest(snap),"intent_digest":digest(intent),"intent":intent}
 for x in ("grants","receipts","attestations","views"): (target/x).mkdir(parents=True,exist_ok=True)
 write_json(target/"intent.json",intent)
 # Deterministically translate legacy gate events; timestamps remain source values.
 prev=None
 rows=[]
 gate=snap.get("gate-log.jsonl",{}).get("content","")
 for n,line in enumerate(gate.splitlines(),1):
  try:old=json.loads(line)
  except Exception as x:raise RuntimeError(f"legacy gate-log.jsonl line {n} invalid: {x}")
  body={"schema":EVENT_SCHEMA,"sequence":n,"previous_event_digest":prev,"timestamp":old.get("ts"),"kind":old.get("event","LEGACY_UNKNOWN"),"result":old.get("result","UNKNOWN"),"actor":"legacy-migration","details":{"legacy":old}}
  eid=digest(body);row={**body,"event_id":eid,"event_digest":eid};rows.append(row);prev=eid
 if not rows:
  body={"schema":EVENT_SCHEMA,"sequence":1,"previous_event_digest":None,"timestamp":state.get("created_at"),"kind":"LEGACY_IMPORT","result":"RECORDED","actor":"legacy-migration","details":{"phase":state.get("phase","UNKNOWN")}}
  eid=digest(body);rows=[{**body,"event_id":eid,"event_digest":eid}]
 _atomic(target/"events.jsonl",b"".join(canonical_bytes(x) for x in rows))
 for g in grants:record(target,"grants",g,"grant_id")
 receipts,_=_json_legacy(d,"evidence-receipts.json",{})
 for n,r in enumerate(receipts.get("receipts",[]) if isinstance(receipts,dict) else []):record(target,"receipts",{**r,"receipt_id":r.get("receipt_id") or r.get("verifier",{}).get("id") or f"LEGACY-{n+1}"},"receipt_id")
 project_views(target)
 write_json(target/"views"/"migration.json",{"schema":"keel.legacy-migration-receipt/v1","generated":True,"source_digest":digest(snap),"intent_digest":digest(intent),"preserved_files":sorted(snap),"recovery":"Retain legacy inputs and rerun the keel.legacy-ledger/v1 reader."})
 return {"status":"MIGRATED","source_digest":digest(snap),"intent_digest":digest(intent),"intent":intent}

def contracts(intent):
 requirements={"schema_version":1,"change_type":intent.get("change_type","implementation"),"requirements":intent.get("requirements",[])}
 criteria=[]
 for er in intent.get("evidence_requirements",[]):
  criteria.append({"id":er.get("acceptance_id") or er["id"].replace("ER-","AC-",1),"requirement_id":er.get("requirement_id"),"statement":er.get("statement") or "Required evidence establishes the requirement", "required":er.get("required",True),"policy":er.get("policy","all"),"evidence":er.get("evidence",[])})
 return requirements,{"schema_version":1,"criteria":criteria}

def effects(intent):
 requests=intent.get("effect_requests",[])
 return {"external_effects":[r.get("description","") for r in requests],"effect_capabilities":sorted({x for r in requests for x in r.get("capabilities",[])}),"irreversible":any(r.get("irreversible") is True for r in requests),"authorization_required":any(r.get("authorization_required") is True for r in requests)}

def risk(intent):
 r=intent.get("risk",{})
 return {"risk_level":r.get("level","standard"),**{k:r.get(k,False) for k in ("control_plane_change","security_privacy_sensitive","migration_or_release_sensitive","high_blast_radius","requires_exec_plan")}}
