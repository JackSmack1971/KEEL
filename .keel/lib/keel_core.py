from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import capability_resolver
import context_compiler
import evidence_graph
import evidence_system
import git_proof
import candidate_attestation
import canonical_ledger
import p0_contract

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PLACEHOLDER_RE = re.compile(r"<!--\s*FILL\b|\{\{[A-Z0-9_]+\}\}")
INTEGRATION_PREFIXES = (
    "git push", "git merge", "gh pr create", "gh pr merge", "gh release", "git tag -s", "git tag -a",
)
LEGACY_INTENT_FILES = ("proposal.md", "delta.md", "requirements.json", "acceptance.json", "scope.txt", "risk.json", "effects.json", "authorization.json", "risk-review.md")
INTENT_FILES = LEGACY_INTENT_FILES  # historical-reader compatibility

def intent_files(root: Path, change_id: str) -> tuple[str, ...]:
    return ("intent.json",) if (ledger_dir(root, change_id) / "intent.json").is_file() else LEGACY_INTENT_FILES
CONTROL_PLANE_PREFIXES = (".codex/", ".keel/", ".agents/skills/")
CONTROL_PLANE_FILES = {"AGENTS.md", "CONTROL_PLANE.md", "WORKFLOW.md"}
CANDIDATE_REF_PREFIX = "refs/keel/candidates/"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_git(root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=check)


def run_git_bytes(root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=check)


def git_root(cwd: Path | None = None) -> Path:
    return git_proof.repository_root(cwd)


def head_commit(root: Path) -> str:
    return git_proof.head_commit(root)


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-keel")
    tmp.write_bytes(data.encode("utf-8"))
    os.replace(tmp, path)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def canonical_json_digest(value: dict) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def validate_id(change_id: str) -> str:
    if not ID_RE.fullmatch(change_id) or ".." in change_id or change_id.endswith("."):
        raise ValueError("change-id must match [a-z0-9][a-z0-9._-]{0,63}, without '..' or trailing '.'")
    return change_id


def ledger_dir(root: Path, change_id: str) -> Path:
    validate_id(change_id)
    p = (root / ".keel" / "ledger" / change_id).resolve()
    p.relative_to((root / ".keel" / "ledger").resolve())
    return p


def active_file(root: Path) -> Path:
    return root / ".keel" / "active-change"


def active_change(root: Path) -> str | None:
    p = active_file(root)
    if not p.is_file():
        return None
    cid = p.read_text(encoding="utf-8").strip()
    validate_id(cid)
    return cid


def state(root: Path, change_id: str):
    d = ledger_dir(root, change_id)
    if (d / "intent.json").is_file():
        intent = canonical_ledger.load_intent(d)
        result = {"schema_version": 2, "change_id": change_id, "mode": intent["mode"], "phase": canonical_ledger.phase(d), "base_commit": intent["base_commit"]}
        view = d / "views" / "verification.json"
        if view.is_file() and read_json(view).get("status") == "PASS": result["verified_content_digest"] = read_json(view).get("content_digest")
        return result
    return read_json(d / "state.json")


def write_state(root: Path, change_id: str, st: dict) -> None:
    d = ledger_dir(root, change_id)
    if (d / "intent.json").is_file():
        canonical_ledger.project_views(d)
        return
    st["updated_at"] = now()
    write_json(d / "state.json", st)


def append_event(root: Path, change_id: str, event: str, result: str, details: dict | None = None) -> None:
    d = ledger_dir(root, change_id)
    if (d / "intent.json").is_file():
        canonical_ledger.append_event(d, "VERIFY_PASS" if event == "VERIFY" and result == "PASS" else "VERIFY_FAIL" if event == "VERIFY" else event, result, details)
        canonical_ledger.project_views(d)
        return
    row = {"ts": now(), "event": event, "result": result}
    if details:
        row["details"] = details
    p = d / "gate-log.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass


