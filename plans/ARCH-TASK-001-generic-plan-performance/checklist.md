Task ID: ARCH-TASK-001
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3 通过 r1 第三次精确交接的 AC10 共用列表布局复验。QA2 已关闭 QA-F01、QA-F02、QA-F03，Human Owner 最终验收待定。
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Acceptance Chain Reference: spec.md 第 9、10 节及 Development Lifecycle Workflow

# QA1 独立验证

2026-11-11 Asia/Shanghai。Verification 以 fresh context 接收精确 r1 handoff，独立读取根契约、作用域文档、角色 TOML、canonical workflow、任务 bundle、正式实现、候选 diff 和自检输出。使用 `project-governance`、`backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer` 核对交付，使用隔离 Playwright Chrome 实测页面。

正式交付为 HEAD `bcafa89fa31bdf62329bced89baebc193323a739` 上的未提交工作树。复算规格 SHA-256 为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`，交接记录为 `c838151c211e1a5b5dfb9705180e3c26210f706c78735f8ba108913038e943a9`。复算候选 manifest `3c0f74dc50845551daec07ad8f0958ec13a3324edf02b9dc3f392ea1f0200ba5`、patch `90a8aff9863c6bfef9571c33ac0b49e5dc84fb6e00fe721f48d08fff1b640cf6`。101 个实施路径与冻结清单、`tasks.md` 逐项 SHA-256 一致，范围外差异 0。反向 patch 仅以 `--check` 验证可匹配正式源码。工作树内另有其他任务的既存变更。 [批准规格](spec.md) · [Development handoff](tasks.md#developer_handoff--arch-task-001-r1) · [冻结 manifest](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/candidate-digests.json) · [冻结 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/approved-source-candidate.patch)

## 验收矩阵

| 条目 | QA1 结果 | 独立证据 |
| --- | --- | --- |
| AC01 迁移和模型 | 通过 | 对照获批的一次实际迁移 journal、退出 0、前驱 `4e6a8b0d2f14` 与新 head `5f7a9c1e3b25`。在同一 dev 只读事务复核 MySQL 8.4.6、3307、服务器身份摘要、上海偏移 +28800 秒与唯一 head。迁移前 19 张旧表皆空，21 个组内 FK、组外 0。6 张新表及 50 张保留表当前 DDL 共 56 项对账一致。用 MySQL 方言核对六个 ORM 表体及六条显式索引与迁移定义相符，旧表退出模型注册，独立质量模型保留。迁移前后 11 个保护表数据摘要、13 个行数一致。当前重查 9 个数据摘要仍一致，其余 2 个采集表含已批准的唯一合成样本。 |
| AC02 JSON 容量与并发 | 通过 | 两张主表各通过 SQL 默认空对象、两个 JSON 列各 100 值和 255 个四字节字符的往返。两个列各提交数组和 101 项对象，合计八次由 MySQL CHECK 拒绝，错误 3819。探针事务回滚后两表均 0 行。HTTP 拒绝非法字段和伪布尔，允许可空人工槽清空。两会话并发成功，保留自动速度 40 和人工 `false`。 |
| AC03 计划更新 | 通过 | 先建 B 后建 A。规范化重发为同一 ID、同创建与更新时间。部分更新只改订单号，重复不推进时间。无效字段、操作员写计划、写反馈槽以及领取后改订单分别拒绝，核对已存值和时间。 |
| AC04 领取 | 通过 | 两个独立请求并发，A 优先，仅一个 `claimed`，另一为 `target_busy`。同请求重试保留批次和冻结订单参数。已登记的第二目标和第二执行者复用同 ID 均为 409。空队列 `no_task`。同优先级验证先建先领，源码确认 SQL 最后以 ID 升序处理相同创建时间。 |
| AC05 批次和人工动作 | 通过 | A/B 回执使用各自原批次和序号 41/42。确认重复保持第一次时间且生产仍未上报，错序及旧批次 409。异常继续占用，主管核验后退回暂停，普通保存仍暂停，保存并恢复后领到新批次和更新后的冻结值。并发同一人工动作分别为 `applied` 与 `duplicate`，改原请求内容为 409。取消和核验动作证据逐项读回。 |
| AC06 角色与集成 | 通过 | 三类账号在临时 grants 下访问两列表和配置。未登录 401，8000 无相应 grants 的主管和操作员 403。独立进程分别只授 `plan`、只授 `performance`，补建均 403。操作员可写人工实绩，无法写计划、补建、读核验详情或保存配置。主管无法保存配置。未登记 MES、SMA 和 8000 关闭的三个集成查询拒绝。登记来源的合成集成请求免前端 token。混合越权包拒绝后原值和时间一致。 |
| AC07 实绩回写与原子性 | 通过 | A 12/11/重复 12/冲突 12 后先处理 B1，再补 A13。A 反馈 300→1200，目标保持 1200、速度 0、人工 `true`。B 反馈保持 50、人工 `false`。A14 为 `already_completed`，核对忽略报告前后全量详情和时间。独立 18001 注入故障发生在 MySQL 已执行 `performance_main` 第一条 DML 之后，响应 503 `task.unavailable`。S0-B 两侧详情、序号及更新时间完全一致，正常 18000 原包重试后才由序号 2/长度 60 更新为 3/61。 |
| AC08 无计划补建 | 通过 | S0-B/S1-B 使用不同 RUN。各先上报无计划、快照订单空，普通建计划 409。默认关闭与显式开启回填分别得到空反馈和 50，均为 `not_required`、绑定 v3 并保留 `running`。补建重试同一 ID，订单锁定、备注可编辑、无待领任务。序号 2 各回写 60，实绩仍只有原反馈槽。 |
| AC09 配置修订 | **失败，QA-F01** | 显示改名 v3/rev3→v3/rev4，两端共享；停用 v4/rev5 后旧 v3 继续回写，新 v4 拒绝停用槽；原槽恢复 v5/rev6。改已占用槽位及复用历史键被拒。过期请求的 HTTP 409 状态正确，跨业务版本的错误键与规格不符。 |
| AC10 列表和浏览器 | **失败，QA-F02、QA-F03** | 独立 Chrome 的三角色实际登录、默认页、详情、配置、英文、人工表单提交和权限均通过。浏览器置于纽约时区仍显示上海秒级时间。筛选、草稿、列宽刷新恢复和重置通过，实测 150→210→210 像素。API 分页次序及正常精确筛选通过。列表 API 接受无显式时区的数字字符串，且带尾随空格的目标键能命中同一记录。 |
| AC11 切换回归 | 通过 | 正常 8000 和 18000 的 16 条通用任务路径及引用 schema 与合同逐项一致。23 个保护方法均仍注册，旧入口族退出，六次旧路由直调为预期 404/405。独立质量 GET 200。既有合成 DAA 样本 seq 1 原包重放 200 `duplicate`，改内容 409，operator 可读最新 3 点和历史 1 条及详情，两个采集页面均发实际 HTTP 200。正常 8000 排除合成范围并读回原有 2 点。设备和监控的四条保护集成路径仍在，采用与写入保持既有关闭范围。 |
| AC12 检查与证据 | 已执行，产品判定见失败项 | 模块、模型、源码编译、定向单元、前端模块检查及构建均通过。独立 HTTP、MySQL、浏览器和一次事务中断证据已固化。复核迁移 journal、保护性前置核对与原空表恢复顺序，恢复步骤仅审阅。 |

## QA-F01 过期配置错误键

AC09 和规格 §6 要求管理员过期配置保存返回 `409 task.config_revision_conflict`。管理员在 v3/rev3 取得配置，另一提交先修改标签至 v3/rev4，再发布停用共享 03 的 v4/rev5。重放以下首次编辑请求。

```http
PUT /api/v1/task-field-configs
Content-Type: application/json

