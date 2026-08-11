"""
文件路径: /backend/scripts/maintenance/ensure_admin_user.py
功能描述: 基础账号幂等初始化脚本
主要功能:
    - 按环境变量控制是否创建管理员、班组长、操作员账号
    - 检查目标账号是否存在
    - 输出稳定的初始化摘要
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.user.models.user import User
from core.security import hash_password
from database import get_sync_db_context
from settings import settings


def ensure_bootstrap_user(
    *,
    target: str,
    enabled: bool,
    username: str,
    password: str,
    name: str,
    role: str,
    reset_password: bool,
) -> int:
    """Create one configured bootstrap user if enabled."""
    if not enabled:
        print(f"target={target} status=skipped reason=bootstrap_disabled")
        return 0

    if not password:
        print(f"target={target} status=failed reason=missing_password username={username}", file=sys.stderr)
        return 2

    with get_sync_db_context() as db:
        existing_user = db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

        if existing_user is not None:
            if reset_password:
                existing_user.password = hash_password(password)
                existing_user.name = existing_user.name or name
                existing_user.role = existing_user.role or role
                existing_user.is_active = True
                db.add(existing_user)
                db.commit()
                print(f"target={target} status=password_reset username={username} role={role}")
                return 0

            print(f"target={target} status=exists username={username} role={role}")
            return 0

        user = User(
            username=username,
            password=hash_password(password),
            name=name,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"target={target} status=created username={username} role={role}")
        return 0


def ensure_admin_user() -> int:
    """Create configured bootstrap users."""
    results = [
        ensure_bootstrap_user(
            target="admin_user",
            enabled=settings.ADMIN_BOOTSTRAP_ENABLED,
            username=settings.ADMIN_BOOTSTRAP_USERNAME,
            password=settings.ADMIN_BOOTSTRAP_PASSWORD,
            name=settings.ADMIN_BOOTSTRAP_NAME,
            role=settings.ADMIN_BOOTSTRAP_ROLE,
            reset_password=settings.ADMIN_BOOTSTRAP_RESET_PASSWORD,
        ),
        ensure_bootstrap_user(
            target="supervisor_user",
            enabled=settings.SUPERVISOR_BOOTSTRAP_ENABLED,
            username=settings.SUPERVISOR_BOOTSTRAP_USERNAME,
            password=settings.SUPERVISOR_BOOTSTRAP_PASSWORD,
            name=settings.SUPERVISOR_BOOTSTRAP_NAME,
            role=settings.SUPERVISOR_BOOTSTRAP_ROLE,
            reset_password=settings.SUPERVISOR_BOOTSTRAP_RESET_PASSWORD,
        ),
        ensure_bootstrap_user(
            target="operator_user",
            enabled=settings.OPERATOR_BOOTSTRAP_ENABLED,
            username=settings.OPERATOR_BOOTSTRAP_USERNAME,
            password=settings.OPERATOR_BOOTSTRAP_PASSWORD,
            name=settings.OPERATOR_BOOTSTRAP_NAME,
            role=settings.OPERATOR_BOOTSTRAP_ROLE,
            reset_password=settings.OPERATOR_BOOTSTRAP_RESET_PASSWORD,
        ),
    ]
    return max(results)


if __name__ == "__main__":
    try:
        raise SystemExit(ensure_admin_user())
    except Exception as exc:
        print(f"target=bootstrap_users status=failed error={exc}", file=sys.stderr)
        raise
