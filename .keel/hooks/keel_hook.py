#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, sys
sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import keel_core as k


def load_input():
    raw = sys.stdin.read()
    if not raw.strip(): return {}
    try: return json.loads(raw)
    except Exception: return {}


def block(reason: str, stop: bool = False):
    if stop:
        print(json.dumps({"decision":"block", "reason":reason}))
        return 0
    print(reason, file=sys.stderr)
    return 2


def tool_paths(inp: dict) -> list[str]:
    ti = inp.get("tool_input") or inp.get("input") or {}
    vals = []
    for key in ("file_path","path","file","filename"):
        v = ti.get(key) if isinstance(ti, dict) else None
        if isinstance(v, str): vals.append(v)
    # Current Codex reports apply_patch/Edit/Write patch content in tool_input.command.
    patch = None
    if isinstance(ti, dict):
        for key in ("patch", "command"):
            if isinstance(ti.get(key), str) and "*** " in ti.get(key):
                patch = ti.get(key); break
    if isinstance(patch, str):
        vals += re.findall(r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$", patch, re.M)
    out=[]
    for v in vals:
        v=v.replace("\\","/")
        while v.startswith("./"): v=v[2:]
        if v not in out: out.append(v)
    return out


def is_ledger_path(p: str, cid: str) -> bool:
    return p.startswith(f".keel/ledger/{cid}/") or p == f"docs/exec-plans/active/{cid}.md"


def normalized_path(root: Path, value: str) -> str:
    p = value.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    try:
        candidate = Path(value)
        if candidate.is_absolute():
            p = candidate.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        pass
    return p


def phase_write_allowed(root: Path, cid: str, phase: str, p: str) -> bool:
    p = normalized_path(root, p)
    prefix = f".keel/ledger/{cid}/"
    rel = p[len(prefix):] if p.startswith(prefix) else None
    if phase == "DISCUSS":
        return rel == "proposal.md"
    if phase == "PLAN":
        if rel in {"proposal.md", "delta.md", "requirements.json", "acceptance.json", "scope.txt", "risk.json", "effects.json", "risk-review.md"}:
            return True
        return p == f"docs/exec-plans/active/{cid}.md"
    return False


def candidate_merge_id(command: str) -> str | None:
    """Return change id only for a simple direct merge of one sealed candidate ref."""
    if any(x in command for x in ("&&", "||", ";", "\n", "\r")):
        return None
    m = re.search(r"(?:^|\s)refs/keel/candidates/([a-z0-9][a-z0-9._-]{0,63})(?:\s|$)", command)
    return m.group(1) if m else None


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    inp = load_input()
    try: root = k.git_root(Path(inp.get("cwd") or Path.cwd()))
    except Exception:
        return 0  # No Git root: KEEL cannot enforce; bootstrap/doctor reports readiness separately.
    cid = None
    try: cid = k.active_change(root)
    except Exception as e: return block(f"KEEL active-change state invalid: {e}", stop=(action=="stop"))
    reason = os.environ.get("KEEL_BYPASS_REASON", "").strip()
    if reason:
        try: k.record_bypass(root, cid, reason, str(inp.get("session_id") or "unknown"))
        except Exception as e: return block(str(e), stop=(action=="stop"))
        return 0

    if action == "context":
        if not cid: return 0
        try:
            compiled = k.compile_context(root, cid, write=True)
            msg = compiled.get("text", "")
        except Exception as e:
            s = k.status_summary(root, cid)
            msg = f"KEEL active change `{cid}`: phase={s.get('phase')} base={s.get('base_commit')}. Context compilation failed: {e}. Re-read the current ledger before a consequential transition."
        limit = k.read_json(root/".keel/config.json").get("hook_summary_max_chars", 6000)
        msg = msg[:int(limit)]
        print(json.dumps({"hookSpecificOutput":{"hookEventName": inp.get("hook_event_name", "SessionStart"), "additionalContext": msg}}))
        return 0

    if action == "pre-tool":
        tool = str(inp.get("tool_name") or inp.get("tool") or "")
        paths = [normalized_path(root, p) for p in tool_paths(inp)]
        if tool in {"apply_patch","Edit","Write"} or paths:
            if not cid: return block("KEEL requires an active change before direct file writes. Start standard/trivial KEEL or stay read-only.")
            st = k.state(root, cid); phase = st.get("phase")
            if phase in {"DISCUSS","PLAN"}:
                bad = [p for p in paths if not phase_write_allowed(root, cid, phase, p)]
                if bad:
                    return block(
                        "KEEL %s phase blocks this write. DISCUSS is proposal-only; PLAN permits proposal/delta/requirements/acceptance/scope/risk/effects/risk-review and the matching ExecPlan. "
                        "state, gate log, verification, and authorization records are script-owned: %s" % (phase, ", ".join(bad))
                    )
            elif phase == "EXECUTE":
                try: scope = k.parse_scope(k.ledger_dir(root,cid)/"scope.txt")
                except Exception as e: return block(f"KEEL scope invalid: {e}")
                bad = [p for p in paths if p.startswith(f".keel/ledger/{cid}/") or not k.scope_match(p, scope)]
                if bad: return block("KEEL EXECUTE forbids plan/ledger mutation and out-of-scope writes. Use `keel.py replan` to change intent/scope: " + ", ".join(bad))
            elif phase in {"VERIFY","SHIP"}:
                if paths:
                    return block("KEEL content is under/after verification. Use `keel.py reopen` for implementation edits or `keel.py replan` for intent/scope edits: " + ", ".join(paths))
        if tool == "Bash":
            ti = inp.get("tool_input") or {}
            cmd = str(ti.get("command") or ti.get("cmd") or "").strip()
            low = " ".join(cmd.lower().split())
            if "record-authorization" in low:
                # The model must not manufacture permission by invoking the recorder itself.
                # An operator can either run the command outside Codex or start Codex with this
                # exact change id in the parent environment to make the invocation auditable.
                if not cid or os.environ.get("KEEL_AUTHORIZATION_CHANGE", "").strip() != cid:
                    return block(
                        "KEEL authorization recording is operator-controlled. Run it outside the agent session, or restart Codex with KEEL_AUTHORIZATION_CHANGE set to the exact active change id after permission is actually granted."
                    )
            if low.startswith("git merge") and not cid:
                merge_cid = candidate_merge_id(cmd)
                if not merge_cid:
                    return block("KEEL integration checkout permits only a simple `git merge ... refs/keel/candidates/<change-id>` handoff when no change is active.")
                try:
                    k.candidate_status(root, merge_cid)
                except Exception as e:
                    return block("KEEL sealed-candidate merge blocked: " + str(e))
                return 0
            if any(low.startswith(p) for p in k.INTEGRATION_PREFIXES):
                if not cid: return block("KEEL integration command requires an active verified change")
                ok, msg = k.current_verified(root, cid)
                if not ok: return block("KEEL integration blocked: " + msg)
                if low.startswith(("git push", "git merge", "gh pr create", "gh pr merge")):
                    try:
                        k.candidate_status(root, cid)
                    except Exception as e:
                        return block("KEEL publish/integration requires a sealed candidate first: " + str(e))
        return 0

    if action == "post-tool":
        if not cid:
            # Detect ungoverned write after the fact; hooks cannot undo it, but force reconciliation.
            try:
                base = k.head_commit(root); paths = k.changed_paths(root, base)
            except Exception: return 0
            material = [p for p in paths if not p.startswith((".keel/",".control-plane/"))]
            if material:
                return block("KEEL detected repository changes without an active ledger. Reconcile/start a change before continuing: " + ", ".join(material[:8]))
            return 0
        st = k.state(root,cid)
        if st.get("phase") in {"EXECUTE","VERIFY","SHIP"}:
            try: errs, _ = k.diff_scope_errors(root,cid)
            except Exception as e: errs=[str(e)]
            if errs: return block("KEEL diff-scope violation after tool use: " + "; ".join(errs[:5]))
            if st.get("phase") == "SHIP":
                ok,msg = k.current_verified(root,cid)
                if not ok: return block("KEEL verified content changed: " + msg)
        return 0

    if action == "stop":
        if not cid: return 0
        st = k.state(root,cid); phase=st.get("phase")
        if phase in {"DISCUSS","PLAN"}:
            print(json.dumps({"systemMessage":f"KEEL change {cid} remains in {phase}; do not describe implementation as complete."}))
            return 0
        if phase == "EXECUTE":
            try: _, paths = k.diff_scope_errors(root,cid)
            except Exception as e: return block(f"KEEL cannot establish diff scope: {e}", stop=True)
            if paths:
                if inp.get("stop_hook_active"):
                    print(json.dumps({"systemMessage":f"KEEL change {cid} remains unverified; stopping to avoid an infinite continuation. Report BLOCKED, not complete."}))
                    return 0
                return block(f"KEEL change {cid} has unverified writes. Run `python3 .keel/bin/keel.py verify` and resolve blockers before completion.", stop=True)
            return 0
        if phase == "SHIP":
            ok,msg = k.current_verified(root,cid)
            if not ok:
                if inp.get("stop_hook_active"):
                    print(json.dumps({"systemMessage":f"KEEL verification became stale: {msg}. Report BLOCKED."})); return 0
                return block("KEEL completion blocked: " + msg, stop=True)
            return 0
        return 0
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
