from __future__ import annotations

import json
from pathlib import Path


def infer_argv(argv: list[str]) -> list[dict]:
    """Infer only explicit, high-confidence capabilities from argv tokens."""
    tokens = [str(item).lower() for item in argv]
    matches: list[dict] = []

    def add(capability: str, reason: str) -> None:
        matches.append({"capability": capability, "reason": reason})

    if tokens[:2] == ["git", "push"]:
        add("git.remote.push", "git push")
    if tokens[:2] == ["git", "commit"]:
        add("git.local.commit", "git commit")
    if tokens[:2] == ["git", "merge"]:
        add("vcs.merge", "git merge")
    if tokens[:2] in (["npm", "publish"], ["pnpm", "publish"], ["yarn", "publish"], ["twine", "upload"]):
        add("package.publish", "package publish/upload")
    if tokens[:2] in (["terraform", "apply"], ["pulumi", "up"]):
        add("infra.apply", "infrastructure apply/up")
    if tokens[:2] in (["kubectl", "apply"], ["helm", "upgrade"]):
        add("cloud.deploy", "cluster deployment command")
    if tokens[:2] == ["alembic", "upgrade"] or ("manage.py" in tokens and "migrate" in tokens) or ("prisma" in tokens and "migrate" in tokens):
        add("database.migrate", "database migration command")
    if tokens[:2] == ["gh", "issue"] and any(value in tokens for value in ("edit", "comment", "close", "reopen")):
        add("issue.modify", "issue mutation command")
    unique = {}
    for match in matches:
        unique.setdefault(match["capability"], match)
    return [unique[key] for key in sorted(unique)]


def audit(root: Path, change_id: str | None = None) -> dict:
    config = json.loads((root / ".keel" / "config.json").read_text(encoding="utf-8"))
    declared: list[str] = []
    if change_id:
        effects = root / ".keel" / "ledger" / change_id / "effects.json"
        if effects.is_file():
            declared = json.loads(effects.read_text(encoding="utf-8")).get("effect_capabilities", [])
    checks = []
    inferred = set()
    for check in config.get("verification_commands", []):
        matches = infer_argv(check.get("argv", []))
        inferred.update(item["capability"] for item in matches)
        checks.append({"id": check.get("id"), "argv": check.get("argv", []), "inferred": matches})
    undeclared = sorted(inferred - set(declared)) if change_id else []
    return {"schema_version": 1, "status": "ADVISORY" if undeclared else "PASS", "read_only": True, "change_id": change_id, "declared_capabilities": sorted(declared), "inferred_capabilities": sorted(inferred), "undeclared_capabilities": undeclared, "checks": checks, "authorization": "not evaluated or granted"}