{"module":"plan","fieldConfigVersion":3,"configRevision":"3","changes":[{"scope":"shared_sync","slotNo":3,"labels":{"zh-CN":"合成生产米数","en-US":"QA metres produced"}}]}
```

实际为 HTTP 409、`code:409`、`data:null`、`errorCode:"task.field_version_conflict"`。同请求在 v3/rev4 时正确返回 `task.config_revision_conflict`。保存入口先比较业务版本，在比较管理员修订号前返回另一错误。请按规格复验两种过期条件。 [配置 Service](../../backend/app/task/services/async_fields.py#L104) · [HTTP 证据](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-http.json)

## QA-F02 创建时间筛选接受未带时区的数字字符串

AC10 和规格 §6 的时间参数要求显式携带时区，实际注册 OpenAPI 为 `date-time`。在正常验收 API 对 `GET /api/v1/plans` 与 `GET /api/v1/performances` 发送下表请求。均携带相同管理员 token 和 `taskNo=GT1-QA92A69E81-A`。请复验两模块的两个时间参数保持同一边界。

| 参数值 | 两模块实际结果 |
| --- | --- |
| `createdFrom=2026-11-11T15:19:58.000000+08:00` | 200，`total=1`，加号经 URL 编码 |
| `createdFrom=2026-11-11T07:19:58.000000Z` | 200，`total=1` |
| `createdFrom=1794381599` 或 `createdTo=1794381599` | 均 200，分别 `total=0` 和 `total=1` |
| `createdFrom=2026-11-11T15:19:59` 或同值 `createdTo` | 均 422 `task.invalid_request` |

路由先把原始 query 交给 datetime coercion，后续上海转换只看到已解析的日期。补充观察为带 `+08:00` 的七位小数秒 `2026-11-11T15:19:59.1234567+08:00` 也返回 200，结果与六位 `.123456` 相同。规格规定保留最多六位，本项 verdict 依据无显式时区的数字输入。 [计划列表路由](../../backend/app/plan/api/routes.py#L17) · [实绩列表路由](../../backend/app/performance/api/routes.py#L17) · [时间探针](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-time-filters.json) · [合法时区对照](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-filter-controls.json)

## QA-F03 列表目标键尾随空格仍匹配

AC10 及规格 R03/R04/R08 要求有效目标键、按原样精确匹配。在上述两条 GET 使用同一合成任务号，`targetKey=LINE-01` 与 `targetKey=LINE-01%20` 均返回 HTTP 200、`total=1`。小写 `line-01` 为 200、`total=0`。实际 schema 为 `ascii_bin`，列表将原始输入直接用于 SQL 等值查询，未应用任务目标标识校验。请复验尾空格不能命中记录。 [计划过滤](../../backend/app/plan/services/async_workflow.py#L170) · [实绩过滤](../../backend/app/performance/services/async_workflow.py#L48) · [目标键对照](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-filter-controls.json)

## 命令与环境

- macOS arm64，Python 3.13.3（项目 `backend/.venv`）、uv 0.7.8、Node v22.19.0、pnpm 11.11.0、独立 Chrome 157.0.8103.39。正式进程使用 8000/5190，合成验收使用回环 18000/15190。短期凭据仅进程内使用，QA 证据不保存凭据。Playwright CLI 离线缓存缺包，退出 1，复用本机已安装的 Playwright 模块驱动独立 Chrome，未访问共享浏览器。
- 以 `TESTING=True` 和合成 DB 端口 1 运行 `.venv/bin/python -B -m app.module_preflight --project-root . --check-only`、`.venv/bin/alembic heads`，退出 0。用 Python `compile()` 编译 60 个候选 Python 文件，MySQL 方言编译比较六张模型表及索引，退出 0。校对 234 个本地相对链接目标，未缺失。 `git diff --check` 与 `git apply --reverse --check <冻结 patch>` 退出 0。
- 同一无 DB 环境执行 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --basetemp=<QA 临时路径>/pytest-fixtures tests/test_generic_task_source.py tests/test_business_module_permissions.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_openapi_router_tags.py`，退出 0，124 passed、10 skipped。重跑显式提供独立 `/private/tmp` basetemp 及已保存的 ARCH-ACQ-002 历史公开 fixture、示例和 Git 根。两次早期结果分别为 122/10/2 和 123/10/1，失败是历史 runner 要求专用基目录及 C2 历史源码未显式配置。跳过项和 Development 记录的历史 QA3 私有导入规则冲突仍属其原历史验证面，本轮未宣称全量回归通过。
- `pnpm check:modules`、`pnpm test:modules`、`pnpm build --outDir <QA 临时目录>` 均退出 0。57 个模块测试通过，构建有 Vite 大 chunk 提示。使用两组空 grants、mock 关闭和本机 API 相对路径的构建配置。
- 在正式 backend 工作目录运行项目 `.venv/bin/python -B` 调用 QA 临时脚本 `workflow_probe.py`、`db_probe.py`、`fault_probe.py`、`run_browser.py`、`regression_probe.py`。主 HTTP 探针实际 153 请求并以 1 退出，对应 QA-F01。DB、故障、浏览器、回归均退出 0。浏览器记录 49 个 API 响应，旧路由及采集回归另记录 16 次 HTTP。两个补充只读探针合计 26 次 GET，见 QA-F02、QA-F03。DB 读证据归一化 `SHOW CREATE TABLE` 的自增计数后比较，保留结构检查。运行时验证无重新迁移，故障注入无真实 PLC 或网络断连。
- 证据保存在本机 ignored 目录 `backend/data/maintenance-evidence/arch-task-001-r1-dev3307/`。迁移 journal SHA-256 `ae208eb864fbc09a12d81646907d14775dd18e1783991279461643bf0d2d39b7` 已与操作记录核对。 [实际切换](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/operation.json) · [迁移 journal](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/alembic-upgrade.log) · [MySQL 对账和容量](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-db.json) · [事务及缺授予](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-transaction.json) · [浏览器](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-browser.json) · [受保护路由和采集](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/QA92A69E81-verification-regressions.json)

