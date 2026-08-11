"""
File Path: /backend/projection/policy_catalog.py
Description: Read-only PLC snapshot-policy catalog for Projection mappings.
Main Features:
    - Parses the deployed v2 policy contract without exposing YAML edits
    - Preserves full PLC, DB-group, and point identity
    - Filters candidates by a handler's fixed raw or latest source
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from projection.registry import ProjectionHandlerGroupIdentity, SnapshotSource


DEFAULT_SNAPSHOT_POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "plc_snapshot_policy.yaml"


class SnapshotPolicyCatalogError(ValueError):
    """The deployed snapshot policy cannot safely serve as a candidate catalog."""


@dataclass(frozen=True)
class SnapshotPolicyPoint:
    """One point identity and its read-only raw/latest eligibility."""

    plc_key: str
    db_number: int
    group_name: str
    point_name: str
    plc_data_type: str
    source_name: str | None
    description: str | None
    raw_enabled: bool
    latest_enabled: bool

    def allows_source(self, snapshot_source: SnapshotSource) -> bool:
        if snapshot_source == "raw":
            return self.raw_enabled
        if snapshot_source == "latest":
            return self.latest_enabled
        raise SnapshotPolicyCatalogError(f"unsupported snapshot source: {snapshot_source}")


class SnapshotPolicyCatalog:
    """Stable in-memory lookup over the deployed v2 snapshot policy."""

    def __init__(self, points: tuple[SnapshotPolicyPoint, ...]):
        by_identity: dict[tuple[str, int, str, str], SnapshotPolicyPoint] = {}
        for point in points:
            identity = (point.plc_key, point.db_number, point.group_name, point.point_name)
            if identity in by_identity:
                raise SnapshotPolicyCatalogError(f"duplicate policy point identity: {identity}")
            by_identity[identity] = point
        if not by_identity:
            raise SnapshotPolicyCatalogError("snapshot policy has no usable points")
        self._points = tuple(
            by_identity[identity]
            for identity in sorted(by_identity)
        )
        self._by_identity = by_identity

    @property
    def points(self) -> tuple[SnapshotPolicyPoint, ...]:
        return self._points

    def get_point(
        self,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
        point_name: str,
    ) -> SnapshotPolicyPoint:
        identity = (plc_key, db_number, group_name, point_name)
        point = self._by_identity.get(identity)
        if point is None:
            raise SnapshotPolicyCatalogError(f"policy point is not available: {identity}")
        return point

    def list_group_points(
        self,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
        snapshot_source: SnapshotSource,
    ) -> tuple[SnapshotPolicyPoint, ...]:
        return tuple(
            point
            for point in self._points
            if point.plc_key == plc_key
            and point.db_number == db_number
            and point.group_name == group_name
            and point.allows_source(snapshot_source)
        )

    def list_group_identities(
        self,
        *,
        plc_key: str,
        snapshot_source: SnapshotSource,
    ) -> tuple[ProjectionHandlerGroupIdentity, ...]:
        """Return DB groups that have at least one point enabled for the source."""
        identities: list[ProjectionHandlerGroupIdentity] = []
        seen: set[tuple[str, int, str]] = set()
        for point in self._points:
            identity = (point.plc_key, point.db_number, point.group_name)
            if point.plc_key != plc_key or identity in seen or not point.allows_source(snapshot_source):
                continue
            seen.add(identity)
            identities.append(
                ProjectionHandlerGroupIdentity(
                    plc_key=point.plc_key,
                    db_number=point.db_number,
                    group_name=point.group_name,
                )
            )
        return tuple(identities)


def load_snapshot_policy_catalog(
    path: Path = DEFAULT_SNAPSHOT_POLICY_PATH,
) -> SnapshotPolicyCatalog:
    """Load the deployed v2 policy as a read-only candidate catalog."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SnapshotPolicyCatalogError(f"snapshot policy file is missing: {path}") from exc
    except yaml.YAMLError as exc:
        raise SnapshotPolicyCatalogError(f"snapshot policy YAML is invalid: {path}") from exc
    return build_snapshot_policy_catalog(payload)


