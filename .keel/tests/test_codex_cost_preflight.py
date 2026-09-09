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