def meaningful_proposal(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "proposal.md missing"
    text = path.read_text(encoding="utf-8", errors="replace")
    if PLACEHOLDER_RE.search(text):
        return False, "proposal contains unresolved placeholder"
    material = " ".join(x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith("#"))
    if len(material) < 40:
        return False, "proposal is too thin; record problem/objective/success evidence"
    return True, "ok"


def delta_valid(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "delta.md missing"
    text = path.read_text(encoding="utf-8", errors="replace")
    if PLACEHOLDER_RE.search(text):
        return False, "delta contains unresolved placeholder"
    sections = {"ADDED": [], "MODIFIED": [], "REMOVED": []}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(ADDED|MODIFIED|REMOVED)\s*$", line.strip(), re.I)
        if m:
            current = m.group(1).upper()
            continue
        if current and line.lstrip().startswith("-"):
            item = line.lstrip()[1:].strip()
            if item and not item.startswith("<"):
                sections[current].append(item)
    if not any(sections.values()):
        return False, "delta requires at least one populated ADDED/MODIFIED/REMOVED bullet"
    return True, "ok"


def parse_scope(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError("scope.txt missing")
    out = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        s = s.replace("\\", "/")
        pp = PurePosixPath(s)
        if pp.is_absolute() or ".." in pp.parts or s.startswith(".git/") or s == ".git":
            raise ValueError(f"unsafe scope pattern: {s}")
        if s not in out:
            out.append(s)
    if not out:
        raise ValueError("scope.txt has no paths/globs")
    return out


def scope_match(rel: str, patterns: list[str]) -> bool:
    rel = rel.replace("\\", "/")
    for pat in patterns:
        if fnmatch.fnmatchcase(rel, pat):
            return True
        if pat.endswith("/**") and rel.startswith(pat[:-3].rstrip("/") + "/"):
            return True
        if not any(c in pat for c in "*?[") and (rel == pat or rel.startswith(pat.rstrip("/") + "/")):
            return True
    return False


def risk_valid_value(r: dict, scope: list[str]) -> tuple[bool, str, dict]:
    if r.get("risk_level") not in {"trivial", "standard", "high"}: return False, "risk_level must be trivial|standard|high", r
    for k in ("control_plane_change", "security_privacy_sensitive", "migration_or_release_sensitive", "high_blast_radius", "requires_exec_plan"):
        if not isinstance(r.get(k), bool): return False, f"{k} must be boolean", r
    touches_cp = any(p in CONTROL_PLANE_FILES or p.startswith(CONTROL_PLANE_PREFIXES) for p in scope)
    if touches_cp and not r.get("control_plane_change"): return False, "scope touches control-plane files but control_plane_change=false", r
    return True, "ok", r


def risk_valid(path: Path, scope: list[str]) -> tuple[bool, str, dict]:
    if not path.is_file():
        return False, "risk.json missing", {}
    try:
        r = read_json(path)
    except Exception as e:
        return False, f"risk.json invalid: {e}", {}
    if r.get("risk_level") not in {"trivial", "standard", "high"}:
        return False, "risk_level must be trivial|standard|high", r
    for k in ("control_plane_change", "security_privacy_sensitive", "migration_or_release_sensitive", "high_blast_radius", "requires_exec_plan"):
        if not isinstance(r.get(k), bool):
            return False, f"{k} must be boolean", r
    touches_cp = any(p in CONTROL_PLANE_FILES or p.startswith(CONTROL_PLANE_PREFIXES) for p in scope)
    if touches_cp and not r.get("control_plane_change"):
        return False, "scope touches control-plane files but control_plane_change=false", r
    if r.get("risk_level") == "trivial" and any(r.get(k) for k in ("control_plane_change", "security_privacy_sensitive", "migration_or_release_sensitive", "high_blast_radius", "requires_exec_plan")):
        return False, "trivial risk cannot carry consequential flags", r
    return True, "ok", r


def effects_valid(path: Path) -> tuple[bool, str, dict]:
    if not path.is_file():
        return False, "effects.json missing", {}
    try:
        e = read_json(path)
    except Exception as ex:
        return False, f"effects.json invalid: {ex}", {}
    if not isinstance(e.get("external_effects"), list) or not all(isinstance(x, str) and x.strip() for x in e.get("external_effects", [])):
        return False, "external_effects must be a list of non-empty strings", e
    if not isinstance(e.get("irreversible"), bool) or not isinstance(e.get("authorization_required"), bool):
        return False, "effects irreversible/authorization_required must be booleans", e
    capabilities = e.get("effect_capabilities", [])
    if not isinstance(capabilities, list) or any(not isinstance(x, str) or not x.strip() for x in capabilities):
        return False, "effect_capabilities must be a list of non-empty strings", e
    contract_path = path.parents[3] / ".keel" / "contracts.json"
    try:
        allowed = set(read_json(contract_path).get("effect_capabilities", []))
    except Exception as ex:
        return False, f"effect capability contract invalid: {ex}", e
    unknown = sorted(set(capabilities) - allowed)
    if unknown:
        return False, "unknown effect capabilities: " + ", ".join(unknown), e
    if (e.get("external_effects") or e.get("irreversible")) and not e.get("authorization_required"):
        return False, "external or irreversible effects require authorization_required=true", e
    if (e.get("external_effects") or e.get("irreversible")) and not capabilities:
        return False, "external or irreversible effects require effect_capabilities", e
    return True, "ok", e


def authorization_shape_valid(path: Path, authorization_required: bool, expected_effects_digest: str | None = None) -> tuple[bool, str, dict]:
    if not path.is_file():
        return False, "authorization.json missing", {}
    try:
        a = read_json(path)
    except Exception as ex:
        return False, f"authorization.json invalid: {ex}", {}
    for key in ("required", "authorized"):
        if not isinstance(a.get(key), bool):
            return False, f"authorization {key} must be boolean", a
    if bool(a.get("required")) != bool(authorization_required):
        return False, "authorization.required must match effects.authorization_required", a
    for key in ("authority", "scope", "evidence_reference"):
        if not isinstance(a.get(key), str):
            return False, f"authorization {key} must be a string", a
    if not isinstance(a.get("effects_digest", ""), str):
        return False, "authorization effects_digest must be a string", a
    if expected_effects_digest is not None and a.get("effects_digest") != expected_effects_digest:
        return False, "authorization is not bound to the current effects.json", a
    return True, "ok", a


def sync_authorization_shape(root: Path, change_id: str, invalidate: bool = False) -> dict:
    """Make authorization shape follow effects deterministically without granting permission."""
    d = ledger_dir(root, change_id)
    ok, msg, effects = effects_valid(d / "effects.json")
    if not ok:
        raise RuntimeError(msg)
    required = bool(effects.get("authorization_required"))
    eff_digest = canonical_json_digest(effects)
    current = {}
    ap = d / "authorization.json"
    if ap.is_file():
        try:
            current = read_json(ap)
        except Exception:
            current = {}
    preserve = (
        not invalidate
        and required
        and current.get("required") is True
        and current.get("authorized") is True
        and current.get("effects_digest") == eff_digest
    )
    if preserve:
        return current
    value = {
        "required": required,
        "authorized": False,
        "authority": "",
        "scope": "",
        "evidence_reference": "",
        "effects_digest": eff_digest,
    }
    write_json(ap, value)
    return value


def authorization_ship_errors(root: Path, change_id: str) -> list[str]:
    d = ledger_dir(root, change_id)
    if (d / "intent.json").is_file():
        intent=canonical_ledger.load_intent(d); requested=[r for r in intent.get("effect_requests",[]) if r.get("authorization_required") is True]
        if not requested: return []
        grants=list((d/"grants").glob("*.json"))
        return [] if grants else ["effect requests require a script-recorded CapabilityGrant"]
    ok, msg, e = effects_valid(d / "effects.json")
    if not ok:
        return [msg]
    eff_digest = canonical_json_digest(e)
    ok, msg, a = authorization_shape_valid(d / "authorization.json", bool(e.get("authorization_required")), eff_digest)
    if not ok:
        return [msg]
    if not e.get("authorization_required"):
        return []
    errors = []
    if not a.get("authorized"):
        errors.append("external/irreversible effect authorization has not been recorded")
    if len(a.get("authority", "").strip()) < 2:
        errors.append("authorization authority is missing")
    if len(a.get("scope", "").strip()) < 8:
        errors.append("authorization scope is too vague")
    if len(a.get("evidence_reference", "").strip()) < 3:
        errors.append("authorization evidence_reference is missing")
    return errors


def risk_requires_review(r: dict) -> bool:
    return r.get("risk_level") == "high" or any(r.get(k) for k in ("control_plane_change", "security_privacy_sensitive", "migration_or_release_sensitive", "high_blast_radius"))


def validate_plan(root: Path, change_id: str) -> list[str]:
    d = ledger_dir(root, change_id)
    if (d / "intent.json").is_file():
        intent = canonical_ledger.load_intent(d); errors = canonical_ledger.validate_intent(intent, require_planned=True)
        requirements, acceptance = canonical_ledger.contracts(intent)
        # Reuse the stable legacy contract validator through ephemeral in-memory-equivalent files in views.
        write_json(d / "views" / "requirements.json", requirements); write_json(d / "views" / "acceptance.json", acceptance)
        errors.extend(evidence_graph.validate_contract(d / "views" / "requirements.json", d / "views" / "acceptance.json", require_nonempty=(intent["mode"] != "trivial"), contracts_path=root / ".keel" / "contracts.json"))
        r=canonical_ledger.risk(intent); scope=intent["scope"]
        ok,msg,r=risk_valid_value(r,scope)
        if not ok: errors.append(msg)
        if risk_requires_review(r) and len(str(intent.get("risk",{}).get("review","")).strip()) < 40: errors.append("high/control-plane/sensitive change requires substantive intent risk.review")
        if r.get("requires_exec_plan") and not (root / "docs" / "exec-plans" / "active" / f"{change_id}.md").is_file(): errors.append(f"required ExecPlan missing: docs/exec-plans/active/{change_id}.md")
        return errors
    errors = []
    ok, msg = meaningful_proposal(d / "proposal.md")
    if not ok: errors.append(msg)
    ok, msg = delta_valid(d / "delta.md")
    if not ok: errors.append(msg)
    mode = state(root, change_id).get("mode", "standard")
    errors.extend(evidence_graph.validate_contract(d / "requirements.json", d / "acceptance.json", require_nonempty=(mode != "trivial"), contracts_path=root / ".keel" / "contracts.json"))
    try:
        scope = parse_scope(d / "scope.txt")
    except Exception as e:
        errors.append(str(e)); scope = []
    ok, msg, r = risk_valid(d / "risk.json", scope)
    if not ok: errors.append(msg)
    ok, msg, e = effects_valid(d / "effects.json")
    if not ok:
        errors.append(msg)
        e = {}
    expected = canonical_json_digest(e) if e else None
    ok, msg, _ = authorization_shape_valid(d / "authorization.json", bool(e.get("authorization_required")), expected)
    if not ok: errors.append(msg)
    if r and risk_requires_review(r):
        rp = d / "risk-review.md"
        material = "" if not rp.is_file() else " ".join(x.strip() for x in rp.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip() and not x.startswith("#"))
        if len(material) < 40 or material.startswith("Not required"):
            errors.append("high/control-plane/sensitive change requires substantive risk-review.md")
    if r and r.get("requires_exec_plan"):
        ep = root / "docs" / "exec-plans" / "active" / f"{change_id}.md"
        if not ep.is_file():
            errors.append(f"required ExecPlan missing: {ep.relative_to(root)}")
    return errors


def changed_paths(root: Path, base: str) -> list[str]:
    return git_proof.changed_paths(root, base)


def is_system_artifact(rel: str, change_id: str) -> bool:
    prefixes = [f".keel/ledger/{change_id}/"]
    if change_id and not change_id.startswith("retro-"):
        prefixes.append(f".keel/ledger/retro-{change_id}/")
    return rel == ".keel/active-change" or rel.startswith(".keel/audit/") or any(rel.startswith(p) for p in prefixes)


def diff_scope_errors(root: Path, change_id: str) -> tuple[list[str], list[str]]:
    st = state(root, change_id)
    base = st.get("base_commit")
    if not base:
        return ["state missing base_commit"], []
    d = ledger_dir(root, change_id)
    scope = canonical_ledger.load_intent(d)["scope"] if (d / "intent.json").is_file() else parse_scope(d / "scope.txt")
    paths = changed_paths(root, base)
    material = [p for p in paths if not is_system_artifact(p, change_id)]
    bad = [p for p in material if not scope_match(p, scope)]
    return [f"out-of-scope path: {p}" for p in bad], material


def content_digest(root: Path, change_id: str) -> str:
    errs, paths = diff_scope_errors(root, change_id)
    if errs:
        raise RuntimeError("; ".join(errs))
    h = hashlib.sha256()
    for rel in sorted(paths):
        h.update(("material:" + rel).encode()); h.update(b"\0")
        mode, data = worktree_entry(root, rel)
        h.update(mode.encode()); h.update(b"\0"); h.update(data)
        h.update(b"\0")
    d = ledger_dir(root, change_id)
    for name in intent_files(root, change_id):
        h.update(("intent:" + name).encode()); h.update(b"\0")
        rel = f".keel/ledger/{change_id}/{name}"
        mode, data = worktree_entry(root, rel)
        h.update(mode.encode()); h.update(b"\0"); h.update(data)
        h.update(b"\0")
    return h.hexdigest()


def worktree_entry(root: Path, rel: str) -> tuple[str, bytes]:
    """Return the Git-relevant mode/content representation of a worktree path."""
    return git_proof.worktree_entry(root, rel)


def commit_changed_paths(root: Path, base: str, commit: str, change_id: str) -> list[str]:
    return [x for x in git_proof.changed_paths(root, base, commit) if not is_system_artifact(x, change_id)]


def git_tree_entry(root: Path, commit: str, rel: str) -> tuple[str, bytes]:
    # `ls-tree -z` is path-safe for spaces and lets us distinguish blobs, symlinks,
    # executable files, gitlinks, and verified deletions.
    return git_proof.tree_entry(root, commit, rel)


def tree_digest(root: Path, change_id: str, commit: str, material_paths: list[str]) -> str:
    """Recompute the verification digest from a Git tree, independent of working files."""
    h = hashlib.sha256()
    for rel in sorted(material_paths):
        h.update(("material:" + rel).encode()); h.update(b"\0")
        mode, data = git_tree_entry(root, commit, rel)
        h.update(mode.encode()); h.update(b"\0"); h.update(data); h.update(b"\0")
    for name in intent_files(root, change_id):
        rel = f".keel/ledger/{change_id}/{name}"
        h.update(("intent:" + name).encode()); h.update(b"\0")
        mode, data = git_tree_entry(root, commit, rel)
        h.update(mode.encode()); h.update(b"\0"); h.update(data); h.update(b"\0")
    return h.hexdigest()


def show_commit_json(root: Path, commit: str, change_id: str, name: str) -> dict:
    return git_proof.show_json(root, commit, f".keel/ledger/{change_id}/{name}")


def verify_commit_tree(root: Path, change_id: str, commit: str, require_exact_diff: bool) -> tuple[str, dict, dict, str]:
    """Verify a committed tree against KEEL evidence; optionally require its whole diff to be the candidate."""
    validate_id(change_id)
    sha = git_proof.resolve_commit(root, commit)
    canonical = run_git(root, ["cat-file", "-e", f"{sha}:.keel/ledger/{change_id}/intent.json"], check=False).returncode == 0
    if canonical:
        intent = show_commit_json(root, sha, change_id, "intent.json")
        events_raw = run_git(root, ["show", f"{sha}:.keel/ledger/{change_id}/events.jsonl"]).stdout
        events = [json.loads(line) for line in events_raw.splitlines() if line]
        current = None
        mapping = {"START":"DISCUSS","DISCUSS":"PLAN","PLAN":"EXECUTE","REPLAN":"PLAN","REOPEN":"EXECUTE","VERIFY_PASS":"SHIP","VERIFY_FAIL":"EXECUTE"}
        for event in events:
            if event.get("kind") in mapping and (event.get("result") in {"PASS","RECORDED"} or event.get("kind") in {"START","REPLAN","REOPEN","VERIFY_PASS","VERIFY_FAIL"}): current = mapping[event["kind"]]
        ver = show_commit_json(root, sha, change_id, "views/verification.json")
        st = {"change_id":change_id,"base_commit":intent["base_commit"],"phase":current,"verified_content_digest":ver.get("content_digest")}
    else:
        st = show_commit_json(root, sha, change_id, "state.json")
        ver = show_commit_json(root, sha, change_id, "verification.json")
    if st.get("change_id") != change_id:
        raise RuntimeError("committed state change_id mismatch")
    if st.get("phase") != "SHIP":
        raise RuntimeError(f"committed ledger phase must be SHIP, got {st.get('phase')}")
    if ver.get("status") != "PASS":
        raise RuntimeError("committed verification status is not PASS")
    if st.get("base_commit") != ver.get("base_commit"):
        raise RuntimeError("committed state/verification base commit mismatch")
    if st.get("verified_content_digest") != ver.get("content_digest"):
        raise RuntimeError("committed state/verification digest mismatch")
    paths = ver.get("changed_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(x, str) and x for x in paths):
        raise RuntimeError("committed verification changed_paths invalid")
    if len(paths) != len(set(paths)):
        raise RuntimeError("committed verification changed_paths contains duplicates")
    if require_exact_diff:
        actual = commit_changed_paths(root, st["base_commit"], sha, change_id)
        if actual != sorted(paths):
            raise RuntimeError(f"candidate commit diff does not match verified changed_paths: expected={sorted(paths)} actual={actual}")
    dig = tree_digest(root, change_id, sha, paths)
    if dig != ver.get("content_digest"):
        raise RuntimeError("independent Git-tree digest does not match verification evidence")
    return sha, st, ver, dig


def candidate_ref(change_id: str) -> str:
    return CANDIDATE_REF_PREFIX + validate_id(change_id)


def candidate_status(root: Path, change_id: str) -> dict:
    ref = candidate_ref(change_id)
    p = run_git(root, ["show-ref", "--hash", "--verify", ref], check=False)
    if p.returncode != 0:
        raise RuntimeError(f"sealed candidate missing: {ref}")
    sha, st, ver, dig = verify_commit_tree(root, change_id, p.stdout.strip(), require_exact_diff=True)
    result = {"change_id": change_id, "ref": ref, "commit": sha, "content_digest": dig, "base_commit": st.get("base_commit"), "changed_paths": ver.get("changed_paths")}
    attestation_ref = candidate_attestation.ATTESTATION_REF_PREFIX + change_id
    attestation_exists = run_git(root, ["show-ref", "--verify", attestation_ref], check=False).returncode == 0
    if attestation_exists:
        attestation = candidate_attestation.read_attestation(root, change_id)
        expected = candidate_attestation.build(root, change_id, sha, st, ver, intent_files(root, change_id))
        if attestation.digest != expected.digest:
            raise RuntimeError("sealed CandidateAttestation differs from committed candidate proof")
        result.update({"attestation_ref": attestation_ref, "attestation_digest": attestation.digest})
    return result


def seal_candidate(root: Path, change_id: str, commit: str) -> dict:
    ok, msg = current_verified(root, change_id)
    if not ok:
        raise RuntimeError("cannot seal stale/unverified working state: " + msg)
    sha, committed_state, committed_verification, dig = verify_commit_tree(root, change_id, commit, require_exact_diff=True)
    head = head_commit(root)
    if head != sha:
        raise RuntimeError(f"seal candidate must name current HEAD ({head}), got {sha}")
    ref = candidate_ref(change_id)
    old = run_git(root, ["show-ref", "--hash", "--verify", ref], check=False)
    if old.returncode == 0 and old.stdout.strip() != sha:
        raise RuntimeError(f"KEEL candidate ref collision: {ref} already points to {old.stdout.strip()}")
    attestation = candidate_attestation.build(root, change_id, sha, committed_state, committed_verification, intent_files(root, change_id))
    attestation_ref = candidate_attestation.ATTESTATION_REF_PREFIX + change_id
    candidate_attestation.write_attestation_object(root, attestation, attestation_ref)
    if old.returncode != 0:
        z = "0" * 40
        p = run_git(root, ["update-ref", ref, sha, z], check=False)
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip() or "git update-ref candidate failed")
    audit_dir = root / ".keel" / "audit"; audit_dir.mkdir(parents=True, exist_ok=True)
    with (audit_dir / "candidates.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": now(), "change_id": change_id, "candidate_commit": sha, "ref": ref, "content_digest": dig,
                            "attestation_ref": attestation_ref, "attestation_digest": attestation.digest,
                            "attestation": attestation.as_dict()}, sort_keys=True) + "\n")
    return candidate_status(root, change_id)


def source_change_present(root: Path, change_id: str) -> bool:
    """Conservatively decide whether changed material needs executable verification.

    Explicit project classifiers win. Known source/toolchain patterns come next. Unknown
    material is treated as substantive unless it is clearly documentation-only.
    """
    cfg = read_json(root / ".keel" / "config.json")
    _, paths = diff_scope_errors(root, change_id)
    for rel in paths:
        cls = capability_resolver.classify_path(rel, cfg)
        if cls == "SOURCE":
            return True
        if cls == "UNKNOWN":
            # Conservative unknown: do not let an unfamiliar DSL/build/runtime artifact
            # evade verification merely because KEEL has never seen its extension.
            return True
    return False


def redact(text: str) -> str:
    # Conservative line-level redaction for common secret assignments/tokens.
    patterns = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|authorization)(\s*[:=]\s*)([^\s,;]+)"),
        re.compile(r"\b(sk-[A-Za-z0-9_-]{10,})\b"),
    ]
    out = text
    for p in patterns:
        if p.groups >= 3:
            out = p.sub(lambda m: m.group(1) + m.group(2) + "<REDACTED>", out)
        else:
            out = p.sub("<REDACTED>", out)
    return out


