"""Small, fail-closed adapter for the documented local Codex app-server stdio API.

This is a transport adapter, not an agent runtime.  It deliberately exposes only
the stable operations needed by KEEL and never handles API credentials.
"""
from __future__ import annotations

import json
import queue
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

import runtime_authorization


class AdapterError(RuntimeError):
    """Base class for transport, protocol, compatibility, and lifecycle errors."""


class MalformedMessage(AdapterError):
    pass


class ProcessExited(AdapterError):
    pass


class RequestTimeout(AdapterError):
    pass


class CompatibilityMismatch(AdapterError):
    pass


@dataclass(frozen=True)
class RuntimeObservation:
    status: str
    reason: str
    initialize: Mapping[str, Any] = field(default_factory=dict)
    account: Mapping[str, Any] = field(default_factory=dict)
    protocol_version: str | None = None
    capability_status: str = "UNKNOWN"


@dataclass(frozen=True)
class TurnObservation:
    request: Mapping[str, Any]
    events: tuple[Mapping[str, Any], ...]
    completed: Mapping[str, Any]


class ProcessLike(Protocol):
    stdin: Any
    stdout: Any
    returncode: int | None

    def poll(self) -> int | None: ...
    def wait(self, timeout: float | None = None) -> int: ...
    def terminate(self) -> None: ...
    def kill(self) -> None: ...


