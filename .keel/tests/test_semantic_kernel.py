import copy
import dataclasses
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".keel" / "lib"))
import semantic_kernel as sk


P = sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, "operator:contract")
RUNTIME_ID = "keel:runtime-profile:local-observation"
RUNTIME_P = sk.Provenance(sk.ProvenanceKind.RUNTIME_OBSERVATION, "codex:session", runtime_profile_id=RUNTIME_ID)
D = "sha256:" + "a" * 64


def common(kind, slug):
    return {"schema": f"keel.{kind}", "schema_version": 1, "identity": f"keel:{kind}:{slug}", "provenance": P}


records = [
    sk.Fact(**common("fact", "repository-clean"), claim="repository is clean"),
    sk.Requirement(**common("requirement", "determinism"), obligation="serialize deterministically"),
    sk.WorkUnit(**common("work-unit", "kernel"), objective="implement kernel", resources=(sk.ResourceIdentity(sk.ResourceKind.REPOSITORY_PATH, ".keel/lib/semantic_kernel.py"),)),
    sk.Edge(**common("edge", "requirement-work"), source_id="keel:requirement:determinism", target_id="keel:work-unit:kernel", edge_type="SATISFIED_BY"),
    sk.EffectRequest(**common("effect-request", "local-write"), effect_type="filesystem.write", subject_id="keel:work-unit:kernel"),
    sk.CapabilityGrant(**common("capability-grant", "local-write"), subject_id="keel:work-unit:kernel", effect_request_id="keel:effect-request:local-write", issuer="operator"),
    sk.EvidenceRequirement(**common("evidence-requirement", "kernel-tests"), subject_id="keel:work-unit:kernel", boundary="candidate", claim="tests pass"),
    sk.EvidenceReceipt(**common("evidence-receipt", "kernel-tests"), requirement_id="keel:evidence-requirement:kernel-tests", subject_id="keel:work-unit:kernel", provider="python", outcome="PASS", subject_digest=D),
    sk.Decision(**common("decision", "representation"), subject_id="keel:work-unit:kernel", resolution="use strict records", authority="operator"),
    sk.Attestation(**common("attestation", "candidate"), subject_id="keel:work-unit:kernel", boundary="candidate", tree_digest=D, intent_digest=D, receipt_ids=("keel:evidence-receipt:kernel-tests",)),
    sk.RuntimeProfile(**{**common("runtime-profile", "local-observation"), "provenance": RUNTIME_P}, runtime="codex", observations=("hooks unverified",)),
]

# Every canonical primitive has a distinct schema, strict round trip, and digest.
assert set(sk.RECORD_TYPES) == {record.KIND for record in records}
for record in records:
    document = sk.to_document(record)
    decoded = sk.decode(json.loads(sk.canonical_bytes(record)))
    assert sk.to_document(decoded) == document
    assert sk.content_digest(decoded) == sk.content_digest(record)

# Dimensions are orthogonal types rather than one overloaded vocabulary.
dimensions = (sk.Validity, sk.Knowledge, sk.Support, sk.Readiness, sk.Lifecycle)
assert len(set(dimensions)) == 5
assert sk.Knowledge.UNKNOWN.value not in {x.value for x in sk.Lifecycle}
assert sk.Support.UNSUPPORTED.value not in {x.value for x in sk.Lifecycle}
assert sk.Readiness.BLOCKED.value not in {x.value for x in sk.Lifecycle}

# Dict insertion order cannot affect canonical bytes or content identity.
left = sk.Requirement(**common("requirement", "ordered"), obligation="stable", attributes={"z": {"b": 2, "a": 1}, "a": True})
right = sk.Requirement(**common("requirement", "ordered"), obligation="stable", attributes={"a": True, "z": {"a": 1, "b": 2}})
assert sk.canonical_bytes(left) == sk.canonical_bytes(right)
assert sk.content_digest(left) == sk.content_digest(right)
assert sk.canonical_bytes(left).endswith(b"\n")

# Authoritative records reject unknown/missing fields and schema/kind/version drift.
base = sk.to_document(records[0])
for mutation in (
    lambda d: d.update(extra=True),
    lambda d: d.pop("claim"),
    lambda d: d.update(kind="mystery"),
    lambda d: d.update(schema="keel.requirement"),
    lambda d: d.update(schema_version=2),
):
    case = copy.deepcopy(base)
    mutation(case)
    try:
        sk.decode(case)
        raise AssertionError("malformed authoritative record was accepted")
    except sk.ModelError:
        pass