## 合成资源与交接

QA1 合成任务号为 `GT1-QA92A69E81-A`、`GT1-QA92A69E81-B`、`GT1-QA92A69E81S0-B`、`GT1-QA92A69E81S1-B`、`GT1-QA92A69E81X-A`、`GT1-QA92A69E81X-B`、`GT1-QA92A69E81N-A`。对应计划 7、实绩 5、批次 4、人工动作 4。字段配置从空 v1/rev1 开始，最终 v5/rev6，v2/v3/v4/v5 分别含 4/6/6/6 定义。故障重试后 S0-B 为序号 3、长度 61。浏览器仅在 B 写入 QA 备注，管理员保存为无变化。回滚探针 `GT1-QA92A69E81CAP-A` 确认 0 行。仅重放原 DAA 合成样本 `GT1-DEVFB8B5B-SAMPLE`、序号 1，历史 ID `5`，未创建新样本。

独立 Chrome 上下文、浏览器和两轮 18001 进程均已停止。QA 私有脚本和临时构建在 `/private/tmp/arch-task-001-r1-qa.L5elEI` 与 `/private/tmp/arch-task-001-r1-qa-build.pReIol`。协调者按已批准范围保留 QA1 合成记录和临时验收进程供返工复现，并在复验所需证据持久化后负责统一停写和精确清理。清理前需核对任务集合、字段版本及已登记采集身份。切换恢复继续依赖协调者保留的私有旧表 DDL、依赖顺序及配置备份。

