"""Versioned transport envelope and correlation primitives."""
from __future__ import annotations
import hashlib, json, re

API_VERSION = 1
_ID = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_ENVELOPE_KEYS = {"api_version", "status", "correlation", "result", "errors"}

def identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase identifier")
    return value

def correlation(change_id: str, **values: str) -> dict:
    result = {"change_id": identifier(change_id, "change_id")}
    for field, value in values.items():
        if value is not None:
            result[field] = identifier(value, field)
    return result

def envelope(result: dict, correlation_ids: dict | None = None) -> dict:
    status = result.get("status")
    return {"api_version": API_VERSION, "status": "FAIL" if status in {"FAIL", "INVALID"} else "PASS",
            "correlation": correlation_ids or {}, "result": result,
            "errors": result.get("errors", []) if isinstance(result, dict) else []}

def render(result: dict, correlation_ids: dict | None = None) -> str:
    return json.dumps(envelope(result, correlation_ids), indent=2, sort_keys=True)

def validate_envelope(value: object) -> list[str]:
    if not isinstance(value, dict): return ["API response must be an object"]
    errors = []
    if value.get("api_version") != API_VERSION: errors.append(f"unsupported api_version: {value.get('api_version')!r}")
    unknown = sorted(set(value) - _ENVELOPE_KEYS)
    if unknown: errors.append("unknown envelope fields: " + ", ".join(unknown))
    if value.get("status") not in {"PASS", "FAIL", "UNAVAILABLE", "INVALID"}: errors.append("invalid envelope status")
    if not isinstance(value.get("correlation"), dict): errors.append("correlation must be an object")
    if not isinstance(value.get("errors"), list) or any(not isinstance(x, str) for x in value.get("errors", [])): errors.append("errors must be a list of strings")
    return errors

def digest(document: dict) -> str:
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
