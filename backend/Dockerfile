# ============================================================================
# AIIS ICS Architecture backend image.
# ============================================================================

# 基础镜像固定到当前验证过的 Python 3.11 slim manifest，避免浮动 build source。
FROM python:3.11-slim@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_LINK_MODE=copy

# 安装系统依赖
RUN sed -i \
    -e 's|http://deb.debian.org/debian|http://mirrors.aliyun.com/debian|g' \
    -e 's|http://deb.debian.org/debian-security|http://mirrors.aliyun.com/debian-security|g' \
    /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 安装固定版本 uv；不使用浮动标签，保持依赖解析工具可复现。
COPY --from=ghcr.io/astral-sh/uv:0.7.8@sha256:0178a92d156b6f6dbe60e3b52b33b421021f46d634aa9f81f42b91445bb81cdf /uv /uvx /bin/

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

# 只复制生产运行入口、业务源码、迁移与明确配置资源。
COPY alembic ./alembic
COPY app ./app
COPY common ./common
COPY config ./config
COPY core ./core
COPY database ./database
COPY projection ./projection
COPY scripts/maintenance ./scripts/maintenance
COPY alembic.ini main.py settings.py ./

# 创建日志目录
RUN mkdir -p logs data

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=12 \
    CMD python -c "import httpx; response = httpx.get('http://127.0.0.1:8000/health', timeout=3); response.raise_for_status()" || exit 1

# 生产入口；host、port 与 worker 数从 /app/.env 读取，reload 永久关闭。
CMD ["python", "main.py"]
