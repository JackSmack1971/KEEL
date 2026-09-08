"""Desired-state reconciliation and bounded WorkUnit scheduling.

This module coordinates canonical ChangeGraph work; it does not execute effects,
grant authority, run an agent runtime, or land a change.  Adapters are the only
execution boundary and may be replaced by Codex/runtime integrations.
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
import semantic_kernel as sk


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
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
    STALE = "STALE"


@dataclass(frozen=True)
class DispatchResult:
    outcome: str
    evidence_fingerprint: str = ""
    strategy_fingerprint: str = ""
    failure_class: FailureClass | str | None = None
    message: str = ""
    artifacts: tuple[str, ...] = ()


class SchedulerAdapter(Protocol):
    def dispatch(self, unit: "UnitView", workspace_id: str) -> DispatchResult: ...


@dataclass
class WorkRecord:
    status: WorkStatus = WorkStatus.PENDING
    workspace_id: str = ""
    dispatch_key: str = ""
    attempts: int = 0
    retry_count: int = 0
    last_seen: float = 0.0
    last_evidence: str = ""
    last_strategy: str = ""
    failure_class: str = ""
    message: str = ""
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status.value, "workspace_id": self.workspace_id,
                "dispatch_key": self.dispatch_key, "attempts": self.attempts,
                "retry_count": self.retry_count, "last_seen": self.last_seen,
                "last_evidence": self.last_evidence, "last_strategy": self.last_strategy,
                "failure_class": self.failure_class, "message": self.message,
                "artifacts": sorted(set(self.artifacts))}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "WorkRecord":
        try: status = WorkStatus(value["status"])
        except (KeyError, ValueError) as exc: raise ValueError("invalid scheduler work status") from exc
        return cls(status=status, workspace_id=str(value.get("workspace_id", "")),
                   dispatch_key=str(value.get("dispatch_key", "")), attempts=int(value.get("attempts", 0)),
                   retry_count=int(value.get("retry_count", 0)), last_seen=float(value.get("last_seen", 0.0)),
                   last_evidence=str(value.get("last_evidence", "")), last_strategy=str(value.get("last_strategy", "")),
                   failure_class=str(value.get("failure_class", "")), message=str(value.get("message", "")),
                   artifacts=list(value.get("artifacts", [])))


@dataclass
class SchedulerState:
    graph_digest: str = ""
    records: dict[str, WorkRecord] = field(default_factory=dict)
    tick: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"schema": "keel.scheduler-state", "schema_version": 1,
                "graph_digest": self.graph_digest, "tick": self.tick,
                "records": {key: self.records[key].to_dict() for key in sorted(self.records)}}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SchedulerState":
        if value.get("schema") != "keel.scheduler-state" or value.get("schema_version") != 1:
            raise ValueError("unsupported scheduler state")
        records = value.get("records", {})
        if not isinstance(records, Mapping): raise ValueError("scheduler records must be an object")
        return cls(graph_digest=str(value.get("graph_digest", "")), tick=int(value.get("tick", 0)),
                   records={str(k): WorkRecord.from_dict(v) for k, v in records.items()})


class StateStore:
    def __init__(self, path: Path): self.path = path
    def load(self) -> SchedulerState:
        if not self.path.exists(): return SchedulerState()
        try: return SchedulerState.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc: raise ValueError("invalid persisted scheduler state") from exc
    def save(self, state: SchedulerState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(state.to_dict(), sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        temporary.replace(self.path)


@dataclass(frozen=True)
class UnitView:
    identity: str
    objective: str
    attributes: Mapping[str, Any]

    @property
    def claims(self) -> tuple[tuple[str, str], ...]:
        raw = self.attributes.get("resource_claims", ())
        result = []
        for claim in raw:
            if isinstance(claim, Mapping): result.append((str(claim.get("resource", "")), str(claim.get("mode", "EXCLUSIVE"))))
        return tuple(sorted(result))

    @property
    def writer(self) -> bool:
        return any(mode == "EXCLUSIVE" for _, mode in self.claims) or bool(self.attributes.get("write_worktree"))

    @property
    def workspace_id(self) -> str:
        value = self.attributes.get("workspace_id", self.identity)
        return str(value)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Scheduler:
    def __init__(self, graph: Mapping[str, Any], adapter: SchedulerAdapter | None = None,
                 state: SchedulerState | None = None, *, max_concurrency: int = 1,
                 stale_after: float = 3600.0, clock: Callable[[], float] = time.time):
        errors = change_graph.validate(graph)
        if errors: raise ValueError("invalid change graph: " + "; ".join(errors))
        if type(max_concurrency) is not int or max_concurrency < 1: raise ValueError("max_concurrency must be positive")
        self.graph = graph; self.adapter = adapter; self.max_concurrency = max_concurrency
        self.stale_after = stale_after; self.clock = clock
        self.units = {record.identity: UnitView(record.identity, record.objective, record.attributes)
                      for record in (sk.decode(raw) for raw in graph["records"]) if isinstance(record, sk.WorkUnit)}
        self.edges = [(r.source_id, r.target_id, r.edge_type) for r in (sk.decode(raw) for raw in graph["records"]) if isinstance(r, sk.Edge)]
        self.state = state or SchedulerState(graph_digest=_digest(graph))
        if self.state.graph_digest and self.state.graph_digest != _digest(graph): raise ValueError("scheduler state belongs to another graph")
        self.state.graph_digest = _digest(graph)
        for identity, unit in self.units.items(): self.state.records.setdefault(identity, WorkRecord(workspace_id=unit.workspace_id))

    def _dependencies(self, identity: str) -> set[str]:
        return {target for source, target, kind in self.edges if source == identity and kind in {"HARD_DEPENDENCY", "ORDERING_ONLY", "ARTIFACT", "REQUIRES_REVIEW", "REQUIRES_VERIFICATION", "REQUIRES_EVIDENCE"}}

    def _resource_free(self, unit: UnitView, active: list[UnitView]) -> bool:
        for other in active:
            if unit.writer and other.workspace_id == unit.workspace_id and other.writer: return False
            for resource, mode in unit.claims:
                for other_resource, other_mode in other.claims:
                    if resource == other_resource or resource.startswith(other_resource + "/") or other_resource.startswith(resource + "/"):
                        if mode == "EXCLUSIVE" or other_mode == "EXCLUSIVE": return False
        return True

    def _mark_stale(self) -> None:
        now = self.clock()
        for record in self.state.records.values():
            if record.status == WorkStatus.RUNNING and self.stale_after >= 0 and now - record.last_seen > self.stale_after:
                record.status = WorkStatus.STALE
                record.message = "dispatch heartbeat expired"

    def reconcile(self, actual: Mapping[str, Any] | None = None) -> dict[str, Any]:
        self.state.tick += 1; self._mark_stale()
        actual = actual or {}
        for identity, value in actual.items():
            if identity not in self.state.records: continue
            status = value.get("status") if isinstance(value, Mapping) else value
            if status == WorkStatus.COMPLETE.value or status == "COMPLETE": self.state.records[identity].status = WorkStatus.COMPLETE
            if isinstance(value, Mapping) and value.get("artifacts"): self.state.records[identity].artifacts = sorted(set(value["artifacts"]))
        runnable, blocked = self.frontier()
        return {"status": "COMPLETE" if all(r.status == WorkStatus.COMPLETE for r in self.state.records.values()) else ("READY" if runnable else "BLOCKED"),
                "runnable": runnable, "blocked": blocked, "tick": self.state.tick}

    def frontier(self) -> tuple[list[str], dict[str, list[str]]]:
        complete = {identity for identity, record in self.state.records.items() if record.status == WorkStatus.COMPLETE}
        active = [self.units[i] for i, r in self.state.records.items() if r.status == WorkStatus.RUNNING]
        slots = max(0, self.max_concurrency - len(active)); runnable: list[str] = []; blocked: dict[str, list[str]] = {}
        for identity in sorted(self.units):
            record = self.state.records[identity]; reasons: list[str] = []
            if record.status in {WorkStatus.COMPLETE, WorkStatus.RUNNING, WorkStatus.ESCALATED}: continue
            missing = sorted(self._dependencies(identity) - complete)
            if missing: reasons.append("dependencies:" + ",".join(missing))
            if not self._resource_free(self.units[identity], active): reasons.append("RESOURCE_CONFLICT")
            if reasons: blocked[identity] = reasons; continue
            if len(runnable) < slots: runnable.append(identity); active.append(self.units[identity])
            else: blocked[identity] = ["BOUNDED_CONCURRENCY"]
        return runnable, blocked

    def dispatch(self) -> dict[str, Any]:
        if self.adapter is None: raise ValueError("dispatch requires an injected adapter")
        report = self.reconcile(); dispatched: list[str] = []
        for identity in report["runnable"]:
            record = self.state.records[identity]; unit = self.units[identity]
            key = _digest({"unit": identity, "graph": self.state.graph_digest, "workspace": unit.workspace_id})
            if record.dispatch_key == key and record.status in {WorkStatus.RUNNING, WorkStatus.COMPLETE}: continue
            record.dispatch_key = key; record.workspace_id = unit.workspace_id; record.attempts += 1; record.last_seen = self.clock(); record.status = WorkStatus.RUNNING
            dispatched.append(identity)
            try: result = self.adapter.dispatch(unit, unit.workspace_id)
            except Exception as exc: result = DispatchResult("FAILED", failure_class=FailureClass.AGENT_FAILURE, message=str(exc))
            previous_evidence, previous_strategy = record.last_evidence, record.last_strategy
            record.last_seen = self.clock(); record.last_evidence = result.evidence_fingerprint; record.last_strategy = result.strategy_fingerprint
            record.artifacts = sorted(set(record.artifacts).union(result.artifacts)); outcome = result.outcome.upper()
            if outcome == "COMPLETE": record.status = WorkStatus.COMPLETE
            elif outcome in {"RUNNING", "ACCEPTED"}: record.status = WorkStatus.RUNNING
            else: self._failure(record, unit, result, previous_evidence, previous_strategy)
        return {"dispatched": dispatched, **self.reconcile()}

    def _failure(self, record: WorkRecord, unit: UnitView, result: DispatchResult, previous_evidence: str, previous_strategy: str) -> None:
        classification = result.failure_class.value if isinstance(result.failure_class, FailureClass) else str(result.failure_class or FailureClass.UNKNOWN.value)
        record.failure_class = classification; record.message = result.message
        policy = unit.attributes.get("retry_policy", {}); max_attempts = int(policy.get("max_attempts", 1)) if isinstance(policy, Mapping) else 1
        changed = (previous_evidence != result.evidence_fingerprint or previous_strategy != result.strategy_fingerprint)
        retryable = classification not in {FailureClass.SPEC_DEFECT.value, FailureClass.AUTHORIZATION_BLOCK.value, FailureClass.INTEGRATION_CONFLICT.value}
        if retryable and record.retry_count < max_attempts and changed:
            record.retry_count += 1; record.status = WorkStatus.PENDING
        elif retryable and not changed and record.attempts > 1:
            record.status = WorkStatus.ESCALATED
        else: record.status = WorkStatus.ESCALATED if not retryable or record.retry_count >= max_attempts else WorkStatus.FAILED


def load_graph(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def frontier_report(graph: Mapping[str, Any], state: SchedulerState | None = None, max_concurrency: int = 1) -> dict[str, Any]:
    scheduler = Scheduler(graph, state=state, max_concurrency=max_concurrency)
    report = scheduler.reconcile()
    return {**report, "read_only": True}