def agents_lint(root: Path) -> list[str]:
    cfg = read_json(root / ".keel" / "config.json")
    max_bytes = int(cfg.get("max_agents_cascade_bytes", 32768))
    max_lines = int(cfg.get("root_agents_max_lines", 100))
    errors = []
    root_agents = root / "AGENTS.md"
    if not root_agents.is_file():
        errors.append("root AGENTS.md missing")
    else:
        if len(root_agents.read_text(encoding="utf-8", errors="replace").splitlines()) > max_lines:
            errors.append(f"root AGENTS.md exceeds {max_lines} lines")
    chosen = {}
    dirs = {root}
    for p in root.rglob("AGENTS*.md"):
        if ".git" in p.parts:
            continue
        dirs.add(p.parent)
    for d in dirs:
        override = d / "AGENTS.override.md"
        normal = d / "AGENTS.md"
        p = override if override.is_file() else normal if normal.is_file() else None
        if p:
            text = p.read_text(encoding="utf-8", errors="replace")
            if PLACEHOLDER_RE.search(text):
                errors.append(f"unresolved instruction placeholder: {p.relative_to(root)}")
            chosen[d.resolve()] = (p, len(p.read_bytes()))
    max_seen = 0
    max_where = root
    for d in dirs:
        try:
            rel_parts = d.resolve().relative_to(root.resolve()).parts
        except ValueError:
            continue
        cur = root.resolve(); total = 0
        if cur in chosen: total += chosen[cur][1]
        for part in rel_parts:
            cur = cur / part
            if cur in chosen: total += chosen[cur][1]
        if total > max_seen:
            max_seen, max_where = total, d
    if max_seen > max_bytes:
        errors.append(f"AGENTS cascade reaches {max_seen} bytes at {max_where.relative_to(root)} > {max_bytes}")
    return errors



