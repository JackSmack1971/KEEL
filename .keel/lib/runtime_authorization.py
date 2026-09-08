"""Pure runtime-trust, authorization, and effect-boundary contracts.

Nothing in this module executes an effect.  Callers supply observations and time;
configuration and legacy authorization flags are never promoted into authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Protocol

import semantic_kernel as sk


REQUIRED_RUNTIME_SURFACES = (
    "repository", "git", "sandbox_permissions", "hook_trust",
    "workspace_isolation", "network_mediation", "external_effect_mediation",
)


class AutonomyDecision(str, Enum):
    ALLOW_AUTONOMOUS = "ALLOW_AUTONOMOUS"
    ALLOW_WITH_STRONGER_VERIFICATION = "ALLOW_WITH_STRONGER_VERIFICATION"
    REQUIRE_CAPABILITY = "REQUIRE_CAPABILITY"
    REQUIRE_INDEPENDENT_REVIEW = "REQUIRE_INDEPENDENT_REVIEW"
    REQUIRE_HUMAN_DECISION = "REQUIRE_HUMAN_DECISION"
    PROHIBIT = "PROHIBIT"


class EffectBoundary(str, Enum):
    MEDIATED = "MEDIATED"
    OBSERVED = "OBSERVED"
    UNCONFINED = "UNCONFINED"


@dataclass(frozen=True)
class TrustFactors:
    consequence: str
    reversibility: str
    uncertainty: str
    observability: str
    evidence_strength: str
    runtime_enforcement: str
    authorization: str
    recovery_cost: str


@dataclass(frozen=True)
class PolicyDecision:
    decision: AutonomyDecision
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class GrantEvaluation:
    valid: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class EffectReceipt:
    request_id: str
    adapter_id: str
    boundary: EffectBoundary
    outcome: str
    subject_digest: str
    observation_reference: str

    def __post_init__(self) -> None:
        sk.validate_identity(self.request_id, "effect-request")
        if not self.adapter_id or not self.outcome or not self.observation_reference:
            raise sk.ModelError("effect receipt fields must be non-empty")
        sk.validate_digest(self.subject_digest)


class EffectAdapter(Protocol):
    """Provider boundary contract; implementations must declare confinement honestly."""
    adapter_id: str
    boundary: EffectBoundary

    def supports(self, request: sk.EffectRequest, profile: sk.RuntimeProfile) -> bool: ...
    def attempt(self, request: sk.EffectRequest, grant: sk.CapabilityGrant) -> EffectReceipt: ...


def _digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def observe_runtime(*, identity: str, runtime: str, source: str,
                    observations: Mapping[str, str], runtime_version: str | None = None,
                    hook_coverage: tuple[str, ...] = (), tool_coverage: tuple[str, ...] = (),
                    providers: tuple[str, ...] = (), tools: tuple[str, ...] = (),
                    unsupported: tuple[str, ...] = (), unobservable: tuple[str, ...] = ()) -> sk.RuntimeProfile:
    """Create a profile from supplied observations, marking every omitted core surface unobserved."""
    surfaces = {name: observations.get(name, "UNOBSERVED") for name in REQUIRED_RUNTIME_SURFACES}
    surfaces.update(observations)
    knowledge = sk.Knowledge.CONFLICTING if "CONFLICTING" in surfaces.values() else sk.Knowledge.STALE if "STALE" in surfaces.values() else sk.Knowledge.UNKNOWN if any(v in {"UNOBSERVED", "UNSUPPORTED"} for v in surfaces.values()) else sk.Knowledge.KNOWN
    support = sk.Support.UNSUPPORTED if "UNSUPPORTED" in surfaces.values() else sk.Support.SUPPORTED
    return sk.RuntimeProfile(schema="keel.runtime-profile", schema_version=1, identity=identity,
        provenance=sk.Provenance(sk.ProvenanceKind.RUNTIME_OBSERVATION, source, runtime_profile_id=identity),
        runtime=runtime, runtime_version=runtime_version, surfaces=surfaces,
        observations=tuple(sorted(f"{k}={v}" for k, v in observations.items())),
        hook_coverage=tuple(sorted(hook_coverage)), tool_coverage=tuple(sorted(tool_coverage)),
        providers=tuple(sorted(providers)), tools=tuple(sorted(tools)),
        unsupported_surfaces=tuple(sorted(unsupported)), unobservable_surfaces=tuple(sorted(unobservable)),
        knowledge=knowledge, support=support)


def _instant(value: str | None) -> datetime | None:
    if value is None: return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise sk.ModelError(f"invalid grant instant: {value}") from exc
    if parsed.tzinfo is None: raise sk.ModelError("grant instant must include a timezone")
    return parsed.astimezone(timezone.utc)


def evaluate_grant(grant: sk.CapabilityGrant, request: sk.EffectRequest, *,
                   work_id: str, change_id: str, intent_digest: str,
                   constraint_context: Mapping[str, Any], at: str,
                   accepted_issuers: tuple[str, ...]) -> GrantEvaluation:
    reasons: list[str] = []
    if grant.subject_id != request.subject_id: reasons.append("subject mismatch")
    if grant.effect_request_id != request.identity: reasons.append("effect request mismatch")
    if grant.work_id != work_id: reasons.append("work mismatch")
    if grant.change_id != change_id: reasons.append("change mismatch")
    if grant.action != (request.action or request.effect_type): reasons.append("action mismatch")
    if grant.resource != request.resource: reasons.append("resource mismatch")
    if grant.intent_digest != intent_digest or request.intent_digest != intent_digest: reasons.append("intent digest mismatch")
    if grant.issuer not in accepted_issuers: reasons.append("issuer not accepted")
    if not grant.evidence_reference: reasons.append("issuer evidence missing")
    for key, expected in grant.constraints.items():
        if constraint_context.get(key) != expected: reasons.append(f"constraint mismatch: {key}")
    now = _instant(at); start = _instant(grant.valid_from); expiry = _instant(grant.expires_at)
    if start and now and now < start: reasons.append("grant not yet valid")
    if expiry and now and now >= expiry: reasons.append("grant expired")
    if grant.max_uses is not None and grant.uses >= grant.max_uses: reasons.append("grant exhausted")
    if grant.validity is not sk.Validity.VALID or grant.knowledge is not sk.Knowledge.KNOWN: reasons.append("grant state not valid and known")
    return GrantEvaluation(not reasons, tuple(reasons))


def evaluate_autonomy(factors: TrustFactors) -> PolicyDecision:
    """Apply a fail-closed ordered ceiling. Values are explicit policy vocabulary."""
    values = vars(factors)
    allowed = {
        "consequence": {"LOW", "MEDIUM", "HIGH", "CATASTROPHIC"}, "reversibility": {"EASY", "BOUNDED", "DIFFICULT", "IRREVERSIBLE"},
        "uncertainty": {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}, "observability": {"STRONG", "PARTIAL", "WEAK", "NONE"},
        "evidence_strength": {"STRONG", "ADEQUATE", "WEAK", "NONE"}, "runtime_enforcement": {"MEDIATED", "OBSERVED", "UNCONFINED", "UNKNOWN"},
        "authorization": {"VALID", "NOT_REQUIRED", "MISSING", "INVALID"}, "recovery_cost": {"LOW", "MEDIUM", "HIGH", "UNBOUNDED"},
    }
    unknown = [f"unsupported {key}={value}" for key, value in values.items() if value not in allowed[key]]
    if unknown: return PolicyDecision(AutonomyDecision.PROHIBIT, tuple(unknown))
    if factors.consequence == "CATASTROPHIC" or factors.reversibility == "IRREVERSIBLE" or factors.recovery_cost == "UNBOUNDED" or factors.authorization == "INVALID":
        return PolicyDecision(AutonomyDecision.PROHIBIT, ("prohibitive consequence, irreversibility, recovery cost, or invalid authority",))
    if factors.authorization == "MISSING": return PolicyDecision(AutonomyDecision.REQUIRE_CAPABILITY, ("a valid capability grant is absent",))
    if factors.runtime_enforcement in {"UNCONFINED", "UNKNOWN"} or factors.observability == "NONE" or factors.uncertainty == "UNKNOWN":
        return PolicyDecision(AutonomyDecision.REQUIRE_HUMAN_DECISION, ("runtime enforcement or decision surface is not sufficiently observable",))
    if factors.consequence == "HIGH" or factors.reversibility == "DIFFICULT" or factors.recovery_cost == "HIGH":
        return PolicyDecision(AutonomyDecision.REQUIRE_INDEPENDENT_REVIEW, ("high consequence or recovery burden requires independent review",))
    if factors.uncertainty == "HIGH" or factors.observability == "WEAK" or factors.evidence_strength in {"WEAK", "NONE"} or factors.runtime_enforcement == "OBSERVED":
        return PolicyDecision(AutonomyDecision.ALLOW_WITH_STRONGER_VERIFICATION, ("available authority is bounded by weak evidence or observation-only enforcement",))
    return PolicyDecision(AutonomyDecision.ALLOW_AUTONOMOUS, ("low bounded consequence with adequate observed enforcement and evidence",))


def execution_readiness(request: sk.EffectRequest, profile: sk.RuntimeProfile,
                        grant_evaluation: GrantEvaluation | None) -> dict[str, Any]:
    blockers = []
    if grant_evaluation is None or not grant_evaluation.valid: blockers.append("valid capability grant required")
    if profile.knowledge is not sk.Knowledge.KNOWN: blockers.append("runtime profile is not fully known")
    return {"planning_valid": True, "execution_ready": not blockers, "blockers": blockers}


def adapt_legacy_effects(document: Mapping[str, Any], *, change_id: str, intent_digest: str) -> tuple[sk.EffectRequest, ...]:
    effects = document.get("external_effects", [])
    capabilities = document.get("effect_capabilities", [])
    if not isinstance(effects, list) or not isinstance(capabilities, list): raise sk.ModelError("legacy effects lists are malformed")
    result = []
    source_digest = _digest(document)
    for index, action in enumerate(effects):
        if not isinstance(action, str) or not action.strip(): raise sk.ModelError("legacy effect must be non-empty text")
        effect_type = capabilities[index] if index < len(capabilities) else "legacy.unknown"
        result.append(sk.EffectRequest(schema="keel.effect-request", schema_version=1,
            identity=f"keel:effect-request:{change_id}-{index}",
            provenance=sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, f"legacy-effects.json#{source_digest}"),
            subject_id=f"keel:work-unit:{change_id}", effect_type=effect_type, action=action,
            resource="UNKNOWN", intent_digest=intent_digest, knowledge=sk.Knowledge.UNKNOWN,
            attributes={"legacy_source_digest": source_digest, "authorization_required": bool(document.get("authorization_required"))}))
    return tuple(result)


def adapt_legacy_authorization(document: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve legacy evidence as a non-authoritative compatibility observation."""
    return {"schema": "keel.legacy-authorization-observation", "source_digest": _digest(document),
            "required": bool(document.get("required")), "reported_authorized": bool(document.get("authorized")),
            "authority": document.get("authority", ""), "evidence_reference": document.get("evidence_reference", ""),
            "capability_grants": [], "permission": "NOT_GRANTED"}
