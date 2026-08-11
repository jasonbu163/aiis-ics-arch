#!/usr/bin/env python3
"""Small smoke client for the public Core health, auth, and user routes."""

from __future__ import annotations

import asyncio
import os

import httpx


BASE_URL = os.getenv("AIIS_CORE_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("AIIS_CORE_SMOKE_USERNAME", "admin")
PASSWORD = os.getenv("AIIS_CORE_SMOKE_PASSWORD", "change-me")


async def main() -> int:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        health = await client.get("/health")
        health.raise_for_status()
        login = await client.post(
            "/api/v1/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
        )
        login.raise_for_status()
        token = login.json()["data"]["accessToken"]
        users = await client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        users.raise_for_status()
        print("Core smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