def preexisting_worktree_changes(root: Path) -> list[str]:
    base = head_commit(root)
    paths = changed_paths(root, base)
    ignored_runtime = {".keel/active-change", ".control-plane/validation.json", ".control-plane/runtime-validation.json"}
    return [p for p in paths if p not in ignored_runtime and not p.startswith(".keel/audit/")]

def doctor(root: Path) -> list[str]:
    errors = []
    for rel in ("AGENTS.md", ".codex/hooks.json", ".codex/config.toml", ".keel/config.json", ".keel/bin/keel.py", ".keel/hooks/keel_hook.py", ".keel/lib/capability_resolver.py", ".keel/lib/context_compiler.py", ".keel/lib/evidence_graph.py", ".keel/lib/evidence_system.py", ".keel/bin/keelbench.py"):
        if not (root / rel).is_file(): errors.append(f"missing {rel}")
    try:
        head_commit(root)
    except Exception as e:
        errors.append(str(e))
    try:
        json.loads((root / ".codex/hooks.json").read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"hooks.json invalid: {e}")
    try:
        cfg = read_json(root / ".keel/config.json")
        if cfg.get("schema_version") != 2: errors.append("unsupported .keel/config.json schema_version")
        errors.extend(evidence_system.validate_registry(cfg.get("verifier_registry", [])))
    except Exception as e:
        errors.append(f"KEEL config invalid: {e}")
    errors.extend(agents_lint(root))
    return errors


def start_change(root: Path, change_id: str, mode: str = "standard", summary: str | None = None, scopes: list[str] | None = None) -> None:
    change_id = validate_id(change_id)
    if mode not in {"standard", "trivial"}:
        raise ValueError("mode must be standard|trivial")
    scopes = scopes or []
    if mode == "trivial" and (not summary or len(summary.strip()) < 12 or not scopes):
        raise ValueError("trivial mode requires --summary and at least one --scope")
    base = head_commit(root)
    existing = active_change(root)
    if existing and existing != change_id:
        raise RuntimeError(f"another KEEL change is active: {existing}")
    dirty = preexisting_worktree_changes(root)
    if dirty:
        raise RuntimeError("refusing to absorb pre-existing worktree changes into a new KEEL change: " + ", ".join(dirty[:12]))
    d = ledger_dir(root, change_id)
    if d.exists() and any(d.iterdir()):
        raise RuntimeError(f"ledger already exists: {change_id}; resume it instead of recreating")
    intent = canonical_ledger.blank_intent(change_id, base, mode, summary, scopes)
    canonical_ledger.create(d, intent)
    atomic_write(active_file(root), change_id + "\n")
    st = state(root, change_id)
    if mode == "trivial":
        append_event(root, change_id, "DISCUSS", "PASS", {"mode": "trivial-fast-path"})
        append_event(root, change_id, "PLAN", "PASS", {"mode": "trivial-fast-path"})


