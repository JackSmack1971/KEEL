#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import keel_core as k
import upgrade_kernel as uk
import mission_graph as mg
import mission_v2 as mv2
import change_graph as cg
import repository_map as rm
import topology_router as tr
import feedback_entropy as fe
import lifecycle
import developer_ux as ux
import effect_inference as effects
import schema_migrations as migrations
import telemetry
import p0_contract


def main() -> int:
    ap = argparse.ArgumentParser(description="KEEL spec-ledger control plane")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="COMMAND")
    sub.add_parser("doctor")
    p = sub.add_parser("bootstrap"); p.add_argument("action", choices=["status"]); p.add_argument("--requires-git", action="store_true")
    p = sub.add_parser("manifest"); p.add_argument("--write", action="store_true")
    sub.add_parser("version")
    p = sub.add_parser("reconcile"); p.add_argument("--change")
    sub.add_parser("contracts")
    for name in ("change-graph", "mission"):
        p = sub.add_parser(name); p.add_argument("action", choices=["validate", "frontier", "status", "normalize", "serialize"]); p.add_argument("path", type=Path); p.add_argument("--state", type=Path)
    # Temporary read-compatibility alias, accepted but intentionally omitted
    # from the normal public command listing.
    p = argparse.ArgumentParser(prog="keel.py mission-v2"); p.add_argument("action", choices=["validate", "frontier", "normalize-v1"]); p.add_argument("path", type=Path)
    sub._name_parser_map["mission-v2"] = p
    p = sub.add_parser("map"); p.add_argument("--stdout", action="store_true")
    p = sub.add_parser("route"); p.add_argument("path", type=Path); p.add_argument("--change")
    p = sub.add_parser("feedback"); p.add_argument("action", choices=["validate", "status", "queue"]); p.add_argument("path", type=Path)
    p = sub.add_parser("entropy"); p.add_argument("action", choices=["scan"])
    sub.add_parser("compat")
    p = sub.add_parser("migrate"); p.add_argument("--check", action="store_true"); p.add_argument("--plan", type=Path)
    p = sub.add_parser("init"); p.add_argument("--check", action="store_true")
    p = sub.add_parser("review"); p.add_argument("--change")
    p = sub.add_parser("ship"); p.add_argument("--change")
    p = sub.add_parser("effects"); p.add_argument("--change")
    p = sub.add_parser("telemetry"); p.add_argument("--change")
    sub.add_parser("discover")
    p = sub.add_parser("context"); p.add_argument("--change"); p.add_argument("--stdout", action="store_true")
    p = sub.add_parser("evidence"); p.add_argument("--change")
    p = sub.add_parser("status"); p.add_argument("--change")
    p = sub.add_parser("next"); p.add_argument("--change")
    p = sub.add_parser("worktree"); p.add_argument("action", choices=["create", "status", "retire"]); p.add_argument("change", nargs="?"); p.add_argument("--path"); p.add_argument("--commit", default="HEAD"); p.add_argument("--force", action="store_true")
    p = sub.add_parser("environment"); p.add_argument("action", choices=["status"])
    p = sub.add_parser("start"); p.add_argument("change"); p.add_argument("--mode", choices=["standard","trivial"], default="standard"); p.add_argument("--summary"); p.add_argument("--scope", action="append", default=[])
    p = sub.add_parser("gate"); p.add_argument("gate", choices=["discuss","plan"]); p.add_argument("--change")
    p = sub.add_parser("verify"); p.add_argument("--change")
    p = sub.add_parser("reopen"); p.add_argument("--change")
    p = sub.add_parser("replan"); p.add_argument("--change")
    p = sub.add_parser("record-authorization"); p.add_argument("--change"); p.add_argument("--authority", required=True); p.add_argument("--scope", required=True); p.add_argument("--evidence-reference", required=True)
    p = sub.add_parser("seal"); p.add_argument("--change"); p.add_argument("--commit", default="HEAD")
    p = sub.add_parser("candidate-status"); p.add_argument("--change", required=True)
    p = sub.add_parser("anchor"); p.add_argument("--change", required=True); p.add_argument("--commit", required=True)
    p = sub.add_parser("config-add-check"); p.add_argument("--id", required=True); p.add_argument("--cwd", default="."); p.add_argument("--timeout", type=int, default=600); p.add_argument("argv", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    try:
        try:
            root = k.git_root(Path.cwd())
        except RuntimeError:
            if args.cmd != "bootstrap":
                raise
            root = Path.cwd().resolve()
        if args.cmd == "doctor":
            errs = k.doctor(root); print(json.dumps({"status":"PASS" if not errs else "FAIL", "errors":errs}, indent=2)); return 0 if not errs else 1
        if args.cmd == "bootstrap":
            result = p0_contract.classify_bootstrap(root, args.requires_git); print(json.dumps(result, indent=2)); return 0 if result["status"] in {"VALID_GIT_REPOSITORY", "COPIED_EXTRACTED_FRAMEWORK", "NOT_A_GIT_REPOSITORY"} else 1
        if args.cmd == "manifest":
            result = p0_contract.manifest_producer(root, args.write); print(json.dumps(result, indent=2)); return 0 if result["status"] in {"WRITTEN", "VERIFIED"} else 1
        if args.cmd == "version":
            result = uk.version_report(root); print(json.dumps(result, indent=2)); return 0 if result["compatibility"] == "COMPATIBLE" else 1
        if args.cmd == "reconcile": print(json.dumps(uk.reconcile(root, args.change), indent=2)); return 0
        if args.cmd == "contracts":
            result = uk.contract_report(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "PASS" else 1
        if args.cmd in {"change-graph", "mission"}:
            source = cg.load(args.path.resolve())
            try:
                graph = cg.normalize(source)
                if args.action == "validate":
                    errors = cg.validate(graph); result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "identity": cg.IDENTITY}
                elif args.action in {"frontier", "status"}:
                    state = cg.load(args.state.resolve()) if args.state else None
                    result = cg.frontier(graph, state)
                elif args.action == "normalize":
                    result = graph
                else:
                    sys.stdout.write(cg.serialize(graph)); return 0
            except (cg.GraphError, ValueError, TypeError) as exc:
                result = {"status": "INVALID", "errors": [str(exc)]}
            print(json.dumps(result, indent=2)); return 0 if result.get("status") not in {"FAIL", "INVALID"} else 1
        if args.cmd == "mission-v2":
            source = mv2.load(args.path.resolve()) if hasattr(mv2, "load") else json.loads(args.path.resolve().read_text(encoding="utf-8"))
            if args.action == "normalize-v1":
                result = mv2.normalize_v1(source)
            elif args.action == "validate":
                result = mv2.validate(source, root=root)
            else:
                result = mv2.frontier(source)
            print(json.dumps(result, indent=2)); return 0 if result.get("status") not in {"INVALID", "UNSUPPORTED"} else 1
        if args.cmd == "map":
            result = rm.build(root)
            if args.stdout:
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps({"status": "WRITTEN", "path": str(rm.write(root, result).relative_to(root))}, indent=2))
            return 0
        if args.cmd == "route":
            result = tr.recommend(tr.load(args.path.resolve()), args.change)
            print(json.dumps(result, indent=2)); return 0 if result["status"] == "PASS" else 1
        if args.cmd == "feedback":
            if args.action == "queue":
                result = fe.queue(root, args.path.resolve())
            else:
                observation = fe.load(args.path.resolve())
                result = {"status": "PASS" if not fe.validate_observation(root, observation) else "FAIL", "errors": fe.validate_observation(root, observation)} if args.action == "validate" else fe.status(root, observation)
            print(json.dumps(result, indent=2)); return 0 if result["status"] == "PASS" else 1
        if args.cmd == "entropy":
            result = fe.entropy_scan(root); print(json.dumps(result, indent=2)); return 0
        if args.cmd == "migrate" and args.plan:
            result = migrations.preflight(args.plan.resolve()); print(json.dumps(result, indent=2)); return 0
        if args.cmd == "compat" or args.cmd == "migrate":
            result = lifecycle.inventory(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "COMPATIBLE" else 1
        if args.cmd == "init":
            result = ux.init_check(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "READY" else 1
        if args.cmd == "review": print(json.dumps(ux.review(root, args.change), indent=2)); return 0
        if args.cmd == "ship":
            result = ux.ship_eligibility(root, args.change); print(json.dumps(result, indent=2)); return 0 if result["status"] == "ELIGIBLE" else 1
        if args.cmd == "effects":
            result = effects.audit(root, args.change); print(json.dumps(result, indent=2)); return 0
        if args.cmd == "telemetry":
            result = telemetry.for_change(root, args.change); print(json.dumps(result, indent=2)); return 0 if result["status"] in {"PASS", "UNAVAILABLE"} else 1
        if args.cmd == "discover":
            result = k.discover_capabilities(root); print(json.dumps(result, indent=2)); return 0 if not result.get("conflicts") else 1
        if args.cmd == "context":
            cid = args.change or k.active_change(root)
            if not cid: raise RuntimeError("no active KEEL change")
            result = k.compile_context(root, cid, write=True)
            if args.stdout: print(result.pop("text"))
            else:
                result.pop("text", None); print(json.dumps(result, indent=2))
            return 0
        if args.cmd == "evidence":
            cid = args.change or k.active_change(root)
            if not cid: raise RuntimeError("no active KEEL change")
            p = k.ledger_dir(root, cid) / "evidence-graph.json"
            if not p.is_file(): raise RuntimeError("evidence-graph.json missing; run verify first")
            print(p.read_text(encoding="utf-8"), end=""); return 0
        if args.cmd == "status": print(json.dumps(k.status_summary(root, args.change), indent=2)); return 0
        if args.cmd == "next": print(json.dumps(k.next_action(root, args.change), indent=2)); return 0
        if args.cmd == "worktree":
            if args.action == "status": print(json.dumps({"worktrees": k.worktree_records(root)}, indent=2)); return 0
            if not args.path: raise RuntimeError("worktree create/retire requires --path")
            if args.action == "create":
                if not args.change: raise RuntimeError("worktree create requires <change-id>")
                result = k.worktree_create(root, args.change, args.path, args.commit)
            else:
                result = k.worktree_retire(root, args.path, args.force)
            print(json.dumps(result, indent=2)); return 0
        if args.cmd == "environment":
            result = k.environment_contract(root); print(json.dumps(result, indent=2)); return 0 if result["status"] != "INVALID" else 1
        if args.cmd == "start": k.start_change(root, args.change, args.mode, args.summary, args.scope); print(json.dumps(k.status_summary(root, args.change), indent=2)); return 0
        cid = getattr(args, "change", None) or k.active_change(root)
        if args.cmd in {"gate","verify","reopen","replan","record-authorization","seal"} and not cid: raise RuntimeError("no active KEEL change")
        if args.cmd == "gate": k.gate(root, cid, args.gate); print(json.dumps(k.status_summary(root, cid), indent=2)); return 0
        if args.cmd == "verify": ev = k.verify_change(root, cid); print(json.dumps(ev, indent=2)); return 0 if ev["status"] == "PASS" else 1
        if args.cmd == "reopen": k.reopen(root, cid); print(json.dumps(k.status_summary(root, cid), indent=2)); return 0
        if args.cmd == "replan": k.replan(root, cid); print(json.dumps(k.status_summary(root, cid), indent=2)); return 0
        if args.cmd == "record-authorization":
            k.record_authorization(root, cid, args.authority, args.scope, args.evidence_reference); print(json.dumps({"status":"AUTHORIZATION_RECORDED","change":cid}, indent=2)); return 0
        if args.cmd == "seal":
            result = k.seal_candidate(root, cid, args.commit); print(json.dumps({"status":"SEALED", **result}, indent=2)); return 0
        if args.cmd == "candidate-status":
            print(json.dumps(k.candidate_status(root, args.change), indent=2)); return 0
        if args.cmd == "anchor": k.anchor(root, args.change, args.commit); print(json.dumps({"status":"ANCHORED","change":args.change,"commit":args.commit}, indent=2)); return 0
        if args.cmd == "config-add-check":
            argv = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv
            if not argv: raise RuntimeError("config-add-check requires command argv after --")
            cfgp = root / ".keel" / "config.json"; cfg = k.read_json(cfgp); checks = cfg.setdefault("verification_commands", [])
            if any(c.get("id") == args.id for c in checks): raise RuntimeError(f"verification id already exists: {args.id}")
            checks.append({"id": args.id, "argv": argv, "cwd": args.cwd, "timeout_sec": args.timeout, "required": True}); k.write_json(cfgp, cfg); print(json.dumps(cfg, indent=2)); return 0
        raise RuntimeError("unhandled command")
    except Exception as e:
        print(f"KEEL ERROR: {e}", file=sys.stderr); return 2

if __name__ == "__main__":
    raise SystemExit(main())