bad_provenance = copy.deepcopy(base)
bad_provenance["provenance"]["extra"] = "silent-loss"
try:
    sk.decode(bad_provenance)
    raise AssertionError("unknown provenance field was accepted")
except sk.ModelError:
    pass

# Identity, provenance, digest, and repository resources fail closed.
for identity in ("fact:x", "keel:fact:UPPER", "keel:fact:../x", "keel:work-unit:wrong-kind", "keel:fact:"):
    try:
        sk.Fact(**{**common("fact", "ok"), "identity": identity}, claim="x")
        raise AssertionError(identity)
    except sk.ModelError:
        pass

for path in ("/etc/passwd", "../escape", "a/../b", r"C:\\Users\\me", r"a\\b", ".git/config", "a//b"):
    try:
        sk.ResourceIdentity(sk.ResourceKind.REPOSITORY_PATH, path)
        raise AssertionError(path)
    except sk.ModelError:
        pass

for provenance in (
    lambda: sk.Provenance(sk.ProvenanceKind.NORMALIZATION, "adapter"),
    lambda: sk.Provenance(sk.ProvenanceKind.DERIVATION, "rule", ("bad-id",), "v1"),
    lambda: sk.Provenance(sk.ProvenanceKind.RUNTIME_OBSERVATION, "runtime"),
    lambda: sk.Provenance(sk.ProvenanceKind.DIRECT_OBSERVATION, "source", rule="invented"),
):
    try:
        provenance()
        raise AssertionError("defective provenance accepted")
    except sk.ModelError:
        pass

try:
    sk.EvidenceReceipt(**common("evidence-receipt", "bad-digest"), requirement_id="keel:evidence-requirement:kernel-tests", subject_id="keel:work-unit:kernel", provider="python", outcome="PASS", subject_digest="abc")
    raise AssertionError("bad digest accepted")
except sk.ModelError:
    pass

# Portable intent rejects host identity in both named and nested/absolute values.
for attributes in ({"hostname": "builder-7"}, {"nested": {"cwd": "/tmp/repo"}}, {"input": "/home/alice/file"}):
    try:
        sk.Requirement(**common("requirement", "host-leak"), obligation="portable", attributes=attributes)
        raise AssertionError(attributes)
    except sk.ModelError:
        pass
try:
    sk.WorkUnit(**common("work-unit", "host-objective"), objective="write /home/alice/project")
    raise AssertionError("host-specific objective accepted")
except sk.ModelError:
    pass
for invalid_value in ({"number": float("nan")}, {"number": float("inf")}):
    try:
        sk.Requirement(**common("requirement", "bad-number"), obligation="portable", attributes=invalid_value)
        raise AssertionError("non-finite canonical number accepted")
    except sk.ModelError:
        pass
try:
    sk.Requirement(**common("requirement", "bad-state"), obligation="typed states", knowledge="UNKNOWN")
    raise AssertionError("untyped state accepted")
except sk.ModelError:
    pass

# Collection validation rejects duplicate IDs and dangling canonical references.
try:
    sk.validate_collection([records[0], dataclasses.replace(records[0])])
    raise AssertionError("duplicate identity accepted")
except sk.ModelError:
    pass
try:
    sk.validate_collection([records[3]])
    raise AssertionError("dangling edge accepted")
except sk.ModelError:
    pass
sk.validate_collection(records)

# Validation and serialization are pure: filesystem/environment/network helpers are unnecessary.
with patch("pathlib.Path.exists", side_effect=AssertionError("filesystem touched")), patch("os.getenv", side_effect=AssertionError("environment touched")):
    sk.validate_collection(records)
    assert sk.decode(sk.to_document(records[1])).identity == records[1].identity

print(json.dumps({"status": "PASS", "primitive_kinds": sorted(sk.RECORD_TYPES), "hostile_checks": ["identity", "duplicates", "unknown-fields", "schemas", "paths", "ordering", "provenance", "portable-intent", "dangling-references", "pure-validation"]}, sort_keys=True))
