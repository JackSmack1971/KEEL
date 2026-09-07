#!/usr/bin/env python3
"""KEEL Codex lifecycle hook.

Security posture:
- fail closed for enforcement events when hook input/bootstrap/state cannot be trusted;
- fail open only when the invocation is conclusively outside a Git worktree;
- normalize repo-relative paths before policy checks;
- use current Codex hook wire shapes while retaining legacy-compatible denial output;
- keep stdout machine-readable for hook events that consume JSON.

Expected placement is typically `.keel/hooks/keel_hook.py`, with `keel_core.py`
under `.keel/lib/`. The loader also supports KEEL_LIB_DIR and ancestor discovery.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve()
SUPPORTED_ACTIONS = {"context", "pre-tool", "post-tool", "stop"}
ACTION_TO_EVENT = {
    "context": "SessionStart",
    "pre-tool": "PreToolUse",
    "post-tool": "PostToolUse",
    "stop": "Stop",
}
CONTEXT_EVENTS = {"SessionStart", "UserPromptSubmit"}
WRITE_TOOL_NAMES = {"apply_patch", "Edit", "Write"}
PATH_KEYS = {
    "file_path", "filepath", "path", "file", "filename", "target_path",
    "destination", "destination_path", "output_path", "src", "dst",
}
PATCH_FILE_RE = re.compile(
    r"^\*\*\*\s+(?:Add|Update|Delete|Move)\s+File:\s*(.+?)\s*$", re.MULTILINE
)
CANDIDATE_REF_RE = re.compile(
    r"(?:^|\s)refs/keel/candidates/([a-z0-9][a-z0-9._-]{0,63})(?:\s|$)"
)


def _emit_json(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def _stderr(message: str) -> None:
    print(message, file=sys.stderr)


def _deny_pretool(reason: str) -> int:
    """Use the current canonical PreToolUse denial shape."""
    _emit_json({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    })
    return 0


def _block_posttool(reason: str) -> int:
    """PostToolUse cannot undo effects; replace the result with policy feedback."""
    _emit_json({
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reason,
        },
    })
    return 0


def _block_stop(reason: str) -> int:
    _emit_json({
        "continue": False,
        "stopReason": reason,
        "systemMessage": reason,
    })
    return 0


def _fail(action: str, reason: str) -> int:
    """Fail closed using an event-appropriate supported output contract."""
    message = f"KEEL hook failure: {reason}"
    if action == "pre-tool":
        return _deny_pretool(message)
    if action == "post-tool":
        return _block_posttool(message)
    if action == "stop":
        return _block_stop(message)
    if action == "context":
        _emit_json({
            "continue": False,
            "stopReason": message,
            "systemMessage": message,
        })
        return 0
    _stderr(message)
    return 2


def _policy_block(action: str, reason: str) -> int:
    if action == "pre-tool":
        return _deny_pretool(reason)
    if action == "post-tool":
        return _block_posttool(reason)
    if action == "stop":
        return _block_stop(reason)
    _stderr(reason)
    return 2


def load_input(action: str) -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError(f"{ACTION_TO_EVENT.get(action, action)} hook received empty stdin")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid hook JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("hook payload must be a JSON object")
    return value


def _lib_candidates() -> Iterable[Path]:
    env_dir = os.environ.get("KEEL_LIB_DIR", "").strip()
    if env_dir:
        yield Path(env_dir).expanduser()

    # Canonical layout: <repo>/.keel/hooks/keel_hook.py -> <repo>/.keel/lib
    if len(HERE.parents) >= 2:
        yield HERE.parents[1] / "lib"

    # Also support a hook living directly under .keel/ or .codex/ and ancestor discovery.
    yield HERE.parent / "lib"
    for parent in HERE.parents:
        yield parent / ".keel" / "lib"
        yield parent / "lib"


def load_keel_core():
    tried: list[str] = []
    seen: set[str] = set()
    for candidate in _lib_candidates():
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        tried.append(key)
        if (resolved / "keel_core.py").is_file():
            sys.path.insert(0, key)
            try:
                import keel_core  # type: ignore
            except Exception as exc:  # import-time failures are policy failures
                raise RuntimeError(f"failed importing keel_core from {key}: {exc}") from exc
            return keel_core
    raise RuntimeError("keel_core.py not found; searched: " + ", ".join(tried))


def git_root(cwd: Path) -> Path | None:
    """Return Git worktree root, None only when conclusively outside a worktree."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable is not available on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("git root discovery timed out") from exc
    except OSError as exc:
        raise RuntimeError(f"git root discovery failed: {exc}") from exc

    if proc.returncode == 0:
        root = proc.stdout.strip()
        if not root:
            raise RuntimeError("git rev-parse succeeded but returned an empty worktree root")
        return Path(root).resolve()

    err = (proc.stderr or proc.stdout).strip().lower()
    not_repo_markers = (
        "not a git repository",
        "not a git repo",
        "outside repository",
    )
    if any(marker in err for marker in not_repo_markers):
        return None
    raise RuntimeError(
        f"git rev-parse failed with exit {proc.returncode}: "
        f"{(proc.stderr or proc.stdout).strip()[:500]}"
    )