def gate(root: Path, change_id: str, which: str) -> None:
    st = state(root, change_id)
    d = ledger_dir(root, change_id)
    which = which.lower()
    if which == "discuss":
        if st.get("phase") != "DISCUSS": raise RuntimeError(f"discuss gate requires DISCUSS, got {st.get('phase')}")
        ok, msg = ((len(canonical_ledger.load_intent(d).get("objective","").strip()) >= 12), "intent objective is too thin") if (d / "intent.json").is_file() else meaningful_proposal(d / "proposal.md")
        if not ok: append_event(root, change_id, "DISCUSS", "FAIL", {"reason": msg}); raise RuntimeError(msg)
        st["phase"] = "PLAN"; write_state(root, change_id, st); append_event(root, change_id, "DISCUSS", "PASS")
    elif which == "plan":
        if st.get("phase") != "PLAN": raise RuntimeError(f"plan gate requires PLAN, got {st.get('phase')}")
        # The model may declare effects during PLAN, but permission state is script-owned.
        # Synchronization can only clear/invalidate authorization; it never grants it.
        if not (d / "intent.json").is_file(): sync_authorization_shape(root, change_id, invalidate=False)
        errs = validate_plan(root, change_id)
        if errs: append_event(root, change_id, "PLAN", "FAIL", {"errors": errs}); raise RuntimeError("; ".join(errs))
        st["phase"] = "EXECUTE"; write_state(root, change_id, st); append_event(root, change_id, "PLAN", "PASS")
    else:
        raise ValueError("supported gates: discuss, plan")



def replan(root: Path, change_id: str) -> None:
    st = state(root, change_id)
    if st.get("phase") not in {"EXECUTE", "VERIFY", "SHIP"}:
        raise RuntimeError(f"replan requires EXECUTE/VERIFY/SHIP, got {st.get('phase')}")
    st["phase"] = "PLAN"
    st.pop("verified_content_digest", None)
    write_state(root, change_id, st)
    d = ledger_dir(root, change_id)
    cleanup = d / "views" if (d / "intent.json").is_file() else d
    for n in ("verification.json", "verification.md", "evidence-graph.json", "evidence-plan.json", "evidence-receipts.json"):
        p = cleanup / n
        if p.exists(): p.unlink()
    if (d / "intent.json").is_file():
        for grant in (d / "grants").glob("*.json"): grant.unlink()
    else:
        # Any legacy intent/scope change requires fresh consequence authorization.
        try: sync_authorization_shape(root, change_id, invalidate=True)
        except Exception: write_json(d / "authorization.json", {"required": False, "authorized": False, "authority": "", "scope": "", "evidence_reference": "", "effects_digest": ""})
    append_event(root, change_id, "REPLAN", "PASS")


def record_authorization(root: Path, change_id: str, authority: str, scope: str, evidence_reference: str) -> None:
    d = ledger_dir(root, change_id)
    _, msg, e = effects_valid(d / "effects.json")
    if msg != "ok":
        raise RuntimeError(msg)
    if not e.get("authorization_required"):
        raise RuntimeError("effects.json does not declare authorization_required=true")
    if len(authority.strip()) < 2 or len(scope.strip()) < 8 or len(evidence_reference.strip()) < 3:
        raise RuntimeError("authorization record requires concrete authority, scope, and evidence reference")
    write_json(d / "authorization.json", {
        "required": True,
        "authorized": True,
        "authority": authority.strip(),
        "scope": scope.strip(),
        "evidence_reference": evidence_reference.strip(),
        "effects_digest": canonical_json_digest(e),
        "recorded_at": now(),
    })
    append_event(root, change_id, "AUTHORIZATION", "RECORDED", {"authority": authority.strip(), "scope": scope.strip(), "evidence_reference": evidence_reference.strip()})

