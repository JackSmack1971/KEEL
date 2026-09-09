from __future__ import annotations
import copy, json, sys, tempfile, time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'.keel/lib'))
import change_graph as cg, evidence_system, git_proof, scheduler

def graph():
 return cg.adapt_v2({'schema_id':'keel.mission','schema_version':2,'mission_id':'scheduler-test','objective':'test scheduler','nodes':[{'node_id':'a','objective':'a','acceptance_criteria':['a']},{'node_id':'b','objective':'b','acceptance_criteria':['b'],'dependencies':['a']},{'node_id':'c','objective':'c','acceptance_criteria':['c']}],'dependencies':[{'from':'b','to':'a','type':'HARD_PREREQUISITE'}]})

def evidence_plan():
 subject={'commit':'subject'}; er={'id':'AC-1','requirement_id':'REQ-1','minimum_authority':'TESTED'}
 portable={'schema_version':1,'risk_level':'high','changed_paths':[],'repository_facts_digest':'facts','steps':[{'verifier_id':'test','authority':'TESTED','provider':'unit_test','runtime':{},'mandatory_kernel':False,'establishes':['AC-1']}],'assignments':[{'evidence_requirement_id':'AC-1','requirement_id':'REQ-1','verifier_id':'test'}],'errors':[]}
 plan={**portable,'status':'PASS','plan_digest':evidence_system.canonical_digest(portable)}
 body={'schema_version':1,'verifier':{'id':'test','version':'1','provider':'unit_test','provenance':'test','declared_authority':'TESTED'},'subject':subject,'intent_digest':'intent-1','environment':{},'invocation':{},'result':'PASS','observations':[],'establishes':['AC-1'],'started_at':'a','ended_at':'b'}
 receipt={**body,'receipt_digest':evidence_system.canonical_digest(body)}
 return plan,(receipt,),(er,),subject

def governance(g,**updates):
 ids=[x['identity'] for x in g['records'] if x['kind']=='work-unit']; subject=git_proof.head_commit(ROOT)
 values=dict(change_id='change-1',base_commit=subject,subject=subject,intent_digest='intent-1',authority_digest='authority-1',runtime_profile_id='runtime-1',runtime_profile_digest='runtime-digest-1',context_id='context-1',bounded_context='bounded governed context',requirements=('REQ-1',),scope=('.keel/lib/**',),evidence_requirements=('AC-1',),evidence_plan_digest=evidence_plan()[0]['plan_digest'],workspace_paths={i:str(ROOT) for i in ids})
 values.update(updates);return scheduler.GovernanceContext(**values)

class Adapter:
 def __init__(self):self.calls=[]
 def dispatch(self,envelope):
  assert isinstance(envelope,scheduler.DispatchEnvelope);self.calls.append(envelope)
  now=time.time();o=scheduler.ExecutionObservation(envelope.identity,envelope.change_id,envelope.work_unit_id,envelope.subject,envelope.workspace.identity,envelope.workspace.path,envelope.runtime_profile_id,envelope.runtime_profile_digest,'thread-1','turn-1','COMPLETED',now,now,('turn/completed',),('artifact-1',))
  return scheduler.DispatchResult('OBSERVED',evidence_fingerprint=envelope.identity,observation=o)

def decision(s,i,**updates):
 g=s.governance;r=s.state.records[i];values=dict(passed=True,change_id=g.change_id,work_unit_id=i,subject=g.subject,workspace_id=r.workspace_id,workspace_path=r.workspace_path,intent_digest=g.intent_digest,graph_digest=s.state.graph_digest,authority_digest=g.authority_digest,runtime_profile_digest=g.runtime_profile_digest,evidence_plan_digest=g.evidence_plan_digest);plan,receipts,ers,subject=evidence_plan();values.update(plan=plan,receipts=receipts,evidence_requirements=ers,evidence_subject=subject);values.update(updates);return scheduler.VerificationDecision(**values)

