"""
文件路径: /tools/plc/point-mapping/src-python/cli/commands.py
功能描述: TIA DB 点表转 plc_points.yaml 工具的命令行入口
"""
from __future__ import annotations

import argparse
from difflib import get_close_matches
import json
from pathlib import Path
import sys
from typing import Any

from converter.converter import DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_PATH, convert_excel_to_yaml
from validation.struct_validation import validate_workbook_source_context
from workbook.init_workbook import (
    DEFAULT_DB_CONFIG_INPUT_PATH,
    DEFAULT_DB_CONFIG_OUTPUT_PATH,
    DEFAULT_WORKBOOK_OUTPUT_PATH,
    init_db_config_workbook,
    init_point_workbook,
)


COMMANDS = ("init-db-config", "init-workbook", "generate-yaml")


def emit(event: str, **payload: Any) -> None:
    print(json.dumps({"event": event, **payload}, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PLC point mapping tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Command-specific options:\n"
            "  main.py init-db-config --help\n"
            "  main.py init-workbook --help\n"
            "  main.py generate-yaml --help"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    init_db_config = subparsers.add_parser(
        "init-db-config",
        help="Create a DB configuration workbook.",
    )
    _add_init_db_config_arguments(init_db_config)
    init_workbook = subparsers.add_parser(
        "init-workbook",
        help="Create one TIA-copy point sheet per DB config row.",
    )
    _add_init_workbook_arguments(init_workbook)
    generate_yaml = subparsers.add_parser(
        "generate-yaml",
        help="Generate plc_points.yaml from the reviewed workbook.",
    )
    _add_generate_yaml_arguments(generate_yaml)
    return parser


def _add_init_db_config_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db-source",
        dest="db_source_path",
        help="TIA .db source export path used to prefill DATA_BLOCK names.",
    )
    parser.add_argument(
        "--workbook-output",
        dest="workbook_output_path",
        help=f"Output DB config workbook path. Defaults to {DEFAULT_DB_CONFIG_OUTPUT_PATH}.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output workbook if it already exists.",
    )


def _add_init_workbook_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db-config",
        dest="db_config_path",
        help=f"Filled DB config workbook path. Defaults to {DEFAULT_DB_CONFIG_INPUT_PATH}.",
    )
    parser.add_argument(
        "--db-source",
        dest="db_source_path",
        required=True,
        help="TIA .db source export path used to verify configured DATA_BLOCK names.",
    )
    parser.add_argument(
        "--workbook-output",
        dest="workbook_output_path",
        help=f"Output point workbook path. Defaults to {DEFAULT_WORKBOOK_OUTPUT_PATH}.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output workbook if it already exists.",
    )


def _add_generate_yaml_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db-workbook",
        dest="workbook_path",
        help=(
            f"Reviewed TIA DB point workbook path. Defaults to {DEFAULT_INPUT_PATH}. "
            f"If you just used init-workbook, pass --db-workbook {DEFAULT_WORKBOOK_OUTPUT_PATH} "
            "or copy the reviewed workbook into the default input path."
        ),
    )
    parser.add_argument(
        "--db-source",
        dest="db_source_path",
        help="TIA .db source export path used for Struct validation.",
    )
    parser.add_argument(
        "--udt-source",
        dest="udt_source_path",
        help="TIA .udt source export path used for Struct validation.",
    )
    parser.add_argument(
        "--plc-points-output",
        dest="plc_points_output_path",
        help=f"Output plc_points.yaml path. Defaults to {DEFAULT_OUTPUT_PATH}.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output YAML if it already exists.",
    )
    parser.add_argument("--plc-ip", default="127.0.0.1", help="Example PLC IP written to YAML.")
    parser.add_argument("--rack", type=int, default=0, help="S7 rack number.")
    parser.add_argument("--slot", type=int, default=1, help="S7 slot number.")


def _validate_optional_source(label: str, path: Path | None) -> None:
    if path is not None and not path.is_file():
        raise FileNotFoundError(f"{label} source file not found: {path}")


def _ensure_can_write_yaml(output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"output YAML already exists: {output_path}; pass --overwrite to replace it")


