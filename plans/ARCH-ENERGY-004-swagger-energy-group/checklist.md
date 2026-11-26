Task ID: ARCH-ENERGY-004
Revision: r1
Status: owner_accepted
Handoff: Human Owner 已最终验收 ARCH-ENERGY-004 r1
Owner Role: Verification
Allowed Writers: Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 独立验证记录

2026-11-25，fresh-context Verification 在正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 独立消费 [规格](spec.md) 和 [开发交接](tasks.md)。HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，候选含未提交改动。以协调者冻结的变更前完整 OpenAPI 为比较基准。

| 验收点 | 实测证据 |
| --- | --- |
| AC01 | Chrome 独立会话实际渲染 FastAPI Swagger 的 164 个操作，只有一个 Energy 分组。21 个能耗方法与路径组合均唯一，包含精确 /energy 的 GET、POST。3 个 Public 标题无锁，9 个 Management 标题有锁。同路径 /integration/energy/samples 的 GET 无锁，POST 有锁。 |
| AC02 | 对 121 个路径生成完整 OpenAPI，仅还原获批的 21 个 tags 与 12 个 summary 后，整个文档与基线相等，覆盖全部非能耗操作及组件。Chrome 中 Equipment observation 组存在，旧单价组已消失。模块禁用及历史 C2 入口随回归执行。 |
| AC03 | 在完整应用 HTTPX ASGITransport 中逐项匿名发送全部 18 个受保护方法，16 个 Web HTTPBearer 与 2 个 ObservationMachineBearer 均返回 401。no_db 合成回归覆盖免 Token 的两条读取和登记 POST、机器鉴权及原有来源、表计和价格权限。 |
| AC04 | 在两个发布快照中逐方法对照实际应用 tags、summary，再还原这些字段，所得两个 JSON 对象分别与冻结前快照完全相等。完整应用对照也覆盖 operationId、security、请求响应及错误契约。旧 v2 SHA-256 为 cf1b37634557f534a933ea2142001fb14b01a47fb349b5205634c42c90857646，003 三文件指纹通过。 |
| AC05 | macOS、项目 uv 环境 Python 3.13.3。检查交接五文件指纹与正式源码，比对变更前 git status -uall 及既有 routes.py 补丁。在临时目录以 HEAD 与既有补丁还原该文件，审阅 ObservationRoute.__init__ 只设置展示标签，剔除该方法与标题关键字后前后 AST 相等。价格改动仅路由标签。无新增文件结构、前端、数据库迁移或运行配置变更。git diff --check、任务文档相对链接均通过。 |

## 可复核命令及摘要

- `shasum -a 256 -c source.sha256` 五项通过。spec、tasks、五文件清单的 SHA-256 依次为 `a186816d39c144dd91ceedceecdf69aab03e0cf74dd54f0fd71f5b2df8899702`、`a4ceeefaf6e39d9a9e3b151dda5d74a3e24124040c7e669a0cf019128e5a19c4`、`76478f0a2ea57374490e3e5ea86184a5cebca4b22e29f9647be698b05d9a3cc5`。
- 在 backend 运行 `uv run --no-sync python compare.py <QA临时目录>`、`uv run --no-sync python docs.py <QA临时目录>`。复核脚本后分别在本次 QA 目录重新生成结果，退出 0。完整 OpenAPI 前后 SHA-256 为 `524ef2fc2c04d8727fcb159d3ff30d8ebf9b748498f21b74cfeceaba39f5cd0f`、`fed5a5acf06bd15a41c641989f1f13fce71340949d58447886d3cfa9496ba2f4`。
- `node swagger.cjs <QA临时目录>`。沙箱内首次启动 Chrome 被中止，获准后独立运行退出 0。1440 × 18000 CSS 像素视口使完整列表渲染。Playwright 拦截全部浏览器请求，仅提供本次 ASGI 取得的 /docs、/openapi.json 及本地 Swagger v5 JS/CSS。
- 在 backend 设置 MYSQL_HOST=127.0.0.1、MYSQL_PORT=1，运行 `uv run --no-sync pytest -q -p no:cacheprovider -m no_db --basetemp=<QA临时目录>/pytest tests/{test_openapi_router_tags,test_energy_public_reads,test_energy_registered_ingest,test_energy_price_api,test_equipment_observation_r10_flow,test_role_api_permission_startup}.py`。以 git archive 单独从 bcafa89fa31bdf62329bced89baebc193323a739 取七个 CORE_PATCH 文件，ARCH_ACQ002_HISTORICAL_BACKEND 指向此目录，ARCH_BE005_REPOSITORY 指向正式源码。

六文件合计 126 通过（含 C2）、1 失败、1 项 SQLite 日期适配弃用警告，退出 1。失败项为 test_openapi_contains_only_public_core_operation_tags。分别取 Git HEAD 原测试配变更前完整 schema、候选测试配独立生成的 schema，两个组合的预期标签减实际标签均精确等于 {Quality - Defects}。此项属于既有测试基线偏差，任务内未发现新增失败。

## 结论与交接

AC01–AC05 通过，verdict 为 qa_passed，交 Human Owner 最终验收。正式源码已整合。本记录验证了隔离的 ASGI、Chrome 与合成 HTTP 行为；协调者另行只读观察本机 8000 dev 已加载 21 个 Energy 操作。生产部署、真实设备、真实数据库写入及迁移不在验证范围。

QA 独立临时目录 /private/tmp/energy004-qa.NzQTJp 已回收，Chrome 已关闭。开发目录 /private/tmp/aiis-energy004-dev.0vqLRo 与协调者目录 /private/tmp/aiis-energy004-coordinator.T8EwPM 由协调者在读取本记录及核验指纹后回收。

## Human Owner 最终验收

2026-11-25（Asia/Shanghai），Human Owner 明确确认「验收 ARCH-ENERGY-004 r1。」协调者已核实 QA 临时目录已回收，并完成 Development 与协调者临时目录回收。本次归档无新增临时资源。
