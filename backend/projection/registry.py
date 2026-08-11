"""
File Path: /backend/projection/registry.py
Description: Controlled Projection handler registry.
Main Features:
    - Aggregates only explicit descriptors from owner sync services
    - Validates fixed snapshot source and typed handler inputs
    - Rejects malformed, duplicate, or failed handler discovery
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Literal, TYPE_CHECKING
import pkgutil

from app.module_registry import get_enabled_module_manifests

if TYPE_CHECKING:
    from projection.policy_catalog import SnapshotPolicyCatalog


SnapshotSource = Literal["raw", "latest"]
ProjectionHandlerCallable = Callable[[Any, "ProjectionInvocationContext", Mapping[str, object]], object]


class ProjectionRegistryError(RuntimeError):
    """Projection handler declaration or controlled discovery failed."""


@dataclass(frozen=True)
class ProjectionHandlerInput:
    """A typed input that an owner handler accepts from a mapping binding."""

    input_key: str
    type: str
    required: bool
    description: str
    accepted_plc_types: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str)
            for value in (self.input_key, self.type, self.description)
        ):
            raise ProjectionRegistryError("handler input text fields must be strings")
        if type(self.required) is not bool:
            raise ProjectionRegistryError("handler input required must be boolean")
        if not isinstance(self.accepted_plc_types, tuple):
            raise ProjectionRegistryError("handler input accepted_plc_types must be a tuple")
        if not self.input_key.strip():
            raise ProjectionRegistryError("handler input_key must not be blank")
        if not self.type.strip():
            raise ProjectionRegistryError("handler input type must not be blank")
        if not self.description.strip():
            raise ProjectionRegistryError("handler input description must not be blank")
        if not self.accepted_plc_types:
            raise ProjectionRegistryError("handler input accepted_plc_types must not be empty")
        if any(
            not isinstance(point_type, str) or not point_type.strip()
            for point_type in self.accepted_plc_types
        ):
            raise ProjectionRegistryError("handler input accepted_plc_types must not contain blanks")
        if len(set(self.accepted_plc_types)) != len(self.accepted_plc_types):
            raise ProjectionRegistryError("handler input accepted_plc_types must be unique")


@dataclass(frozen=True)
class ProjectionHandlerGroupIdentity:
    """One PLC DB group a handler explicitly owns."""

    plc_key: str
    db_number: int
    group_name: str

    def __post_init__(self) -> None:
        if not isinstance(self.plc_key, str) or not isinstance(self.group_name, str):
            raise ProjectionRegistryError("handler group identity text fields must be strings")
        if not self.plc_key.strip() or not self.group_name.strip():
            raise ProjectionRegistryError("handler group identity text fields must not be blank")
        if type(self.db_number) is not int or self.db_number <= 0:
            raise ProjectionRegistryError("handler group identity db_number must be a positive integer")


@dataclass(frozen=True)
class ProjectionInvocationContext:
    """Fact provenance supplied by the future Projection runner."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    source_snapshot_id: int
    collected_at: object
    quality: str

    def __post_init__(self) -> None:
        if not self.plc_key.strip() or not self.group_name.strip():
            raise ValueError("Projection provenance requires plc_key and group_name")
        if type(self.device_id) is not int or self.device_id <= 0:
            raise ValueError("Projection provenance requires a positive device_id")
        if type(self.db_number) is not int or self.db_number <= 0:
            raise ValueError("Projection provenance requires a positive db_number")
        if type(self.source_snapshot_id) is not int or self.source_snapshot_id <= 0:
            raise ValueError("Projection provenance requires a positive source_snapshot_id")
        if not isinstance(self.quality, str):
            raise ValueError("Projection provenance requires a string quality")


