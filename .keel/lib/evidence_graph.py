from __future__ import annotations

import fnmatch
import json
from pathlib import Path

REQ_ID_PREFIX = "REQ-"
AC_ID_PREFIX = "AC-"
SUPPORTED_PROVIDERS = {"command", "changed_path", "file_exists", "unit_test", "browser", "visual", "log_query", "metric_query", "trace_query", "schema", "security", "benchmark", "hardware", "human_review", "external_ci"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _providers(contracts_path: Path | None) -> set[str]:
    if contracts_path is None or not contracts_path.is_file():
        return SUPPORTED_PROVIDERS
    try:
        value = read_json(contracts_path).get("evidence_providers", [])
        return {"changed_path", "file_exists"} | {x for x in value if isinstance(x, str)}
    except Exception:
        return set()


def validate_contract(requirements_path: Path, acceptance_path: Path, require_nonempty: bool = True, contracts_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        req = read_json(requirements_path)
    except Exception as e:
        return [f"requirements.json invalid: {e}"]
    try:
        acc = read_json(acceptance_path)
    except Exception as e:
        return [f"acceptance.json invalid: {e}"]
    requirements = req.get("requirements")
    criteria = acc.get("criteria")
    if not isinstance(requirements, list):
        errors.append("requirements.json requirements must be a list"); requirements = []
    if not isinstance(criteria, list):
        errors.append("acceptance.json criteria must be a list"); criteria = []
    if require_nonempty and not requirements:
        errors.append("standard change requires at least one requirement")
    if require_nonempty and not criteria:
        errors.append("standard change requires at least one acceptance criterion")
    providers = _providers(contracts_path)
    req_ids = set()
    for r in requirements:
        if not isinstance(r, dict): errors.append("requirement entries must be objects"); continue
        rid = r.get("id"); statement = r.get("statement")
        if not isinstance(rid, str) or not rid.startswith(REQ_ID_PREFIX): errors.append(f"invalid requirement id: {rid!r}"); continue
        if rid in req_ids: errors.append(f"duplicate requirement id: {rid}")
        req_ids.add(rid)
        if not isinstance(statement, str) or len(statement.strip()) < 8: errors.append(f"requirement {rid} statement too thin")
    ac_ids = set()
    covered_requirements = set()
    for c in criteria:
        if not isinstance(c, dict): errors.append("acceptance entries must be objects"); continue
        aid = c.get("id"); rid = c.get("requirement_id"); statement = c.get("statement")
        if not isinstance(aid, str) or not aid.startswith(AC_ID_PREFIX): errors.append(f"invalid acceptance id: {aid!r}"); continue
        if aid in ac_ids: errors.append(f"duplicate acceptance id: {aid}")
        ac_ids.add(aid)
        if rid not in req_ids: errors.append(f"acceptance {aid} references unknown requirement {rid!r}")
        else: covered_requirements.add(rid)
        if not isinstance(statement, str) or len(statement.strip()) < 8: errors.append(f"acceptance {aid} statement too thin")
        if c.get("policy", "all") not in {"all", "any"}: errors.append(f"acceptance {aid} policy must be all|any")
        if not isinstance(c.get("required", True), bool): errors.append(f"acceptance {aid} required must be boolean")
        evidence = c.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"acceptance {aid} requires at least one evidence edge"); continue
        for edge in evidence:
            if not isinstance(edge, dict): errors.append(f"acceptance {aid} evidence entries must be objects"); continue
            provider = edge.get("provider")
            if provider not in providers:
                errors.append(f"acceptance {aid} unsupported evidence provider: {provider!r}")
            if provider == "schema":
                if not isinstance(edge.get("path"), str):
                    errors.append(f"acceptance {aid} schema evidence requires path")
                if "schema_version" in edge and not isinstance(edge.get("schema_version"), int):
                    errors.append(f"acceptance {aid} schema_version must be an integer")
                if "required_keys" in edge and (not isinstance(edge.get("required_keys"), list) or any(not isinstance(x, str) for x in edge.get("required_keys", []))):
                    errors.append(f"acceptance {aid} required_keys must be a list of strings")
            elif provider not in {"changed_path", "file_exists"} and not isinstance(edge.get("check_id"), str):
                errors.append(f"acceptance {aid} {provider} evidence requires check_id")
            if provider in {"changed_path", "file_exists"} and not isinstance(edge.get("path"), str):
                errors.append(f"acceptance {aid} {provider} evidence requires path")
    for rid in sorted(req_ids - covered_requirements):
        errors.append(f"requirement {rid} has no acceptance criterion")
    return errors


def _path_match(path: str, pattern: str) -> bool:
    if fnmatch.fnmatchcase(path, pattern): return True
    if pattern.endswith("/**") and path.startswith(pattern[:-3].rstrip("/") + "/"): return True
    if not any(c in pattern for c in "*?[") and (path == pattern or path.startswith(pattern.rstrip("/") + "/")): return True
    return False


def evaluate(root: Path, requirements_path: Path, acceptance_path: Path, checks: list[dict], changed_paths: list[str], contracts_path: Path | None = None) -> dict:
    contract_errors = validate_contract(requirements_path, acceptance_path, require_nonempty=True, contracts_path=contracts_path)
    if contract_errors:
        return {"schema_version": 1, "status": "FAIL", "errors": contract_errors, "criteria": []}
    req = read_json(requirements_path); acc = read_json(acceptance_path)
    check_map = {c.get("id"): c for c in checks if isinstance(c, dict) and isinstance(c.get("id"), str)}
    criterion_rows = []
    errors = []
    for c in acc["criteria"]:
        edge_rows = []
        for edge in c["evidence"]:
            provider = edge["provider"]
            passed = False; detail = ""
            if provider == "command":
                check = check_map.get(edge["check_id"])
                passed = bool(check and check.get("exit_code") == 0)
                detail = f"check={edge['check_id']} exit={None if not check else check.get('exit_code')}"
            elif provider == "changed_path":
                matched = [p for p in changed_paths if _path_match(p, edge["path"])]
                passed = bool(matched); detail = "matched=" + ",".join(matched[:8])
            elif provider == "file_exists":
                target = (root / edge["path"]).resolve()
                try: target.relative_to(root.resolve()); passed = target.exists(); detail = f"exists={passed}"
                except ValueError: passed = False; detail = "path escapes repository"
            elif provider == "schema":
                target = (root / edge["path"]).resolve()
                try:
                    target.relative_to(root.resolve())
                    document = read_json(target)
                    version_ok = "schema_version" not in edge or document.get("schema_version") == edge["schema_version"]
                    keys_ok = all(key in document for key in edge.get("required_keys", []))
                    passed = target.is_file() and isinstance(document, dict) and version_ok and keys_ok
                    detail = f"parseable={target.is_file()} version={version_ok} required_keys={keys_ok}"
                except (ValueError, OSError, json.JSONDecodeError):
                    passed = False; detail = "invalid, missing, or out-of-repository JSON"
            else:
                check = check_map.get(edge["check_id"])
                passed = bool(check and check.get("exit_code") == 0)
                detail = f"provider={provider} check={edge['check_id']} exit={None if not check else check.get('exit_code')}"
            edge_rows.append({"provider": provider, "passed": passed, "detail": detail, **{k:v for k,v in edge.items() if k != "provider"}})
        policy = c.get("policy", "all")
        passed = all(x["passed"] for x in edge_rows) if policy == "all" else any(x["passed"] for x in edge_rows)
        status = "PASS" if passed else "FAIL"
        row = {"id": c["id"], "requirement_id": c["requirement_id"], "statement": c["statement"], "required": c.get("required", True), "policy": policy, "status": status, "evidence": edge_rows}
        criterion_rows.append(row)
        if row["required"] and not passed:
            errors.append(f"acceptance criterion failed: {row['id']}")
    requirement_coverage = []
    for requirement in req["requirements"]:
        rid = requirement["id"]
        rows = [row for row in criterion_rows if row["requirement_id"] == rid]
        requirement_coverage.append({
            "requirement_id": rid,
            "criterion_ids": [row["id"] for row in rows],
            "criterion_count": len(rows),
            "passed": bool(rows) and all(row["status"] == "PASS" for row in rows),
        })
    return {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "requirements": req["requirements"],
        "criteria": criterion_rows,
        "requirement_coverage": requirement_coverage,
        "summary": {
            "required": sum(1 for c in criterion_rows if c["required"]),
            "passed_required": sum(1 for c in criterion_rows if c["required"] and c["status"] == "PASS"),
            "requirements_total": len(req["requirements"]),
            "requirements_covered": sum(1 for row in requirement_coverage if row["criterion_count"] > 0),
            "requirements_passing": sum(1 for row in requirement_coverage if row["passed"]),
        },
    }
