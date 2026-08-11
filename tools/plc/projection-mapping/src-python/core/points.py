"""
File Path: /tools/plc/projection-mapping/src-python/core/points.py
Description: PLC snapshot-policy candidate loading and validation.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from core.common import ToolError, load_yaml, read_json
from core.targets import normalize_schema, normalize_targets


def bool_value(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ToolError(f"plc_snapshot_policy.yaml point {label} must be true/false")


def available_sources(point: dict[str, Any]) -> str:
    sources = []
    if point["raw_enabled"]:
        sources.append("raw")
    if point["latest_enabled"]:
        sources.append("latest")
    return "+".join(sources)


def flatten_snapshot_policy(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ToolError("plc_snapshot_policy.yaml must contain a policy object")
    if "version" in payload or "groups" in payload:
        raise ToolError(
            "plc_snapshot_policy.yaml uses the old top-level version/groups shape; "
            "regenerate snapshot-policy so it mirrors plc_points.yaml"
        )

    policy_points: list[dict[str, Any]] = []
    candidate_points: list[dict[str, Any]] = []
    for plc_key, plc_config in payload.items():
        if not isinstance(plc_config, dict):
            raise ToolError(f"plc_snapshot_policy.yaml top-level key {plc_key} must be a PLC policy object")
        if plc_config.get("snapshot_policy_version") != 2:
            raise ToolError(f"plc_snapshot_policy.yaml PLC {plc_key} must use snapshot_policy_version: 2")
        for group in plc_config.get("groups") or []:
            if not isinstance(group, dict):
                continue
            group_name = str(group.get("name") or "").strip()
            if not group_name:
                raise ToolError(f"plc_snapshot_policy.yaml PLC {plc_key} has a group without name")
            db_number = group.get("db_number")
            for point in group.get("points") or []:
                if not isinstance(point, dict):
                    continue
                point_name = str(point.get("name") or "").strip()
                if not point_name:
                    continue
                location = f"{plc_key}.{group_name}.{point_name}"
                normalized = {
                    "plc_key": str(plc_key),
                    "db_number": db_number,
                    "group_name": group_name,
                    "point_name": point_name,
                    "source_name": point.get("source_name"),
                    "plc_data_type": point.get("type"),
                    "offset": point.get("offset"),
                    "bit": point.get("bit"),
                    "desc": point.get("desc"),
                    "raw_enabled": bool_value(point.get("raw_enabled"), f"{location}.raw_enabled"),
                    "raw_policy": point.get("raw_policy"),
                    "latest_enabled": bool_value(point.get("latest_enabled"), f"{location}.latest_enabled"),
                }
                normalized["available_sources"] = available_sources(normalized)
                policy_points.append(normalized)
                if normalized["raw_enabled"] or normalized["latest_enabled"]:
                    candidate_points.append(normalized)

    if not policy_points:
        raise ToolError("plc_snapshot_policy.yaml does not contain usable points")
    if not candidate_points:
        raise ToolError("plc_snapshot_policy.yaml does not enable any raw/latest candidate points")
    duplicate_names = sorted(
        name for name, count in Counter(point["point_name"] for point in candidate_points).items() if count > 1
    )
    if duplicate_names:
        raise ToolError(f"duplicate PLC point names in plc_snapshot_policy.yaml candidates: {duplicate_names[:20]}")

    return {
        "points": candidate_points,
        "policy_point_count": len(policy_points),
        "candidate_point_count": len(candidate_points),
        "raw_enabled_count": sum(1 for point in policy_points if point["raw_enabled"]),
        "latest_enabled_count": sum(1 for point in policy_points if point["latest_enabled"]),
    }


def validate_inputs(targets_path: Path, schema_path: Path, snapshot_policy_path: Path) -> dict[str, Any]:
    targets = normalize_targets(read_json(targets_path))
    schema = normalize_schema(read_json(schema_path))
    policy_state = flatten_snapshot_policy(load_yaml(snapshot_policy_path))

    missing_tables = [table for table in targets if table not in schema]
    if missing_tables:
        raise ToolError(f"target tables missing from table_schema.json: {missing_tables}")

    return {
        "targets": targets,
        "schema": schema,
        **policy_state,
    }
