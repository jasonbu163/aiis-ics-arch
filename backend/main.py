"""
File Path: /backend/main.py
Description: Production, container, and packaged FastAPI application entrypoint.
Main Features:
    - Creates the FastAPI application and initializes API process logging
    - Starts Uvicorn without reload for production execution
    - Exposes explicit schema and bootstrap-user maintenance actions
"""
from __future__ import annotations

import argparse
import multiprocessing
import os
import sys
import time
from pathlib import Path

multiprocessing.freeze_support()

import uvicorn

from common.log import logger, setup_logger
from core.registrar import create_app
from settings import settings


if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)


def configure_timezone() -> None:
    """Apply the configured process timezone on platforms that support tzset."""
    os.environ["TZ"] = settings.TZ
    if hasattr(time, "tzset"):
        time.tzset()


configure_timezone()
setup_logger("api")

app = create_app()

logger.info("{} v{} application loaded", app.title, app.version)


def run_maintenance(action: str) -> int:
    """Run one explicit maintenance action without starting the API server."""
    if action == "schema":
        from scripts.maintenance.bootstrap_or_migrate_schema import (
            bootstrap_or_migrate_schema,
        )

        return bootstrap_or_migrate_schema()

    if action == "bootstrap-users":
        from scripts.maintenance.ensure_admin_user import ensure_admin_user

        return ensure_admin_user()

    raise ValueError(f"Unsupported maintenance action: {action}")


def run_server() -> None:
    """Start the production server with reload permanently disabled."""
    frozen = getattr(sys, "frozen", False)
    workers = 1 if frozen else settings.BACKEND_WORKERS
    application = app if frozen else "main:app"

    if frozen and settings.BACKEND_WORKERS != 1:
        logger.warning(
            "Packaged runtime forces one worker; configured BACKEND_WORKERS={} is ignored",
            settings.BACKEND_WORKERS,
        )

    uvicorn.run(
        application,
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        workers=workers,
        reload=False,
        log_config=None,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AIIS ICS Architecture backend runtime")
    parser.add_argument(
        "--maintenance",
        choices=("schema", "bootstrap-users"),
        help="Run one explicit maintenance action, then exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.maintenance:
        return run_maintenance(args.maintenance)
    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
