from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel/lib"))
import codex_adapter_kernel as adapter
import runtime_authorization as ra
import semantic_kernel as sk


def profile():
    return ra.observe_runtime(identity="keel:runtime-profile:preflight-test", runtime="codex", source="test",
                              observations={"repository":"OBSERVED", "git":"OBSERVED", "hook_trust":"OBSERVED"})


GOOD = {"auth_mode":"MANAGED_CHATGPT", "provider":"CODEX", "entitlement":"INCLUDED",
        "rate_limit":"AVAILABLE", "paid_continuation":"UNAVAILABLE", "reset_credit":"UNAVAILABLE"}


def check(observations, expected="BLOCKED", resumable=False):
    calls = []
    outcome = adapter.invoke_autonomous_codex(profile(), observations, lambda _: calls.append("invoked"))
    assert outcome.status == expected
    assert outcome.resumable is resumable
    assert calls == ([] if expected == "BLOCKED" else ["invoked"])
    return outcome


def hostile_scenario(name, observations, expected="BLOCKED", resumable=False):
    outcome = check(observations, expected, resumable)
    print(f"scenario {name} PASS ({outcome.status})")
    return outcome


# Keep each hostile-matrix row independently visible to the test runner/audit.
hostile_scenario("managed-chatgpt-auth", GOOD, "INVOKED")
hostile_scenario("api-key-auth", {**GOOD, "auth_mode":"API_KEY"})
hostile_scenario("unknown-auth", {**GOOD, "auth_mode":"UNRECOGNIZED"})
hostile_scenario("unsupported-provider-auth", {**GOOD, "provider":"BEDROCK"})
hostile_scenario("exhausted-limit", {**GOOD, "rate_limit":"EXHAUSTED"}, resumable=True)
hostile_scenario("available-reset-credit", {**GOOD, "reset_credit":"AVAILABLE"})
hostile_scenario("ambiguous-paid-continuation", {**GOOD, "paid_continuation":"AVAILABLE"})
hostile_scenario("malformed-or-missing-observations", None)

mid_session_calls = []
first = adapter.invoke_autonomous_codex(profile(), GOOD, lambda _: mid_session_calls.append("first"))
second = adapter.invoke_autonomous_codex(profile(), {**GOOD, "auth_mode":"API_KEY"}, lambda _: mid_session_calls.append("second"))
assert first.status == "INVOKED" and second.status == "BLOCKED" and mid_session_calls == ["first"]
print("scenario mid-session-auth-mode-change PASS (INVOKED then BLOCKED)")


# Retain the original aggregate hostile-matrix assertions.
assert check(GOOD, "INVOKED").status == "INVOKED"
for key, value in (("auth_mode", "API_KEY"), ("auth_mode", "UNRECOGNIZED"),
                   ("provider", "BEDROCK"), ("paid_continuation", "AVAILABLE")):
    observations = dict(GOOD); observations[key] = value; check(observations)
check(None)
exhausted = check({**GOOD, "rate_limit":"EXHAUSTED"}, resumable=True)
resumed_calls = []
resumed = adapter.invoke_autonomous_codex(profile(), GOOD, lambda _: resumed_calls.append("resumed"))
assert exhausted.resumable and resumed.status == "INVOKED" and resumed_calls == ["resumed"]
check({**GOOD, "reset_credit":"AVAILABLE"})
check({**GOOD, "rate_limit":"AVAILABLE", "reset_credit":"UNKNOWN"})
check({key: value for key, value in GOOD.items() if key != "provider"})
check({**GOOD, "provider": 42})
check({**GOOD, "unexpected": "field"})

forbidden_calls = []
blocked = adapter.invoke_autonomous_codex(profile(), {**GOOD, "rate_limit":"EXHAUSTED"},
    lambda _: forbidden_calls.append("credit-purchase-or-reset-or-rotation-or-secondary-provider"))
assert blocked.status == "BLOCKED" and forbidden_calls == []

forbidden_operations = {
    "credit-purchase": [],
    "rate-limit-reset-consumption": [],
    "identity-rotation": [],
    "secondary-provider-fallback": [],
}
adapter.invoke_autonomous_codex(profile(), {**GOOD, "rate_limit":"EXHAUSTED"},
    lambda _: forbidden_operations["credit-purchase"].append("invoked"))
adapter.invoke_autonomous_codex(profile(), {**GOOD, "reset_credit":"AVAILABLE"},
    lambda _: forbidden_operations["rate-limit-reset-consumption"].append("invoked"))
adapter.invoke_autonomous_codex(profile(), {**GOOD, "auth_mode":"API_KEY"},
    lambda _: forbidden_operations["identity-rotation"].append("invoked"))
adapter.invoke_autonomous_codex(profile(), {**GOOD, "provider":"BEDROCK"},
    lambda _: forbidden_operations["secondary-provider-fallback"].append("invoked"))
assert forbidden_operations["credit-purchase"] == []
assert forbidden_operations["rate-limit-reset-consumption"] == []
assert forbidden_operations["identity-rotation"] == []
assert forbidden_operations["secondary-provider-fallback"] == []
print("forbidden operation credit-purchase PASS")
print("forbidden operation rate-limit-reset-consumption PASS")
print("forbidden operation identity-rotation PASS")
print("forbidden operation secondary-provider-fallback PASS")


class BrokenProfile:
    @property
    def runtime(self):
        raise RuntimeError("preflight observation error")


error_forbidden_operations = {
    "credit-purchase": [],
    "rate-limit-reset-consumption": [],
    "identity-rotation": [],
    "secondary-provider-fallback": [],
}
try:
    adapter.invoke_autonomous_codex(BrokenProfile(), GOOD,
        lambda _: error_forbidden_operations["credit-purchase"].append("invoked"))
except RuntimeError as error:
    assert str(error) == "preflight observation error"
else:
    raise AssertionError("expected preflight exception")
assert error_forbidden_operations["credit-purchase"] == []
assert error_forbidden_operations["rate-limit-reset-consumption"] == []
assert error_forbidden_operations["identity-rotation"] == []
assert error_forbidden_operations["secondary-provider-fallback"] == []
print("forbidden operation exception-path PASS")

calls = []
first = adapter.invoke_autonomous_codex(profile(), GOOD, lambda _: calls.append("first"))
second = adapter.invoke_autonomous_codex(profile(), {**GOOD, "auth_mode":"API_KEY"}, lambda _: calls.append("second"))
assert first.status == "INVOKED" and second.status == "BLOCKED" and calls == ["first"]

request = sk.EffectRequest(schema="keel.effect-request", schema_version=1,
    identity="keel:effect-request:codex", provenance=sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, "test"),
    effect_type="codex.invoke", subject_id="keel:work-unit:codex", action="invoke", resource="codex",
    intent_digest="sha256:" + "a" * 64)
profiled, result = ra.apply_codex_cost_preflight(profile(), GOOD)
assert profiled.cost_status == "SUPPORTED" and result.supported
readiness = ra.execution_readiness(request, profiled, None)
assert not readiness["execution_ready"] and any("capability grant" in item for item in readiness["blockers"])

blocked = ra.default_codex_cost_preflight()[1].to_dict()
assert not any(token in repr(blocked) for token in ("email", "account", "credential", "token"))
print("Codex cost preflight hostile matrix PASS")
