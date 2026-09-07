from __future__ import annotations

import fnmatch
import json
from pathlib import Path, PurePosixPath

REQ_ID_PREFIX = "REQ-"
AC_ID_PREFIX = "AC-"
SUPPORTED_PROVIDERS = {"command", "changed_path", "file_exists", "unit_test", "browser", "visual", "log_query", "metric_query", "trace_query", "schema", "security", "benchmark", "hardware", "human_review", "external_ci"}
REQUIREMENT_TYPES = {"behavior", "quality", "security", "migration", "performance", "architecture", "documentation"}
PRIORITIES = {"must", "should", "could"}
EVIDENCE_TYPES = {"automated-test", "human-review", "schema", "benchmark", "runtime", "changed-path"}
ASSERTION_TYPES = {"exit_code", "output_contains", "output_not_contains", "json_key", "metric_at_least", "metric_at_most"}
PROOF_SURFACE_MARKERS = ("test", "verify", "evidence", "contract", "threshold", "config")


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


def _implementation_paths(value, label: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{label}.implementation_paths must be a list of non-empty strings")
        return
    for item in value:
        normalized = item.replace("\\", "/")
        parsed = PurePosixPath(normalized)
        if parsed.is_absolute() or ".." in parsed.parts:
            errors.append(f"{label}.implementation_paths contains unsafe path: {item}")


def classify_semantic_paths(paths: list[str]) -> list[dict]:
    markers = {
        "public_api": ("api", "openapi", "schema"),
        "permissions": ("auth", "permission", "policy"),
        "dependencies": ("lock", "requirements", "package", "pyproject", "cargo"),
        "security": ("security", "secret", "crypto"),
        "deployment": ("docker", "deploy", "workflow"),
        "verification_surface": PROOF_SURFACE_MARKERS,
    }
    rows = []
    for path in sorted(set(paths)):
        lower = path.lower()
        categories = sorted(kind for kind, needles in markers.items() if any(needle in lower for needle in needles))
        rows.append({"path": path, "categories": categories, "consequence": "HIGH" if categories else "NORMAL", "provenance": "bounded path-marker classifier; advisory"})
    return rows


def oracle_integrity(changed_paths: list[str], verification_paths: list[str] | None = None) -> dict:
    verification_paths = verification_paths or []
    changed = sorted(set(changed_paths))
    proof_changes = [path for path in changed if any(marker in path.lower() for marker in PROOF_SURFACE_MARKERS)]
    independent = any(path not in proof_changes and path not in changed and Path(path).suffix in {".py", ".js", ".ts", ".yml", ".yaml", ".json"} for path in verification_paths)
    return {"status": "REQUIRES_INDEPENDENT_VERIFICATION" if proof_changes and not independent else "CLEAR", "proof_surface_changes": proof_changes, "independent_oracle_detected": independent, "policy": "proof changes may widen verification, never weaken it"}


def _assertion(check: dict | None, assertion: dict) -> tuple[bool, str]:
    if not check:
        return False, "check missing"
    kind = assertion.get("type")
    if kind == "exit_code":
        expected = assertion.get("equals", 0)
        return check.get("exit_code") == expected, f"exit={check.get('exit_code')} expected={expected}"
    text = str(check.get("excerpt", ""))
    if kind == "output_contains":
        value = str(assertion.get("value", "")); return bool(value and value in text), f"contains={value in text}"
    if kind == "output_not_contains":
        value = str(assertion.get("value", "")); return bool(value and value not in text), f"not_contains={value not in text}"
    if kind == "json_key":
        try:
            document = json.loads(text)
            current = document
            for key in assertion.get("path", []): current = current[key]
            expected = assertion.get("equals")
            return (expected is None or current == expected), f"json_key={current!r}"
        except (TypeError, KeyError, IndexError, json.JSONDecodeError):
            return False, "json assertion could not parse output"
    if kind in {"metric_at_least", "metric_at_most"}:
        try: value = float(assertion["value"]); observed = float(assertion["observed"])
        except (KeyError, TypeError, ValueError): return False, "metric assertion missing numeric values"
        passed = observed >= value if kind == "metric_at_least" else observed <= value
        return passed, f"metric={observed} bound={value}"
    return False, f"unsupported assertion type={kind!r}"


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
        if r.get("type", "behavior") not in REQUIREMENT_TYPES: errors.append(f"requirement {rid} type must be one of {sorted(REQUIREMENT_TYPES)}")
        if r.get("priority", "must") not in PRIORITIES: errors.append(f"requirement {rid} priority must be one of {sorted(PRIORITIES)}")
        _implementation_paths(r.get("implementation_paths"), f"requirement {rid}", errors)
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
        if "evidence_type" in c and c.get("evidence_type") not in EVIDENCE_TYPES: errors.append(f"acceptance {aid} evidence_type must be one of {sorted(EVIDENCE_TYPES)}")
        _implementation_paths(c.get("implementation_paths"), f"acceptance {aid}", errors)
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
                assertion = edge.get("assertion", {"type": "exit_code", "equals": 0})
                passed, detail = _assertion(check, assertion)
                detail = f"check={edge['check_id']} {detail}"
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
                assertion = edge.get("assertion", {"type": "exit_code", "equals": 0})
                passed, detail = _assertion(check, assertion)
                detail = f"provider={provider} check={edge['check_id']} {detail}"
            edge_rows.append({"provider": provider, "passed": passed, "detail": detail, **{k:v for k,v in edge.items() if k != "provider"}})
        policy = c.get("policy", "all")
        passed = all(x["passed"] for x in edge_rows) if policy == "all" else any(x["passed"] for x in edge_rows)
        surfaces = c.get("implementation_paths", [])
        matched_surfaces = sorted({path for path in changed_paths for pattern in surfaces if _path_match(path, pattern)})
        surface_passed = not surfaces or bool(matched_surfaces)
        if surfaces and not surface_passed:
            errors.append(f"acceptance criterion implementation surface unmatched: {c['id']}")
        passed = passed and surface_passed
        status = "PASS" if passed else "FAIL"
        row = {"id": c["id"], "requirement_id": c["requirement_id"], "statement": c["statement"], "required": c.get("required", True), "policy": policy, "status": status, "evidence_type": c.get("evidence_type"), "implementation_paths": surfaces, "implementation_matches": matched_surfaces, "implementation_surface_passed": surface_passed, "evidence": edge_rows}
        criterion_rows.append(row)
        if row["required"] and not passed:
            errors.append(f"acceptance criterion failed: {row['id']}")
    requirement_coverage = []
    for requirement in req["requirements"]:
        rid = requirement["id"]
        rows = [row for row in criterion_rows if row["requirement_id"] == rid]
        requirement_coverage.append({
            "requirement_id": rid,
            "type": requirement.get("type", "behavior"),
            "priority": requirement.get("priority", "must"),
            "implementation_paths": requirement.get("implementation_paths", []),
            "criterion_ids": [row["id"] for row in rows],
            "criterion_count": len(rows),
            "passed": bool(rows) and all(row["status"] == "PASS" for row in rows),
        })
    oracle = oracle_integrity(changed_paths, [p for c in checks for p in c.get("verification_paths", [])])
    if oracle["status"] != "CLEAR":
        errors.append("oracle integrity requires an independent verification path: " + ", ".join(oracle["proof_surface_changes"]))
    return {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "semantic_diff": classify_semantic_paths(changed_paths),
        "oracle_integrity": oracle,
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
