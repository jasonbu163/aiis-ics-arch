"""
File Path: /tools/lineage-audit/src-python/audit/common.py
Description: Shared I/O and normalization helpers for lineage audit.
Main Features:
    - Provides JSON Lines evidence output.
    - Provides CSV/JSON writers and stable row IDs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

from .constants import PROJECT_ROOT, TOOL_OWNED_OUTPUTS

def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(resolved)


def emit(event: str, **payload: Any) -> None:
    record = {"event": event, **payload}
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def clean_tool_outputs(outputs_dir: Path) -> None:
    for name in TOOL_OWNED_OUTPUTS:
        path = outputs_dir / name
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def add_row_ids(rows: list[dict[str, Any]], prefix: str, key_fields: list[str]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    rows_with_ids: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        stable_key = "|".join(str(row.get(field, "")) for field in key_fields)
        if not stable_key.strip("|"):
            stable_key = str(index)
        digest = hashlib.sha1(stable_key.encode("utf-8")).hexdigest()[:12]
        row_id = f"{prefix}:{digest}"
        duplicate_count = seen.get(row_id, 0)
        seen[row_id] = duplicate_count + 1
        if duplicate_count:
            row_id = f"{row_id}:{duplicate_count + 1}"
        rows_with_ids.append({"row_id": row_id, **row})
    return rows_with_ids


def normalize_path(path: str) -> str:
    cleaned = path.strip().strip("`'\"")
    cleaned = re.sub(r"\$\{[^}]+\}", "{param}", cleaned)
    cleaned = re.sub(r"\{[^}/]+\}", "{param}", cleaned)
    cleaned = re.sub(r"<[^>/]+>", "{param}", cleaned)
    cleaned = re.sub(r":\w+", "{param}", cleaned)
    cleaned = re.sub(r"//+", "/", cleaned)
    if cleaned and not cleaned.startswith("/"):
        cleaned = "/" + cleaned
    return cleaned.rstrip("/") or "/"


def route_regex(path: str) -> re.Pattern[str]:
    normalized = normalize_path(path)
    escaped = re.escape(normalized)
    escaped = escaped.replace(re.escape("{param}"), r"[^/]+")
    return re.compile(f"^{escaped}$")
