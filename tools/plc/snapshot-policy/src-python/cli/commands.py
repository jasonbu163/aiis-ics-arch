"""
文件路径: /tools/plc/snapshot-policy/src-python/cli/commands.py
功能描述: PLC 快照 raw/latest 范围策略工具的命令行执行面
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
import time
from pathlib import Path
from typing import Any

from core.config import DEFAULT_CONFIG_PATH, DEFAULT_POLICY_OUTPUT_PATH, DEFAULT_WORKBOOK_INPUT_PATH, DEFAULT_WORKBOOK_OUTPUT_PATH
from core.points import load_points
from core.policy import write_policy_yaml
from core.workbook import read_policy_workbook, write_policy_workbook


COMMANDS = ("init-workbook", "generate-yaml")


def emit(event: str, **fields: Any) -> None:
    print(json.dumps({"event": event, **fields}, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PLC snapshot policy tool.")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    init_parser = subparsers.add_parser(
        "init-workbook",
        help="Generate a raw/latest snapshot policy review workbook from plc_points.yaml.",
    )
    add_plc_points_argument(init_parser)
    init_parser.add_argument(
        "--workbook-output",
        default=str(DEFAULT_WORKBOOK_OUTPUT_PATH),
        help=f"Output XLSX path. Defaults to {DEFAULT_WORKBOOK_OUTPUT_PATH}.",
    )
    init_parser.add_argument("--overwrite", action="store_true", help="Replace an existing workbook output.")

    generate_parser = subparsers.add_parser(
        "generate-yaml",
        help="Generate plc_snapshot_policy.yaml from a reviewed workbook.",
    )
    add_plc_points_argument(generate_parser)
    generate_parser.add_argument(
        "--workbook",
        default=str(DEFAULT_WORKBOOK_INPUT_PATH),
        help=f"Reviewed XLSX input path. Defaults to {DEFAULT_WORKBOOK_INPUT_PATH}.",
    )
    generate_parser.add_argument(
        "--policy-output",
        default=str(DEFAULT_POLICY_OUTPUT_PATH),
        help=f"Generated plc_snapshot_policy.yaml output path. Defaults to {DEFAULT_POLICY_OUTPUT_PATH}.",
    )
    generate_parser.add_argument("--overwrite", action="store_true", help="Replace an existing YAML output.")
    return parser


def add_plc_points_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--plc-points",
        default=str(DEFAULT_CONFIG_PATH),
        help=f"PLC point contract path. Defaults to {DEFAULT_CONFIG_PATH}.",
    )


def main(argv: list[str] | None = None) -> int:
    started_at = time.time()
    parser = build_parser()
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if not raw_args:
        parser.print_help()
        return 0
    if raw_args[0] not in COMMANDS and raw_args[0] not in {"-h", "--help"}:
        suggestion = difflib.get_close_matches(raw_args[0], COMMANDS, n=1)
        hint = f" Did you mean '{suggestion[0]}'?" if suggestion else ""
        parser.exit(2, f"{parser.prog}: error: unknown command '{raw_args[0]}'.{hint}\n")

    args = parser.parse_args(raw_args)
    config_path = Path(args.plc_points)

    try:
        emit("snapshot_policy_start", command=args.command, plc_points=str(config_path))
        points = load_points(config_path)

        if args.command == "init-workbook":
            workbook_output = Path(args.workbook_output)
            ensure_can_write(workbook_output, overwrite=args.overwrite)
            write_policy_workbook(points, workbook_output)
            raw_enabled_default_count = sum(
                1 for point in points if any("\u4e00" <= char <= "\u9fff" for char in f"{point.source_name}{point.desc}")
            )
            emit(
                "snapshot_policy_init_complete",
                command=args.command,
                status="ok",
                output=str(workbook_output),
                point_count=len(points),
                default_raw_enabled_count=raw_enabled_default_count,
                default_latest_enabled_count=len(points),
                duration_ms=round((time.time() - started_at) * 1000),
            )
            return 0

        workbook_path = Path(args.workbook)
        rows = read_policy_workbook(points, workbook_path)
        output_path = Path(args.policy_output)
        ensure_can_write(output_path, overwrite=args.overwrite)
        write_policy_yaml(rows, output_path)
        emit(
            "snapshot_policy_generate_complete",
            command=args.command,
            status="ok",
            workbook=str(workbook_path),
            output=str(output_path),
            point_count=len(points),
            policy_row_count=len(rows),
            raw_enabled_count=sum(1 for row in rows if row.raw_enabled),
            latest_enabled_count=sum(1 for row in rows if row.latest_enabled),
            duration_ms=round((time.time() - started_at) * 1000),
        )
        return 0
    except Exception as exc:
        emit(
            "snapshot_policy_failed",
            command=getattr(args, "command", None),
            status="failed",
            error=str(exc),
            duration_ms=round((time.time() - started_at) * 1000),
        )
        print(f"snapshot_policy error {exc}", file=sys.stderr)
        return 1


def ensure_can_write(path: Path, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists; pass --overwrite to replace it")
