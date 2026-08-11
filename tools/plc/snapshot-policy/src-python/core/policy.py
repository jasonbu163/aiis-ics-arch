"""
文件路径: /tools/plc/snapshot-policy/src-python/core/policy.py
功能描述: 生成 control-agent 可读取的 plc_snapshot_policy.yaml v2
"""
from __future__ import annotations

from pathlib import Path
from collections import defaultdict

import yaml

from core.models import SnapshotPolicyRow


PLC_POLICY_FIELDS = {"groups", "point_count", "raw_point_count", "latest_point_count", "snapshot_policy_version"}
GROUP_POLICY_FIELDS = {"points", "point_count", "raw_point_count", "latest_point_count", "group_name"}
POINT_POLICY_FIELDS = {"plc_key", "raw_enabled", "raw_policy", "latest_enabled", "reason"}


def write_policy_yaml(
    rows: list[SnapshotPolicyRow],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_by_plc: dict[str, list[SnapshotPolicyRow]] = defaultdict(list)
    for row in rows:
        if not row.point.plc_key:
            raise ValueError(f"{row.point.name}: missing PLC key")
        rows_by_plc[row.point.plc_key].append(row)

    payload = {
        plc_key: build_plc_payload(plc_rows)
        for plc_key, plc_rows in sorted(rows_by_plc.items())
    }
    output_path.write_text(
        "# File Path: /control-agent/config/plc_snapshot_policy.yaml\n"
        "# Description: Generated PLC decoded-payload raw/latest point-scope policy for Control Agent.\n"
        "# Main Features:\n"
        "#   - Controls which decoded PLC points enter raw snapshot payloads\n"
        "#   - Controls which decoded PLC points enter latest snapshot payloads\n"
        "#   - Mirrors plc_points.yaml PLC/group/point structure with added policy fields\n"
        "#   - Leaves raw row retention days to CONTROL_AGENT_PLC_RAW_HOT_RETENTION_DAYS\n"
        "#   - Generated from tools/plc/snapshot-policy reviewed XLSX\n\n"
        + yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def build_plc_payload(plc_rows: list[SnapshotPolicyRow]) -> dict[str, object]:
    first_point = plc_rows[0].point
    payload = {
        key: value
        for key, value in first_point.plc_metadata.items()
        if key not in PLC_POLICY_FIELDS
    }
    payload["snapshot_policy_version"] = 2
    payload["point_count"] = len(plc_rows)
    payload["raw_point_count"] = sum(1 for row in plc_rows if row.raw_enabled)
    payload["latest_point_count"] = sum(1 for row in plc_rows if row.latest_enabled)

    rows_by_group: dict[tuple[int, str], list[SnapshotPolicyRow]] = defaultdict(list)
    for row in plc_rows:
        rows_by_group[(row.point.db_number, row.point.group_name)].append(row)
    payload["groups"] = [
        build_group_payload(group_rows)
        for _group_key, group_rows in sorted(rows_by_group.items())
    ]
    return payload


def build_group_payload(group_rows: list[SnapshotPolicyRow]) -> dict[str, object]:
    first_point = group_rows[0].point
    payload = {
        key: value
        for key, value in first_point.group_metadata.items()
        if key not in GROUP_POLICY_FIELDS
    }
    payload["name"] = first_point.group_name
    payload["db_number"] = first_point.db_number
    payload["point_count"] = len(group_rows)
    payload["raw_point_count"] = sum(1 for row in group_rows if row.raw_enabled)
    payload["latest_point_count"] = sum(1 for row in group_rows if row.latest_enabled)
    payload["points"] = [
        build_point_payload(row)
        for row in sorted(
            group_rows,
            key=lambda item: (
                item.point.offset,
                item.point.bit if item.point.bit is not None else 0,
                item.point.name,
            ),
        )
    ]
    return payload


def build_point_payload(row: SnapshotPolicyRow) -> dict[str, object]:
    point = row.point
    payload = {
        key: value
        for key, value in point.point_metadata.items()
        if key not in POINT_POLICY_FIELDS
    }
    payload["name"] = point.name
    payload["source_name"] = point.source_name
    payload["type"] = point.data_type
    payload["offset"] = point.offset
    if point.bit is not None:
        payload["bit"] = point.bit
    else:
        payload.pop("bit", None)
    if point.desc or "desc" in point.point_metadata:
        payload["desc"] = point.desc
    payload["raw_enabled"] = row.raw_enabled
    payload["raw_policy"] = row.raw_policy
    payload["latest_enabled"] = row.latest_enabled
    payload["reason"] = row.reason
    return payload
