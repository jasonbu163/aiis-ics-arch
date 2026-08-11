"""
文件路径: /tools/plc/s7-virtual-plc/src-python/core/config.py
功能描述: S7 虚拟 PLC 工具的路径和 .env 读取
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[5]
TOOL_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "tools" / "config" / "plc_points.yaml"
DEFAULT_PROFILE_INPUT_PATH = TOOL_ROOT / "inputs" / "simulation_profile.xlsx"
DEFAULT_PROFILE_OUTPUT_PATH = TOOL_ROOT / "outputs" / "simulation_profile.xlsx"
TOOL_ENV_PATH = TOOL_ROOT / ".env"


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_setting(
    name: str,
    cli_value: str | int | None,
    *,
    environment: Mapping[str, str] | None = None,
    tool_values: Mapping[str, str] | None = None,
) -> str | int | None:
    """Resolve a simulator setting with CLI, OS environment, then tool .env priority."""
    if _is_configured(cli_value):
        return cli_value

    operating_system = os.environ if environment is None else environment
    if _is_configured(operating_system.get(name)):
        return operating_system[name]

    tool_env = read_env_file(TOOL_ENV_PATH) if tool_values is None else tool_values
    if _is_configured(tool_env.get(name)):
        return tool_env[name]
    return None


def env_value(name: str, default: str) -> str:
    value = resolve_setting(name, None)
    return default if value is None else str(value)


def _is_configured(value: str | int | None) -> bool:
    return value is not None and bool(str(value).strip())