@dataclass(frozen=True)
class ProjectionHandlerDescriptor:
    """Explicit owner-owned declaration for one allowed Projection handler."""

    handler_key: str
    owner_module: str
    description: str
    snapshot_source: SnapshotSource
    handler_version: str
    inputs: tuple[ProjectionHandlerInput, ...]
    allowed_group_identities: tuple[ProjectionHandlerGroupIdentity, ...]
    invoke: ProjectionHandlerCallable
    auxiliary_group_identities: tuple[ProjectionHandlerGroupIdentity, ...] = field(default_factory=tuple)
    policy_derived_auxiliary_latest_groups: bool = False

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str)
            for value in (
                self.handler_key,
                self.owner_module,
                self.description,
                self.snapshot_source,
                self.handler_version,
            )
        ):
            raise ProjectionRegistryError("handler descriptor text fields must be strings")
        if not isinstance(self.inputs, tuple):
            raise ProjectionRegistryError("handler descriptor inputs must be a tuple")
        if not isinstance(self.allowed_group_identities, tuple):
            raise ProjectionRegistryError("handler descriptor allowed_group_identities must be a tuple")
        if not isinstance(self.auxiliary_group_identities, tuple):
            raise ProjectionRegistryError("handler descriptor auxiliary_group_identities must be a tuple")
        if type(self.policy_derived_auxiliary_latest_groups) is not bool:
            raise ProjectionRegistryError(
                "handler descriptor policy_derived_auxiliary_latest_groups must be boolean"
            )
        if any(not isinstance(item, ProjectionHandlerInput) for item in self.inputs):
            raise ProjectionRegistryError(
                "handler descriptor inputs must be ProjectionHandlerInput instances"
            )
        if any(
            not isinstance(item, ProjectionHandlerGroupIdentity)
            for item in self.allowed_group_identities
        ):
            raise ProjectionRegistryError(
                "handler descriptor allowed_group_identities must be ProjectionHandlerGroupIdentity instances"
            )
        if any(
            not isinstance(item, ProjectionHandlerGroupIdentity)
            for item in self.auxiliary_group_identities
        ):
            raise ProjectionRegistryError(
                "handler descriptor auxiliary_group_identities must be ProjectionHandlerGroupIdentity instances"
            )
        if not self.handler_key.strip() or not self.owner_module.strip():
            raise ProjectionRegistryError("handler_key and owner_module must not be blank")
        if not self.handler_key.startswith(f"{self.owner_module}."):
            raise ProjectionRegistryError("handler_key must use its owner_module prefix")
        if not self.description.strip() or not self.handler_version.strip():
            raise ProjectionRegistryError("handler description and version must not be blank")
        if self.snapshot_source not in {"raw", "latest"}:
            raise ProjectionRegistryError("snapshot_source must be raw or latest")
        if not self.inputs:
            raise ProjectionRegistryError("handler descriptor must declare at least one input")
        if not self.allowed_group_identities:
            raise ProjectionRegistryError(
                "handler descriptor must declare at least one allowed group identity"
            )
        input_keys = tuple(item.input_key for item in self.inputs)
        if len(set(input_keys)) != len(input_keys):
            raise ProjectionRegistryError("handler descriptor input_key values must be unique")
        if len(set(self.allowed_group_identities)) != len(self.allowed_group_identities):
            raise ProjectionRegistryError("handler descriptor allowed_group_identities must be unique")
        if len(set(self.auxiliary_group_identities)) != len(self.auxiliary_group_identities):
            raise ProjectionRegistryError("handler descriptor auxiliary_group_identities must be unique")
        if not callable(self.invoke):
            raise ProjectionRegistryError("handler descriptor invoke target must be callable")

    def validate_inputs(self, inputs: Mapping[str, object]) -> None:
        declared_keys = {item.input_key for item in self.inputs}
        unknown_keys = set(inputs) - declared_keys
        if unknown_keys:
            raise ValueError(f"unknown Projection handler inputs: {sorted(unknown_keys)}")
        missing_keys = [item.input_key for item in self.inputs if item.required and item.input_key not in inputs]
        if missing_keys:
            raise ValueError(f"missing required Projection handler inputs: {missing_keys}")

    def allows_group(self, *, plc_key: str, db_number: int, group_name: str) -> bool:
        """Return whether the full PLC DB group is within the handler's fixed scope."""
        return any(
            identity.plc_key == plc_key
            and identity.db_number == db_number
            and identity.group_name == group_name
            for identity in self.allowed_group_identities
        )

    def resolved_auxiliary_group_identities(
        self,
        *,
        catalog: "SnapshotPolicyCatalog | None" = None,
    ) -> tuple[ProjectionHandlerGroupIdentity, ...]:
        """Return explicit plus policy-derived auxiliary latest groups."""
        identities = list(self.auxiliary_group_identities)
        if self.policy_derived_auxiliary_latest_groups:
            if catalog is None:
                raise ProjectionRegistryError(
                    "policy-derived auxiliary groups require a snapshot policy catalog"
                )
            primary_identities = set(self.allowed_group_identities)
            for primary_identity in self.allowed_group_identities:
                identities.extend(
                    identity
                    for identity in catalog.list_group_identities(
                        plc_key=primary_identity.plc_key,
                        snapshot_source="latest",
                    )
                    if identity not in primary_identities
                )

        unique: list[ProjectionHandlerGroupIdentity] = []
        seen: set[ProjectionHandlerGroupIdentity] = set()
        for identity in identities:
            if identity in seen:
                continue
            seen.add(identity)
            unique.append(identity)
        return tuple(unique)

    def allows_auxiliary_group(
        self,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
        catalog: "SnapshotPolicyCatalog | None" = None,
    ) -> bool:
        """Return whether the group may provide optional latest inputs."""
        return any(
            identity.plc_key == plc_key
            and identity.db_number == db_number
            and identity.group_name == group_name
            for identity in self.resolved_auxiliary_group_identities(catalog=catalog)
        )

    def input_definition(self, input_key: str) -> ProjectionHandlerInput | None:
        """Return the declared input contract for an input key."""
        return next((item for item in self.inputs if item.input_key == input_key), None)

    def binding_snapshot_source(
        self,
        *,
        input_key: str,
        plc_key: str,
        db_number: int,
        group_name: str,
        primary_group_identity: ProjectionHandlerGroupIdentity,
        catalog: "SnapshotPolicyCatalog | None" = None,
    ) -> SnapshotSource | None:
        """Return the fact source a binding may use, or None when disallowed."""
        input_definition = self.input_definition(input_key)
        if input_definition is None:
            return None
        if (
            plc_key == primary_group_identity.plc_key
            and db_number == primary_group_identity.db_number
            and group_name == primary_group_identity.group_name
        ):
            return self.snapshot_source
        if input_definition.required:
            return None
        if self.allows_auxiliary_group(
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
            catalog=catalog,
        ):
            return "latest"
        return None


