# AIIS ICS Architecture 后端

English version: [README.md](README.md)

本目录是可复用的 FastAPI/SQLAlchemy Core。它负责认证、系统管理、模块发现、Schema maintenance、Projection 控制面和项目无关的 monitor 现场事实。使用方项目只需按约定增加业务模块，不修改 Core 组合根。

## Core 模块

~~~text
app/
├── user/             # 认证与账号 API
├── system/           # 字典与 Projection 控制面 API
├── control_agent/    # 后端侧 CA 授权合同
├── schema_maintenance/
├── monitor/          # 只保留 collector/raw/latest 事实
├── aiis_demo/        # manifest 参考模块
└── module_registry.py
~~~

普通模块通过 app/<module>/manifest.py opt-in。enabled=False 会隐藏模块 API；Registry 不会创建数据表。新增表必须走显式 Alembic revision 或获批的 schema-maintenance 动作。user 与 control_agent 是安全/运行时边界，继续在 app/router.py 显式挂载。

monitor Core 只返回 collector 健康状态和项目无关的 PLC DB-block raw/latest 事实。HMI、温度、能耗、过程曲线和生产实绩由项目仓库自己的模块负责。

## 运行边界

- FastAPI handler 调用 async Service/CRUD，不能轮询 PLC。
- 常驻 Rust/Tauri control-agent 负责 PLC 采集，并通过批准的合同写入现场事实。
- Celery、Redis、Beat、Flower 和 Python Worker runtime 不是 Core 依赖。
- Core baseline 现在是只包含十四张 Core 表的单一 `d4e6f8a0b2c4` Alembic root。其 upgrade 实际操作与当前
  SQLAlchemy metadata 由 `tests/test_core_migration_baseline.py` 机械核对；私有项目仓继续保留自己的历史
  migration 图。

## 本地检查

~~~bash
uv sync
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q
~~~

静态迁移检查可以在占位环境下运行 `uv run alembic heads`、`uv run alembic history` 和 offline SQL render。
源码检查不应连接真实数据库或执行在线迁移；Schema 工作必须使用单独获批的非生产数据库任务。

已批准的 `ARCH-DOCKER-001` smoke 从 backend 源码构建本镜像，并由一次性 `alembic upgrade head` 服务和
API 服务复用。它只连接同一 Compose 的 `mysql:3306`，使用可丢弃的 MySQL `8.4.6` volume；smoke env
被忽略，且每次运行后必须删除。

## 打包

main.py 是禁用 reload 的应用入口；run.py 是本地开发入口；build.py 是可选 PyInstaller 源码打包路径，不会复制真实 .env、数据 dump 或客户输入。详见 BUILD.zh-CN.md。
