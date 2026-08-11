#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
RELOAD="${RELOAD:-1}"
AUTO_MIGRATE="${AUTO_MIGRATE:-0}"

echo "启动 FastAPI 后端"
echo "工作目录: $SCRIPT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "未检测到 uv，请先安装 uv"
  exit 1
fi

if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "已根据 .env.example 创建 .env，请确认配置后再启动"
  else
    echo "缺少 .env，且找不到 .env.example"
    exit 1
  fi
fi

if [ "$AUTO_MIGRATE" = "1" ]; then
  echo "执行数据库迁移: alembic upgrade head"
  uv run alembic upgrade head
fi

echo "接口文档: http://127.0.0.1:${PORT}/docs"
echo "健康检查: http://127.0.0.1:${PORT}/health"

if [ "$RELOAD" = "1" ]; then
  exec uv run uvicorn main:app --reload --host "$HOST" --port "$PORT"
else
  exec uv run uvicorn main:app --host "$HOST" --port "$PORT"
fi