QA1 verdict 为 **`qa_failed`**。QA-F01、QA-F02、QA-F03 为当前正式交付的可复现偏差，交协调者转回 Development。无独立环境 blocker。QA1 对受控现有 dev 的结果留给 Human Owner 最终验收。真实设备、DAA/SMA/CA/FF 联调、生产和长稳运行无本轮实证。Verification 仓库唯一写入为本 checklist。

## QA2 独立验证

2026-11-11 Asia/Shanghai。fresh-context Verification 独立核对根和相关模块契约、角色 TOML、canonical workflow、完整任务 bundle、正式源码、两次交接差异和可用测试证据。复验使用 `project-governance` 和 `backend-arch`，覆盖 r1 第二次交接的 API 返工、受保护入口、当前 schema 与合成数据。QA1 已通过且交付未变的浏览器及业务闭环证据继续有效。

正式工作树 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`。复算获批 `spec.md` SHA-256 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`、第二次交接 `tasks.md` SHA-256 `15d46e1f79f8688be601f746886e8367a85fac03152cbb9372bad3120992a60f`、更新前 QA1 checklist SHA-256 `a9e72c9e907c99e068b69301913481d5a5ff4889450d19b4587e8173abd18772`。QA1 正文自 `# QA1 独立验证` 起原字节 SHA-256 `5e18a63ce3610eec9645a91e58acf8ba67b6b85cd0a5a8f9d60fa2a0228d4823`，原文和历史 verdict 保留。

