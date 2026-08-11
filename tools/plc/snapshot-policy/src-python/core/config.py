"""
文件路径: /tools/plc/snapshot-policy/src-python/core/config.py
功能描述: PLC 快照策略工具的默认路径配置
"""
from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[5]
TOOL_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "tools" / "config" / "plc_points.yaml"
DEFAULT_WORKBOOK_INPUT_PATH = TOOL_ROOT / "inputs" / "plc_snapshot_policy.xlsx"
DEFAULT_WORKBOOK_OUTPUT_PATH = TOOL_ROOT / "outputs" / "plc_snapshot_policy.xlsx"
DEFAULT_POLICY_OUTPUT_PATH = TOOL_ROOT / "outputs" / "plc_snapshot_policy.yaml"