def normalized_path(root: Path, value: str) -> str:
    raw = value.strip().strip('"\'')
    if not raw:
        return ""

    candidate = Path(raw)
    try:
        if candidate.is_absolute():
            resolved = candidate.resolve(strict=False)
            try:
                return resolved.relative_to(root.resolve()).as_posix()
            except ValueError:
                # Preserve absolute external paths so scope checks can reject them.
                return resolved.as_posix()
    except (OSError, RuntimeError):
        pass

    p = raw.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    # Collapse harmless duplicate separators without inventing filesystem state.
    p = re.sub(r"/{2,}", "/", p)
    return p


def _collect_path_values(value: Any, *, key: str | None = None) -> list[str]:
    """Conservatively collect explicit path-valued fields from structured tool input."""
    out: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            lk = str(k).lower()
            if lk in PATH_KEYS:
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, list):
                    out.extend(x for x in v if isinstance(x, str))
            elif isinstance(v, (dict, list)):
                out.extend(_collect_path_values(v, key=lk))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                out.extend(_collect_path_values(item, key=key))
    return out


def tool_paths(inp: dict[str, Any], root: Path) -> list[str]:
    ti = inp.get("tool_input")
    if ti is None:
        # Compatibility with older synthetic fixtures; current Codex uses tool_input.
        ti = inp.get("input")

    vals = _collect_path_values(ti)

    if isinstance(ti, dict):
        for field in ("command", "patch"):
            patch = ti.get(field)
            if isinstance(patch, str) and "*** " in patch:
                vals.extend(PATCH_FILE_RE.findall(patch))

    out: list[str] = []
    for value in vals:
        p = normalized_path(root, value)
        if p and p not in out:
            out.append(p)
    return out


def phase_write_allowed(root: Path, cid: str, phase: str, path: str) -> bool:
    p = normalized_path(root, path)
    prefix = f".keel/ledger/{cid}/"
    rel = p[len(prefix):] if p.startswith(prefix) else None
    if phase == "DISCUSS":
        return rel == "proposal.md"
    if phase == "PLAN":
        if rel in {
            "proposal.md", "delta.md", "requirements.json", "acceptance.json",
            "scope.txt", "risk.json", "effects.json", "risk-review.md",
        }:
            return True
        return p == f"docs/exec-plans/active/{cid}.md"
    return False


def candidate_merge_id(command: str) -> str | None:
    """Return change id only for a simple direct merge of one sealed candidate ref."""
    # Reject compound shell programs, redirections, substitutions, and multiline input.
    if any(token in command for token in ("&&", "||", ";", "\n", "\r", "`", "$(", ">", "<", "|")):
        return None
    match = CANDIDATE_REF_RE.search(command)
    return match.group(1) if match else None


def _bash_command(inp: dict[str, Any]) -> str:
    ti = inp.get("tool_input")
    if not isinstance(ti, dict):
        return ""
    value = ti.get("command")
    if value is None:
        value = ti.get("cmd")  # compatibility for older fixtures
    return str(value or "").strip()