class ProjectionRegistry:
    """An immutable lookup over descriptors discovered from approved modules."""

    def __init__(self, descriptors: Iterable[ProjectionHandlerDescriptor]):
        by_key: dict[str, ProjectionHandlerDescriptor] = {}
        for descriptor in descriptors:
            if not isinstance(descriptor, ProjectionHandlerDescriptor):
                raise ProjectionRegistryError("registry descriptors must be ProjectionHandlerDescriptor instances")
            if descriptor.handler_key in by_key:
                raise ProjectionRegistryError(f"duplicate handler_key: {descriptor.handler_key}")
            by_key[descriptor.handler_key] = descriptor
        self._handlers = tuple(by_key[key] for key in sorted(by_key))
        self._by_key = by_key

    @classmethod
    def from_descriptors(
        cls,
        descriptors: Iterable[ProjectionHandlerDescriptor],
    ) -> "ProjectionRegistry":
        return cls(descriptors)

    @property
    def handlers(self) -> tuple[ProjectionHandlerDescriptor, ...]:
        return self._handlers

    def get(self, handler_key: str) -> ProjectionHandlerDescriptor:
        descriptor = self.get_optional(handler_key)
        if descriptor is None:
            raise ProjectionRegistryError(f"unknown handler_key: {handler_key}")
        return descriptor

    def get_optional(self, handler_key: str) -> ProjectionHandlerDescriptor | None:
        return self._by_key.get(handler_key)


def build_projection_registry(
    module_names: Iterable[str] | None = None,
) -> ProjectionRegistry:
    """Build a registry by scanning only enabled module service packages."""
    selected_names = (
        tuple(module_names)
        if module_names is not None
        else tuple(manifest.name for manifest in get_enabled_module_manifests())
    )
    descriptors: list[ProjectionHandlerDescriptor] = []
    for module_name in sorted(selected_names):
        descriptors.extend(_discover_module_descriptors(module_name))
    return ProjectionRegistry.from_descriptors(descriptors)


def _discover_module_descriptors(module_name: str) -> tuple[ProjectionHandlerDescriptor, ...]:
    services_package_path = f"app.{module_name}.services"
    try:
        services_package = import_module(services_package_path)
    except ModuleNotFoundError as exc:
        if exc.name == services_package_path:
            return ()
        raise ProjectionRegistryError(
            f"failed to import Projection services package: {services_package_path}"
        ) from exc
    except Exception as exc:
        raise ProjectionRegistryError(
            f"failed to import Projection services package: {services_package_path}"
        ) from exc

    package_paths = getattr(services_package, "__path__", None)
    if package_paths is None:
        raise ProjectionRegistryError(f"Projection services path is not a package: {services_package_path}")

    descriptors: list[ProjectionHandlerDescriptor] = []
    module_infos = sorted(pkgutil.iter_modules(package_paths), key=lambda item: item.name)
    for module_info in module_infos:
        if not module_info.name.startswith("sync_"):
            continue
        service_module_path = f"{services_package_path}.{module_info.name}"
        try:
            service_module = import_module(service_module_path)
        except Exception as exc:
            raise ProjectionRegistryError(
                f"failed to import Projection handler module: {service_module_path}"
            ) from exc
        descriptor = getattr(service_module, "projection_handler", None)
        if descriptor is None:
            continue
        if not isinstance(descriptor, ProjectionHandlerDescriptor):
            raise ProjectionRegistryError(
                f"{service_module_path}.projection_handler must be a ProjectionHandlerDescriptor"
            )
        if descriptor.owner_module != module_name:
            raise ProjectionRegistryError(
                f"{service_module_path}.projection_handler owner_module must be {module_name!r}"
            )
        descriptors.append(descriptor)
    return tuple(descriptors)
