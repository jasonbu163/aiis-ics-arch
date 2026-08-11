"""
File Path: /tools/plc/projection-mapping/src-python/core/paths.py
Description: Default paths for the projection-mapping tool.
"""
from __future__ import annotations

from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGETS_PATH = TOOL_ROOT / "inputs" / "projection_targets.json"
DEFAULT_SCHEMA_PATH = TOOL_ROOT / "inputs" / "table_schema.json"
DEFAULT_SNAPSHOT_POLICY_PATH = TOOL_ROOT / "inputs" / "plc_snapshot_policy.yaml"
DEFAULT_SCHEMA_OUTPUT_PATH = TOOL_ROOT / "outputs" / "table_schema.json"
DEFAULT_TARGET_CANDIDATE_OUTPUT_PATH = TOOL_ROOT / "outputs" / "projection_targets.candidate.json"
DEFAULT_XLSX_OUTPUT_PATH = TOOL_ROOT / "outputs" / "plc_projection_mapping.xlsx"
DEFAULT_MAPPING_XLSX_PATH = TOOL_ROOT / "inputs" / "plc_projection_mapping.xlsx"
DEFAULT_RULES_OUTPUT_PATH = TOOL_ROOT / "outputs" / "projection_rules.yaml"