def verify_change(root: Path, change_id: str) -> dict:
    """Plan and execute receipt-authoritative verification, then emit legacy views."""
    st = state(root, change_id)
    if st.get("phase") not in {"EXECUTE", "VERIFY"}:
        raise RuntimeError(f"verify requires EXECUTE/VERIFY, got {st.get('phase')}")
    errs = validate_plan(root, change_id)
    errs.extend(authorization_ship_errors(root, change_id))
    scope_errs, material = diff_scope_errors(root, change_id); errs.extend(scope_errs)
    if not material: errs.append("no material changed paths since KEEL base commit")
    errs.extend(doctor(root))
    d = ledger_dir(root, change_id); cfg = read_json(root / ".keel/config.json")
    registry = cfg.get("verifier_registry", [])
    registry_errors = evidence_system.validate_registry(registry); errs.extend(registry_errors)
    intent = canonical_ledger.load_intent(d) if (d / "intent.json").is_file() else None
    requirements, acceptance = canonical_ledger.contracts(intent) if intent else (read_json(d / "requirements.json"), read_json(d / "acceptance.json"))
    ers = evidence_system.evidence_requirements(requirements, acceptance)
    risk = canonical_ledger.risk(intent).get("risk_level", "standard") if intent else read_json(d / "risk.json").get("risk_level", "standard")
    plan_value = evidence_system.plan(registry, ers, material, risk, {"source_change": source_change_present(root, change_id)})
    plan_path = d / "views" / "evidence-plan.json" if intent else d / "evidence-plan.json"
    write_json(plan_path, plan_value)
    if plan_value["status"] != "PASS": errs.extend(plan_value["errors"])
    digest = None
    if not scope_errs:
        try: digest = content_digest(root, change_id)
        except Exception as e: errs.append(f"content digest failed: {e}")
    intent_value = {name: worktree_entry(root, f".keel/ledger/{change_id}/{name}")[1].decode("utf-8", errors="surrogateescape") for name in intent_files(root, change_id)}
    intent_digest = evidence_system.canonical_digest(intent_value)
    head = run_git(root, ["rev-parse", "HEAD"], check=False).stdout.strip()
    subject = {"kind":"git-worktree","base_commit":st["base_commit"],"head_commit":head,"content_digest":digest,"changed_paths":material}
    by_id = {v["id"]:v for v in registry if isinstance(v,dict) and "id" in v}
    results, receipts = [], []
    for step in plan_value.get("steps", []) if plan_value["status"] == "PASS" else []:
        v = by_id[step["verifier_id"]]; runtime = dict(step["runtime"])
        argv = [x.replace("{base_commit}", st["base_commit"]) for x in runtime["argv"]]
        runtime["argv"] = argv; executed_step = {**step, "runtime":runtime}
        command = {"id":v["id"],"argv":argv,"cwd":runtime.get("cwd","."),"authorized":True}
        resolution = p0_contract.resolve_command(root, command, authorized=True)
        started = evidence_system.utc_now(); t0=time.monotonic(); code=None; out=""
        if resolution["status"] == p0_contract.PASS:
            cwd=(root/runtime.get("cwd",".")).resolve()
            try: cwd.relative_to(root.resolve())
            except ValueError: resolution={"status":"INVALID","reason":"cwd escapes root"}
            else:
                try:
                    proc=subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=int(runtime.get("timeout_sec",600)))
                    code=proc.returncode; out=proc.stdout+("\n" if proc.stdout and proc.stderr else "")+proc.stderr
                except subprocess.TimeoutExpired as e:
                    code=124; out=(e.stdout or "")+"\n"+(e.stderr or "")
        elapsed=int((time.monotonic()-t0)*1000); ended=evidence_system.utc_now()
        literal="PASS" if code == 0 else "FAIL" if code is not None else "INCONCLUSIVE"
        excerpt=redact("\n".join(out.splitlines()[-20:]))[-8000:]
        observations=[{"kind":"command-result","exit_code":code,"duration_ms":elapsed,"excerpt":excerpt,"resolution":resolution}]
        receipts.append(evidence_system.receipt(v,executed_step,subject,intent_digest,literal,observations,started,ended))
        results.append({"id":v["id"],"argv":argv,"cwd":runtime.get("cwd","."),"exit_code":code,"duration_ms":elapsed,"required":True,"excerpt":excerpt,"resolution":resolution})
    if intent:
        for n, receipt in enumerate(receipts): canonical_ledger.record(d, "receipts", {**receipt, "receipt_id": receipt.get("receipt_digest") or f"receipt-{n+1}"}, "receipt_id")
        write_json(d / "views" / "evidence-receipts.json", {"schema_version":1,"subject":subject,"intent_digest":intent_digest,"receipts":receipts,"generated":True})
    else: write_json(d / "evidence-receipts.json", {"schema_version":1,"subject":subject,"intent_digest":intent_digest,"receipts":receipts})
    evaluation=evidence_system.evaluate(plan_value,receipts,ers,subject,intent_digest)
    if evaluation["status"] != "PASS": errs.extend(evaluation["errors"] or ["receipt evidence is inconclusive"])
    # Compatibility only: old consumers may read these projections, but they grant no authority.
    graph_projection={"schema_version":2,"projection_of":"evidence-receipts.json","status":"PASS" if evaluation["status"]=="PASS" else "FAIL","change_type":requirements.get("change_type","implementation"),"verification_class":"IMPLEMENTATION_ACCEPTANCE","implementation_status":"PASS" if evaluation["status"]=="PASS" else "NOT_VERIFIED","errors":evaluation["errors"],"criteria":[],"requirement_coverage":evaluation["coverage"],"summary":{"required":evaluation["summary"]["required"],"passed_required":evaluation["summary"]["established"],"requirements_total":len(ers),"requirements_covered":evaluation["summary"]["established"],"requirements_passing":evaluation["summary"]["established"]}}
    write_json(d / "views" / "evidence-graph.json" if intent else d / "evidence-graph.json", graph_projection)
    status="PASS" if not errs else "FAIL"; change_type=requirements.get("change_type","implementation"); implementation_status="PASS" if evaluation["status"]=="PASS" else "NOT_VERIFIED"
    evidence={"schema_version":4,"authority":"evidence-receipts.json","compatibility_projection":True,"change_id":change_id,"base_commit":st["base_commit"],"verified_at":now(),"status":status,"verification_class":"IMPLEMENTATION_ACCEPTANCE","change_type":change_type,"implementation_status":implementation_status,"content_digest":digest,"intent_digest":intent_digest,"evidence_plan_digest":plan_value["plan_digest"],"changed_paths":material,"errors":sorted(set(errs)),"checks":results,"acceptance":graph_projection["summary"]}
    write_json(d / "views" / "verification.json" if intent else d / "verification.json",evidence)
    md=["# Verification","",f"Status: `{status}`",f"Authority: `evidence-receipts.json`",f"Subject digest: `{digest or 'UNAVAILABLE'}`",f"Intent digest: `{intent_digest}`","","## Selected verifiers"]+[f"- `{r['id']}` exit `{r['exit_code']}` ({r['duration_ms']} ms)" for r in results]+["","## Receipt coverage"]+[f"- `{c['evidence_requirement_id']}` `{c['status']}` via `{c['verifier_id']}`" for c in evaluation["coverage"]]
    if errs: md += ["","## Blockers"]+[f"- {e}" for e in sorted(set(errs))]
    atomic_write(d / "views" / "verification.md" if intent else d / "verification.md","\n".join(md)+"\n")
    append_event(root,change_id,"EXECUTE","PASS" if not scope_errs else "FAIL",{"changed_paths":material,"scope_errors":scope_errs}); append_event(root,change_id,"VERIFY",status,{"content_digest":digest,"errors":sorted(set(errs)),"evidence_plan_digest":plan_value["plan_digest"]})
    authority=status=="PASS" and (change_type=="planning_only" or implementation_status=="PASS")
    if authority: st["phase"]="SHIP"; st["verified_content_digest"]=digest
    else: st["phase"]="EXECUTE"; st.pop("verified_content_digest",None)
    write_state(root,change_id,st); return evidence


def current_verified(root: Path, change_id: str) -> tuple[bool, str]:
    st = state(root, change_id)
    if st.get("phase") != "SHIP": return False, f"phase is {st.get('phase')}, not SHIP"
    d = ledger_dir(root, change_id)
    vpath = d / "views" / "verification.json" if (d / "intent.json").is_file() else d / "verification.json"
    if not vpath.is_file(): return False, "verification.json missing"
    v = read_json(vpath)
    if v.get("status") != "PASS": return False, "verification status is not PASS"
    if v.get("change_type", "implementation") != "planning_only" and v.get("implementation_status") != "PASS":
        return False, "implementation acceptance is not PASS"
    try: dig = content_digest(root, change_id)
    except Exception as e: return False, str(e)
    if dig != v.get("content_digest") or dig != st.get("verified_content_digest"):
        return False, "content changed after verification; reopen and verify again"
    return True, "ok"


def anchored_status(root: Path, change_id: str) -> tuple[str, str]:
    """Classify sealed-candidate evidence without rewriting the preserved ledger phase."""
    try:
        candidate = candidate_status(root, change_id)
    except Exception as exc:
        return "invalid", f"sealed candidate evidence is invalid: {exc}"

    landed_ref = f"refs/keel/ledger/{change_id}"
    landed = run_git(root, ["show-ref", "--hash", "--verify", landed_ref], check=False)
    if landed.returncode != 0:
        return "pending", f"landed ledger ref is missing: {landed_ref}"
    landed_sha = landed.stdout.strip()

    note = run_git(root, ["notes", "--ref=keel", "show", landed_sha], check=False)
    if note.returncode != 0:
        return "invalid", "landed commit KEEL note is missing"
    expected = {
        "keel-change-id": change_id,
        "sealed-candidate": candidate["commit"],
        "landed-commit": landed_sha,
        "verified-content-digest": candidate["content_digest"],
    }
    note_values = {}
    for line in note.stdout.splitlines():
        key, separator, value = line.partition(": ")
        if separator:
            note_values[key] = value
    mismatches = [key for key, value in expected.items() if note_values.get(key) != value]
    if mismatches:
        return "invalid", "landed KEEL note provenance mismatch: " + ", ".join(mismatches)

    audit_path = root / ".keel" / "audit" / "anchors.jsonl"
    if not audit_path.is_file():
        return "invalid", "anchor audit evidence is missing"
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            row.get("change_id") == change_id
            and row.get("candidate_commit") == candidate["commit"]
            and row.get("landed_commit") == landed_sha
            and row.get("content_digest") == candidate["content_digest"]
        ):
            return "anchored", "candidate and landed anchor evidence are consistent"
    return "invalid", "matching anchor audit evidence is missing"


def reopen(root: Path, change_id: str) -> None:
    st = state(root, change_id)
    if st.get("phase") not in {"VERIFY", "SHIP"}:
        raise RuntimeError(f"reopen requires VERIFY/SHIP, got {st.get('phase')}")
    st["phase"] = "EXECUTE"; st.pop("verified_content_digest", None); write_state(root, change_id, st)
    for n in ("verification.json", "verification.md", "evidence-graph.json", "evidence-plan.json", "evidence-receipts.json"):
        p = ledger_dir(root, change_id) / n
        if p.exists(): p.unlink()
    append_event(root, change_id, "REOPEN", "PASS")