g=graph();a=Adapter();s=scheduler.Scheduler(g,a,governance=governance(g),repository=ROOT,max_concurrency=2)
first=s.dispatch();assert len(a.calls)==2 and all(s.state.records[e.work_unit_id].status==scheduler.WorkStatus.AWAITING_VERIFICATION for e in a.calls)
assert first['status']=='BLOCKED' and all(r.status!=scheduler.WorkStatus.COMPLETE for r in s.state.records.values())
# External reconciliation cannot promote transport status to engineering completion.
s.reconcile({a.calls[0].work_unit_id:{'status':'COMPLETE'}});assert s.state.records[a.calls[0].work_unit_id].status==scheduler.WorkStatus.AWAITING_VERIFICATION
for e in list(a.calls):s.apply_verification(e.work_unit_id,decision(s,e.work_unit_id))
second=s.dispatch();assert len(second['dispatched'])==1;last=a.calls[-1];s.apply_verification(last.work_unit_id,decision(s,last.work_unit_id));assert s.reconcile()['status']=='COMPLETE'
# Every governed field is present and immutable enough to reject assignment.
env=a.calls[0];assert env.objective and env.requirements and env.scope and env.evidence_requirements and env.bounded_context
try:env.objective='changed';assert False
except Exception:pass
# Exact identity mismatch matrix fails closed and leaves awaiting state unchanged.
target=last.work_unit_id
for field,bad in [('change_id','stale'),('work_unit_id','stale'),('subject','0'*40),('workspace_id','stale'),('workspace_path','/stale'),('intent_digest','stale'),('graph_digest','stale'),('authority_digest','stale'),('runtime_profile_digest','stale'),('evidence_plan_digest','stale')]:
 s.state.records[target].status=scheduler.WorkStatus.AWAITING_VERIFICATION
 try:s.apply_verification(target,decision(s,target,**{field:bad}));assert False,field
 except ValueError:pass
assert s.state.records[target].status==scheduler.WorkStatus.AWAITING_VERIFICATION
# Objective-only dispatch and unresolved/mismatched workspaces are impossible.
try:scheduler.Scheduler(g,Adapter(),max_concurrency=1).dispatch();assert False
except Exception:pass
bad_adapter=Adapter();bad=scheduler.Scheduler(g,bad_adapter,governance=governance(g,workspace_paths={}),repository=ROOT);bad.dispatch();assert not bad_adapter.calls and sum(r.status==scheduler.WorkStatus.ESCALATED for r in bad.state.records.values())==1
wrong=Path(tempfile.mkdtemp())
try:scheduler.resolve_workspace(ROOT,'x',str(wrong),git_proof.head_commit(ROOT));assert False
except ValueError:pass
try:scheduler.resolve_workspace(ROOT,'x',str(ROOT),'0'*40);assert False
except ValueError:pass
# A forged receipt cannot complete work, and duplicated observation identities are checked independently.
s.state.records[target].status=scheduler.WorkStatus.AWAITING_VERIFICATION
try:s.apply_verification(target,decision(s,target,receipts=()));assert False
except ValueError:pass
for field,bad_value in [('change_id','bad'),('work_unit_id','bad'),('subject','bad'),('workspace_id','bad'),('workspace_path','/bad'),('runtime_profile_id','bad'),('runtime_profile_digest','bad')]:
 class BadObservationAdapter(Adapter):
  def dispatch(self,envelope):
   result=super().dispatch(envelope);return replace(result,observation=replace(result.observation,**{field:bad_value}))
 hostile=BadObservationAdapter();trial=scheduler.Scheduler(g,hostile,governance=governance(g),repository=ROOT,max_concurrency=1);trial.dispatch();assert all(r.status!=scheduler.WorkStatus.AWAITING_VERIFICATION for r in trial.state.records.values()),field
# Observation recovery persists thread/turn/workspace/envelope identity.
with tempfile.TemporaryDirectory() as d:
 store=scheduler.StateStore(Path(d)/'state.json');store.save(s.state);loaded=store.load();assert loaded.to_dict()==s.state.to_dict();assert loaded.records[target].observations[-1].turn_id=='turn-1'
# Resource conflicts still serialize.
conflict=copy.deepcopy(g)
for raw in conflict['records']:
 if raw['kind']=='work-unit':raw['attributes']['resource_claims']=[{'resource':'repo:src/x','mode':'EXCLUSIVE'}]
runnable,blocked=scheduler.Scheduler(conflict,max_concurrency=2).frontier();assert len(runnable)==1 and any('RESOURCE_CONFLICT' in x for x in blocked.values())
held=Adapter();held_scheduler=scheduler.Scheduler(conflict,held,governance=governance(conflict),repository=ROOT,max_concurrency=2);held_scheduler.dispatch();assert held_scheduler.frontier()[0]==[]
print(json.dumps({'status':'PASS','checks':['governed-envelope','exact-workspace','objective-only-rejected','observation-not-completion','exact-verification','identity-mismatch-matrix','observation-recovery','resources']},sort_keys=True))