def _run_conversion(
    *,
    command: str,
    workbook_path: Path,
    output_path: Path,
    plc_ip: str,
    rack: int,
    slot: int,
    db_source_path: Path | None = None,
    udt_source_path: Path | None = None,
    overwrite: bool = False,
) -> int:
    try:
        _validate_optional_source("DB", db_source_path)
        _validate_optional_source("UDT", udt_source_path)
        emit(
            "start",
            command=command,
            input=str(workbook_path),
            workbook=str(workbook_path),
            output=str(output_path),
            db_source=str(db_source_path) if db_source_path else None,
            udt_source=str(udt_source_path) if udt_source_path else None,
        )
        _ensure_can_write_yaml(output_path, overwrite)
        if db_source_path or udt_source_path:
            source_context = validate_workbook_source_context(workbook_path, db_source_path, udt_source_path)
            emit(
                "source_context",
                command=command,
                db_source=str(db_source_path) if db_source_path else None,
                udt_source=str(udt_source_path) if udt_source_path else None,
                **source_context.to_event_payload(),
            )
            if not source_context.ok:
                raise ValueError(
                    f"DB/UDT source validation failed with {len(source_context.errors)} error(s). "
                    f"Workbook checked: {workbook_path}. If this is not the reviewed TIA workbook, "
                    f"pass --db-workbook {DEFAULT_WORKBOOK_OUTPUT_PATH} after init-workbook, or copy the "
                    f"reviewed workbook to {DEFAULT_INPUT_PATH}."
                )
        result = convert_excel_to_yaml(
            workbook_path,
            output_path,
            plc_ip,
            rack,
            slot,
            db_source_path=db_source_path,
            udt_source_path=udt_source_path,
        )
        groups = result["PLC_1"]["groups"]
        point_count = sum(len(group["points"]) for group in groups)
        emit(
            "complete",
            command=command,
            output=str(output_path),
            group_count=len(groups),
            point_count=point_count,
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary must report concise failure evidence.
        emit("failed", command=command, error=str(exc))
        return 1


def _run_generate_yaml(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate plc_points.yaml from a reviewed TIA DB workbook.",
        prog="main.py generate-yaml",
    )
    _add_generate_yaml_arguments(parser)
    args = parser.parse_args(argv)
    return _run_conversion(
        command="generate-yaml",
        workbook_path=Path(args.workbook_path or DEFAULT_INPUT_PATH),
        output_path=Path(args.plc_points_output_path or DEFAULT_OUTPUT_PATH),
        plc_ip=args.plc_ip,
        rack=args.rack,
        slot=args.slot,
        db_source_path=Path(args.db_source_path) if args.db_source_path else None,
        udt_source_path=Path(args.udt_source_path) if args.udt_source_path else None,
        overwrite=args.overwrite,
    )


def _run_init_db_config(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Create a DB configuration workbook.",
        prog="main.py init-db-config",
    )
    _add_init_db_config_arguments(parser)
    args = parser.parse_args(argv)
    output_path = Path(args.workbook_output_path or DEFAULT_DB_CONFIG_OUTPUT_PATH)
    db_source_path = Path(args.db_source_path) if args.db_source_path else None
    try:
        _validate_optional_source("DB", db_source_path)
        emit(
            "start",
            command="init-db-config",
            db_source=str(db_source_path) if db_source_path else None,
            output=str(output_path),
        )
        result = init_db_config_workbook(
            output_path,
            db_source_path,
            overwrite=args.overwrite,
        )
        emit("complete", command="init-db-config", **result)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary must report concise failure evidence.
        emit("failed", command="init-db-config", error=str(exc))
        return 1


def _run_init_workbook(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Create one TIA-copy point sheet per DB config row.",
        prog="main.py init-workbook",
    )
    _add_init_workbook_arguments(parser)
    args = parser.parse_args(argv)
    db_config_path = Path(args.db_config_path or DEFAULT_DB_CONFIG_INPUT_PATH)
    db_source_path = Path(args.db_source_path)
    output_path = Path(args.workbook_output_path or DEFAULT_WORKBOOK_OUTPUT_PATH)
    try:
        _validate_optional_source("DB", db_source_path)
        emit(
            "start",
            command="init-workbook",
            db_config=str(db_config_path),
            db_source=str(db_source_path),
            output=str(output_path),
        )
        result = init_point_workbook(
            db_config_path,
            db_source_path,
            output_path,
            overwrite=args.overwrite,
        )
        emit("complete", command="init-workbook", **result)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary must report concise failure evidence.
        emit("failed", command="init-workbook", error=str(exc))
        return 1


def _suggest_command(value: str) -> str | None:
    if value.startswith("-") or "/" in value or "\\" in value:
        return None
    matches = get_close_matches(value, COMMANDS, n=1, cutoff=0.72)
    return matches[0] if matches else None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    effective_argv = sys.argv[1:] if argv is None else argv
    if not effective_argv or effective_argv[0] in {"-h", "--help"}:
        parser.print_help()
        return 0

    command = effective_argv[0]
    if command == "init-db-config":
        return _run_init_db_config(effective_argv[1:])
    if command == "init-workbook":
        return _run_init_workbook(effective_argv[1:])
    if command == "generate-yaml":
        return _run_generate_yaml(effective_argv[1:])

    suggested_command = _suggest_command(command)
    if suggested_command:
        parser.error(f"unknown command {command!r}. Did you mean {suggested_command!r}?")

    parser.error(f"unknown command {command!r}. Valid commands: {', '.join(COMMANDS)}")
    return 2
