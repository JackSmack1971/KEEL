"""Pure canonical semantic records for the staged KEEL kernel migration.

This module deliberately has no integration with the landed lifecycle.  It only
defines values, validation, canonical encoding, and content identity.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, ClassVar, Mapping


SCHEMA_VERSION = 1
IDENTITY_RE = re.compile(r"^keel:(fact|requirement|work-unit|edge|effect-request|capability-grant|evidence-requirement|evidence-receipt|decision|attestation|runtime-profile):[a-z0-9][a-z0-9._-]{0,127}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


class ModelError(ValueError):
    """An authoritative semantic record is malformed or unsupported."""


class Validity(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class Knowledge(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"


class Support(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class Readiness(str, Enum):
    READY = "READY"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"


class Lifecycle(str, Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    SEALED = "SEALED"
    INTEGRATING = "INTEGRATING"
    LANDED = "LANDED"
    FAILED = "FAILED"


class ProvenanceKind(str, Enum):
    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"
    NORMALIZATION = "NORMALIZATION"
    DERIVATION = "DERIVATION"
    RUNTIME_OBSERVATION = "RUNTIME_OBSERVATION"


class ResourceKind(str, Enum):
    REPOSITORY_PATH = "REPOSITORY_PATH"
    REPOSITORY = "REPOSITORY"


def _nonempty(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{label} must be a non-empty string")


def validate_identity(value: str, expected_kind: str | None = None) -> None:
    if not isinstance(value, str) or not IDENTITY_RE.fullmatch(value) or ".." in value:
        raise ModelError(f"malformed canonical identity: {value!r}")
    if expected_kind and value.split(":", 2)[1] != expected_kind:
        raise ModelError(f"identity {value!r} does not identify {expected_kind}")


def validate_digest(value: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ModelError(f"malformed content digest: {value!r}")


def repository_path(value: str) -> str:
    """Normalize a portable repository-relative POSIX path without touching disk."""
    if not isinstance(value, str) or not value or "\\" in value or WINDOWS_ABSOLUTE_RE.match(value):
        raise ModelError("repository path must be non-empty portable POSIX text")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix() or value in {".", ".."} or ".." in path.parts:
        raise ModelError(f"invalid repository-relative path: {value!r}")
    if any(part in {"", ".", ".git"} for part in path.parts):
        raise ModelError(f"unsafe repository-relative path: {value!r}")
    return value


@dataclass(frozen=True)
class ResourceIdentity:
    kind: ResourceKind
    path: str = "."

    def __post_init__(self) -> None:
        if self.kind is ResourceKind.REPOSITORY:
            if self.path != ".":
                raise ModelError("repository resource path must be '.'")
        else:
            repository_path(self.path)

    @property
    def identity(self) -> str:
        return "repo:." if self.kind is ResourceKind.REPOSITORY else f"repo:{self.path}"


@dataclass(frozen=True)
class Provenance:
    kind: ProvenanceKind
    source: str
    inputs: tuple[str, ...] = ()
    rule: str | None = None
    runtime_profile_id: str | None = None

    def __post_init__(self) -> None:
        _nonempty(self.source, "provenance source")
        if len(set(self.inputs)) != len(self.inputs):
            raise ModelError("provenance inputs must be unique")
        for item in self.inputs:
            validate_identity(item)
        transformed = self.kind in {ProvenanceKind.NORMALIZATION, ProvenanceKind.DERIVATION}
        if transformed and (not self.inputs or not self.rule):
            raise ModelError("normalization/derivation provenance requires inputs and rule")
        if not transformed and self.rule is not None:
            raise ModelError("observation provenance cannot claim a transformation rule")
        if self.kind is ProvenanceKind.RUNTIME_OBSERVATION:
            if self.runtime_profile_id is None:
                raise ModelError("runtime observation requires runtime_profile_id")
            validate_identity(self.runtime_profile_id, "runtime-profile")
        elif self.runtime_profile_id is not None:
            raise ModelError("runtime_profile_id is only valid for runtime observation")


def _portable(value: Any, key: str = "") -> None:
    forbidden = {"hostname", "host", "username", "user", "home", "cwd", "pid", "process_id", "timestamp"}
    if key.lower() in forbidden:
        raise ModelError(f"host-specific field is forbidden in portable intent: {key}")
    if isinstance(value, Mapping):
        for k, v in value.items():
            if not isinstance(k, str):
                raise ModelError("canonical mapping keys must be strings")
            _portable(v, k)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _portable(item, key)
    elif isinstance(value, str) and any(
        token.startswith(("/", "file://", "~")) or WINDOWS_ABSOLUTE_RE.match(token)
        for token in value.split()
    ):
        raise ModelError(f"host-specific absolute value is forbidden in portable intent: {value!r}")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ModelError("canonical numbers must be finite")
    elif value is not None and not isinstance(value, (str, int, bool, float, Enum, ResourceIdentity, Provenance)):
        raise ModelError(f"unsupported canonical value type: {type(value).__name__}")


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class Record:
    KIND: ClassVar[str]
    schema: str
    schema_version: int
    identity: str
    provenance: Provenance
    validity: Validity = Validity.VALID
    knowledge: Knowledge = Knowledge.KNOWN
    support: Support = Support.SUPPORTED
    readiness: Readiness = Readiness.WAITING
    lifecycle: Lifecycle = Lifecycle.DRAFT
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema != f"keel.{self.KIND}" or type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise ModelError(f"unsupported schema identity/version: {self.schema!r}/{self.schema_version!r}")
        validate_identity(self.identity, self.KIND)
        if not isinstance(self.provenance, Provenance):
            raise ModelError("provenance must be a Provenance value")
        for name, enum_type in (("validity", Validity), ("knowledge", Knowledge), ("support", Support), ("readiness", Readiness), ("lifecycle", Lifecycle)):
            if not isinstance(getattr(self, name), enum_type):
                raise ModelError(f"{name} must be a {enum_type.__name__} value")
        if not isinstance(self.attributes, Mapping):
            raise ModelError("attributes must be a mapping")
        _portable(self.attributes)
        if self.KIND in PORTABLE_KIND_NAMES:
            _portable(_plain(self.provenance), "provenance")
            for model_field in dataclasses.fields(self):
                if model_field.name not in {"schema", "schema_version", "identity", "provenance"}:
                    _portable(getattr(self, model_field.name), model_field.name)
        object.__setattr__(self, "attributes", _freeze(self.attributes))


@dataclass(frozen=True)
class Fact(Record):
    KIND: ClassVar[str] = "fact"
    claim: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); _nonempty(self.claim, "claim")


@dataclass(frozen=True)
class Requirement(Record):
    KIND: ClassVar[str] = "requirement"
    obligation: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); _nonempty(self.obligation, "obligation")


@dataclass(frozen=True)
class WorkUnit(Record):
    KIND: ClassVar[str] = "work-unit"
    objective: str = ""
    resources: tuple[ResourceIdentity, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__(); _nonempty(self.objective, "objective")
        if not all(isinstance(r, ResourceIdentity) for r in self.resources): raise ModelError("work resources must be ResourceIdentity values")
        if len({r.identity for r in self.resources}) != len(self.resources): raise ModelError("work resources must be unique")


@dataclass(frozen=True)
class Edge(Record):
    KIND: ClassVar[str] = "edge"
    source_id: str = ""
    target_id: str = ""
    edge_type: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.source_id); validate_identity(self.target_id); _nonempty(self.edge_type, "edge_type")


@dataclass(frozen=True)
class EffectRequest(Record):
    KIND: ClassVar[str] = "effect-request"
    effect_type: str = ""
    subject_id: str = ""
    resources: tuple[ResourceIdentity, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__(); _nonempty(self.effect_type, "effect_type"); validate_identity(self.subject_id)
        if not all(isinstance(r, ResourceIdentity) for r in self.resources): raise ModelError("effect resources must be ResourceIdentity values")
        if len({r.identity for r in self.resources}) != len(self.resources): raise ModelError("effect resources must be unique")


@dataclass(frozen=True)
class CapabilityGrant(Record):
    KIND: ClassVar[str] = "capability-grant"
    subject_id: str = ""
    effect_request_id: str = ""
    issuer: str = ""
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.subject_id); validate_identity(self.effect_request_id, "effect-request"); _nonempty(self.issuer, "issuer")


@dataclass(frozen=True)
class EvidenceRequirement(Record):
    KIND: ClassVar[str] = "evidence-requirement"
    subject_id: str = ""
    boundary: str = ""
    claim: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.subject_id); _nonempty(self.boundary, "boundary"); _nonempty(self.claim, "claim")


@dataclass(frozen=True)
class EvidenceReceipt(Record):
    KIND: ClassVar[str] = "evidence-receipt"
    requirement_id: str = ""
    subject_id: str = ""
    provider: str = ""
    outcome: str = ""
    subject_digest: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.requirement_id, "evidence-requirement"); validate_identity(self.subject_id); _nonempty(self.provider, "provider"); _nonempty(self.outcome, "outcome"); validate_digest(self.subject_digest)


@dataclass(frozen=True)
class Decision(Record):
    KIND: ClassVar[str] = "decision"
    subject_id: str = ""
    resolution: str = ""
    authority: str = ""

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.subject_id); _nonempty(self.resolution, "resolution"); _nonempty(self.authority, "authority")


@dataclass(frozen=True)
class Attestation(Record):
    KIND: ClassVar[str] = "attestation"
    subject_id: str = ""
    boundary: str = ""
    tree_digest: str = ""
    intent_digest: str = ""
    receipt_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__(); validate_identity(self.subject_id); _nonempty(self.boundary, "boundary"); validate_digest(self.tree_digest); validate_digest(self.intent_digest)
        for value in self.receipt_ids: validate_identity(value, "evidence-receipt")


@dataclass(frozen=True)
class RuntimeProfile(Record):
    KIND: ClassVar[str] = "runtime-profile"
    runtime: str = ""
    observations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__(); _nonempty(self.runtime, "runtime")


RECORD_TYPES = {cls.KIND: cls for cls in (Fact, Requirement, WorkUnit, Edge, EffectRequest, CapabilityGrant, EvidenceRequirement, EvidenceReceipt, Decision, Attestation, RuntimeProfile)}
PORTABLE_KIND_NAMES = {Requirement.KIND, WorkUnit.KIND, EffectRequest.KIND, EvidenceRequirement.KIND, Decision.KIND}


def _plain(value: Any) -> Any:
    if isinstance(value, Enum): return value.value
    if dataclasses.is_dataclass(value):
        return {f.name: _plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Mapping): return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [_plain(v) for v in value]
    return value


def to_document(record: Record) -> dict[str, Any]:
    return {"kind": record.KIND, **_plain(record)}


def canonical_bytes(value: Record | Mapping[str, Any]) -> bytes:
    document = to_document(value) if isinstance(value, Record) else _plain(value)
    return (json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def content_digest(value: Record | Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _strict(data: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(data) - allowed
    missing = allowed - set(data)
    if unknown: raise ModelError(f"unknown {label} field(s): {', '.join(sorted(unknown))}")
    if missing: raise ModelError(f"missing {label} field(s): {', '.join(sorted(missing))}")


def decode(document: Mapping[str, Any]) -> Record:
    """Strictly decode one authoritative schema document."""
    if not isinstance(document, Mapping): raise ModelError("record document must be a mapping")
    kind = document.get("kind")
    cls = RECORD_TYPES.get(kind)
    if cls is None: raise ModelError(f"unknown primitive kind: {kind!r}")
    fields = {f.name for f in dataclasses.fields(cls)}
    _strict(document, fields | {"kind"}, "record")
    values = {name: document[name] for name in fields}
    try:
        p = values["provenance"]
        _strict(p, {"kind", "source", "inputs", "rule", "runtime_profile_id"}, "provenance")
        values["provenance"] = Provenance(ProvenanceKind(p["kind"]), p["source"], tuple(p["inputs"]), p["rule"], p["runtime_profile_id"])
        for name, enum in (("validity", Validity), ("knowledge", Knowledge), ("support", Support), ("readiness", Readiness), ("lifecycle", Lifecycle)):
            values[name] = enum(values[name])
        if "resources" in values:
            values["resources"] = tuple(_decode_resource(v) for v in values["resources"])
        for name in ("conditions", "receipt_ids", "observations"):
            if name in values: values[name] = tuple(values[name])
        return cls(**values)
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ModelError): raise
        raise ModelError(f"invalid {kind} record: {exc}") from exc


def _decode_resource(value: Mapping[str, Any]) -> ResourceIdentity:
    if not isinstance(value, Mapping): raise ModelError("resource must be a mapping")
    _strict(value, {"kind", "path"}, "resource")
    return ResourceIdentity(ResourceKind(value["kind"]), value["path"])


def validate_collection(records: tuple[Record, ...] | list[Record]) -> None:
    """Validate identity uniqueness and references, without any I/O."""
    if not all(isinstance(record, Record) for record in records): raise ModelError("collection values must be canonical records")
    identities = [record.identity for record in records]
    if len(set(identities)) != len(identities): raise ModelError("duplicate canonical identity")
    known = set(identities)
    for record in records:
        for field_name in ("source_id", "target_id", "subject_id", "effect_request_id", "requirement_id"):
            reference = getattr(record, field_name, None)
            if reference and reference not in known: raise ModelError(f"dangling reference {reference!r} from {record.identity}")
        for reference in getattr(record, "receipt_ids", ()):
            if reference not in known: raise ModelError(f"dangling receipt reference {reference!r}")
