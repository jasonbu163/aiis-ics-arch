"""
File Path: /backend/build.py
Description: PyInstaller build entry for the optional no-Docker backend package.
Main Features:
    - Builds the production main.py entry in one-directory mode
    - Bundles migrations and runtime configuration resources
    - Copies only an editable .env example and creates empty state directories
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import PyInstaller.__main__


BACKEND_ROOT = Path(__file__).resolve().parent
BUILD_DIR = BACKEND_ROOT / "build"
DIST_DIR = BACKEND_ROOT / "dist"
APP_NAME = "aiis-ics-architecture-backend"


def emit(**payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


def clean_generated_directory(path: Path) -> None:
    resolved = path.resolve()
    if resolved.parent != BACKEND_ROOT:
        raise RuntimeError(f"Refusing to clean path outside backend root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def add_data(source: str, target: str) -> str:
    return f"--add-data={BACKEND_ROOT / source}{os.pathsep}{target}"


def build() -> Path:
    os.chdir(BACKEND_ROOT)
    clean_generated_directory(BUILD_DIR)
    clean_generated_directory(DIST_DIR)

    emit(event="backend.package.build", status="started", app=APP_NAME)
    PyInstaller.__main__.run(
        [
            str(BACKEND_ROOT / "main.py"),
            f"--name={APP_NAME}",
            "--onedir",
            "--clean",
            "--noconfirm",
            f"--distpath={DIST_DIR}",
            f"--workpath={BUILD_DIR}",
            f"--specpath={BUILD_DIR}",
            "--collect-submodules=app",
            "--collect-submodules=projection",
            "--collect-submodules=scripts.maintenance",
            "--hidden-import=aiomysql",
            "--hidden-import=pymysql",
            "--hidden-import=asyncpg",
            "--hidden-import=psycopg2",
            add_data("alembic", "alembic"),
            add_data("alembic.ini", "."),
            add_data("config", "config"),
        ]
    )

    output_dir = DIST_DIR / APP_NAME
    shutil.copy2(BACKEND_ROOT / ".env.example", output_dir / ".env.example")
    (output_dir / "logs").mkdir(exist_ok=True)
    (output_dir / "storage").mkdir(exist_ok=True)

    emit(
        event="backend.package.build",
        status="completed",
        output=str(output_dir),
        config=str(output_dir / ".env"),
    )
    return output_dir


if __name__ == "__main__":
    build()
