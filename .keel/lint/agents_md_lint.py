#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve(); sys.path.insert(0, str(HERE.parents[1]/"lib"))
import keel_core as k

ap = argparse.ArgumentParser()
ap.add_argument("--root", type=Path)
args = ap.parse_args()
try:
    root = args.root.resolve() if args.root else k.git_root(Path.cwd())
    errors = k.agents_lint(root)
    print(json.dumps({"status":"PASS" if not errors else "FAIL", "errors":errors}, indent=2))
    raise SystemExit(0 if not errors else 1)
except Exception as e:
    print(f"AGENTS LINT ERROR: {e}", file=sys.stderr); raise SystemExit(2)