def build_snapshot_policy_catalog(payload: Any) -> SnapshotPolicyCatalog:
    """Validate an in-memory v2 policy payload for tests and runtime loading."""
    if not isinstance(payload, dict) or not payload:
        raise SnapshotPolicyCatalogError("snapshot policy must contain PLC policy objects")
    if "version" in payload or "groups" in payload:
        raise SnapshotPolicyCatalogError("snapshot policy must use the v2 PLC-keyed shape")

    points: list[SnapshotPolicyPoint] = []
    for plc_key, plc_policy in sorted(payload.items()):
        if not isinstance(plc_key, str) or not plc_key.strip() or not isinstance(plc_policy, dict):
            raise SnapshotPolicyCatalogError("each snapshot policy entry must be a named PLC object")
        if plc_policy.get("snapshot_policy_version") != 2:
            raise SnapshotPolicyCatalogError(
                f"snapshot policy PLC {plc_key} must use snapshot_policy_version: 2"
            )
        groups = plc_policy.get("groups")
        if not isinstance(groups, list):
            raise SnapshotPolicyCatalogError(f"snapshot policy PLC {plc_key} groups must be a list")
        group_identities: set[tuple[str, int, str]] = set()
        for group in groups:
            group_identity, group_points = _parse_group(plc_key, group)
            if group_identity in group_identities:
                raise SnapshotPolicyCatalogError(
                    f"duplicate policy group identity: {group_identity}"
                )
            group_identities.add(group_identity)
            points.extend(group_points)
    return SnapshotPolicyCatalog(tuple(points))


def _parse_group(
    plc_key: str,
    group: Any,
) -> tuple[tuple[str, int, str], list[SnapshotPolicyPoint]]:
    if not isinstance(group, dict):
        raise SnapshotPolicyCatalogError(f"snapshot policy PLC {plc_key} contains a non-object group")
    group_name = group.get("name")
    db_number = group.get("db_number")
    points = group.get("points")
    if not isinstance(group_name, str) or not group_name.strip():
        raise SnapshotPolicyCatalogError(f"snapshot policy PLC {plc_key} group requires name")
    if type(db_number) is not int or db_number <= 0:
        raise SnapshotPolicyCatalogError(f"snapshot policy PLC {plc_key} group requires positive db_number")
    if not isinstance(points, list):
        raise SnapshotPolicyCatalogError(f"snapshot policy PLC {plc_key} group {group_name} points must be a list")

    return (
        (plc_key, db_number, group_name),
        [
            _parse_point(plc_key, db_number, group_name, point)
            for point in points
        ],
    )


def _parse_point(
    plc_key: str,
    db_number: int,
    group_name: str,
    point: Any,
) -> SnapshotPolicyPoint:
    if not isinstance(point, dict):
        raise SnapshotPolicyCatalogError(
            f"snapshot policy group {plc_key}/{db_number}/{group_name} contains a non-object point"
        )
    point_name = point.get("name")
    plc_data_type = point.get("type")
    raw_enabled = point.get("raw_enabled")
    latest_enabled = point.get("latest_enabled")
    if not isinstance(point_name, str) or not point_name.strip():
        raise SnapshotPolicyCatalogError("snapshot policy point requires name")
    if not isinstance(plc_data_type, str) or not plc_data_type.strip():
        raise SnapshotPolicyCatalogError(f"snapshot policy point {point_name} requires type")
    if type(raw_enabled) is not bool or type(latest_enabled) is not bool:
        raise SnapshotPolicyCatalogError(
            f"snapshot policy point {point_name} raw_enabled/latest_enabled must be boolean"
        )
    source_name = point.get("source_name")
    description = point.get("desc")
    if source_name is not None and not isinstance(source_name, str):
        raise SnapshotPolicyCatalogError(f"snapshot policy point {point_name} source_name must be a string")
    if description is not None and not isinstance(description, str):
        raise SnapshotPolicyCatalogError(f"snapshot policy point {point_name} desc must be a string")
    return SnapshotPolicyPoint(
        plc_key=plc_key,
        db_number=db_number,
        group_name=group_name,
        point_name=point_name,
        plc_data_type=plc_data_type,
        source_name=source_name,
        description=description,
        raw_enabled=raw_enabled,
        latest_enabled=latest_enabled,
    )