def record_bypass(root: Path, change_id: str | None, reason: str, session_id: str = "unknown") -> None:
    reason = reason.strip()
    if len(reason) < 8:
        raise RuntimeError("KEEL_BYPASS_REASON must contain a concrete reason (>=8 chars)")
    audit_dir = root / ".keel" / "audit"; audit_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(f"{session_id}\0{change_id}\0{reason}".encode()).hexdigest()
    seen_path = audit_dir / "bypass-seen.json"
    seen = read_json(seen_path) if seen_path.is_file() else {}
    if key in seen: return
    seen[key] = now(); write_json(seen_path, seen)
    row = {"ts": now(), "session_id": session_id, "change_id": change_id, "reason": reason}
    with (audit_dir / "bypass.jsonl").open("a", encoding="utf-8") as f: f.write(json.dumps(row, sort_keys=True) + "\n")
    if change_id:
        append_event(root, change_id, "BYPASS", "AUDIT", {"reason": reason, "session_id": session_id})
        rid = "retro-" + change_id
        base_commit = state(root, change_id).get("base_commit")
    else:
        rid = "retro-emergency-" + hashlib.sha256(f"{session_id}\0{reason}".encode()).hexdigest()[:12]
        base_commit = head_commit(root)
    rd = ledger_dir(root, rid)
    if not rd.exists():
        rd.mkdir(parents=True)
        atomic_write(rd / "proposal.md", f"# Retro process debt\n\nEmergency KEEL bypass occurred{f' for `{change_id}`' if change_id else ''}. Reconstruct the actual delta, effects, evidence, authorization, and missing verification.\n\nReason: {reason}\n")
        atomic_write(rd / "delta.md", "## ADDED\n\n## MODIFIED\n- Reconstruct and validate emergency change after stabilization.\n\n## REMOVED\n")
        write_json(rd / "requirements.json", {"schema_version": 1, "requirements": [{"id":"REQ-RETRO","statement":"Reconstruct the emergency change intent, effects, and required recovery evidence","source":"emergency-bypass"}]})
        write_json(rd / "acceptance.json", {"schema_version": 1, "criteria": [{"id":"AC-RETRO","requirement_id":"REQ-RETRO","statement":"Retrospective evidence must explicitly verify the reconstructed emergency change","required":True,"policy":"all","evidence":[{"provider":"file_exists","path":f"docs/exec-plans/active/{rid}.md"}]}]})
        atomic_write(rd / "scope.txt", "# Populate from actual emergency diff during retrospective.\n")
        write_json(rd / "risk.json", {"risk_level":"high","control_plane_change":False,"security_privacy_sensitive":False,"migration_or_release_sensitive":True,"high_blast_radius":True,"requires_exec_plan":True})
        write_json(rd / "effects.json", {"external_effects":["Emergency action occurred; reconstruct exact effects"],"irreversible":False,"authorization_required":True})
        write_json(rd / "authorization.json", {"required":True,"authorized":False,"authority":"","scope":"","evidence_reference":""})
        atomic_write(rd / "risk-review.md", "# Risk review\n\nPending post-incident reconstruction; this file records unresolved process debt and is not evidence of approval.\n")
        write_json(rd / "state.json", {"schema_version":1,"change_id":rid,"mode":"retro","phase":"DISCUSS","base_commit":base_commit,"created_at":now(),"updated_at":now()})
        append_event(root, rid, "CREATED_FROM_BYPASS", "DEBT", {"source_change": change_id, "reason": reason})


def anchor(root: Path, change_id: str, commit: str) -> None:
    # Final anchoring is independent of the mutable working tree and requires a previously sealed candidate.
    validate_id(change_id)
    candidate = candidate_status(root, change_id)
    resolved = run_git(root, ["rev-parse", f"{commit}^{{commit}}"], check=False)
    if resolved.returncode != 0:
        raise RuntimeError(f"invalid landed commit: {commit}")
    sha = resolved.stdout.strip()
    landed_state = show_commit_json(root, sha, change_id, "state.json")
    landed_verification = show_commit_json(root, sha, change_id, "verification.json")
    if landed_state.get("phase") != "SHIP":
        raise RuntimeError(f"landed ledger phase must be SHIP, got {landed_state.get('phase')}")
    if landed_verification.get("status") != "PASS":
        raise RuntimeError("landed verification status is not PASS")
    for key in ("base_commit", "content_digest", "changed_paths"):
        if landed_verification.get(key) != show_commit_json(root, candidate["commit"], change_id, "verification.json").get(key):
            raise RuntimeError(f"landed verification {key} differs from sealed candidate")
    if landed_state.get("verified_content_digest") != candidate["content_digest"]:
        raise RuntimeError("landed state digest differs from sealed candidate")
    # Recompute exactly the candidate's verified material+intent bytes from the landed tree.
    landed_digest = tree_digest(root, change_id, sha, candidate["changed_paths"])
    if landed_digest != candidate["content_digest"]:
        raise RuntimeError("landed Git-tree content does not match sealed candidate verification digest")
    ancestry = run_git(root, ["merge-base", "--is-ancestor", candidate["commit"], sha], check=False).returncode == 0
    relation = "candidate-ancestor" if ancestry else "content-equivalent"
    ref = f"refs/keel/ledger/{change_id}"
    old = run_git(root, ["show-ref", "--hash", "--verify", ref], check=False)
    if old.returncode == 0 and old.stdout.strip() != sha:
        raise RuntimeError(f"KEEL ref collision: {ref} already points to {old.stdout.strip()}")
    if old.returncode != 0:
        z = "0" * 40
        p = run_git(root, ["update-ref", ref, sha, z], check=False)
        if p.returncode != 0: raise RuntimeError(p.stderr.strip() or "git update-ref failed")
    note = run_git(root, ["notes", "--ref=keel", "show", sha], check=False)
    note_text = (
        f"keel-change-id: {change_id}\n"
        f"sealed-candidate: {candidate['commit']}\n"
        f"landed-commit: {sha}\n"
        f"integration-relation: {relation}\n"
        "verification-class: LANDED_COMPLETION\n"
        f"verified-content-digest: {candidate['content_digest']}\n"
    )
    if note.returncode == 0:
        if note.stdout != note_text:
            raise RuntimeError("existing refs/notes/keel note collides with expected KEEL attestation anchor")
    else:
        p = run_git(root, ["notes", "--ref=keel", "add", "-m", note_text, sha], check=False)
        if p.returncode != 0: raise RuntimeError(p.stderr.strip() or "git notes add failed")
    audit_dir = root / ".keel" / "audit"; audit_dir.mkdir(parents=True, exist_ok=True)
    with (audit_dir / "anchors.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts":now(),"change_id":change_id,"candidate_commit":candidate["commit"],"landed_commit":sha,"relation":relation,"ref":ref,"content_digest":candidate["content_digest"],"attestation_digest":candidate.get("attestation_digest"),"verification_class":"LANDED_COMPLETION"}, sort_keys=True) + "\n")
    if active_change(root) == change_id:
        active_file(root).unlink(missing_ok=True)


def discover_capabilities(root: Path) -> dict:
    cfg = read_json(root / ".keel" / "config.json")
    result = capability_resolver.resolve(root, cfg)
    capability_resolver.write_resolution(root, result)
    return result


def compile_context(root: Path, change_id: str, write: bool = True) -> dict:
    st = state(root, change_id)
    cfg = read_json(root / ".keel" / "config.json")
    try:
        _, paths = diff_scope_errors(root, change_id)
    except Exception:
        paths = []
    text, meta = context_compiler.compile_packet(root, change_id, st, cfg, ledger_dir(root, change_id), paths)
    if write:
        md, js = context_compiler.write_packet(root, change_id, text, meta)
        meta = dict(meta, markdown=str(md.relative_to(root)), metadata=str(js.relative_to(root)))
    meta["text"] = text
    return meta


