#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "lib"))
import keel_core as k
import change_graph as cg
import fact_graph
import lifecycle
import effect_inference as effects
import schema_migrations as migrations
import telemetry
import p0_contract
import canonical_ledger
import scheduler


def main() -> int:
    ap = argparse.ArgumentParser(description="KEEL spec-ledger control plane")
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="COMMAND")
    sub.add_parser("doctor")
    p = sub.add_parser("bootstrap"); p.add_argument("action", choices=["status"]); p.add_argument("--requires-git", action="store_true")
    p = sub.add_parser("manifest"); p.add_argument("--write", action="store_true")
    sub.add_parser("version")
    p = sub.add_parser("reconcile"); p.add_argument("--change")
    sub.add_parser("contracts")
    p = sub.add_parser("change-graph"); p.add_argument("action", choices=["validate", "frontier", "status", "normalize", "serialize"]); p.add_argument("path", type=Path); p.add_argument("--state", type=Path)
    p = sub.add_parser("scheduler"); p.add_argument("action", choices=["frontier", "status"]); p.add_argument("path", type=Path); p.add_argument("--state", type=Path); p.add_argument("--max-concurrency", type=int, default=1)
    sub.add_parser("facts")
    sub.add_parser("compat")
    p = sub.add_parser("migrate"); p.add_argument("--check", action="store_true"); p.add_argument("--plan", type=Path)
    p = sub.add_parser("ledger"); p.add_argument("action", choices=["migrate","project","validate"]); p.add_argument("--change", required=True); p.add_argument("--output", type=Path)
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
    p = sub.add_parser("landing"); p.add_argument("action", choices=["prepare", "integrate", "verify"]); p.add_argument("--change", required=True); p.add_argument("--target-ref"); p.add_argument("--strategy", choices=["merge", "squash", "rebase"], default="merge"); p.add_argument("--commit")
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
            result = lifecycle.version_report(root); print(json.dumps(result, indent=2)); return 0 if result["compatibility"] == "COMPATIBLE" else 1
        if args.cmd == "reconcile": print(json.dumps(lifecycle.reconcile(root, args.change), indent=2)); return 0
        if args.cmd == "contracts":
            result = lifecycle.contract_report(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "PASS" else 1
        if args.cmd == "change-graph":
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
        if args.cmd == "scheduler":
            graph = cg.normalize(cg.load(args.path.resolve()))
            persisted = scheduler.StateStore(args.state.resolve()).load() if args.state else None
            result = scheduler.frontier_report(graph, persisted, args.max_concurrency)
            print(json.dumps(result, indent=2)); return 0 if result.get("status") != "INVALID" else 1
        if args.cmd == "facts":
            print(fact_graph.build(root).serialize(), end=""); return 0
        if args.cmd == "ledger":
            d=k.ledger_dir(root,args.change)
            if args.action == "migrate": result=canonical_ledger.migrate_legacy(d,args.output.resolve() if args.output else None)
            elif args.action == "project": canonical_ledger.project_views(d); result={"status":"PROJECTED","change":args.change}
            else:
                errors=canonical_ledger.validate_intent(canonical_ledger.load_intent(d),require_planned=False); canonical_ledger.read_events(d); result={"status":"PASS" if not errors else "FAIL","errors":errors}
            print(json.dumps(result,indent=2)); return 0 if result.get("status") not in {"FAIL"} else 1
        if args.cmd == "migrate" and args.plan:
            result = migrations.preflight(args.plan.resolve()); print(json.dumps(result, indent=2)); return 0
        if args.cmd == "compat" or args.cmd == "migrate":
            result = lifecycle.inventory(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "COMPATIBLE" else 1
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
            d = k.ledger_dir(root, cid); p = d / "views" / "evidence-receipts.json" if (d / "intent.json").is_file() else d / "evidence-receipts.json"
            if not p.is_file(): raise RuntimeError("evidence receipts missing; run verify first")
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
        if args.cmd == "landing":
            if args.action == "prepare":
                if not args.target_ref: raise RuntimeError("landing prepare requires --target-ref")
                result = k.prepare_landing(root, args.change, args.target_ref, args.strategy)
            elif args.action == "verify":
                if not args.commit: raise RuntimeError("landing verify requires --commit")
                result = k.verify_landing(root, args.change, args.commit)
            else:
                result = k.integrate_landing(root, args.change, args.target_ref, args.commit)
            print(json.dumps(result, indent=2)); return 0
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
