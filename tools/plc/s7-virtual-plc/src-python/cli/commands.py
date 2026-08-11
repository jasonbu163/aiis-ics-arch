"""
文件路径: /tools/plc/s7-virtual-plc/src-python/cli/commands.py
功能描述: S7 虚拟 PLC 工具的命令行启动面
"""
from __future__ import annotations

import argparse
from difflib import get_close_matches
import signal
import sys
import time
from pathlib import Path
from typing import Any

from snap7.type import SrvArea

from core.config import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_PROFILE_INPUT_PATH,
    DEFAULT_PROFILE_OUTPUT_PATH,
    env_value,
    resolve_setting,
)
from core.identity import VirtualPlcIdentity, resolve_virtual_plc_identity
from core.loader import load_plc_config, load_virtual_areas
from core.profile import load_profile_rules, write_profile_template
from core.runtime import refresh_areas
from core.strict_server import StrictTsapServer


COMMANDS = ("init-profile", "dry-run", "serve")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="S7 virtual PLC tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Command-specific options:\n"
            "  main.py init-profile --help\n"
            "  main.py dry-run --help\n"
            "  main.py serve --help\n\n"
            "No bare or default startup is performed."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    init_parser = subparsers.add_parser("init-profile", help="Generate simulation_profile.xlsx and exit.")
    _add_config_argument(init_parser)
    _add_plc_key_argument(init_parser)
    _add_profile_output_argument(init_parser)
    init_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output profile workbook if it already exists.",
    )
    init_parser.set_defaults(func=command_init_profile)

    dry_run_parser = subparsers.add_parser("dry-run", help="Validate config/profile without opening a TCP port.")
    _add_config_argument(dry_run_parser)
    _add_plc_key_argument(dry_run_parser)
    _add_profile_argument(dry_run_parser)
    _add_identity_arguments(dry_run_parser)
    dry_run_parser.set_defaults(func=command_dry_run)

    serve_parser = subparsers.add_parser("serve", help="Start the resident Snap7 virtual PLC.")
    _add_config_argument(serve_parser)
    _add_plc_key_argument(serve_parser)
    _add_profile_argument(serve_parser)
    _add_server_arguments(serve_parser)
    serve_parser.set_defaults(func=command_serve)
    return parser


def _add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to plc_points.yaml.")


def _add_profile_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        default=env_value("PLC_SIM_PROFILE_XLSX", str(DEFAULT_PROFILE_INPUT_PATH)),
        help="Path to validated simulation_profile.xlsx.",
    )


def _add_profile_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile-output",
        default=str(DEFAULT_PROFILE_OUTPUT_PATH),
        help="Output path used by init-profile.",
    )


def _add_plc_key_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--plc-key", default=env_value("PLC_SIM_PLC_KEY", "PLC_1"), help="Top-level PLC key in YAML.")


def _add_server_arguments(parser: argparse.ArgumentParser) -> None:
    _add_identity_arguments(parser)
    parser.add_argument(
        "--interval",
        type=float,
        default=float(env_value("PLC_SIM_INTERVAL_SECONDS", "1.0")),
        help="Refresh interval in seconds.",
    )


def _add_identity_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rack", default=None, help="Virtual PLC rack; CLI overrides PLC_SIM_RACK.")
    parser.add_argument("--slot", default=None, help="Virtual PLC slot; CLI overrides PLC_SIM_SLOT.")
    parser.add_argument("--port", type=int, default=None, help="Virtual PLC TCP port; CLI overrides PLC_SIM_PORT.")


def _ensure_can_write(output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"output profile already exists: {output_path}; pass --overwrite to replace it")


