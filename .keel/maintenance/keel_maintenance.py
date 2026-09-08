#!/usr/bin/env python3
"""Optional, read-only maintenance entry point; not a KEEL kernel command."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import feedback_entropy


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional KEEL repository maintenance")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("entropy")
    feedback = commands.add_parser("feedback")
    feedback.add_argument("action", choices=["validate", "status", "queue"])
    feedback.add_argument("path", type=Path)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    if args.command == "entropy":
        result = feedback_entropy.entropy_scan(root)
    elif args.action == "queue":
        result = feedback_entropy.queue(root, args.path.resolve())
    else:
        observation = feedback_entropy.load(args.path.resolve())
        if args.action == "status":
            result = feedback_entropy.status(root, observation)
        else:
            errors = feedback_entropy.validate_observation(root, observation)
            result = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
