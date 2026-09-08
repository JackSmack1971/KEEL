#!/usr/bin/env python3
"""Thin Codex wire adapter for the deterministic KEEL adapter kernel."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
ACTION_EVENTS = {
    "context": frozenset({"SessionStart", "UserPromptSubmit"}),
    "pre-tool": frozenset({"PreToolUse"}),
    "post-tool": frozenset({"PostToolUse"}),
    "stop": frozenset({"Stop"}),
}


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def _deny(action: str, reason: str) -> int:
    message = f"KEEL: {reason}"
    if action == "pre-tool":
        _emit({"hookSpecificOutput":{"hookEventName":"PreToolUse", "permissionDecision":"deny",
              "permissionDecisionReason":message}})
    elif action == "post-tool":
        _emit({"decision":"block", "reason":message,
              "hookSpecificOutput":{"hookEventName":"PostToolUse", "additionalContext":message}})
    else:
        _emit({"continue":False, "stopReason":message, "systemMessage":message})
    return 0


def _load_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip(): raise ValueError("hook received empty stdin")
    value = json.loads(raw)
    if not isinstance(value, dict): raise ValueError("hook payload must be an object")
    return value


def _lib_candidates() -> Iterable[Path]:
    if os.environ.get("KEEL_LIB_DIR", "").strip(): yield Path(os.environ["KEEL_LIB_DIR"]).expanduser()
    yield HERE.parents[1] / "lib"
    for parent in HERE.parents: yield parent / ".keel" / "lib"


def _load_kernel():
    for candidate in _lib_candidates():
        if (candidate / "keel_core.py").is_file() and (candidate / "codex_adapter_kernel.py").is_file():
            sys.path.insert(0, str(candidate.resolve()))
            import keel_core  # type: ignore
            import codex_adapter_kernel  # type: ignore
            return keel_core, codex_adapter_kernel
    raise RuntimeError("trusted KEEL kernel modules were not found")


def _git_root(cwd: Path) -> Path | None:
    try:
        proc = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", timeout=10, check=False)
    except Exception as exc: raise RuntimeError(f"Git authority discovery failed: {exc}") from exc
    if proc.returncode == 0:
        if not proc.stdout.strip(): raise RuntimeError("Git returned an empty worktree root")
        return Path(proc.stdout.strip()).resolve()
    diagnostic = (proc.stderr or proc.stdout).strip().lower()
    if "not a git repository" in diagnostic or "not a git repo" in diagnostic:
        return None  # conclusive outside-authority fail-open
    raise RuntimeError(f"Git authority discovery was inconclusive (exit {proc.returncode}): {diagnostic[:300]}")


def _render(action: str, event: str, outcome: Any) -> int:
    kind = str(getattr(outcome.kind, "value", outcome.kind))
    if kind == "DENY": return _deny(action, outcome.reason)
    if kind == "CONTEXT":
        _emit({"hookSpecificOutput":{"hookEventName":event, "additionalContext":outcome.context}})
    elif kind == "OBSERVE" and outcome.reason:
        _emit({"systemMessage":outcome.reason} if action == "stop" else
              {"hookSpecificOutput":{"hookEventName":event, "additionalContext":outcome.reason}})
    return 0


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in ACTION_EVENTS:
        print("Usage: keel_hook.py {context|pre-tool|post-tool|stop}", file=sys.stderr); return 64
    try:
        payload = _load_input()
        actual = payload.get("hook_event_name")
        events = ACTION_EVENTS[action]
        event = str(actual) if actual is not None else sorted(events)[0]
        if event not in events: raise ValueError(f"action {action!r} does not accept event {event!r}")
        cwd = Path(str(payload.get("cwd"))) if isinstance(payload.get("cwd"), str) and payload["cwd"].strip() else Path.cwd()
        root = _git_root(cwd)
        if root is None: return 0
        core, kernel = _load_kernel()
        query = kernel.normalize_query(payload, event)
        outcome = kernel.query(core, root, query, bypass_reason=os.environ.get("KEEL_BYPASS_REASON", "").strip())
        return _render(action, event, outcome)
    except Exception as exc:
        return _deny(action, f"trusted adapter state unavailable: {exc}")


if __name__ == "__main__": raise SystemExit(main())
