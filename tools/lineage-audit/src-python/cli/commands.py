"""
File Path: /tools/lineage-audit/src-python/cli/commands.py
Description: CLI entrypoint for lineage audit.
Main Features:
    - Provides the canonical command surface used by main.py.
    - Emits JSON Lines command evidence.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from audit.common import emit, rel
from audit.constants import DEFAULT_BACKEND_ROOT, DEFAULT_FRONTEND_ROOT, DEFAULT_OUTPUTS_DIR
from audit.models import ToolError
from audit.runner import audit
from reports.writers import write_outputs

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate UI -> API -> DB lineage audit reports.")
    parser.add_argument("--frontend-root", type=Path, default=DEFAULT_FRONTEND_ROOT)
    parser.add_argument("--backend-root", type=Path, default=DEFAULT_BACKEND_ROOT)
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = time.monotonic()
    emit(
        "start",
        frontend_root=rel(args.frontend_root),
        backend_root=rel(args.backend_root),
        outputs_dir=rel(args.outputs_dir),
    )
    try:
        state = audit(args.frontend_root, args.backend_root)
        paths = write_outputs(state, args.outputs_dir, args.frontend_root, args.backend_root)
    except ToolError as exc:
        emit("failed", error=str(exc), duration_ms=round((time.monotonic() - started_at) * 1000))
        return 1
    emit(
        "complete",
        duration_ms=round((time.monotonic() - started_at) * 1000),
        frontend_route_count=len(state.frontend_routes),
        frontend_api_count=len(state.frontend_apis),
        frontend_usage_count=len(state.frontend_usages),
        backend_route_count=len(state.backend_routes),
        mock_finding_count=len(state.mock_findings),
        component_link_count=len(state.component_links),
        outputs={key: rel(value) for key, value in paths.items()},
    )
    return 0
