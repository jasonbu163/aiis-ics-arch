"""
File Path: /tools/lineage-mapping-studio/src-python/cli/commands.py
Description: CLI and watcher entrypoints for lineage graph generation.
Main Features:
  - Provides the canonical command surface used by main.py.
  - Builds or watches graph JSON with component-level input overrides.
  - Emits JSON Lines command evidence.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from graph.builder import build_graph
from graph.io import DEFAULT_INPUTS_DIR, DEFAULT_OUTPUT, DEFAULT_XLSX, mtime_signature, resolve_sources
from graph.models import ToolError


def emit(event: str, **payload: Any) -> None:
    print(json.dumps({"event": event, **payload}, ensure_ascii=False), flush=True)


def resolve_sources_from_args(args: argparse.Namespace):
    return resolve_sources(
        inputs_dir=Path(args.inputs_dir),
        audit_outputs_dir=Path(args.audit_outputs_dir) if args.audit_outputs_dir else None,
        frontend_dir=Path(args.frontend_dir) if args.frontend_dir else None,
        backend_dir=Path(args.backend_dir) if args.backend_dir else None,
        database_dir=Path(args.database_dir) if args.database_dir else None,
        xlsx_path=Path(args.xlsx) if args.xlsx else None,
    )


def command_build(args: argparse.Namespace) -> int:
    sources = resolve_sources_from_args(args)
    output_path = Path(args.output)
    emit(
        "start",
        command="build-graph",
        inputs_dir=str(sources.default_inputs_dir),
        audit_outputs_dir=str(sources.audit_outputs_dir) if sources.audit_outputs_dir else None,
        xlsx=str(sources.xlsx) if sources.xlsx else None,
        output=str(output_path),
    )
    graph = build_graph(sources)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    emit("complete", command="build-graph", output=str(output_path), **graph["stats"])
    return 0


def command_watch(args: argparse.Namespace) -> int:
    sources = resolve_sources_from_args(args)
    output_path = Path(args.output)
    interval = float(args.interval)
    paths = sources.watched_paths()
    emit(
        "start",
        command="watch-graph",
        inputs_dir=str(sources.default_inputs_dir),
        audit_outputs_dir=str(sources.audit_outputs_dir) if sources.audit_outputs_dir else None,
        xlsx=str(sources.xlsx) if sources.xlsx else None,
        output=str(output_path),
        interval=interval,
        watched=[str(path) for path in paths],
    )
    last_signature: tuple[tuple[str, float | None], ...] | None = None
    while True:
        current_signature = mtime_signature(paths)
        if current_signature != last_signature:
            last_signature = current_signature
            graph = build_graph(sources)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
            emit("updated", command="watch-graph", output=str(output_path), **graph["stats"])
        time.sleep(interval)


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--inputs-dir", default=str(DEFAULT_INPUTS_DIR), help="Default Studio-local inputs directory.")
    parser.add_argument("--audit-outputs-dir", help="Optional lineage-audit outputs directory. Overrides frontend/backend/database sources together.")
    parser.add_argument("--frontend-dir", help="Optional explicit frontend evidence directory.")
    parser.add_argument("--backend-dir", help="Optional explicit backend evidence directory.")
    parser.add_argument("--database-dir", help="Optional explicit database evidence directory.")
    parser.add_argument("--xlsx", default=str(DEFAULT_XLSX), help="Projection workbook path for Field -> PLC links.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build file-driven lineage graph JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-graph", help="Build lineage_graph.json once.")
    add_source_arguments(build)
    build.set_defaults(func=command_build)

    watch = subparsers.add_parser("watch-graph", help="Rebuild graph JSON when source input mtimes change.")
    add_source_arguments(watch)
    watch.add_argument("--interval", default="2.0")
    watch.set_defaults(func=command_watch)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ToolError as exc:
        emit("failed", command=args.command, error=str(exc))
        return 1