def next_action(root: Path, change_id: str | None = None) -> dict:
    cid = change_id or active_change(root)
    if not cid:
        return {
            "schema_version": 1,
            "status": "IDLE",
            "change_id": None,
            "phase": None,
            "blockers": [],
            "legal_actions": [],
            "recommended_action": None,
        }
    st = state(root, cid)
    phase = st.get("phase")
    result = {
        "schema_version": 1,
        "status": "ACTIONABLE",
        "change_id": cid,
        "phase": phase,
        "blockers": [],
        "legal_actions": [],
        "recommended_action": None,
    }

    def action(action_id: str, command: str, reason: str) -> dict:
        return {"id": action_id, "command": command, "reason": reason}

    if phase == "DISCUSS":
        result["recommended_action"] = action("gate-discuss", f"keel gate discuss --change {cid}", "proposal must pass the DISCUSS gate")
    elif phase == "PLAN":
        result["recommended_action"] = action("gate-plan", f"keel gate plan --change {cid}", "intent, scope, risk, and effects must pass the PLAN gate")
    elif phase in {"EXECUTE", "VERIFY"}:
        vpath = ledger_dir(root, cid) / "verification.json"
        prior = read_json(vpath) if vpath.is_file() else {}
        if prior.get("status") == "PASS" and prior.get("change_type", "implementation") != "planning_only" and prior.get("implementation_status") != "PASS":
            result["recommended_action"] = action("implement", f"complete implementation and behavioral acceptance before keel verify --change {cid}", "planning readiness passed, but implementation acceptance is not verified")
        else:
            result["recommended_action"] = action("verify", f"keel verify --change {cid}", "run canonical checks and evaluate the acceptance graph")
    elif phase == "SHIP":
        ref = candidate_ref(cid)
        sealed = run_git(root, ["show-ref", "--verify", ref], check=False).returncode == 0
        if sealed:
            anchor_state, message = anchored_status(root, cid)
            if anchor_state == "anchored":
                result["status"] = "IDLE"
                result["phase"] = phase
                return result
            if anchor_state == "invalid":
                result["status"] = "BLOCKED"
                result["blockers"].append({"id": "invalid-anchor-evidence", "detail": message})
                return result

        vpath = ledger_dir(root, cid) / "verification.json"
        prior = read_json(vpath) if vpath.is_file() else {}
        if prior.get("status") == "PASS" and prior.get("change_type", "implementation") != "planning_only" and prior.get("implementation_status") != "PASS":
            result["recommended_action"] = action("implement", f"complete implementation and behavioral acceptance before keel verify --change {cid}", "historical readiness evidence does not provide implementation authority")
            result["legal_actions"].append(result["recommended_action"])
            return result

        verified, message = current_verified(root, cid)
        if not verified:
            result["status"] = "BLOCKED"
            result["blockers"].append({"id": "stale-verification", "detail": message})
            result["recommended_action"] = action("reopen", f"keel reopen --change {cid}", "implementation must be reopened before changing stale verified content")
        elif not sealed:
            result["recommended_action"] = action("seal", f"keel seal --change {cid} --commit HEAD", "the verified commit must become a sealed candidate")
        else:
            result["recommended_action"] = action("integrate-anchor", f"keel anchor --change {cid} --commit <landed-sha>", "the sealed candidate must be integrated and independently anchored after landing")
    else:
        result["status"] = "BLOCKED"
        result["blockers"].append({"id": "unknown-phase", "detail": f"unsupported KEEL phase: {phase!r}"})

    if result["recommended_action"]:
        result["legal_actions"].append(result["recommended_action"])
    return result


def worktree_records(root: Path) -> list[dict]:
    raw = run_git(root, ["worktree", "list", "--porcelain"]).stdout
    records = []
    current: dict = {}
    for line in raw.splitlines() + [""]:
        if line.startswith("worktree "):
            if current:
                records.append(current)
            current = {"path": str(Path(line[9:]).resolve())}
        elif line.startswith("HEAD "):
            current["head"] = line[5:].strip()
        elif line.startswith("branch "):
            branch = line[7:].strip()
            current["branch"] = branch.removeprefix("refs/heads/")
        elif line == "detached":
            current["detached"] = True
        elif line == "bare":
            current["bare"] = True
        elif not line and current:
            records.append(current)
            current = {}
    unique = {item["path"]: item for item in records}
    for item in unique.values():
        item.setdefault("branch", None)
        item.setdefault("detached", False)
        item.setdefault("bare", False)
    return [unique[path] for path in sorted(unique)]


def worktree_create(root: Path, change_id: str, path: str, commit: str = "HEAD") -> dict:
    validate_id(change_id)
    target = Path(path)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if target == root.resolve():
        raise RuntimeError("worktree path cannot be the primary worktree")
    if target.exists():
        raise RuntimeError(f"worktree path already exists: {target}")
    run_git(root, ["worktree", "add", "--detach", str(target), commit])
    record = next((item for item in worktree_records(root) if os.path.normcase(item["path"]) == os.path.normcase(str(target))), None)
    if not record:
        raise RuntimeError("Git created the worktree but it was not present in registered worktree status")
    return {"change_id": change_id, **record}


def worktree_retire(root: Path, path: str, force: bool = False) -> dict:
    target = Path(path)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if target == root.resolve():
        raise RuntimeError("refusing to retire the primary worktree")
    record = next((item for item in worktree_records(root) if os.path.normcase(item["path"]) == os.path.normcase(str(target))), None)
    if not record:
        raise RuntimeError(f"path is not a registered Git worktree: {target}")
    dirty = bool(run_git(target, ["status", "--porcelain", "--untracked-files=all"], check=True).stdout.strip())
    if dirty and not force:
        raise RuntimeError("worktree is dirty; pass --force to retire it")
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(target))
    run_git(root, args)
    return {"path": str(target), "retired": True, "dirty": dirty, "forced": force}


def environment_contract(root: Path) -> dict:
    config_path = root / ".keel" / "config.json"
    config = read_json(config_path) if config_path.is_file() else {}
    contract = config.get("environment_contract")
    if contract is None:
        return {"schema_version": 1, "status": "UNCONFIGURED", "contract": None, "errors": []}
    errors = []
    if not isinstance(contract, dict):
        return {"schema_version": 1, "status": "INVALID", "contract": contract, "errors": ["environment_contract must be an object"]}
    if contract.get("schema_version", 1) != 1:
        errors.append("environment_contract.schema_version must be 1")
    for key in ("setup", "start", "stop"):
        value = contract.get(key)
        if value is not None and (not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value)):
            errors.append(f"environment_contract.{key} must be null or a non-empty argv list")
    isolation = contract.get("isolation", {})
    if not isinstance(isolation, dict) or not all(isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip() for key, value in isolation.items()):
        errors.append("environment_contract.isolation must map non-empty string keys to non-empty string values")
    status = "INVALID" if errors else ("CONFIGURED" if any(contract.get(key) for key in ("setup", "start", "stop")) or bool(isolation) else "UNCONFIGURED")
    return {"schema_version": 1, "status": status, "contract": contract, "errors": errors}


def status_summary(root: Path, change_id: str | None = None) -> dict:
    cid = change_id or active_change(root)
    if not cid: return {"active_change": None, "keel": "IDLE"}
    st = state(root, cid)
    result = {"active_change": cid, "mode": st.get("mode"), "phase": st.get("phase"), "base_commit": st.get("base_commit")}
    if st.get("phase") == "SHIP":
        ok, msg = current_verified(root, cid); result["verified_current"] = ok; result["verification_message"] = msg
    else:
        try:
            errs, paths = diff_scope_errors(root, cid); result["changed_paths"] = paths; result["scope_errors"] = errs
        except Exception as e:
            result["scope_errors"] = [str(e)]
    return result
