Task ID: ARCH-ENERGY-004
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 精确 r1 已进入正式工作树，交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-ENERGY-004 r1 实施与开发自检

依据 Human Owner 精确批准的 [r1 规格](spec.md)，SHA-256 为 `a186816d39c144dd91ceedceecdf69aab03e0cf74dd54f0fd71f5b2df8899702`。正式源码位置为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，叠加协调者已盘点的工作树变更。

## 实施

- `backend/app/equipment_observation/api/routes.py` 的原观测路由类按能耗路径设置文档标签。对三项免 Token 操作设置 `Public —` 标题，对九项管理员操作设置 `Management —` 标题。其余操作标题、原注册过程和路由处理函数保持原合同。
- `backend/app/energy/api/energy_price.py` 的三项能源单价操作使用同一 `Energy` 标签。
- `backend/tests/test_openapi_router_tags.py` 对现行能耗操作逐项校验标签、管理标题和认证，并查验非能耗操作无 `Energy` 标签。
- `contracts/published/http-api/energy-public-reads-v1/openapi.json` 与 `contracts/published/http-api/energy-registered-ingest-v1/openapi.json` 仅同步已批准的标签与标题元数据。

这五个文件是本次候选范围。旧 v2 发布工件及 ARCH-ENERGY-003 三文件的 SHA-256 与协调者记录的基线一致。

## Development 自检

| 验收点 | 实际验证 |
| --- | --- |
| AC01 能耗操作集中 | 生成完整 OpenAPI，核对 121 条路径、164 个操作，其中 21 个能耗操作各有且只有 `Energy` 标签。实际 Chrome 加载 FastAPI ASGI 生成的 Swagger 页面及 Swagger UI 官方脚本，DOM 见唯一 `Energy` 分组与 21 条不同方法／路径，3 个 Public 无授权锁、9 个 Management 有锁。相同 `/integration/energy/samples` 的 GET 和 POST 分别无锁及有锁。 |
| AC02 既有分组保留 | 仅归一获批的能耗标签／标题后，调整前后完整应用 OpenAPI 对象完全相等，浏览器仍显示原 `Equipment observation`。带冻结历史源的 C2 原入口测试通过，同时核验禁用 HR 入口。 |
| AC03 认证区分 | 新分组回归逐项对照匿名 GET、登记 POST、机器 Bearer 和 Web Bearer。既有无数据库 HTTP 回归覆盖公有查询、登记批次、旧机器发现与多表计写入、能耗单价的原权限。 |
| AC04 合同与快照 | OpenAPI 整体对照覆盖原方法、路径、operationId、参数、组件、认证和错误文档。发布两份快照逐方法对照实际标签／标题，归一这两个字段后与协调者保留的原快照相等。旧 v2 JSON 哈希检查成功。 |
| AC05 工程与交付 | 使用项目锁定 uv 环境运行聚焦测试及无数据库回归。所有变更路径直接进入正式工作树，未引入数据库结构调整。开发隔离结果与本机 dev 只读结果分别记录如下。 |

### 命令与实际结果

1. 在 `backend/` 设置 `MYSQL_HOST=127.0.0.1`、`MYSQL_PORT=1`，执行 `uv run --no-sync pytest -q -p no:cacheprovider -m no_db --basetemp=<本次临时目录>/pytest`，选择 `test_openapi_router_tags.py`、`test_energy_public_reads.py`、`test_energy_registered_ingest.py`、`test_energy_price_api.py`、`test_equipment_observation_r10_flow.py`、`test_role_api_permission_startup.py`。首轮退出 1，125 通过、2 失败，另有 1 项既有 SQLite 日期适配弃用提示。
   - 全局标签测试仍要求已退役的 `Quality - Defects`。使用 Git HEAD 的原测试期望及协调者变更前完整 OpenAPI 复核，缺少的唯一预期标签与候选相同。此项保留为已存在的基线失败。
   - C2 首轮缺少其要求的 `ARCH_ACQ002_HISTORICAL_BACKEND`。从删除旧 projection helper 之前的 Git 提交 `bcafa89fa31bdf62329bced89baebc193323a739` 通过 `git archive` 收集 `tests/module_admission_fixtures.py` 中七个 `CORE_PATCH` 文件到任务临时目录，设置该变量及 `ARCH_BE005_REPOSITORY` 后仅重跑 C2，1 通过，退出 0。
   - 使用上述 C2 夹具重跑前五个测试文件，以 `-k 'not test_openapi_contains_only_public_core_operation_tags'` 排除已复现的基线失败，102 通过、1 未选、1 项既有警告，退出 0。
2. 在 `backend/` 以相同无数据库环境运行 `uv run --no-sync python <本次临时目录>/compare.py <本次临时目录>`。以协调者生成的变更前 OpenAPI 校验完整语义差异，并逐操作校验两份发布快照。变更前后完整 OpenAPI SHA-256 分别为 `524ef2fc2c04d8727fcb159d3ff30d8ebf9b748498f21b74cfeceaba39f5cd0f` 与 `fed5a5acf06bd15a41c641989f1f13fce71340949d58447886d3cfa9496ba2f4`。
3. 由 `uv run --no-sync python <本次临时目录>/docs.py <本次临时目录>` 通过 HTTPX ASGITransport 读取隔离应用真实 `/docs` 与 `/openapi.json`。使用项目 FastAPI 默认引用的 jsDelivr Swagger UI v5 JS／CSS，Playwright 在真实 Chrome 中拦截文档、OpenAPI 与静态资源并从临时文件响应，阻止其他浏览器请求。以 1440 × 18000 视口使 Swagger 的虚拟列表完整渲染，`node <本次临时目录>/swagger.cjs <本次临时目录>` 退出 0。截取分组标题及前十项操作用于核对。JS／CSS SHA-256 分别为 `b164c5a22535e40dae08c00271674a67e437ec195098c55fcedf8ffac7ac3c88` 与 `7eb9f5a125e4bc9b3f0b71869b66d1a3d7c501f972f53d44ef91c2ae6c5bda5e`。
4. `git diff --check`、五个候选文件的 `shasum -a 256 -c`、已批准规格和本记录的本地链接校验均通过。Alembic 路径无本任务改动。

### 正式 dev 只读核对

协调者对现有本机 8000 服务自动重载后的端点执行只读核对。Swagger 文档和 OpenAPI 均为 HTTP 200，21 个能耗操作均属 `Energy`。两个免 Token GET 返回 200，`/energy/current` 匿名访问返回 401。OpenAPI 的同路径 GET 无安全方案，POST 仍为机器 Bearer。以上为协调者的实际 dev 观察，不替代独立验证。无真实 POST、数据库迁移或主动重启。

## 交接与临时资源

候选 SHA-256 清单位于 `/private/tmp/aiis-energy004-dev.0vqLRo/source.sha256`，清单摘要为 `76478f0a2ea57374490e3e5ea86184a5cebca4b22e29f9647be698b05d9a3cc5`。正式工作树当前已整合且尚未提交。基线快照、档案指纹及原有变更清单由协调者保存于 `/private/tmp/aiis-energy004-coordinator.T8EwPM/`。

Chrome 会话已关闭。ASGI 测试在进程内运行，Chrome 拦截全部测试页面请求，均无额外 HTTP 服务监听。保留 `/private/tmp/aiis-energy004-dev.0vqLRo/` 的日志、夹具、前后差异复验脚本、浏览器资源／截图与候选指纹，供 fresh-context Verification 查证。独立记录落盘且无需返工后由协调者回收。
