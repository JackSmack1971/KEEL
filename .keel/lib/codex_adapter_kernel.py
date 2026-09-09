"""Deterministic KEEL policy query for Codex runtime adapters.

The module never executes tools and never claims hook confinement.  It consumes an
already-established repository root plus a lifecycle compatibility facade and returns
an adapter-neutral outcome.  Codex wire parsing/rendering belongs in the hook.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

import runtime_authorization as ra

CONTEXT_EVENTS = frozenset({"SessionStart", "UserPromptSubmit"})
ENFORCEMENT_EVENTS = frozenset({"PreToolUse", "PostToolUse", "Stop"})
SUPPORTED_EVENTS = CONTEXT_EVENTS | ENFORCEMENT_EVENTS
PATH_KEYS = frozenset({"file_path", "filepath", "path", "file", "filename",
                       "target_path", "destination", "destination_path",
                       "output_path", "src", "dst"})
DIRECT_WRITE_TOOLS = frozenset({"apply_patch", "Edit", "Write", "write_file",
                                "create_file", "delete_file", "move_file"})
PATCH_FILE_RE = re.compile(r"^\*\*\*\s+(?:Add|Update|Delete|Move)\s+File:\s*(.+?)\s*$", re.MULTILINE)
CANDIDATE_REF_RE = re.compile(r"(?:^|\s)refs/keel/candidates/([a-z0-9][a-z0-9._-]{0,63})(?:\s|$)")


class OutcomeKind(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    CONTEXT = "CONTEXT"
    OBSERVE = "OBSERVE"


@dataclass(frozen=True)
class KernelQuery:
    event: str
    tool_name: str = ""
    tool_input: Mapping[str, Any] = field(default_factory=dict)
    session_id: str = "unknown"
    stop_hook_active: bool = False
    runtime_version: str | None = None


@dataclass(frozen=True)
class KernelOutcome:
    kind: OutcomeKind
    reason: str = ""
    context: str = ""
    profile_digest: str = ""
    coverage: tuple[str, ...] = ()
    effect_already_occurred: bool = False


@dataclass(frozen=True)
class AutonomousInvocation:
    status: str
    reason: str
    resumable: bool = False


def invoke_autonomous_codex(profile: Any, observations: Mapping[str, Any] | None, invoke: Any) -> AutonomousInvocation:
    """The sole adapter seam that may call a Codex invoker; preflight precedes it."""
    profiled, result = ra.apply_codex_cost_preflight(profile, observations)
    if not result.supported:
        return AutonomousInvocation("BLOCKED", result.reason, result.resumable)
    invoke(profiled)
    return AutonomousInvocation("INVOKED", result.reason)


def normalize_query(payload: Mapping[str, Any], expected_event: str) -> KernelQuery:
    actual = payload.get("hook_event_name")
    if actual is not None and str(actual) != expected_event:
        raise ValueError(f"expected {expected_event!r}, received {actual!r}")
    if expected_event not in SUPPORTED_EVENTS:
        raise ValueError(f"unsupported Codex event {expected_event!r}")
    tool_input = payload.get("tool_input", payload.get("input", {}))
    if tool_input is None:
        tool_input = {}
    if not isinstance(tool_input, Mapping):
        raise ValueError("tool_input must be an object")
    return KernelQuery(event=expected_event,
        tool_name=str(payload.get("tool_name") or payload.get("tool") or ""),
        tool_input=dict(tool_input), session_id=str(payload.get("session_id") or "unknown"),
        stop_hook_active=bool(payload.get("stop_hook_active")),
        runtime_version=str(payload["runtime_version"]) if payload.get("runtime_version") else None)


def normalize_path(root: Path, value: str) -> str:
    raw = value.strip().strip("'\"")
    if not raw:
        return ""
    candidate = Path(raw)
    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
        try:
            return resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            return resolved.as_posix()
    value = re.sub(r"/{2,}", "/", raw.replace("\\", "/"))
    while value.startswith("./"):
        value = value[2:]
    return value


def _path_values(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in PATH_KEYS:
                if isinstance(child, str): result.append(child)
                elif isinstance(child, list): result.extend(x for x in child if isinstance(x, str))
            elif isinstance(child, (Mapping, list)): result.extend(_path_values(child))
    elif isinstance(value, list):
        for child in value:
            if isinstance(child, (Mapping, list)): result.extend(_path_values(child))
    return result


def tool_paths(query: KernelQuery, root: Path) -> tuple[str, ...]:
    values = _path_values(query.tool_input)
    for field_name in ("command", "patch"):
        value = query.tool_input.get(field_name)
        if isinstance(value, str) and "*** " in value:
            values.extend(PATCH_FILE_RE.findall(value))
    return tuple(dict.fromkeys(p for p in (normalize_path(root, v) for v in values) if p))


def tool_family(name: str) -> str:
    if name in DIRECT_WRITE_TOOLS: return "local-write"
    if name in {"Bash", "shell", "exec_command"}: return "local-process"
    if name.startswith("mcp__") or name.startswith("MCP:"): return "mcp-function"
    return "local-function" if name else "unknown"


def _mutation_candidate(query: KernelQuery, paths: tuple[str, ...]) -> bool:
    family = tool_family(query.tool_name)
    if family == "local-write": return True
    # Unknown MCP/local functions are observed but not denied merely for carrying a
    # path. Only explicit mutating tool names enter pre-effect filesystem scope policy.
    tokens = set(re.split(r"[^a-z]+", query.tool_name.lower()))
    return bool(paths) and family in {"mcp-function", "local-function"} and bool(
        tokens & {"write", "edit", "delete", "remove", "create", "move", "rename"})


def _phase_write_allowed(root: Path, cid: str, phase: str, path: str) -> bool:
    path = normalize_path(root, path); prefix = f".keel/ledger/{cid}/"
    rel = path[len(prefix):] if path.startswith(prefix) else None
    if phase == "DISCUSS": return rel == "proposal.md"
    if phase == "PLAN":
        return rel in {"proposal.md", "delta.md", "requirements.json", "acceptance.json",
                       "scope.txt", "risk.json", "effects.json", "risk-review.md"} or path == f"docs/exec-plans/active/{cid}.md"
    return False


def _dirty_violations(k: Any, root: Path, cid: str, phase: str) -> list[str]:
    st = k.state(root, cid); base = str(st.get("base_commit") or "").strip()
    if not base: raise RuntimeError("active KEEL state has no base_commit")
    paths = list(dict.fromkeys(normalize_path(root, str(p)) for p in k.changed_paths(root, base)))
    if phase in {"DISCUSS", "PLAN"}: return [p for p in paths if not _phase_write_allowed(root, cid, phase, p)]
    if phase == "EXECUTE":
        directory = k.ledger_dir(root, cid)
        scope = k.canonical_ledger.load_intent(directory)["scope"] if (directory / "intent.json").is_file() else k.parse_scope(directory / "scope.txt")
        return [p for p in paths if p.startswith(f".keel/ledger/{cid}/") or not k.scope_match(p, scope)]
    return []


def _profile(query: KernelQuery) -> Any:
    family = tool_family(query.tool_name)
    return ra.observe_runtime(identity="keel:runtime-profile:codex-hook-invocation", runtime="codex",
        runtime_version=query.runtime_version, source=f"observed-hook-event:{query.event}",
        observations={"repository":"OBSERVED", "git":"OBSERVED", "hook_trust":"OBSERVED"},
        hook_coverage=tuple(sorted(SUPPORTED_EVENTS)), tool_coverage=(family,),
        tools=(query.tool_name,) if query.tool_name else (),
        unobservable=("alternate-clients", "direct-processes", "undelivered-tool-events"))


def _deny(reason: str, profile: Any, *, post: bool = False) -> KernelOutcome:
    return KernelOutcome(OutcomeKind.DENY, reason=reason,
        profile_digest=ra.runtime_profile_digest(profile), coverage=profile.tool_coverage,
        effect_already_occurred=post)


def _explicit_allow(profile: Any, reason: str = "kernel policy permits this query") -> KernelOutcome:
    decision = ra.evaluate_repository_enforcement(authority=ra.RepositoryAuthority.APPLIES,
        enforcement_expected=True, trusted_state=True, policy_permits=True)
    if not decision.permitted: return _deny("; ".join(decision.reasons), profile)
    return KernelOutcome(OutcomeKind.ALLOW, reason=reason, profile_digest=ra.runtime_profile_digest(profile), coverage=profile.tool_coverage)


def query(k: Any, root: Path, q: KernelQuery, *, bypass_reason: str = "") -> KernelOutcome:
    """Evaluate one normalized event against canonical/compatibility kernel state."""
    profile = _profile(q)
    try: cid = k.active_change(root)
    except Exception as exc: return _deny(f"KEEL active-change state invalid: {exc}", profile, post=q.event == "PostToolUse")
    trust = ra.evaluate_repository_enforcement(authority=ra.RepositoryAuthority.APPLIES,
        enforcement_expected=q.event in ENFORCEMENT_EVENTS, trusted_state=True)
    if not trust.permitted:
        return _deny("; ".join(trust.reasons), profile, post=q.event == "PostToolUse")
    if bypass_reason:
        try: k.record_bypass(root, cid, bypass_reason, q.session_id)
        except Exception as exc: return _deny(f"KEEL bypass recording failed: {exc}", profile, post=q.event == "PostToolUse")
        return _explicit_allow(profile, "operator-provided KEEL bypass was recorded")
    if q.event in CONTEXT_EVENTS:
        if not cid: return _explicit_allow(profile, "no active KEEL change")
        try:
            compiled = k.compile_context(root, cid, write=True)
            config = k.read_json(root / ".keel/config.json")
            limit = max(256, min(int(config.get("hook_summary_max_chars", 6000)), 50_000))
            return KernelOutcome(OutcomeKind.CONTEXT, context=str(compiled.get("text", ""))[:limit],
                profile_digest=ra.runtime_profile_digest(profile), coverage=profile.hook_coverage)
        except Exception as exc: return _deny(f"trusted KEEL context unavailable: {exc}", profile)
    if q.event == "PreToolUse": return _pre_tool(k, root, cid, q, profile)
    if q.event == "PostToolUse": return _post_tool(k, root, cid, q, profile)
    return _stop(k, root, cid, q, profile)


def _pre_tool(k: Any, root: Path, cid: str | None, q: KernelQuery, profile: Any) -> KernelOutcome:
    paths = tool_paths(q, root); family = tool_family(q.tool_name)
    mutation_candidate = _mutation_candidate(q, paths)
    if family == "local-write" and not paths:
        return _deny("write target paths are absent or use an unrecognized wire shape", profile)
    if mutation_candidate:
        if not cid: return _deny("KEEL requires an active change before repository file writes", profile)
        try: phase = str(k.state(root, cid).get("phase"))
        except Exception as exc: return _deny(f"trusted KEEL lifecycle state unavailable: {exc}", profile)
        if phase in {"DISCUSS", "PLAN"}:
            bad = [p for p in paths if not _phase_write_allowed(root, cid, phase, p)]
        elif phase == "EXECUTE":
            try:
                directory = k.ledger_dir(root, cid)
                scope = k.canonical_ledger.load_intent(directory)["scope"] if (directory / "intent.json").is_file() else k.parse_scope(directory / "scope.txt")
            except Exception as exc: return _deny(f"trusted KEEL scope unavailable: {exc}", profile)
            bad = [p for p in paths if p.startswith(f".keel/ledger/{cid}/") or not k.scope_match(p, scope)]
        elif phase in {"VERIFY", "SHIP"}: bad = list(paths)
        else: return _deny(f"unknown KEEL lifecycle phase {phase!r}", profile)
        if bad: return _deny(f"kernel lifecycle/scope policy denies: {', '.join(bad)}", profile)
    if family == "local-process":
        cmd = str(q.tool_input.get("command", q.tool_input.get("cmd", ""))).strip()
        low = " ".join(cmd.lower().split())
        if "record-authorization" in low and (not cid or os.environ.get("KEEL_AUTHORIZATION_CHANGE", "").strip() != cid):
            return _deny("authorization recording requires operator-established parent-session authority", profile)
        if any(low.startswith(p) for p in tuple(k.INTEGRATION_PREFIXES)):
            if low.startswith("git merge") and not cid:
                match = CANDIDATE_REF_RE.search(cmd)
                simple = match and not any(x in cmd for x in ("&&", "||", ";", "\n", "`", "$(", ">", "<", "|"))
                if not simple: return _deny("integration checkout accepts only a simple sealed-candidate merge", profile)
                try: k.candidate_status(root, match.group(1))
                except Exception as exc: return _deny(f"sealed candidate unavailable: {exc}", profile)
                return _explicit_allow(profile, "sealed-candidate handoff is eligible")
            if not cid: return _deny("integration command requires an active verified change", profile)
            try: ok, message = k.current_verified(root, cid)
            except Exception as exc: return _deny(f"trusted verification state unavailable: {exc}", profile)
            if not ok: return _deny(f"integration is not eligible: {message}", profile)
            if low.startswith(("git push", "git merge", "gh pr create", "gh pr merge")):
                try: k.candidate_status(root, cid)
                except Exception as exc: return _deny(f"sealed candidate unavailable: {exc}", profile)
    return _explicit_allow(profile)


def _post_tool(k: Any, root: Path, cid: str | None, q: KernelQuery, profile: Any) -> KernelOutcome:
    if not cid:
        try: paths = [normalize_path(root, str(p)) for p in k.changed_paths(root, k.head_commit(root))]
        except Exception as exc: return _deny(f"post-effect repository observation failed: {exc}", profile, post=True)
        material = [p for p in paths if p and not p.startswith((".keel/",))]
        if material: return _deny("post-effect observation found ungoverned changes: " + ", ".join(material[:8]), profile, post=True)
        return KernelOutcome(OutcomeKind.OBSERVE, reason="post-tool observation found no policy violation; this hook cannot undo effects; effects cannot be undone",
            profile_digest=ra.runtime_profile_digest(profile), coverage=profile.tool_coverage, effect_already_occurred=True)
    try: phase = str(k.state(root, cid).get("phase"))
    except Exception as exc: return _deny(f"post-effect lifecycle observation failed: {exc}", profile, post=True)
    try:
        bad = _dirty_violations(k, root, cid, phase) if phase in {"DISCUSS", "PLAN", "EXECUTE"} else []
        if phase in {"EXECUTE", "VERIFY", "SHIP"}:
            errors, _ = k.diff_scope_errors(root, cid); bad.extend(map(str, errors))
        if phase == "SHIP":
            ok, message = k.current_verified(root, cid)
            if not ok: bad.append(str(message))
    except Exception as exc: return _deny(f"post-effect policy observation failed: {exc}", profile, post=True)
    reason = ("post-effect policy violation (the hook cannot undo executed effects): " + "; ".join(bad[:12])) if bad else "post-tool observation passed; this hook cannot undo effects; effects cannot be undone"
    return KernelOutcome(OutcomeKind.OBSERVE, reason=reason, profile_digest=ra.runtime_profile_digest(profile), coverage=profile.tool_coverage, effect_already_occurred=True)


def _stop(k: Any, root: Path, cid: str | None, q: KernelQuery, profile: Any) -> KernelOutcome:
    if not cid: return _explicit_allow(profile, "no active KEEL change")
    try: phase = str(k.state(root, cid).get("phase"))
    except Exception as exc: return _deny(f"trusted lifecycle state unavailable at Stop: {exc}", profile)
    if phase in {"DISCUSS", "PLAN"}: return KernelOutcome(OutcomeKind.OBSERVE, reason=f"change remains in {phase}; do not claim implementation completion", profile_digest=ra.runtime_profile_digest(profile))
    if phase == "EXECUTE":
        try: _, paths = k.diff_scope_errors(root, cid)
        except Exception as exc: return _deny(f"diff scope unavailable at Stop: {exc}", profile)
        if paths and not q.stop_hook_active: return _deny("unverified writes require kernel verification before completion", profile)
        return KernelOutcome(OutcomeKind.OBSERVE, reason="change remains unverified" if paths else "no material writes require verification", profile_digest=ra.runtime_profile_digest(profile))
    if phase == "VERIFY": return KernelOutcome(OutcomeKind.OBSERVE, reason="verification has not advanced to SHIP", profile_digest=ra.runtime_profile_digest(profile))
    if phase == "SHIP":
        try: ok, message = k.current_verified(root, cid)
        except Exception as exc: return _deny(f"verification state unavailable at Stop: {exc}", profile)
        return _explicit_allow(profile, "verified SHIP state") if ok else _deny(f"verification is stale: {message}", profile)
    return _deny(f"unknown KEEL lifecycle phase {phase!r}", profile)