def _phase_dirty_paths(k: Any, root: Path, cid: str) -> list[str]:
    """Return paths changed from the KEEL base commit, normalized and deduplicated."""
    st = k.state(root, cid)
    base = str(st.get("base_commit") or "").strip()
    if not base:
        raise RuntimeError("active KEEL state has no base_commit")
    paths = k.changed_paths(root, base)
    out: list[str] = []
    for value in paths or []:
        p = normalized_path(root, str(value))
        if p and p not in out:
            out.append(p)
    return out


def _validate_phase_tree(k: Any, root: Path, cid: str, phase: str) -> list[str]:
    """Catch Bash/other-tool mutations that bypass direct file-tool path inspection."""
    paths = _phase_dirty_paths(k, root, cid)
    if phase in {"DISCUSS", "PLAN"}:
        return [p for p in paths if not phase_write_allowed(root, cid, phase, p)]
    if phase == "EXECUTE":
        scope = k.parse_scope(k.ledger_dir(root, cid) / "scope.txt")
        return [
            p for p in paths
            if p.startswith(f".keel/ledger/{cid}/") or not k.scope_match(p, scope)
        ]
    return []


def _validate_event_name(action: str, inp: dict[str, Any]) -> None:
    expected = ACTION_TO_EVENT[action]
    actual = inp.get("hook_event_name")
    if action == "context" and (actual is None or str(actual) in CONTEXT_EVENTS):
        return
    if actual is not None and str(actual) != expected:
        raise ValueError(f"action {action!r} received hook_event_name {actual!r}; expected {expected!r}")


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in SUPPORTED_ACTIONS:
        _stderr("Usage: keel_hook.py {context|pre-tool|post-tool|stop}")
        return 64

    try:
        inp = load_input(action)
        _validate_event_name(action, inp)
    except Exception as exc:
        return _fail(action, f"invalid Codex hook input: {exc}")

    cwd_value = inp.get("cwd")
    cwd = Path(str(cwd_value)) if isinstance(cwd_value, str) and cwd_value.strip() else Path.cwd()
    try:
        root = git_root(cwd)
    except Exception as exc:
        return _fail(action, f"cannot establish Git worktree root from {cwd}: {exc}")

    # Outside a Git worktree, KEEL intentionally does not enforce repository policy.
    if root is None:
        return 0

    try:
        k = load_keel_core()
    except Exception as exc:
        return _fail(action, str(exc))

    try:
        cid = k.active_change(root)
    except Exception as exc:
        return _policy_block(action, f"KEEL active-change state invalid: {exc}")

    bypass_reason = os.environ.get("KEEL_BYPASS_REASON", "").strip()
    if bypass_reason:
        try:
            k.record_bypass(root, cid, bypass_reason, str(inp.get("session_id") or "unknown"))
        except Exception as exc:
            return _policy_block(action, f"KEEL bypass recording failed: {exc}")
        return 0

    if action == "context":
        if not cid:
            return 0
        try:
            compiled = k.compile_context(root, cid, write=True)
            msg = str(compiled.get("text", ""))
        except Exception as exc:
            try:
                summary = k.status_summary(root, cid)
                msg = (
                    f"KEEL active change `{cid}`: phase={summary.get('phase')} "
                    f"base={summary.get('base_commit')}. Context compilation failed: {exc}. "
                    "Re-read the current ledger before a consequential transition."
                )
            except Exception as summary_exc:
                return _fail(action, f"context compilation failed ({exc}); status fallback also failed ({summary_exc})")

        try:
            config = k.read_json(root / ".keel/config.json")
            limit = int(config.get("hook_summary_max_chars", 6000))
        except Exception as exc:
            return _fail(action, f"cannot read hook_summary_max_chars: {exc}")
        limit = max(256, min(limit, 50_000))
        msg = msg[:limit]
        _emit_json({
            "hookSpecificOutput": {
                "hookEventName": str(inp.get("hook_event_name") or "SessionStart"),
                "additionalContext": msg,
            }
        })
        return 0

    if action == "pre-tool":
        tool = str(inp.get("tool_name") or inp.get("tool") or "")
        paths = tool_paths(inp, root)

        if tool in WRITE_TOOL_NAMES or paths:
            if not cid:
                return _policy_block(
                    action,
                    "KEEL requires an active change before direct file writes. "
                    "Start standard/trivial KEEL or stay read-only.",
                )
            try:
                st = k.state(root, cid)
                phase = st.get("phase")
            except Exception as exc:
                return _policy_block(action, f"KEEL cannot read active state: {exc}")

            # apply_patch is a write tool. If no path can be extracted, deny instead of
            # silently letting a changed/unknown patch wire format bypass policy.
            if tool == "apply_patch" and not paths:
                return _policy_block(
                    action,
                    "KEEL could not determine target paths from apply_patch input; "
                    "denying the write because the hook wire format is unrecognized.",
                )

            if phase in {"DISCUSS", "PLAN"}:
                bad = [p for p in paths if not phase_write_allowed(root, cid, str(phase), p)]
                if bad:
                    return _policy_block(
                        action,
                        "KEEL %s phase blocks this write. DISCUSS is proposal-only; PLAN permits "
                        "proposal/delta/requirements/acceptance/scope/risk/effects/risk-review and "
                        "the matching ExecPlan. State, gate log, verification, and authorization "
                        "records are script-owned: %s" % (phase, ", ".join(bad)),
                    )
            elif phase == "EXECUTE":
                try:
                    scope = k.parse_scope(k.ledger_dir(root, cid) / "scope.txt")
                except Exception as exc:
                    return _policy_block(action, f"KEEL scope invalid: {exc}")
                bad = [
                    p for p in paths
                    if p.startswith(f".keel/ledger/{cid}/") or not k.scope_match(p, scope)
                ]
                if bad:
                    return _policy_block(
                        action,
                        "KEEL EXECUTE forbids plan/ledger mutation and out-of-scope writes. "
                        "Use `keel.py replan` to change intent/scope: " + ", ".join(bad),
                    )
            elif phase in {"VERIFY","SHIP"} and paths:
                return _policy_block(
                    action,
                    "KEEL content is under/after verification. Use `keel.py reopen` for "
                    "implementation edits or `keel.py replan` for intent/scope edits: " + ", ".join(paths),
                )
            elif phase not in {"DISCUSS", "PLAN", "EXECUTE", "VERIFY", "SHIP"}:
                return _policy_block(action, f"KEEL refuses writes in unknown phase {phase!r}")

        if tool == "Bash":
            cmd = _bash_command(inp)
            low = " ".join(cmd.lower().split())

            if "record-authorization" in low:
                if not cid or os.environ.get("KEEL_AUTHORIZATION_CHANGE", "").strip() != cid:
                    return _policy_block(
                        action,
                        "KEEL authorization recording is operator-controlled. Run it outside the "
                        "agent session, or restart Codex with KEEL_AUTHORIZATION_CHANGE set to the "
                        "exact active change id after permission is actually granted.",
                    )

            if low.startswith("git merge") and not cid:
                merge_cid = candidate_merge_id(cmd)
                if not merge_cid:
                    return _policy_block(
                        action,
                        "KEEL integration checkout permits only a simple `git merge ... "
                        "refs/keel/candidates/<change-id>` handoff when no change is active.",
                    )
                try:
                    k.candidate_status(root, merge_cid)
                except Exception as exc:
                    return _policy_block(action, "KEEL sealed-candidate merge blocked: " + str(exc))
                return 0

            try:
                integration_prefixes = tuple(k.INTEGRATION_PREFIXES)
            except Exception as exc:
                return _policy_block(action, f"KEEL integration policy unavailable: {exc}")

            if any(low.startswith(prefix) for prefix in integration_prefixes):
                if not cid:
                    return _policy_block(action, "KEEL integration command requires an active verified change")
                try:
                    ok, msg = k.current_verified(root, cid)
                except Exception as exc:
                    return _policy_block(action, f"KEEL verification state unavailable: {exc}")
                if not ok:
                    return _policy_block(action, "KEEL integration blocked: " + str(msg))
                if low.startswith(("git push", "git merge", "gh pr create", "gh pr merge")):
                    try:
                        k.candidate_status(root, cid)
                    except Exception as exc:
                        return _policy_block(
                            action,
                            "KEEL publish/integration requires a sealed candidate first: " + str(exc),
                        )
        return 0

    if action == "post-tool":
        if not cid:
            try:
                base = k.head_commit(root)
                paths = [normalized_path(root, str(p)) for p in k.changed_paths(root, base)]
            except Exception as exc:
                return _fail(action, f"cannot inspect ungoverned repository changes: {exc}")
            material = [p for p in paths if p and not p.startswith((".keel/", ".control-plane/"))]
            if material:
                return _policy_block(
                    action,
                    "KEEL detected repository changes without an active ledger. Reconcile/start a "
                    "change before continuing: " + ", ".join(material[:8]),
                )
            return 0

        try:
            st = k.state(root, cid)
            phase = st.get("phase")
        except Exception as exc:
            return _fail(action, f"cannot read active KEEL state: {exc}")

        # Detect side effects from Bash/MCP/unknown tools that bypassed path extraction.
        if phase in {"DISCUSS", "PLAN", "EXECUTE"}:
            try:
                bad = _validate_phase_tree(k, root, cid, str(phase))
            except Exception as exc:
                return _fail(action, f"cannot validate repository tree against {phase} policy: {exc}")
            if bad:
                return _policy_block(
                    action,
                    f"KEEL {phase} tree-policy violation after tool use: " + ", ".join(bad[:12]),
                )

        if phase in {"EXECUTE", "VERIFY", "SHIP"}:
            try:
                errs, _ = k.diff_scope_errors(root, cid)
            except Exception as exc:
                return _fail(action, f"cannot establish KEEL diff scope: {exc}")
            if errs:
                return _policy_block(
                    action,
                    "KEEL diff-scope violation after tool use: " + "; ".join(map(str, errs[:5])),
                )
            if phase == "SHIP":
                try:
                    ok, msg = k.current_verified(root, cid)
                except Exception as exc:
                    return _fail(action, f"cannot validate SHIP verification state: {exc}")
                if not ok:
                    return _policy_block(action, "KEEL verified content changed: " + str(msg))
        return 0

    if action == "stop":
        if not cid:
            return 0
        try:
            st = k.state(root, cid)
            phase = st.get("phase")
        except Exception as exc:
            return _fail(action, f"cannot read active KEEL state: {exc}")

        if phase in {"DISCUSS", "PLAN"}:
            _emit_json({
                "systemMessage": (
                    f"KEEL change {cid} remains in {phase}; do not describe implementation as complete."
                )
            })
            return 0

        if phase == "EXECUTE":
            try:
                _, paths = k.diff_scope_errors(root, cid)
            except Exception as exc:
                return _block_stop(f"KEEL cannot establish diff scope: {exc}")
            if paths:
                if inp.get("stop_hook_active"):
                    _emit_json({
                        "systemMessage": (
                            f"KEEL change {cid} remains unverified; stopping to avoid an infinite "
                            "continuation. Report BLOCKED, not complete."
                        )
                    })
                    return 0
                return _block_stop(
                    f"KEEL change {cid} has unverified writes. Run `python3 .keel/bin/keel.py verify` "
                    "and resolve blockers before completion."
                )
            return 0

        if phase == "SHIP":
            try:
                ok, msg = k.current_verified(root, cid)
            except Exception as exc:
                return _block_stop(f"KEEL cannot establish verification state: {exc}")
            if not ok:
                if inp.get("stop_hook_active"):
                    _emit_json({
                        "systemMessage": f"KEEL verification became stale: {msg}. Report BLOCKED."
                    })
                    return 0
                return _block_stop("KEEL completion blocked: " + str(msg))
            return 0

        if phase == "VERIFY":
            _emit_json({
                "systemMessage": (
                    f"KEEL change {cid} remains in VERIFY; verification has not advanced to SHIP. "
                    "Do not report the change as shipped."
                )
            })
            return 0

        return _block_stop(f"KEEL refuses completion in unknown phase {phase!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
