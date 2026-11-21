"""
File Path: /backend/run.py
Description: Local and Docker development entrypoint for the FastAPI application.
Main Features:
    - Reads backend host and port from the active .env file
    - Starts Uvicorn with source reload enabled
    - Uses a readable development console for the reloader and server
    - Keeps development-only behavior out of production and packaged execution
"""
from __future__ import annotations

import os

import uvicorn

from settings import settings


def main() -> None:
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        workers=1,
        reload=True,
        reload_excludes=[".venv/*", "logs/*", "data/*"],
    )


if __name__ == "__main__":
    # The reload supervisor passes this mode to each new server process.
    os.environ["_AIIS_BACKEND_DEV_LOGGING"] = "1"
    main()