class CodexAppServerAdapter:
    """Drive one local app-server connection with bounded, deterministic reads."""

    CLIENT_INFO = {"name": "keel", "title": "KEEL", "version": "1.0"}
    STABLE_METHODS = frozenset({"initialize", "account/read", "thread/start", "thread/resume", "turn/start"})

    def __init__(self, process: ProcessLike, *, request_timeout: float = 10.0,
                 runtime_profile: Any | None = None,
                 cost_observations: Mapping[str, Any] | None = None):
        if request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        self.process = process
        self.request_timeout = request_timeout
        self.runtime_profile = runtime_profile
        self.cost_observations = cost_observations
        self._next_id = 1
        self._messages: queue.Queue[object] = queue.Queue()
        self._notifications: list[Mapping[str, Any]] = []
        self._closed = False
        self._initialized = False
        self._reader = threading.Thread(target=self._read_loop, name="keel-codex-reader", daemon=True)
        self._reader.start()

    @classmethod
    def launch(cls, command: Sequence[str] = ("codex", "app-server", "--listen", "stdio://"), *, timeout: float = 10.0, env: Mapping[str, str] | None = None) -> "CodexAppServerAdapter":
        command = tuple(command)
        if command and command[0] == "codex":
            resolved = shutil.which("codex")
            if resolved is None:
                raise AdapterError("UNVERIFIED_RUNTIME: codex executable is not installed or reachable")
            command = (resolved, *command[1:])
        try:
            process = subprocess.Popen(list(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                                       bufsize=1, env=dict(env) if env is not None else None)
        except (OSError, ValueError) as exc:
            raise AdapterError(f"UNVERIFIED_RUNTIME: app-server is unavailable: {exc}") from exc
        return cls(process, request_timeout=timeout)

    def _read_loop(self) -> None:
        try:
            for line in self.process.stdout:
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except (json.JSONDecodeError, TypeError) as exc:
                    self._messages.put(MalformedMessage("malformed or partial JSONL frame"))
                    self._messages.put(exc)
                    return
                if not isinstance(value, dict):
                    self._messages.put(MalformedMessage("JSON-RPC frame must be an object"))
                    return
                self._messages.put(value)
        except (OSError, ValueError) as exc:
            self._messages.put(ProcessExited(str(exc)))
        finally:
            self._messages.put(ProcessExited(f"app-server exited with code {self.process.poll()}"))

    def _send(self, message: Mapping[str, Any]) -> None:
        if self._closed or self.process.poll() is not None:
            raise ProcessExited("app-server is not running")
        try:
            self.process.stdin.write(json.dumps(dict(message), separators=(",", ":")) + "\n")
            self.process.stdin.flush()
        except (OSError, ValueError, AttributeError) as exc:
            raise ProcessExited("could not write to app-server") from exc

    def _request(self, method: str, params: Mapping[str, Any] | None = None, *, timeout: float | None = None) -> Mapping[str, Any]:
        if method not in self.STABLE_METHODS:
            raise CompatibilityMismatch(f"unsupported non-load-bearing method: {method}")
        request_id = self._next_id
        self._next_id += 1
        self._send({"id": request_id, "method": method, **({"params": dict(params)} if params is not None else {})})
        deadline = time.monotonic() + (self.request_timeout if timeout is None else timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RequestTimeout(f"timed out waiting for {method}")
            try:
                message = self._messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise RequestTimeout(f"timed out waiting for {method}") from exc
            if isinstance(message, (AdapterError, Exception)):
                raise message
            if not isinstance(message, Mapping):
                raise MalformedMessage("internal message queue contained a non-object")
            if "id" not in message:
                if "method" not in message or not isinstance(message.get("method"), str):
                    raise MalformedMessage("notification lacks method")
                self._notifications.append(message)
                continue
            if message.get("id") != request_id:
                raise MalformedMessage("response id did not match the outstanding request")
            if "error" in message:
                error = message["error"]
                raise CompatibilityMismatch(f"{method} rejected by app-server: {error}")
            result = message.get("result")
            if not isinstance(result, Mapping):
                raise MalformedMessage(f"{method} response lacks an object result")
            return result

    def initialize_and_inspect(self) -> RuntimeObservation:
        try:
            initialized = self._request("initialize", {"clientInfo": dict(self.CLIENT_INFO)})
            self._send({"method": "initialized", "params": {}})
            account = self._request("account/read", {"refreshToken": False})
            if not isinstance(account.get("account"), (Mapping, type(None))) or not isinstance(account.get("requiresOpenaiAuth"), bool):
                raise MalformedMessage("account/read response has undocumented shape")
            required = ("userAgent", "platformFamily", "platformOs")
            if not all(key in initialized for key in required):
                raise CompatibilityMismatch("initialize response lacks documented runtime metadata")
            self._initialized = True
            return RuntimeObservation("PASS", "documented initialization and account inspection completed",
                                      initialized, account, None, "STABLE_DOCUMENTED_SURFACE")
        except AdapterError:
            raise
        except Exception as exc:
            raise AdapterError(str(exc)) from exc

    def start_thread(self, *, cwd: str | None = None, ephemeral: bool = True) -> str:
        params: dict[str, Any] = {"ephemeral": ephemeral}
        if cwd is not None:
            params["cwd"] = cwd
        result = self._request("thread/start", params)
        thread = result.get("thread")
        if not isinstance(thread, Mapping) or not isinstance(thread.get("id"), str) or not thread["id"]:
            raise MalformedMessage("thread/start response lacks thread.id")
        return str(thread["id"])

    def resume_thread(self, thread_id: str) -> str:
        if not thread_id:
            raise ValueError("thread_id must be non-empty")
        result = self._request("thread/resume", {"threadId": thread_id})
        thread = result.get("thread")
        if not isinstance(thread, Mapping) or thread.get("id") != thread_id:
            raise MalformedMessage("thread/resume response has unexpected thread.id")
        return thread_id

    def submit_turn(self, thread_id: str, text: str, *, profile: Any, cost_observations: Mapping[str, Any] | None, timeout: float | None = None, max_events: int = 1024, max_event_bytes: int = 262144) -> TurnObservation:
        if not thread_id or not text or max_events < 1 or max_event_bytes < 1:
            raise ValueError("thread_id, text, and positive max_events are required")
        eligibility = runtime_authorization.codex_cost_preflight(profile, cost_observations)
        if not eligibility.supported:
            raise AdapterError(f"ZERO_INCREMENTAL_COST BLOCKED: {eligibility.reason}")
        result = self._request("turn/start", {"threadId": thread_id, "input": [{"type": "text", "text": text}]}, timeout=timeout)
        turn = result.get("turn")
        if not isinstance(turn, Mapping) or not isinstance(turn.get("id"), str):
            raise MalformedMessage("turn/start response lacks turn.id")
        turn_id = turn["id"]
        events: list[Mapping[str, Any]] = []
        event_bytes = 0
        deadline = time.monotonic() + (self.request_timeout if timeout is None else timeout)
        while len(events) < max_events:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RequestTimeout(f"timed out waiting for turn/completed {turn_id}")
            try:
                message = self._messages.get(timeout=remaining)
            except queue.Empty as exc:
                raise RequestTimeout(f"timed out waiting for turn/completed {turn_id}") from exc
            if isinstance(message, (AdapterError, Exception)):
                raise message
            if not isinstance(message, Mapping) or not isinstance(message.get("method"), str):
                raise MalformedMessage("turn event is not a notification")
            event_bytes += len(json.dumps(message, sort_keys=True, separators=(",", ":")).encode())
            if event_bytes > max_event_bytes:
                raise MalformedMessage("turn events exceeded bounded observation size")
            events.append(message)
            if message["method"] == "turn/completed":
                params = message.get("params")
                completed = params.get("turn") if isinstance(params, Mapping) else None
                if not isinstance(completed, Mapping) or completed.get("id") != turn_id:
                    raise MalformedMessage("turn/completed has unexpected turn")
                return TurnObservation({"threadId": thread_id, "text": text}, tuple(events), completed)
        raise RequestTimeout(f"turn exceeded max_events before completion: {turn_id}")

    def dispatch(self, envelope: Any) -> Any:
        """Execute one complete governed envelope and report transport observation only."""
        from scheduler import DispatchEnvelope, DispatchResult, ExecutionObservation, FailureClass
        if not isinstance(envelope, DispatchEnvelope):
            raise ValueError("dispatch requires a complete DispatchEnvelope")
        started_at = time.time()
        try:
            actual_profile = self.runtime_profile
            actual_identity = getattr(actual_profile, "identity", "")
            actual_digest = runtime_authorization.runtime_profile_digest(actual_profile) if actual_profile is not None else ""
            if actual_identity != envelope.runtime_profile_id or actual_digest != envelope.runtime_profile_digest:
                raise AdapterError("runtime profile identity does not match governed dispatch")
            if not self._initialized:
                self.initialize_and_inspect()
            # The validated worktree is load-bearing: never create an unbound thread.
            thread_id = self.start_thread(cwd=envelope.workspace.path)
            prompt = json.dumps(envelope.to_dict(), sort_keys=True, separators=(",", ":"))
            turn = self.submit_turn(thread_id, prompt, profile=self.runtime_profile,
                                    cost_observations=self.cost_observations)
            turn_id = str(turn.completed.get("id", ""))
            observation = ExecutionObservation(
                envelope.identity, envelope.change_id, envelope.work_unit_id, envelope.subject,
                envelope.workspace.identity, envelope.workspace.path, envelope.runtime_profile_id,
                envelope.runtime_profile_digest, thread_id, turn_id,
                str(turn.completed.get("status", "UNKNOWN")).upper(), started_at, time.time(),
                tuple(json.dumps(event, sort_keys=True, separators=(",", ":")) for event in turn.events),
                tuple(sorted({str(event.get("params", {}).get("item", {}).get("id"))
                              for event in turn.events if isinstance(event.get("params"), Mapping)
                              and isinstance(event.get("params", {}).get("item"), Mapping)
                              and event.get("params", {}).get("item", {}).get("id")})))
            return DispatchResult("OBSERVED", evidence_fingerprint=envelope.identity,
                                  message="Codex execution observed; KEEL verification required",
                                  artifacts=observation.artifacts, observation=observation)
        except AdapterError as exc:
            return DispatchResult("FAILED", failure_class=FailureClass.AUTHORIZATION_BLOCK if "ZERO_INCREMENTAL_COST" in str(exc) else FailureClass.AGENT_FAILURE, message=str(exc))

    def close(self, *, timeout: float = 2.0) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.process.stdin.close()
        except (OSError, ValueError, AttributeError):
            pass
        try:
            self.process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, TimeoutError, OSError):
            try:
                self.process.terminate()
                self.process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, TimeoutError, OSError):
                try:
                    self.process.kill()
                    self.process.wait(timeout=timeout)
                except (OSError, TimeoutError):
                    pass
        self._reader.join(timeout=timeout)

    def __enter__(self) -> "CodexAppServerAdapter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
