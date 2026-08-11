<!--
  File Path: /backend/app/README.zh-CN.md
  Description: 后端应用模块中文说明
  Main Features:
    - 解释 backend app 模块归属
    - 记录受控 package-aware manifest 自发现用法
    - 定义安全的模块注册边界
-->
# 后端 App 业务模块

[English version](README.md)

`backend/app/` 承载 FastAPI 业务模块，以及后端组合根使用的受控 manifest 自发现。本目录 README 是结构说明，不是任务跟踪文件。后端工作状态继续归属 [../PLAN.zh-CN.md](../PLAN.zh-CN.md)，模块注册历史依据见 [../plans/B11-backend-module-manifest-autoregistration.md](../plans/B11-backend-module-manifest-autoregistration.md)。

## 注册模型

后端使用受控 package-aware 自发现，而不是无边界扫描整个目录：

- [module_registry.py](module_registry.py) 只枚举已导入 `app` package 的直接子 package。
- 只有 `app.<module>.manifest` 直接导出类型为 `ModuleManifest` 且 `name` 严格匹配 package 名的 `manifest` 才 opt in。
- 没有 `manifest.py` 的 package 会被跳过，不提供 route、model 或 Projection；manifest 内部 import、导出类型错误和名称错误都会显式失败。
- [router.py](router.py) 继续集中负责 router 创建和路由汇总。
- enabled manifest 进入普通 router 与 Projection owner discovery；disabled manifest 不进入二者，但仍导入其 model package 供 SQLAlchemy metadata 与 migration 检查。
- Alembic 与显式 schema-maintenance action 仍是唯一 Schema 变更入口；model import 不执行 DDL 或 migration。

安全与现场 runtime 边界保持显式：

- `user` 路由在 [router.py](router.py) 中直接挂载，因为认证和用户管理是安全边界入口。
- `control_agent` 路由直接挂载，因为它是现场 runtime 与授权边界 API。
- 已退役的 Worker-control 基础设施不再属于 `app/` 或普通自发现。

## 标准业务模块结构

```text
backend/app/<module>/
├── __init__.py                  # 很薄的包入口；不做注册副作用
├── manifest.py                  # 只放 registry 元数据
├── api/
│   └── routes.py                # FastAPI APIRouter 定义
├── models/                      # SQLAlchemy 模型
├── schemas/                     # Pydantic 契约
├── crud/                        # 数据库访问 helper
├── services/                    # 业务编排与事务边界
├── mocks/                       # 业务 mock provider 包；无实现时也保留无副作用入口
└── seeds/                       # seed provider 包；导入时绝不执行写入
```

少数历史模块或特殊模块可能包含额外文件，但新增普通业务模块应向这个结构收敛。

## 项目本地参考源

当新模块需要对照当前 package 结构时，优先使用项目本地的
[`aiis_demo/`](aiis_demo/README.zh-CN.md)。它只作 reference，且固定为
`enabled=False`；因此正常组合不会暴露其 route 或 Projection owner。它的空 models package
会为 metadata discovery 导入，但不声明任何 table。不要把它当作业务模板、授权授予或 AIIS
shared skill/template。复制它时必须有意识地替换所有 demo 名称和 payload，重新设计业务权限；
一旦引入真实持久化，必须另行新增 Alembic migration。

## Manifest 规则

`manifest.py` 只声明元数据：

```python
from app.module_registry import ModuleManifest

manifest = ModuleManifest(
    name="equipment",
    order=50,
    routers=("app.equipment.api.routes:router",),
    models_package="app.equipment.models",
    permissions=("equipment",),
)
```

规则：

- `manifest.py` 必须可安全导入、无副作用。
- 导入 manifest 时不得打开数据库、消息 broker、PLC、摄像头、ERP 或网络连接。
- 导入 manifest 时不得启动线程、loop、timer、worker 或 migration。
- 路由字符串使用显式 `module:attribute` 导入路径。
- 显式声明 model package，确保 Alembic metadata 和测试能看到预期表。
- 合规 manifest 本身就是模块 opt-in；不再维护第二份中央模块清单。

## 新增普通业务模块

1. 创建 `backend/app/<module>/`，固定包含 `__init__.py`、`manifest.py`、`api/`、`models/`、`schemas/`、`crud/`、`services/`、`mocks/` 和 `seeds/`。
2. 在 `api/routes.py` 中实现 `APIRouter`。
3. SQLAlchemy model 放在 `models/` 下，并在 `models/__init__.py` 中导入 Alembic 需要看到的模型。
4. 新增只包含元数据的 `manifest.py`。
5. 如果需要后端诊断 mock 数据，将 provider 放入 `mocks/`，并且只在 `settings.BACKEND_MOCK_ENABLED` 为 true 时由 Service 调用。
6. 保持 manifest 可安全导入，并新增或更新聚焦测试，覆盖 route、metadata 以及 enabled/disabled 语义。
7. 数据库结构变化必须新增 Alembic migration。registry model import 不替代 migration。

认证、高危控制、现场 runtime 这类边界模块，在没有明确架构决策前不要 opt in 普通自发现；它们必须保持显式边界。

## 离线自建模块 SOP

