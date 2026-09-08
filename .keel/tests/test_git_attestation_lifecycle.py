from __future__ import annotations
import hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'.keel/lib'))
import candidate_attestation as ca, evidence_system
spec=importlib.util.spec_from_file_location('core',ROOT/'.keel/lib/keel_core.py'); core=importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
CID='proof-test'
def git(root,*args,check=True):
 r=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True); 
 if check and r.returncode: raise RuntimeError(r.stderr)
 return r.stdout.strip()
def write(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def commit(root,msg): git(root,'add','.'); git(root,'-c','user.name=T','-c','user.email=t@x','commit','-qm',msg); return git(root,'rev-parse','HEAD')
def fixture(directory):
 root=directory/'repo'; root.mkdir(); git(root,'init','-q'); (root/'.keel/ledger').mkdir(parents=True); write(root/'.keel/config.json',{'schema_version':2,'verifier_registry':[]}); (root/'README').write_text('base\n'); base=commit(root,'base')
 d=root/f'.keel/ledger/{CID}'; d.mkdir();
 intent={'proposal.md':'proposal\n','delta.md':'## MODIFIED\n- proof\n','requirements.json':'{}\n','acceptance.json':'{}\n','scope.txt':'material.txt\n','risk.json':'{}\n','effects.json':'{}\n','authorization.json':'{}\n','risk-review.md':'review\n'}
 for name,data in intent.items(): (d/name).write_text(data)
 (root/'material.txt').write_text('candidate\n');
 state={'change_id':CID,'phase':'EXECUTE','base_commit':base}; write(d/'state.json',state)
 plan_body={'schema_version':1,'risk_level':'high','changed_paths':['material.txt'],'repository_facts_digest':'0'*64,'steps':[],'assignments':[],'errors':[]}; plan={**plan_body,'status':'PASS','plan_digest':evidence_system.canonical_digest(plan_body)}; write(d/'evidence-plan.json',plan)
 body={'schema_version':1,'verifier':{'id':'proof-tests'},'subject':{},'intent_digest':'','environment':{},'invocation':{},'result':'PASS','observations':[],'establishes':[],'started_at':'s','ended_at':'e'}; receipt={**body,'receipt_digest':evidence_system.canonical_digest(body)}; write(d/'evidence-receipts.json',{'schema_version':1,'receipts':[receipt]})
 intent_value={name:data for name,data in intent.items()}; intent_digest=evidence_system.canonical_digest(intent_value)
 content=core.content_digest(root,CID); verification={'status':'PASS','implementation_status':'PASS','change_type':'implementation','base_commit':base,'content_digest':content,'intent_digest':intent_digest,'evidence_plan_digest':plan['plan_digest'],'changed_paths':['material.txt']}; write(d/'verification.json',verification); state.update(phase='SHIP',verified_content_digest=content); write(d/'state.json',state)
 candidate=commit(root,'candidate'); return root,base,candidate

def raises(text,fn):
 try: fn()
 except RuntimeError as e: assert text in str(e),(text,str(e))
 else: raise AssertionError('expected '+text)
def main():
 subprocess.run([sys.executable,'-B',str(ROOT/'.keel/tests/test_git_proof.py')],check=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'.keel/tests/test_candidate_attestation.py')],check=True)
 # Exact seal, attestation payload, post-verification edit, changed intent, and ref collision.
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); sealed=core.seal_candidate(root,CID,candidate); att=ca.read_attestation(root,CID)
  assert sealed['attestation_digest']==att.digest and att.candidate_commit==candidate and att.candidate_tree==git(root,'rev-parse',candidate+'^{tree}') and att.material_digest and att.evidence_receipts[0]['receipt_id']=='proof-tests'
  (root/'material.txt').write_text('edited\n'); raises('stale/unverified',lambda:core.seal_candidate(root,CID,candidate)); (root/'material.txt').write_text('candidate\n')
  (root/f'.keel/ledger/{CID}/proposal.md').write_text('changed intent\n'); raises('stale/unverified',lambda:core.seal_candidate(root,CID,candidate)); git(root,'checkout','--',f'.keel/ledger/{CID}/proposal.md')
  other=git(root,'rev-parse',base); git(root,'update-ref',f'refs/keel/candidates/collision',other); raises('candidate ref collision',lambda:(git(root,'update-ref',f'refs/keel/candidates/{CID}',other),core.seal_candidate(root,CID,candidate))[1])
 # Committed candidate content drift is rejected independently.
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); (root/'material.txt').write_text('drift\n'); drift=commit(root,'drift'); raises('Git-tree digest',lambda:core.verify_commit_tree(root,CID,drift,True))
 # Unrelated mainline and content-equivalent squash/rebase anchor; material drift and collisions reject.
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); core.seal_candidate(root,CID,candidate)
  git(root,'checkout','-q','--detach',base); (root/'unrelated').write_text('mainline\n'); commit(root,'unrelated');
  git(root,'checkout','-q',candidate,'--','material.txt',f'.keel/ledger/{CID}'); landed=commit(root,'squashed candidate'); assert git(root,'merge-base','--is-ancestor',candidate,landed,check=False)==''
  core.anchor(root,CID,landed); status,reason=core.anchored_status(root,CID); assert status=='anchored',reason
  note=git(root,'notes','--ref=keel','show',landed); assert 'integration-relation: content-equivalent' in note
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); core.seal_candidate(root,CID,candidate); (root/'material.txt').write_text('drift\n'); drift=commit(root,'drift'); raises('content does not match',lambda:core.anchor(root,CID,drift))
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); core.seal_candidate(root,CID,candidate); git(root,'notes','--ref=keel','add','-m','keel-change-id: proof-test\nwrong: note',candidate); raises('note collides',lambda:core.anchor(root,CID,candidate))
 with tempfile.TemporaryDirectory() as td:
  root,base,candidate=fixture(Path(td)); core.seal_candidate(root,CID,candidate); git(root,'update-ref',f'refs/keel/ledger/{CID}',base); raises('ref collision',lambda:core.anchor(root,CID,candidate))
 print('Git attestation lifecycle tests PASS')
if __name__=='__main__': main()