独立比对两次 manifest、累积 patch、10 份首轮源文件和当前正式工作树。101 个路径集合和正式文件摘要全部匹配，10 个后端文件有变化、91 个摘要不变。变化限列表参数及精确匹配、集成时间参数、配置修订冲突、manifest 导出及定向回归。第二次 manifest SHA-256 `5c8b9cda15bbca659100679abc01dc8819fd3b94e1fcd42e9b82215a534170c3`，patch SHA-256 `65814e55dc9d09549c15edd7861be14be8dce51030b2d8b4e077d537a321d96e`。 [第二次交接](tasks.md#第二次-developer_handoff--arch-task-001-r1) · [正式源码摘要](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source-digests.json) · [累积 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source.patch)

### 验收复核

| 验收项 | QA2 结论 | 证据 |
| --- | --- | --- |
| AC01 迁移与模型 | 通过 | 既有 `127.0.0.1:3307` 的只读事务确认服务器身份摘要、MySQL 8.4.6、上海时钟偏移 28800 秒、唯一已应用 `5f7a9c1e3b25`。读取六张任务表及 50 张保留表 `SHOW CREATE TABLE`，归一化自增计数后均与已核对的迁移后证据一致。源码 preflight 和 Alembic heads 通过。迁移执行证据沿用 QA1。 |
| AC02–AC08 | 通过 | 沿用 QA1 的容量及并发、计划更新、领取和批次动作、角色、实绩事务、两种补建路径证据。本轮重放 A 的真实回执与最终快照验证调整后的 API 仍按原时刻判定幂等，已完成后的序号 14 继续 `already_completed`。正常入口拒绝无授予人员和关闭的集成查询。 |
| AC09 配置修订 | 通过，QA-F01 关闭 | 计划和实绩管理员入口分别实测四组 `fieldConfigVersion`/`configRevision`。`3/"3"`、`4/"5"`、`5/"5"` 均 HTTP 409 `task.config_revision_conflict`，`4/"6"` 为 409 `task.field_version_conflict`。当前 `5/"6"` 空修改均 200。两页当前和 v3 配置完整 `data` 复核前后一致。QA1 的仅展示改名、业务发布、历史回写、恢复和冲突键证据保留。 |
| AC10 列表与浏览器 | 通过，QA-F02、QA-F03 关闭 | 两个列表四个时间参数的正负 epoch、无时区、七位小数、非法时区和尾随垃圾共 28 项均为 422 `task.invalid_request`。按 A 两侧实际 `createdAt` 测试 `+08:00` 和等价 `Z`，共 16 项，逐微秒核对起点含、终点不含。`LINE-01` 返回 A，`line-01` 为 200 空集，尾随空格、前导空格、控制字符、全角、空和超长共 14 项为 422。登录、默认页、筛选、角色、双语、列宽及草稿继续引用 QA1 的真实浏览器证据。Human Owner 后来提出的共用列表分段和时间提示位置由后续交接核验。 |
| AC11 切换回归 | 通过 | 正常 `8000` 及测试 `18000` 的运行 OpenAPI 均 HTTP 200，16 路径和 12 个引用 schema 与发布候选一致，原 23 个保护方法均在。正常质量和采集最新列表读取 200，三个退役入口直调 404，三个正常关闭的任务集成查询 403。已通过的采集样本重放、采集历史和浏览器回归沿用 QA1。 |
| AC12 检查与证据 | 通过 | 正式后端定向无库测试 130 passed、10 skipped。返工路径编译、模块 preflight、源码唯一 head、反向 patch 与空白检查均通过。实测 HTTP 和 MySQL 结果见本节。前端构建和恢复步骤保留 QA1 证据。 |

对模拟 CA/FF 回执 `ackObservedAt` 和 SMA `observedAt`、`startedAt`、`completedAt` 的 48 次非法字段探针均 HTTP 422 `task.invalid_request`。请求体探针覆盖 JSON 数字和字符串 epoch、缺时区、过精度及非法偏移。原 A 回执与序号 13 快照分别用 `+08:00`、等价 `Z` 重放，四次 HTTP 200 `duplicate`。在原 A 已完成的前提下，两种时区写法附显式 `startedAt` 重放序号 14，均 HTTP 200 `already_completed`。PLC 首次接收时间、实绩采样时间、序号、业务值、更新时间及四份字段配置的完整响应 `data` 均保持。A 的计划目标和反馈均为 1200、实绩速度 0、人工结果 `true`、序号 13。B 反馈 50、速度 40、人工结果 `false`、序号 3。MySQL 只读再次核对两单槽位文本以及 QA1 合成计数 7 计划、5 实绩、4 批次、4 动作。当前配置 v5/rev6，定义版本 v2/v3/v4/v5 分别为 4/6/6/6 条。

### 命令、限制与交接

- macOS 15.7.7 arm64，Python 3.13.3，uv 0.7.8。项目 `backend/.venv`，合成 API `18000`，正常 API `8000`，现有 dev MySQL `3307`。初次默认沙盒直连 loopback 被拒绝，经本机验证权限执行。初次 HTTP 探针把既有质量入口的信封套用任务接口 `timestamp` 断言，退出 1，收窄至任务入口后完整重跑退出 0。QA2 探针不改业务记录、配置或采集事实，不执行迁移，凭据不进入输出和任务文档。
- 正式 `backend/` 下，设置 `TESTING=True MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 PYTHONDONTWRITEBYTECODE=1`，执行 `.venv/bin/python -B -m app.module_preflight --project-root . --check-only` 与 `.venv/bin/python -B -m alembic heads`，均退出 0。`git diff --check`、`git apply --reverse --check backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff2-source.patch`、10 个返工 Python 文件的 `compile()` 与文本行尾检查均退出 0。
- 同一无 DB 环境使用 ARCH-ACQ-002 历史公开 backend、同源夹具目录和正式 `ARCH_BE005_REPOSITORY`，运行 `.venv/bin/python -B -m pytest -q -m no_db -p no:cacheprovider --basetemp=/private/tmp/arch-task-001-r1-qa2.ArBQRb/pytest tests/test_generic_task_source.py tests/test_business_module_permissions.py tests/test_business_integration_storage.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_openapi_router_tags.py --tb=short`，退出 0，130 passed、10 skipped，40.13 秒。全量回归和原历史 QA3 私有导入限制仍保留首次交接记录的边界。
- 正式 `backend/` 下分别执行 `.venv/bin/python -B /private/tmp/arch-task-001-r1-qa2.ArBQRb/http_recheck.py` 与 `.venv/bin/python -B /private/tmp/arch-task-001-r1-qa2.ArBQRb/schema_read.py`。前者独立实际 HTTP 166 次，56 次 200、8 次 409、90 次 422、2 次 401、7 次 403、3 次 404，见上方分项。后者 `SET TRANSACTION READ ONLY` 后执行版本、表 DDL 和合成标记的查询并回滚，退出 0。辅助脚本和脱敏请求摘要在该任务临时目录，验收结论及必要结果已固化在本清单。正式验收进程、夹具和独立证据由协调者按最终复核和清理安排接续。

QA2 对精确 r1 第二次交接的 verdict 为 **`qa_passed`**。QA-F01、QA-F02、QA-F03 已关闭，无 blocker。验收结果交 Human Owner。后续页面布局反馈仍需对应交接复核，最终验收待 Human Owner 决定。现场设备、DAA/SMA/CA/FF 原生联调、生产和长稳运行仍在本轮证据范围之外。Verification 在仓库中只更新本清单。

## QA3 独立验证

2026-11-11 Asia/Shanghai。Verification 以 fresh context 独立读取根契约、前端作用域文档、角色 TOML、canonical workflow、完整任务 bundle、正式源码、两次交接差异及 Development 测试输出。使用 `project-governance`、`frontend-ui`、`i18n-workflow`。本轮复验 r1 第三次交接的 AC10 共用列表布局及相关 AC12 前端检查。其他标准沿用 QA1 和 QA2 证据。

正式源码工作树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，交付范围未提交。复算 `spec.md` SHA-256 为 `bbaf4b2d47881f5db884b53846af47b40c11ad2a28dfb62015f40e624def83fa`，第三次交接 `tasks.md` 为 `e32b4495588b9af67917b6b0933c5eaec17aec1024f686d0fd571e9172ba8058`，更新前 QA2 checklist 为 `d90e366168a618bf11dd1e00ebb93598f8dfde8fffe269878ab066e3d7a58b06`。QA1 和 QA2 正文自 `# QA1 独立验证` 起的原字节 SHA-256 为 `47bb517a31e3546bbd938997c18b8662da27faa27b7ca030477111668d0f84df`，本次原样保留。

第三次 manifest SHA-256 为 `0c7bf1422c1e3638581af87ac1184bb7adba9a543dd01224b8ad3fc59f1a94e1`，累积 patch 为 `19703fb48d7df6b18e610b4d3e01240ba2b690bd103933460b549859235055da`。正式树与 manifest 101/101 路径摘要一致，路径集合与第二次交接相同，唯一变化为 `TaskPage.vue`，当前 SHA-256 `a7e6f0d63893190efa45af8bb1ceaa34764682e24ddad8dfbd6906d37416c748`。从两个累积 patch 重建该 SFC 对比，差异为标题帮助、筛选和分页布局及壳层留白。两个路由的入口继续共用该组件。`git apply --reverse --check` 和 `git diff --check` 均退出 0。 [第三次交接](tasks.md#第三次-developer_handoff--arch-task-001-r1-共用列表布局) · [正式源码摘要](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff3-source-digests.json) · [累积 patch](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/handoff3-source.patch)

### 验收复核

| 验收项 | QA3 结论 | 独立证据 |
| --- | --- | --- |
| AC10 三段与桌面紧凑布局 | 通过 | 在正式 `http://127.0.0.1:5190` 复核 `/plan/list`、`/performance/list`。`1280×900` 展开侧栏，中英文各页均为同一卡片内的标题与操作、独立筛选、表格与分页。两个分隔线可见，筛选四列横排，查询与重置靠右。筛选段高 164 px，表格自 y=325 开始。壳层顶部区域结束于 y=84，卡片从 y=92 开始。 |
| AC10 窄屏换行与壳层 | 通过 | `430×920` 经真实按钮收起侧栏后，两路由中英文筛选均为单列，输入和操作均在卡片及视口宽度内，查询与重置左对齐。卡片顶部 y=194，壳层顶部区域结束于 y=186。问号可命中，文档宽为 430 px，表格和分页分设横向滚动容器。 |
| AC10 双语时间提示 | 通过 | 两页分别使用各模块 `workflow.timeZone`，两模块各自的 83 个工作流键中英文顶层集合一致。使用真实壳层语言开关，两种视口共八组均验证标题旁问号、精确中文「业务时间：上海时间（UTC+08:00）」和英文「Business time: Shanghai (UTC+08:00)」。悬停时问号未获焦点，鼠标移开并确认提示消失后，通过 `Shift+Tab` 使问号进入 `:focus-visible`，提示再次出现，按 Esc 后消失。八组正文均无常驻时区说明。 |
| AC10 查询与重置 | 通过 | 登录响应 200，进入默认 `/plan/list`。两视口与两语言下，按 QA1 合成任务号查询，各页真实列表 GET 响应均 HTTP 200、`code=200`、`total=1`，对应行渲染。点击重置后任务号输入清空，后续 GET 不含 `taskNo`，计划、实绩分别回到 7 和 5 条。 |
| AC12 前端模块、构建及链接 | 通过 | 正式 `frontend-js/` 的 `pnpm check:modules`、`pnpm test:modules`、`pnpm build --outDir <QA3 临时目录>/dist` 均退出 0。57 passed、0 failed、0 skipped。保留两条测试夹具无活动实例的 `onBeforeUnmount` 警告和 Vite 大 chunk 提示。QA3 新增相对链接及目标标题存在。 |

### 命令、限制与交接

- 环境为 macOS 15.7.7 arm64、Node v22.19.0、pnpm 11.11.0、独立 Chrome 157.0.8103.39 与本机 Playwright `1.64.0-alpha-1789764292000`。初次默认沙盒的 loopback `curl` 退出 7，端口存在监听，经本机验证权限重试后 HTTP 200。浏览器探针由正式 `backend/` 的 `.venv/bin/python -B` 读取项目登录配置，经 stdin 传至 `node /private/tmp/arch-task-001-qa3.D5wkLU/browser.cjs <脱敏 JSON 路径>`，退出 0。只保存路径、聚合数量、提示和界面几何，浏览器 context 和进程已关闭。
- 浏览器记录 56 个 API GET 和一次登录 POST，应用页面异常与额外业务写请求均为 0。正常 `8000` / `5190` 服务未重启或改配，QA3 未调用临时验收端口。该轮使用已留存 QA1 夹具，只执行列表和配置读取，无任务、配置或采集写入，无迁移和清理。脱敏 JSON 的 SHA-256 为 `81fa407e757de814708de78888db7c0db96c538f65de43e94f6777aee7594ab7`，保存在本机 ignored 证据目录。 [独立浏览器证据](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/qa3-browser-layout.json)
- 前端检查使用 `pnpm_config_verify_deps_before_run=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' VITE_FRONTEND_MOCK_ENABLED=false VITE_API_BASE_URL=/api/v1`。构建和测试日志位于 `/private/tmp/arch-task-001-qa3-build.r9jZ8m`。两处 QA3 临时目录仅用于复查命令和构建日志，持久结果已写入本清单与本机证据，交协调者确认归属后回收。
- 独立浏览器复验结束后，协调者按已批准的范围清理合成夹具和临时验收进程。协调者证据记录 `18000` / `15190` 已停，常规 `8000` / `5190` 均为 HTTP 200，计划及实绩均为 0 条，字段配置回到 v1/rev1 且无字段定义。清理后 50 个保护表结构、11 个数据摘要、13 个行数对账通过，正常采集读取 2 点。 [进程收尾](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/acceptance-process-cleanup.json) · [清理后复核](../../backend/data/maintenance-evidence/arch-task-001-r1-dev3307/final-protected-runtime-check.json)
- 旧卷材报表及实绩打印入口在 r1 §7 R09 一次性切换中退役。该范围同时撤下旧报表依赖的 `print_records` 和旧实绩关系，通用报表重建另立范围。 [获批切换规格](spec.md#7-旧卷材一次性切换)

QA3 对精确 r1 第三次交接的 verdict 为 **`qa_passed`**，无 blocker。结果交 Human Owner 做最终验收。QA1 和 QA2 的历史限制继续适用，现场设备、DAA/SMA/CA/FF 原生联调、生产部署和长稳运行仍待对应范围验证。正式交付中 Verification 唯一更新为本清单。
