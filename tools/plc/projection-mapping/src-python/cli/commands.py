"""
File Path: /tools/plc/projection-mapping/src-python/cli/commands.py
Description: CLI commands for projection-mapping.
"""
from __future__ import annotations

import argparse
from difflib import get_close_matches
from pathlib import Path
import sys

from core.common import ToolError, emit
from core.database import export_schema, list_tables
from core.paths import (
    DEFAULT_MAPPING_XLSX_PATH,
    DEFAULT_RULES_OUTPUT_PATH,
    DEFAULT_SCHEMA_OUTPUT_PATH,
    DEFAULT_SCHEMA_PATH,
    DEFAULT_SNAPSHOT_POLICY_PATH,
    DEFAULT_TARGET_CANDIDATE_OUTPUT_PATH,
    DEFAULT_TARGETS_PATH,
    DEFAULT_XLSX_OUTPUT_PATH,
)
from core.points import validate_inputs
from core.workbook import generate_rules, generate_xlsx, validate_mapping_workbook


COMMANDS = (
    "validate-inputs",
    "list-tables",
    "export-schema",
    "generate-xlsx",
    "validate-xlsx",
    "generate-rules",
)


def ensure_can_write(output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        raise ToolError(f"output already exists: {output_path}; pass --overwrite to replace it")


def command_validate_inputs(args: argparse.Namespace) -> int:
    state = validate_inputs(Path(args.targets), Path(args.schema), Path(args.snapshot_policy))
    emit(
        "complete",
        command="validate-inputs",
        target_count=len(state["targets"]),
        table_count=len(state["schema"]),
        point_count=len(state["points"]),
        policy_point_count=state["policy_point_count"],
        candidate_point_count=state["candidate_point_count"],
        raw_enabled_count=state["raw_enabled_count"],
        latest_enabled_count=state["latest_enabled_count"],
    )
    return 0


def command_export_schema(args: argparse.Namespace) -> int:
    ensure_can_write(Path(args.output), args.overwrite)
    emit("start", command="export-schema", targets=str(args.targets), output=str(args.output))
    result = export_schema(args.database_url, Path(args.targets), Path(args.output))
    emit(
        "complete",
        command="export-schema",
        output=str(args.output),
        table_count=len(result["tables"]),
        column_count=sum(len(table["columns"]) for table in result["tables"]),
    )
    return 0


def command_list_tables(args: argparse.Namespace) -> int:
    ensure_can_write(Path(args.output), args.overwrite)
    emit("start", command="list-tables", output=str(args.output))
    result = list_tables(args.database_url, Path(args.output))
    emit(
        "complete",
        command="list-tables",
        output=str(args.output),
        table_count=len(result["tables"]),
    )
    return 0


def command_generate_xlsx(args: argparse.Namespace) -> int:
    ensure_can_write(Path(args.output), args.overwrite)
    emit("start", command="generate-xlsx", output=str(args.output))
    result = generate_xlsx(Path(args.targets), Path(args.schema), Path(args.snapshot_policy), Path(args.output))
    emit("complete", command="generate-xlsx", **result)
    return 0


def command_validate_xlsx(args: argparse.Namespace) -> int:
    emit("start", command="validate-xlsx", mapping=str(args.mapping))
    result = validate_mapping_workbook(
        Path(args.mapping),
        Path(args.targets),
        Path(args.schema),
        Path(args.snapshot_policy),
    )
    emit("complete", command="validate-xlsx", **result)
    return 0


def command_generate_rules(args: argparse.Namespace) -> int:
    ensure_can_write(Path(args.output), args.overwrite)
    emit("start", command="generate-rules", mapping=str(args.mapping), output=str(args.output))
    result = generate_rules(
        Path(args.mapping),
        Path(args.targets),
        Path(args.schema),
        Path(args.snapshot_policy),
        Path(args.output),
    )
    emit("complete", command="generate-rules", **result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PLC projection mapping helper.")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    validate_parser = subparsers.add_parser("validate-inputs", help="Validate target/schema/snapshot-policy inputs.")
    validate_parser.add_argument("--targets", default=str(DEFAULT_TARGETS_PATH), help="projection_targets.json path.")
    validate_parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="table_schema.json path.")
    validate_parser.add_argument("--snapshot-policy", default=str(DEFAULT_SNAPSHOT_POLICY_PATH), help="plc_snapshot_policy.yaml path.")
    validate_parser.set_defaults(func=command_validate_inputs)

    export_parser = subparsers.add_parser("export-schema", help="Export selected table schemas from MySQL/MariaDB.")
    export_parser.add_argument("--targets", default=str(DEFAULT_TARGETS_PATH), help="projection_targets.json path.")
    export_parser.add_argument("--output", default=str(DEFAULT_SCHEMA_OUTPUT_PATH), help="Output table_schema.json path.")
    export_parser.add_argument("--database-url", required=True, help="Explicit MySQL/MariaDB database URL.")
    export_parser.add_argument("--overwrite", action="store_true", help="Replace an existing table_schema.json output.")
    export_parser.set_defaults(func=command_export_schema)

    list_parser = subparsers.add_parser("list-tables", help="List database tables as a projection_targets-compatible candidate JSON.")
    list_parser.add_argument("--output", default=str(DEFAULT_TARGET_CANDIDATE_OUTPUT_PATH), help="Output candidate projection_targets JSON path.")
    list_parser.add_argument("--database-url", required=True, help="Explicit MySQL/MariaDB database URL.")
    list_parser.add_argument("--overwrite", action="store_true", help="Replace an existing candidate JSON output.")
    list_parser.set_defaults(func=command_list_tables)

    xlsx_parser = subparsers.add_parser("generate-xlsx", help="Generate a fillable projection mapping workbook.")
    xlsx_parser.add_argument("--targets", default=str(DEFAULT_TARGETS_PATH), help="projection_targets.json path.")
    xlsx_parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Confirmed table_schema.json path.")
    xlsx_parser.add_argument("--snapshot-policy", default=str(DEFAULT_SNAPSHOT_POLICY_PATH), help="Reviewed plc_snapshot_policy.yaml path.")
    xlsx_parser.add_argument("--output", default=str(DEFAULT_XLSX_OUTPUT_PATH), help="Output workbook path.")
    xlsx_parser.add_argument("--overwrite", action="store_true", help="Replace an existing workbook output.")
    xlsx_parser.set_defaults(func=command_generate_xlsx)

    validate_xlsx_parser = subparsers.add_parser("validate-xlsx", help="Validate a completed projection mapping workbook.")
    validate_xlsx_parser.add_argument("--mapping", default=str(DEFAULT_MAPPING_XLSX_PATH), help="Completed plc_projection_mapping.xlsx path.")
    validate_xlsx_parser.add_argument("--targets", default=str(DEFAULT_TARGETS_PATH), help="projection_targets.json path.")
    validate_xlsx_parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Confirmed table_schema.json path.")
    validate_xlsx_parser.add_argument("--snapshot-policy", default=str(DEFAULT_SNAPSHOT_POLICY_PATH), help="Reviewed plc_snapshot_policy.yaml path.")
    validate_xlsx_parser.set_defaults(func=command_validate_xlsx)

    rules_parser = subparsers.add_parser("generate-rules", help="Generate projection_rules.yaml from a completed workbook.")
    rules_parser.add_argument("--mapping", default=str(DEFAULT_MAPPING_XLSX_PATH), help="Completed plc_projection_mapping.xlsx path.")
    rules_parser.add_argument("--targets", default=str(DEFAULT_TARGETS_PATH), help="projection_targets.json path.")
    rules_parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH), help="Confirmed table_schema.json path.")
    rules_parser.add_argument("--snapshot-policy", default=str(DEFAULT_SNAPSHOT_POLICY_PATH), help="Reviewed plc_snapshot_policy.yaml path.")
    rules_parser.add_argument("--output", default=str(DEFAULT_RULES_OUTPUT_PATH), help="Output projection_rules.yaml path.")
    rules_parser.add_argument("--overwrite", action="store_true", help="Replace an existing projection_rules.yaml output.")
    rules_parser.set_defaults(func=command_generate_rules)

    return parser


def suggest_command(value: str) -> str | None:
    if value.startswith("-") or "/" in value or "\\" in value:
        return None
    matches = get_close_matches(value, COMMANDS, n=1, cutoff=0.72)
    return matches[0] if matches else None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if not raw_args or raw_args[0] in {"-h", "--help"}:
        parser.print_help()
        return 0
    if raw_args[0].startswith("-"):
        parser.error(f"explicit command required: {', '.join(COMMANDS)}")

    command = raw_args[0]
    if command not in COMMANDS:
        suggested_command = suggest_command(command)
        if suggested_command:
            parser.error(f"unknown command {command!r}. Did you mean {suggested_command!r}?")
        parser.error(f"unknown command {command!r}. Valid commands: {', '.join(COMMANDS)}")

    args = parser.parse_args(raw_args)
    try:
        return args.func(args)
    except ToolError as exc:
        emit("failed", command=args.command, error=str(exc))
        return 2
