"""Governed desired-state reconciliation and bounded WorkUnit scheduling.

KEEL constructs immutable dispatch contracts and evaluates exact-subject evidence;
injected Codex adapters only execute envelopes and report observations.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

import change_graph
import evidence_system
import git_proof
import semantic_kernel as sk


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _required(label: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty")
    return value


class FailureClass(str, Enum):
    IMPLEMENTATION_DEFECT = "IMPLEMENTATION_DEFECT"
    SPEC_DEFECT = "SPEC_DEFECT"
    ENVIRONMENT_FAILURE = "ENVIRONMENT_FAILURE"
    VERIFIER_FAILURE = "VERIFIER_FAILURE"
    DEPENDENCY_DRIFT = "DEPENDENCY_DRIFT"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    AUTHORIZATION_BLOCK = "AUTHORIZATION_BLOCK"
    INTEGRATION_CONFLICT = "INTEGRATION_CONFLICT"
    AGENT_FAILURE = "AGENT_FAILURE"
    UNKNOWN = "UNKNOWN"


class WorkStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    STALE = "STALE"


@dataclass(frozen=True)
class WorkspaceBinding:
    identity: str
    path: str
    subject: str

    def __post_init__(self) -> None:
        _required("workspace identity", self.identity); _required("workspace path", self.path); _required("workspace subject", self.subject)
        if not Path(self.path).is_absolute(): raise ValueError("workspace path must be absolute")


@dataclass(frozen=True)
class DispatchEnvelope:
    change_id: str
    work_unit_id: str
    base_commit: str
    subject: str
    workspace: WorkspaceBinding
    intent_digest: str
    graph_digest: str
    authority_digest: str
    runtime_profile_id: str
    runtime_profile_digest: str
    context_id: str
    bounded_context: str
    objective: str
    requirements: tuple[str, ...]
    scope: tuple[str, ...]
    resource_claims: tuple[tuple[str, str], ...]
    evidence_requirements: tuple[str, ...]
    evidence_plan_digest: str
    stop_protocol: str
    completion_protocol: str

    def __post_init__(self) -> None:
        for label in ("change_id", "work_unit_id", "base_commit", "subject", "intent_digest", "graph_digest", "authority_digest", "runtime_profile_id", "runtime_profile_digest", "context_id", "bounded_context", "objective", "evidence_plan_digest", "stop_protocol", "completion_protocol"):
            _required(label, getattr(self, label))
        if not self.requirements: raise ValueError("applicable requirements must be non-empty")
        if not self.scope: raise ValueError("declared scope must be non-empty")
        if not self.evidence_requirements: raise ValueError("evidence requirements must be non-empty")
        if self.workspace.subject != self.subject: raise ValueError("workspace subject does not match dispatch subject")

    def to_dict(self) -> dict[str, Any]:
        return {"schema":"keel.dispatch-envelope/v1", "change_id":self.change_id, "work_unit_id":self.work_unit_id,
                "base_commit":self.base_commit, "subject":self.subject,
                "workspace":{"identity":self.workspace.identity,"path":self.workspace.path,"subject":self.workspace.subject},
                "intent_digest":self.intent_digest,"graph_digest":self.graph_digest,"authority_digest":self.authority_digest,
                "runtime_profile":{"identity":self.runtime_profile_id,"digest":self.runtime_profile_digest},
                "context":{"identity":self.context_id,"content":self.bounded_context},"objective":self.objective,
                "requirements":list(self.requirements),"scope":list(self.scope),
                "resource_claims":[{"resource":r,"mode":m} for r,m in self.resource_claims],
                "evidence_requirements":list(self.evidence_requirements),"evidence_plan_digest":self.evidence_plan_digest,
                "protocol":{"stop":self.stop_protocol,"completion":self.completion_protocol}}

    @property
    def identity(self) -> str: return _digest(self.to_dict())


@dataclass(frozen=True)
class ExecutionObservation:
    envelope_id: str
    change_id: str
    work_unit_id: str
    subject: str
    workspace_id: str
    workspace_path: str
    runtime_profile_id: str
    runtime_profile_digest: str
    thread_id: str
    turn_id: str
    outcome: str
    started_at: float
    completed_at: float
    events: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for label in ("envelope_id","change_id","work_unit_id","subject","workspace_id","workspace_path","runtime_profile_id","runtime_profile_digest","thread_id","turn_id","outcome"):
            _required(label, getattr(self,label))
        if self.completed_at < self.started_at: raise ValueError("observation timestamps are reversed")

    def to_dict(self) -> dict[str, Any]: return {"envelope_id":self.envelope_id,"change_id":self.change_id,"work_unit_id":self.work_unit_id,"subject":self.subject,"workspace_id":self.workspace_id,"workspace_path":self.workspace_path,"runtime_profile_id":self.runtime_profile_id,"runtime_profile_digest":self.runtime_profile_digest,"thread_id":self.thread_id,"turn_id":self.turn_id,"outcome":self.outcome,"started_at":self.started_at,"completed_at":self.completed_at,"events":list(self.events),"artifacts":list(self.artifacts)}
    @classmethod
    def from_dict(cls, v: Mapping[str,Any]) -> "ExecutionObservation": return cls(**{**dict(v),"events":tuple(v.get("events",())),"artifacts":tuple(v.get("artifacts",()))})


@dataclass(frozen=True)
class VerificationDecision:
    passed: bool
    change_id: str
    work_unit_id: str
    subject: str
    workspace_id: str
    workspace_path: str
    intent_digest: str
    graph_digest: str
    authority_digest: str
    runtime_profile_digest: str
    evidence_plan_digest: str
    plan: Mapping[str, Any]
    receipts: tuple[Mapping[str, Any], ...]
    evidence_requirements: tuple[Mapping[str, Any], ...]
    evidence_subject: Mapping[str, Any]


@dataclass(frozen=True)
class GovernanceContext:
    change_id: str; base_commit: str; subject: str; intent_digest: str; authority_digest: str
    runtime_profile_id: str; runtime_profile_digest: str; context_id: str; bounded_context: str
    requirements: tuple[str,...]; scope: tuple[str,...]; evidence_requirements: tuple[str,...]
    evidence_plan_digest: str; workspace_paths: Mapping[str,str]
    stop_protocol: str = "Stop on identity drift, authorization failure, scope violation, or unverifiable state."
    completion_protocol: str = "Report execution only; KEEL exact-subject evidence evaluation alone establishes completion."


@dataclass(frozen=True)
class DispatchResult:
    outcome: str
    evidence_fingerprint: str = ""
    strategy_fingerprint: str = ""
    failure_class: FailureClass | str | None = None
    message: str = ""
    artifacts: tuple[str, ...] = ()
    observation: ExecutionObservation | None = None


class SchedulerAdapter(Protocol):
    def dispatch(self, envelope: DispatchEnvelope) -> DispatchResult: ...


def resolve_workspace(repository: Path, workspace_id: str, intended_path: str, subject: str) -> WorkspaceBinding:
    repository = repository.resolve(); intended = Path(intended_path).resolve()
    try:
        raw = git_proof.run(repository, ["worktree","list","--porcelain"]).stdout
    except Exception as exc: raise ValueError("workspace registry could not be resolved") from exc
    registered = {Path(line[9:]).resolve() for line in raw.splitlines() if line.startswith("worktree ")}
    if intended not in registered: raise ValueError("workspace is not an exact registered Git worktree")
    try:
        root = git_proof.repository_root(intended); actual = git_proof.head_commit(intended)
    except RuntimeError as exc: raise ValueError("workspace Git identity could not be resolved") from exc
    if root != intended or actual != subject: raise ValueError("workspace path or subject does not match governed dispatch")
    return WorkspaceBinding(workspace_id, str(intended), actual)


@dataclass
class WorkRecord:
    status: WorkStatus = WorkStatus.PENDING; workspace_id: str = ""; workspace_path: str = ""; dispatch_key: str = ""; envelope_id: str = ""
    attempts: int = 0; retry_count: int = 0; last_seen: float = 0.0; last_evidence: str = ""; last_strategy: str = ""; failure_class: str = ""; message: str = ""
    artifacts: list[str] = field(default_factory=list); observations: list[ExecutionObservation] = field(default_factory=list); verification_receipt: str = ""
    def to_dict(self) -> dict[str,Any]: return {"status":self.status.value,"workspace_id":self.workspace_id,"workspace_path":self.workspace_path,"dispatch_key":self.dispatch_key,"envelope_id":self.envelope_id,"attempts":self.attempts,"retry_count":self.retry_count,"last_seen":self.last_seen,"last_evidence":self.last_evidence,"last_strategy":self.last_strategy,"failure_class":self.failure_class,"message":self.message,"artifacts":sorted(set(self.artifacts)),"observations":[o.to_dict() for o in self.observations],"verification_receipt":self.verification_receipt}
    @classmethod
    def from_dict(cls,v:Mapping[str,Any])->"WorkRecord":
        try: status=WorkStatus(v["status"])
        except (KeyError,ValueError) as exc: raise ValueError("invalid scheduler work status") from exc
        return cls(status=status,workspace_id=str(v.get("workspace_id","")),workspace_path=str(v.get("workspace_path","")),dispatch_key=str(v.get("dispatch_key","")),envelope_id=str(v.get("envelope_id","")),attempts=int(v.get("attempts",0)),retry_count=int(v.get("retry_count",0)),last_seen=float(v.get("last_seen",0)),last_evidence=str(v.get("last_evidence","")),last_strategy=str(v.get("last_strategy","")),failure_class=str(v.get("failure_class","")),message=str(v.get("message","")),artifacts=list(v.get("artifacts",[])),observations=[ExecutionObservation.from_dict(x) for x in v.get("observations",[])],verification_receipt=str(v.get("verification_receipt","")))


@dataclass
class SchedulerState:
    graph_digest: str=""; records: dict[str,WorkRecord]=field(default_factory=dict); tick:int=0
    def to_dict(self)->dict[str,Any]: return {"schema":"keel.scheduler-state","schema_version":2,"graph_digest":self.graph_digest,"tick":self.tick,"records":{k:self.records[k].to_dict() for k in sorted(self.records)}}
    @classmethod
    def from_dict(cls,v:Mapping[str,Any])->"SchedulerState":
        if v.get("schema")!="keel.scheduler-state" or v.get("schema_version") not in {1,2}: raise ValueError("unsupported scheduler state")
        records=v.get("records",{});
        if not isinstance(records,Mapping): raise ValueError("scheduler records must be an object")
        return cls(str(v.get("graph_digest","")),{str(k):WorkRecord.from_dict(x) for k,x in records.items()},int(v.get("tick",0)))


class StateStore:
    def __init__(self,path:Path): self.path=path
    def load(self)->SchedulerState:
        if not self.path.exists(): return SchedulerState()
        try:return SchedulerState.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError,json.JSONDecodeError,ValueError,TypeError) as exc:raise ValueError("invalid persisted scheduler state") from exc
    def save(self,state:SchedulerState)->None:
        self.path.parent.mkdir(parents=True,exist_ok=True); temporary=self.path.with_suffix(self.path.suffix+".tmp"); temporary.write_text(json.dumps(state.to_dict(),sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8"); temporary.replace(self.path)


@dataclass(frozen=True)
class UnitView:
    identity:str; objective:str; attributes:Mapping[str,Any]
    @property
    def claims(self)->tuple[tuple[str,str],...]: return tuple(sorted((str(x.get("resource","")),str(x.get("mode","EXCLUSIVE"))) for x in self.attributes.get("resource_claims",()) if isinstance(x,Mapping)))
    @property
    def writer(self)->bool:return any(m=="EXCLUSIVE" for _,m in self.claims) or bool(self.attributes.get("write_worktree"))
    @property
    def workspace_id(self)->str:return str(self.attributes.get("workspace_id",self.identity))


class Scheduler:
    def __init__(self,graph:Mapping[str,Any],adapter:SchedulerAdapter|None=None,state:SchedulerState|None=None,*,governance:GovernanceContext|None=None,repository:Path|None=None,max_concurrency:int=1,stale_after:float=3600.0,clock:Callable[[],float]=time.time):
        errors=change_graph.validate(graph)
        if errors:raise ValueError("invalid change graph: "+"; ".join(errors))
        if type(max_concurrency) is not int or max_concurrency<1:raise ValueError("max_concurrency must be positive")
        self.graph=graph;self.adapter=adapter;self.governance=governance;self.repository=repository;self.max_concurrency=max_concurrency;self.stale_after=stale_after;self.clock=clock
        self.units={r.identity:UnitView(r.identity,r.objective,r.attributes) for r in (sk.decode(x) for x in graph["records"]) if isinstance(r,sk.WorkUnit)}
        self.edges=[(r.source_id,r.target_id,r.edge_type) for r in (sk.decode(x) for x in graph["records"]) if isinstance(r,sk.Edge)]
        self.state=state or SchedulerState(graph_digest=_digest(graph))
        if self.state.graph_digest and self.state.graph_digest!=_digest(graph):raise ValueError("scheduler state belongs to another graph")
        self.state.graph_digest=_digest(graph)
        for i,u in self.units.items():self.state.records.setdefault(i,WorkRecord(workspace_id=u.workspace_id))
    def _dependencies(self,i):return {t for s,t,k in self.edges if s==i and k in {"HARD_DEPENDENCY","ORDERING_ONLY","ARTIFACT","REQUIRES_REVIEW","REQUIRES_VERIFICATION","REQUIRES_EVIDENCE"}}
    def _resource_free(self,u,active):
        for o in active:
            if u.writer and o.workspace_id==u.workspace_id and o.writer:return False
            for r,m in u.claims:
                for rr,mm in o.claims:
                    if (r==rr or r.startswith(rr+"/") or rr.startswith(r+"/")) and (m=="EXCLUSIVE" or mm=="EXCLUSIVE"):return False
        return True
    def _mark_stale(self):
        now=self.clock()
        for r in self.state.records.values():
            if r.status==WorkStatus.RUNNING and self.stale_after>=0 and now-r.last_seen>self.stale_after:r.status=WorkStatus.STALE;r.message="dispatch heartbeat expired"
    def reconcile(self,actual:Mapping[str,Any]|None=None):
        self.state.tick+=1;self._mark_stale()
        # External transport state may update artifacts, but can never assert COMPLETE.
        for i,v in (actual or {}).items():
            if i in self.state.records and isinstance(v,Mapping) and v.get("artifacts"):self.state.records[i].artifacts=sorted(set(v["artifacts"]))
        runnable,blocked=self.frontier(); return {"status":"COMPLETE" if all(r.status==WorkStatus.COMPLETE for r in self.state.records.values()) else ("READY" if runnable else "BLOCKED"),"runnable":runnable,"blocked":blocked,"tick":self.state.tick}
    def frontier(self):
        complete={i for i,r in self.state.records.items() if r.status==WorkStatus.COMPLETE};active=[self.units[i] for i,r in self.state.records.items() if r.status in {WorkStatus.RUNNING,WorkStatus.AWAITING_VERIFICATION}];slots=max(0,self.max_concurrency-len(active));runnable=[];blocked={}
        for i in sorted(self.units):
            r=self.state.records[i];reasons=[]
            if r.status in {WorkStatus.COMPLETE,WorkStatus.RUNNING,WorkStatus.AWAITING_VERIFICATION,WorkStatus.ESCALATED}:continue
            missing=sorted(self._dependencies(i)-complete)
            if missing:reasons.append("dependencies:"+",".join(missing))
            if not self._resource_free(self.units[i],active):reasons.append("RESOURCE_CONFLICT")
            if reasons:blocked[i]=reasons
            elif len(runnable)<slots:runnable.append(i);active.append(self.units[i])
            else:blocked[i]=["BOUNDED_CONCURRENCY"]
        return runnable,blocked
    def _envelope(self,u:UnitView)->DispatchEnvelope:
        if self.governance is None or self.repository is None:raise ValueError("governed dispatch requires GovernanceContext and repository")
        g=self.governance
        if g.subject!=git_proof.head_commit(self.repository):raise ValueError("governed subject is stale")
        if git_proof.resolve_commit(self.repository,g.base_commit)!=g.base_commit:raise ValueError("governed base commit is not canonical")
        if git_proof.run(self.repository,["merge-base","--is-ancestor",g.base_commit,g.subject],check=False).returncode:raise ValueError("governed base is not an ancestor of subject")
        path=g.workspace_paths.get(u.workspace_id)
        if not path:raise ValueError("workspace identity is unresolved")
        workspace=resolve_workspace(self.repository,u.workspace_id,path,g.subject)
        return DispatchEnvelope(g.change_id,u.identity,g.base_commit,g.subject,workspace,g.intent_digest,self.state.graph_digest,g.authority_digest,g.runtime_profile_id,g.runtime_profile_digest,g.context_id,g.bounded_context,u.objective,g.requirements,g.scope,u.claims,g.evidence_requirements,g.evidence_plan_digest,g.stop_protocol,g.completion_protocol)
    def dispatch(self):
        if self.adapter is None:raise ValueError("dispatch requires an injected adapter")
        report=self.reconcile();dispatched=[]
        for i in report["runnable"]:
            r=self.state.records[i];u=self.units[i]
            try: envelope=self._envelope(u)
            except Exception as exc:self._failure(r,u,DispatchResult("FAILED",failure_class=FailureClass.AUTHORIZATION_BLOCK,message=str(exc)),r.last_evidence,r.last_strategy);continue
            key=envelope.identity
            if r.dispatch_key==key and r.status in {WorkStatus.RUNNING,WorkStatus.AWAITING_VERIFICATION,WorkStatus.COMPLETE}:continue
            r.dispatch_key=key;r.envelope_id=envelope.identity;r.workspace_id=u.workspace_id;r.workspace_path=envelope.workspace.path;r.attempts+=1;r.last_seen=self.clock();r.status=WorkStatus.RUNNING;dispatched.append(i)
            try:result=self.adapter.dispatch(envelope)
            except Exception as exc:result=DispatchResult("FAILED",failure_class=FailureClass.AGENT_FAILURE,message=str(exc))
            pe,ps=r.last_evidence,r.last_strategy;r.last_seen=self.clock();r.last_evidence=result.evidence_fingerprint;r.last_strategy=result.strategy_fingerprint;r.artifacts=sorted(set(r.artifacts).union(result.artifacts));outcome=result.outcome.upper()
            if outcome=="OBSERVED" and result.observation:
                observation=result.observation
                observed=(observation.envelope_id,observation.change_id,observation.work_unit_id,observation.subject,observation.workspace_id,observation.workspace_path,observation.runtime_profile_id,observation.runtime_profile_digest)
                expected=(envelope.identity,envelope.change_id,envelope.work_unit_id,envelope.subject,envelope.workspace.identity,envelope.workspace.path,envelope.runtime_profile_id,envelope.runtime_profile_digest)
                if observed!=expected:self._failure(r,u,DispatchResult("FAILED",failure_class=FailureClass.DEPENDENCY_DRIFT,message="observation identity mismatch"),pe,ps)
                else:r.observations.append(observation);r.status=WorkStatus.AWAITING_VERIFICATION;r.message="execution observed; exact-subject verification required"
            elif outcome in {"RUNNING","ACCEPTED"}:r.status=WorkStatus.RUNNING
            else:self._failure(r,u,result,pe,ps)
        return {"dispatched":dispatched,**self.reconcile()}
    def apply_verification(self,identity:str,decision:VerificationDecision)->None:
        if identity not in self.units or self.governance is None:raise ValueError("unknown or ungovened WorkUnit")
        r=self.state.records[identity];g=self.governance
        if r.status!=WorkStatus.AWAITING_VERIFICATION:raise ValueError("WorkUnit is not awaiting verification")
        expected=(True,g.change_id,identity,g.subject,r.workspace_id,r.workspace_path,g.intent_digest,self.state.graph_digest,g.authority_digest,g.runtime_profile_digest,g.evidence_plan_digest)
        actual=(decision.passed,decision.change_id,decision.work_unit_id,decision.subject,decision.workspace_id,decision.workspace_path,decision.intent_digest,decision.graph_digest,decision.authority_digest,decision.runtime_profile_digest,decision.evidence_plan_digest)
        if actual!=expected or decision.plan.get("plan_digest")!=g.evidence_plan_digest:raise ValueError("verification decision is stale, mismatched, or unsuccessful")
        evaluation=evidence_system.evaluate(dict(decision.plan),[dict(x) for x in decision.receipts],[dict(x) for x in decision.evidence_requirements],dict(decision.evidence_subject),g.intent_digest)
        if evaluation.get("status")!="PASS":raise ValueError("KEEL exact-subject evidence evaluation did not pass")
        r.verification_receipt=_digest([dict(x) for x in decision.receipts]);r.status=WorkStatus.COMPLETE;r.message="exact-subject KEEL evidence evaluation passed"
    def _failure(self,r,u,result,previous_evidence,previous_strategy):
        classification=result.failure_class.value if isinstance(result.failure_class,FailureClass) else str(result.failure_class or FailureClass.UNKNOWN.value);r.failure_class=classification;r.message=result.message;policy=u.attributes.get("retry_policy",{});max_attempts=int(policy.get("max_attempts",1)) if isinstance(policy,Mapping) else 1;changed=previous_evidence!=result.evidence_fingerprint or previous_strategy!=result.strategy_fingerprint;retryable=classification not in {FailureClass.SPEC_DEFECT.value,FailureClass.AUTHORIZATION_BLOCK.value,FailureClass.INTEGRATION_CONFLICT.value}
        if retryable and r.retry_count<max_attempts and changed:r.retry_count+=1;r.status=WorkStatus.PENDING
        elif retryable and not changed and r.attempts>1:r.status=WorkStatus.ESCALATED
        else:r.status=WorkStatus.ESCALATED if not retryable or r.retry_count>=max_attempts else WorkStatus.FAILED


def load_graph(path:Path)->dict[str,Any]:return json.loads(path.read_text(encoding="utf-8"))
def frontier_report(graph:Mapping[str,Any],state:SchedulerState|None=None,max_concurrency:int=1)->dict[str,Any]:
    report=Scheduler(graph,state=state,max_concurrency=max_concurrency).reconcile();return {**report,"read_only":True}