无法联网、没有生成器或只想手工新增普通后端业务模块时，使用这条路径。优先复制结构最接近的 registry-backed 模块，再有意识地改名。

1. 选择相近源模块。先用项目本地 [`aiis_demo/`](aiis_demo/README.zh-CN.md) 对照 package 与
   disabled 组合机制；已有业务行为可参考 `plan`、`monitor`、`equipment` 或 `quality`。不要用
   `user` 或 `control_agent` 作为普通模块模板。
2. 将目录复制为 `backend/app/<new-module>/`。
3. 保持 `__init__.py` 很薄。它可以暴露包元信息，但不得注册 router、为了副作用导入 service，或启动运行时工作。
4. 将 Python 模块、类名、schema、service 函数和表名从旧业务含义改为新业务含义。
5. 更新 `api/routes.py`：route prefix、tags、endpoint 名称、依赖注入和 service 调用。
6. 更新 `schemas/`：请求、查询、响应和分页契约。后端内部保持 `snake_case`；前端输出 JSON 的 alias 由 schema / response 序列化负责。
7. 更新 `models/`：表名、索引、约束和关系。确保 `models/__init__.py` 导入 Alembic 必须看到的全部 model class。
8. 更新 `crud/`：只放持久化 helper。CRUD 函数不得提交或回滚事务。
9. 更新 `services/`：业务动作、事务边界、状态流转、审计 / 日志事件和外部集成处理。
10. 诊断 mock 固定放在 `mocks/`，seed provider 固定放在 `seeds/`；两个 package 都必须可安全导入，mock 使用仍由 `settings.BACKEND_MOCK_ENABLED` 保护。
11. 更新 `manifest.py`：`name`、`order`、`routers`、`models_package` 和 `permissions`。
12. 保持 manifest package 导入有效，由受控 immediate-child 自发现自动 opt in。
13. 任何数据库结构变化都必须新增 Alembic revision。registry model import 不替代 migration。
14. 新增或更新聚焦测试，覆盖 route 暴露、metadata 注册、响应契约和关键业务失败。

执行这条 SOP 时不要新增依赖。优先复用项目内 common response helper、schema base、日志工具和既有数据库 / session 模式。

## 复制 / 改名检查清单

复制已有后端模块后，先跑这些本地搜索，再进入测试：

```bash
rg -n "<old_module>|OldBusinessName|old_business_table" backend/app/<new-module>
rg -n "<new-module>|app\\.<new-module>|<new_module>" backend/app/<new-module>/manifest.py
rg -n --glob '!**/*.md' "api/mock\\.py" backend/app/<new-module>
```

期望结果：

- 不再残留旧模块 import path，除非明确复用。
- `manifest.name` 与目录名完全一致。
- `manifest.routers` 指向新模块的 route 对象。
- 模块拥有数据表时，`manifest.models_package` 指向新模块 `models` 包。
- manifest 名称与直接 package 名完全一致，且没有把显式边界模块加入普通自发现。
- route prefix 和 tags 与新模块一致。
- 表名、schema 名、service 名、错误 / 状态 key 与新业务含义一致。
- 后端业务 mock 没有放在 `api/mock.py` 下。
- 任何 table、index、enum 或 constraint 变化都有 Alembic revision。

如果模块没有公开 HTTP API，则省略 `routers` 并说明原因。如果模块没有数据库表，则省略 `models_package`，并用测试证明该 registry 行为是有意的。

## Restart 与 no-hot-unload 语义

修改 manifest 的 `enabled` 可能触发开发 source watcher 对整个 backend 进程 autoreload；若 watcher
未重载，必须手动重启。新增、删除或改名模块/package，或改变 router/models/services 拓扑时，必须
重启 backend 进程或对应容器，使 discovery 与 composition 从零重建。正式/生产环境源码或 package
变化必须 restart/redeploy。已经组合的 FastAPI 应用不会 hot-unload 已挂载 router：运行中把 manifest
从 enabled 改为 disabled 只有重启后才生效。

## 分层边界

- API handler 保持很薄：鉴权、校验、依赖注入、调用 Service、返回 response model。
- Service 承载业务编排和事务边界。
- Service 负责在 `BACKEND_MOCK_ENABLED=true` 时选择模块内 mock provider；真实集成检查必须使用 `BACKEND_MOCK_ENABLED=false`。
- CRUD 只放持久化 helper，不提交或回滚事务。
- Domain 规则不导入 FastAPI 对象或数据库 Session。
- 后端内部使用 `snake_case`；前端输出 JSON 命名由后端 schema 和响应序列化负责。
- 设备与 PLC 仿真归 Control Agent 或 PLC 开发工具；后端业务 API mock 数据使用 `BACKEND_MOCK_ENABLED`。

## 验证

修改 registry-backed 模块后，至少执行：

```bash
cd backend
uv run pytest tests/test_module_structure.py tests/test_module_registry.py tests/test_migrations.py
rg -n -P --glob '!**/*.md' "\\bMOCK_ENABLE\\b" app settings.py .env*
rg -n --glob '!**/*.md' "api/mock\\.py" app
```

更大范围后端变更应运行对应聚焦测试，必要时再执行：

```bash
uv run python -m compileall -q app core database scripts tests
```
