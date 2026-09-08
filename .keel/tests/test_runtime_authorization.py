from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import runtime_authorization as ra
import semantic_kernel as sk

D = "sha256:" + "a" * 64
P = sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, "operator:test")
common = {"schema": "keel.effect-request", "schema_version": 1, "identity": "keel:effect-request:deploy", "provenance": P}
request = sk.EffectRequest(**common, effect_type="cloud.deploy", subject_id="keel:work-unit:deploy", action="deploy", resource="cluster:prod", intent_digest=D)
grant = sk.CapabilityGrant(schema="keel.capability-grant", schema_version=1, identity="keel:capability-grant:deploy", provenance=P,
    subject_id=request.subject_id, effect_request_id=request.identity, issuer="operator", work_id="work-7", change_id="change-7",
    action="deploy", resource="cluster:prod", constraints={"region": "eu"}, intent_digest=D, evidence_reference="ticket:7",
    valid_from="2026-09-01T00:00:00Z", expires_at="2026-10-01T00:00:00Z", max_uses=2, uses=0)

# Missing observations stay unknown; no configuration is promoted to observation.
partial = ra.observe_runtime(identity="keel:runtime-profile:partial", runtime="codex", source="test", observations={"git": "OBSERVED"}, tools=("shell",))
assert partial.knowledge is sk.Knowledge.UNKNOWN
assert partial.surfaces["hook_trust"] == "UNOBSERVED"
assert partial.runtime_version is None
assert sk.decode(sk.to_document(partial)) == partial
conflicting = ra.observe_runtime(identity="keel:runtime-profile:conflict", runtime="codex", source="test", observations={"hook_trust": "CONFLICTING"})
assert conflicting.knowledge is sk.Knowledge.CONFLICTING
unsupported = ra.observe_runtime(identity="keel:runtime-profile:unsupported", runtime="codex", source="test", observations={"workspace_isolation": "UNSUPPORTED"})
assert unsupported.support is sk.Support.UNSUPPORTED

# Every binding is enforced, including intent drift, expiry, exhaustion, and constraints.
args = dict(work_id="work-7", change_id="change-7", intent_digest=D, constraint_context={"region": "eu"}, at="2026-09-08T00:00:00Z", accepted_issuers=("operator",))
assert ra.evaluate_grant(grant, request, **args).valid
mutations = (
    (dataclasses.replace(grant, subject_id="keel:work-unit:other"), request, args),
    (dataclasses.replace(grant, action="delete"), request, args),
    (dataclasses.replace(grant, resource="cluster:other"), request, args),
    (dataclasses.replace(grant, work_id="other"), request, args),
    (dataclasses.replace(grant, change_id="other"), request, args),
    (dataclasses.replace(grant, intent_digest="sha256:" + "b" * 64), request, args),
    (dataclasses.replace(grant, issuer="stranger"), request, args),
    (dataclasses.replace(grant, constraints={"region": "us"}), request, args),
    (dataclasses.replace(grant, uses=2), request, args),
    (grant, request, {**args, "at": "2026-10-01T00:00:00Z"}),
)
for candidate, effect, kwargs in mutations: assert not ra.evaluate_grant(candidate, effect, **kwargs).valid

# The hostile policy matrix reaches all outcomes with an ordered fail-closed ceiling.
base = ra.TrustFactors("LOW", "EASY", "LOW", "STRONG", "STRONG", "MEDIATED", "VALID", "LOW")
cases = {
    ra.AutonomyDecision.ALLOW_AUTONOMOUS: base,
    ra.AutonomyDecision.ALLOW_WITH_STRONGER_VERIFICATION: dataclasses.replace(base, evidence_strength="WEAK"),
    ra.AutonomyDecision.REQUIRE_CAPABILITY: dataclasses.replace(base, authorization="MISSING"),
    ra.AutonomyDecision.REQUIRE_INDEPENDENT_REVIEW: dataclasses.replace(base, consequence="HIGH"),
    ra.AutonomyDecision.REQUIRE_HUMAN_DECISION: dataclasses.replace(base, runtime_enforcement="UNCONFINED"),
    ra.AutonomyDecision.PROHIBIT: dataclasses.replace(base, reversibility="IRREVERSIBLE"),
}
for expected, factors in cases.items(): assert ra.evaluate_autonomy(factors).decision is expected

# Planning remains valid while execution waits on both runtime evidence and a grant.
readiness = ra.execution_readiness(request, partial, None)
assert readiness["planning_valid"] is True and readiness["execution_ready"] is False

# Effect adapter/receipt vocabulary distinguishes actual confinement claims.
for boundary in ra.EffectBoundary:
    receipt = ra.EffectReceipt(request.identity, "adapter:test", boundary, "NOT_ATTEMPTED", D, "fixture:test")
    assert receipt.boundary is boundary

# Legacy authorized=true is retained as reported evidence but produces no grant.
legacy_auth = {"required": True, "authorized": True, "authority": "operator", "evidence_reference": "chat:1", "effects_digest": D}
adapted_auth = ra.adapt_legacy_authorization(legacy_auth)
assert adapted_auth["reported_authorized"] is True
assert adapted_auth["permission"] == "NOT_GRANTED" and adapted_auth["capability_grants"] == []
legacy_effects = {"external_effects": ["deploy"], "effect_capabilities": ["cloud.deploy"], "irreversible": False, "authorization_required": True}
adapted = ra.adapt_legacy_effects(legacy_effects, change_id="change-7", intent_digest=D)
assert len(adapted) == 1 and adapted[0].knowledge is sk.Knowledge.UNKNOWN
assert ra.adapt_legacy_effects(legacy_effects, change_id="change-7", intent_digest=D) == adapted

print(json.dumps({"status": "PASS", "checks": ["runtime-negative-states", "grant-bindings", "intent-drift", "expiry", "max-use", "six-policy-outcomes", "effect-boundaries", "planning-without-grant", "legacy-no-grant"]}, sort_keys=True))
