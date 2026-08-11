# 后端脚本

English version: [README.md](README.md)

Core 脚本表面保持最小：

| 目录 | 用途 |
| --- | --- |
| maintenance/ | 显式 Schema 与 bootstrap-user 操作 |
| api_smoke/ | 只读 HTTP 冒烟入口 |

脚本必须使用 backend 环境运行：

~~~bash
uv run python scripts/maintenance/ensure_admin_user.py
~~~

本目录脚本不会启动 Worker、轮询 PLC、默认执行 migration 或读取项目输入。数据库写入必须使用显式动作并确认单独获批的目标。