def _error_message(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


def command_init_profile(args: argparse.Namespace) -> int:
    try:
        config_path = Path(args.config)
        areas = load_virtual_areas(config_path, args.plc_key)
        total_points = sum(len(area.points) for area in areas.values())
        output_path = Path(args.profile_output)
        _ensure_can_write(output_path, args.overwrite)
        write_profile_template(areas, output_path)
        print(f"init_profile status=ok output={output_path} db_count={len(areas)} point_count={total_points}")
        return 0
    except Exception as exc:
        print(f"s7_virtual_plc error {_error_message(exc)}", file=sys.stderr)
        return 1


def _prepare_runtime(
    args: argparse.Namespace,
) -> tuple[Path, Path, float, VirtualPlcIdentity, float, dict[int, Any], dict[str, Any], dict[str, Any]]:
    config_path = Path(args.config)
    started_at = time.time()
    plc_config = load_plc_config(config_path, args.plc_key)
    port_value = resolve_setting("PLC_SIM_PORT", args.port)
    identity = resolve_virtual_plc_identity(
        plc_key=args.plc_key,
        plc_config=plc_config,
        rack_value=resolve_setting("PLC_SIM_RACK", args.rack),
        slot_value=resolve_setting("PLC_SIM_SLOT", args.slot),
        port="1102" if port_value is None else port_value,
    )
    interval = getattr(args, "interval", 1.0)
    areas = load_virtual_areas(config_path, args.plc_key)
    profile_path = Path(args.profile)
    rules = load_profile_rules(areas, profile_path)
    first_refresh = refresh_areas(areas, rules=rules, tick=0, started_at=started_at)
    return config_path, profile_path, started_at, identity, interval, areas, rules, first_refresh


def command_dry_run(args: argparse.Namespace) -> int:
    try:
        config_path, profile_path, _started_at, identity, _interval, areas, _rules, first_refresh = _prepare_runtime(args)
        _print_runtime_summary(config_path, profile_path, identity, areas, first_refresh)
        print("dry_run=true status=ok")
        return 0
    except Exception as exc:
        print(f"s7_virtual_plc error {_error_message(exc)}", file=sys.stderr)
        return 1


def command_serve(args: argparse.Namespace) -> int:
    try:
        config_path, profile_path, started_at, identity, interval, areas, rules, first_refresh = _prepare_runtime(args)
    except Exception as exc:
        print(f"s7_virtual_plc error {_error_message(exc)}", file=sys.stderr)
        return 1

    _print_runtime_summary(config_path, profile_path, identity, areas, first_refresh)
    return _run_server(identity, interval, started_at, areas, rules)


def _print_runtime_summary(
    config_path: Path,
    profile_path: Path,
    identity: VirtualPlcIdentity,
    areas: dict[int, Any],
    first_refresh: dict[str, Any],
) -> None:
    total_points = sum(len(area.points) for area in areas.values())
    total_bytes = sum(len(area.memory) for area in areas.values())
    print(
        "s7_virtual_plc summary "
        f"config={config_path} profile={profile_path} db_count={len(areas)} "
        f"point_count={total_points} total_bytes={total_bytes}"
    )
    print(
        "s7_virtual_plc identity "
        f"plc_key={identity.plc_key} rack={identity.rack} slot={identity.slot} "
        f"port={identity.port} expected_called_tsap=0x{identity.expected_called_tsap:04X}"
    )
    for area in areas.values():
        print(f"db_area DB{area.db_number} size={len(area.memory)} points={len(area.points)}")
    print(
        f"initial_refresh updated={first_refresh['updated']} skipped={first_refresh['skipped']} "
        f"samples={first_refresh['samples']}"
    )


def _run_server(
    identity: VirtualPlcIdentity,
    interval: float,
    started_at: float,
    areas: dict[int, Any],
    rules: dict[str, Any],
) -> int:
    try:
        server = StrictTsapServer(identity.expected_called_tsap, on_tsap_rejected=_print_tsap_rejection)
        stop_requested = False

        def stop(_signum: int | None = None, _frame: Any | None = None) -> None:
            nonlocal stop_requested
            stop_requested = True

        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

        for area in areas.values():
            server.register_area(SrvArea.DB, area.db_number, area.memory)
        server.start(tcp_port=identity.port)
        print(
            "s7_virtual_plc started "
            f"host=0.0.0.0 port={identity.port} rack={identity.rack} slot={identity.slot} "
            f"expected_called_tsap=0x{identity.expected_called_tsap:04X} interval={interval}"
        )

        tick = 1
        while not stop_requested:
            summary = refresh_areas(areas, rules=rules, tick=tick, started_at=started_at)
            print(
                "refresh "
                f"tick={tick} updated={summary['updated']} skipped={summary['skipped']} "
                f"unsupported={summary['unsupported']} "
                f"samples={summary['samples']}"
            )
            tick += 1
            time.sleep(max(interval, 0.1))
    except Exception as exc:
        print(f"s7_virtual_plc error {_error_message(exc)}", file=sys.stderr)
        return 1
    finally:
        if "server" in locals():
            try:
                server.stop()
            finally:
                server.destroy()
        print("s7_virtual_plc stopped")

    return 0


def _print_tsap_rejection(expected_called_tsap: int, received_called_tsap: int | None) -> None:
    received = (
        f"0x{received_called_tsap:04X}"
        if received_called_tsap is not None
        else "missing_or_malformed"
    )
    print(
        "s7_virtual_plc tsap_rejected "
        f"expected_called_tsap=0x{expected_called_tsap:04X} received_called_tsap={received}",
        flush=True,
    )


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
    if effective_argv[0].startswith("-"):
        parser.error("explicit command required: init-profile, dry-run or serve")

    command = effective_argv[0]
    if command not in COMMANDS:
        suggested_command = _suggest_command(command)
        if suggested_command:
            parser.error(f"unknown command {command!r}. Did you mean {suggested_command!r}?")
        parser.error(f"unknown command {command!r}. Valid commands: {', '.join(COMMANDS)}")

    args = parser.parse_args(effective_argv)
    return args.func(args)
