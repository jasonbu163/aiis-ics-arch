"""
File Path: /backend/run.py
Description: Local and Docker development entrypoint for the FastAPI application.
Main Features:
    - Reads backend host and port from the active .env file
    - Starts Uvicorn with source reload enabled
    - Keeps development-only behavior out of production and packaged execution
"""
from __future__ import annotations

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
        log_config=None,
    )


if __name__ == "__main__":
    main()
