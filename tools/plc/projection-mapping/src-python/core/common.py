"""
File Path: /tools/plc/projection-mapping/src-python/core/common.py
Description: Shared IO, errors and JSON Lines evidence helpers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ToolError(RuntimeError):
    """Raised for expected user-facing tool errors."""


def emit(event: str, **payload: Any) -> None:
    record = {"event": event, **payload}
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except FileNotFoundError as exc:
        raise ToolError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(f"invalid JSON file: {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, ensure_ascii=False, indent=2)
        file_obj.write("\n")


def load_yaml(path: Path) -> Any:
    try:
        import yaml
    except ImportError as exc:
        raise ToolError("PyYAML is required to read YAML files") from exc

    try:
        with path.open("r", encoding="utf-8") as file_obj:
            return yaml.safe_load(file_obj)
    except FileNotFoundError as exc:
        raise ToolError(f"missing YAML file: {path}") from exc


def write_yaml(path: Path, payload: Any) -> None:
    try:
        import yaml
    except ImportError as exc:
        raise ToolError("PyYAML is required to write YAML files") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_obj:
        yaml.safe_dump(payload, file_obj, allow_unicode=True, sort_keys=False)
