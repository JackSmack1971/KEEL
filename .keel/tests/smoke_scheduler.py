from __future__ import annotations
import json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'.keel/lib'))
import change_graph as cg,evidence_system,git_proof,scheduler
class LocalAdapter:
 def __init__(self):self.calls=[]
 def dispatch(self,e):
  self.calls.append(e);now=time.time();o=scheduler.ExecutionObservation(e.identity,e.change_id,e.work_unit_id,e.subject,e.workspace.identity,e.workspace.path,e.runtime_profile_id,e.runtime_profile_digest,'thread','turn','COMPLETED',now,now)
  return scheduler.DispatchResult('OBSERVED','local','smoke',observation=o)
source={'schema_id':'keel.mission','schema_version':2,'mission_id':'local-smoke','objective':'local','nodes':[{'node_id':'prepare','objective':'prepare','acceptance_criteria':['done']},{'node_id':'verify','objective':'verify','acceptance_criteria':['done'],'dependencies':['prepare']}],'dependencies':[{'from':'verify','to':'prepare','type':'HARD_PREREQUISITE'}]}
graph=cg.adapt_v2(source);adapter=LocalAdapter();ids=[x['identity'] for x in graph['records'] if x['kind']=='work-unit'];subject=git_proof.head_commit(ROOT)
er={'id':'AC','requirement_id':'REQ','minimum_authority':'TESTED'};evidence_subject={'commit':subject};portable={'schema_version':1,'risk_level':'high','changed_paths':[],'repository_facts_digest':'facts','steps':[{'verifier_id':'test','authority':'TESTED','provider':'unit_test','runtime':{},'mandatory_kernel':False,'establishes':['AC']}],'assignments':[{'evidence_requirement_id':'AC','requirement_id':'REQ','verifier_id':'test'}],'errors':[]};plan={**portable,'status':'PASS','plan_digest':evidence_system.canonical_digest(portable)};body={'schema_version':1,'verifier':{'id':'test','version':'1','provider':'unit_test','provenance':'test','declared_authority':'TESTED'},'subject':evidence_subject,'intent_digest':'intent','environment':{},'invocation':{},'result':'PASS','observations':[],'establishes':['AC'],'started_at':'a','ended_at':'b'};receipt={**body,'receipt_digest':evidence_system.canonical_digest(body)}
g=scheduler.GovernanceContext('change',subject,subject,'intent','authority','runtime','runtime-digest','context','bounded context',('REQ',),('scope',),('AC',),plan['plan_digest'],{i:str(ROOT) for i in ids})
def verify(run,i):run.apply_verification(i,scheduler.VerificationDecision(True,'change',i,subject,i,str(ROOT),'intent',run.state.graph_digest,'authority','runtime-digest',plan['plan_digest'],plan,(receipt,),(er,),evidence_subject))
with tempfile.TemporaryDirectory() as directory:
 store=scheduler.StateStore(Path(directory)/'scheduler.json');run=scheduler.Scheduler(graph,adapter,state=store.load(),governance=g,repository=ROOT,max_concurrency=1);run.dispatch();verify(run,adapter.calls[-1].work_unit_id);store.save(run.state)
 resumed=scheduler.Scheduler(graph,adapter,state=store.load(),governance=g,repository=ROOT,max_concurrency=1);resumed.dispatch();verify(resumed,adapter.calls[-1].work_unit_id);store.save(resumed.state);assert all(r.status==scheduler.WorkStatus.COMPLETE for r in resumed.state.records.values());assert len(adapter.calls)==2
print(json.dumps({'status':'PASS','external_effects':False,'observed_then_verified_workunits':2},sort_keys=True))
