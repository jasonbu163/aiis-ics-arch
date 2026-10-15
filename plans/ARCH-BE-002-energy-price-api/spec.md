Task ID: ARCH-BE-002
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已明确批准 r3，一并修复旧测试并完成验证；交 Development 按 r3 修复单个既有测试文件、完成全部 r2/r3 验证并记录 handoff，随后 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 可复用能源价格 API 交付及完整 no_db 套件的现行公开配置断言兼容
Owner: aiis-ics-arch 公共 auxiliary 模块的能源单价切片
Related Task: ARCH-FE-002, ARCH-FE-003
Acceptance Chain Reference: ARCH-BE-002 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-13

# r3：仅迁移一项过时的公开配置测试断言

本 r3 在下方 r2 的实现、数据、权限、migration、风险和全部验收合同上，仅增补以下单个测试文件的
写入范围。r2 的批准与完整原文保留；r3 批准以本次 Human Owner 明确回复为依据，不要求重新批准既有三接口
业务方案。Development 已创建 tasks.md，记录 `in_progress` 和完整 no_db 的测试失败；尚未交接，
尚无 QA checklist.md，不能记录 QA 或最终通过。

## 失败依据与最小修复

Development 报告在 r2 必需的完整 `uv run pytest -q -m no_db` 中遇到既有 baseline failure。
PM 只读核对 [test_monitor_frontend_permissions.py](../../backend/tests/test_monitor_frontend_permissions.py)
及 `git show HEAD`，确认该测试当前与 HEAD 均读取 `VITE_ROLE_PAGE_ACCESS_JSON` 并要求 `{}`；
但两个公开前端示例在 HEAD 与当前工作树均已使用 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]'` 和
`VITE_OPERATOR_PAGE_ACCESS_JSON='[]'`。旧 helper 必然在缺少旧 key 时抛出
`AssertionError: ... is missing VITE_ROLE_PAGE_ACCESS_JSON`。这是测试与已接受前端配置合同的漂移，
不是能源价格实现需要恢复旧配置。PM 没有运行项目测试或改实现，不虚构 DEV 退出码 / 通过数量。

## R3-001：精确新增 allowlist

仅增加 `backend/tests/test_monitor_frontend_permissions.py`，允许把旧对象读取 / `{}` 断言迁移为
现行 supervisor / operator 两数组；保留 `pytestmark = pytest.mark.no_db`、两份公开模板覆盖及
“公开模板默认不授予项目页面访问”的原测试目标：

| 文件 / 情形 | 必需断言 |
| --- | --- |
| `frontend-js/.env.example` | 两新 key 均存在，各自 JSON 能解析为 list，且分别等于 `[]`。 |
| `frontend-js/.env.docker.dev.example` | 同上，不能只测 host example。 |
| 退役合同 / 项目授权 | 不依赖或回退到旧 role 对象；缺新 key、非法 JSON、错误类型或任一非空 grant 均使测试失败；保留对 `monitor.realtime` 不获公开默认授权的覆盖。可断言无活动旧 key。 |

文件读取仍仅限这两份公开 example，不读取真实 `.env*`、进程环境或运行配置；不安装 dotenv 或任何
新依赖。helper / 测试命名可随现行两数组含义作必要调整；不重构其他测试，不增改 frontend source、
example 值、真实 env、权限策略、业务源码、migration、配置或依赖。

该单文件新增与 r2 全部 allowlist 合并后才是 r3 实施面。r2 内原有 Development 任务文档路径继续
有效，批准后由 Development 在其 tasks 中如实记录 r2 failure、r3 新增改动及精确 Revision handoff；
禁止因 r3 草案提前写入此测试或将原失败记录为通过。若发现其他范围外失败，继续给出具体证据回 PM。

## r3 验收、风险与批准 gate

- AC-r2-001..005 完整保留；新增 AC-r3-001：两个公开 example 的 supervisor / operator 空数组和
  无项目默认授权断言通过，该测试保留 no_db 标记，不出现旧 key fallback / skip / xfail。
- 在与 r2 相同的公开隔离源码 fixture 中，先运行该单文件，再运行完整 `uv run pytest -q -m no_db`，
  记录真实命令 / 退出码；不能删除测试、缩小套件、只跑能源用例或降低 AC-r2-005 以绕过失败。
  fixture 仅需携带两份已公开 example；不携带任何真实前端 env。
- AC-r3-002：相对 r2 实施基线，额外 diff 只在该测试文件；当前前端 source / env、BE003、旧 Core
  root、其他任务与工作树改动受保护。r1/r2 历史原文完整保留，Development self-check 仍非独立 QA。
  fresh-context Verification 最终验证 r3 完整交付与上述新增项，不只验证一项测试修复。

风险仅为错误地把公开配置测试迁移变成实际授权变更；以零 env / source 增量、两角色空数组严格断言
和差异审计控制。运行 / 数据库 deferred gate 沿用 r2，未新增操作授权。

2026-10-13：PM 只读确认后形成 ARCH-BE-002 r3 draft。主协调者仅需向 Human Owner 提交本单文件
测试断言迁移的范围批准；待其明确批准，PM 记录决定再交 Development。适用 `project-governance`，
技术验证继续使用 `backend-arch`；无需新增前端 / env 实施、API 方案讨论或独立测试依赖。

2026-10-13：主协调者传递 Human Owner 明确回复“批准 r3，一并修复旧测试并完成验证”。据此将
本精确 r3 状态记录为 `owner_approved`，范围、allowlist、验收和风险保持上述原合同，交 Development
修复旧测试并完成完整验证后交 fresh-context Verification。此批准不等于 QA 结论、Human Owner
最终验收或运行 / 数据库操作授权。

# r2 历史批准规格（以下原文完整保留）

Task ID: ARCH-BE-002
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准 BE002 进入 Development，并明确在当前 aiis-ics-arch 实施可复用业务模块及同步边界；交 Development 按 r2 实施并创建 tasks.md，随后 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 可复用能源单价当前值、历史查询与追加保存的后端模块
Owner: aiis-ics-arch 公共 auxiliary 模块的能源单价切片
Related Task: ARCH-FE-003
Acceptance Chain Reference: ARCH-BE-002 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-13

# r2 实施范围与批准依据

本节为当前 r2 范围权威，下方 r1 草案原文完整保留。2026-10-13，Human Owner 明确“批准 be002进入dev”，
并在主协调者说明 r1 尚缺目标仓库 / 公共模块边界后，答复“在当前 aiis-ics-arch 实施，并同步明确可复用
业务模块边界”。r2 据这两项真实授权，将原 r1 三接口方向、推荐规则与必要源码 / 文档清单具体化，
记录为 `owner_approved`；不把最初只批准写草案的历史改写为当时已批准实现，也不推断最终验收。

目标工作树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`。新增 `backend/app/auxiliary/` 公共业务模块，
仅承载能源单价切片；`manifest.name="auxiliary"`、`enabled=True`、`order=60`，声明 router、models
和 `energy-price-read` / `energy-price-manage` 两权限。通过现有 Registry 注册三 API；不修改组合根
或增加第二份中央模块列表。源码注册不代表运行中服务已重载、真实数据库已迁移或已部署。

公共能力允许包含领域 Model / Schema / Service / CRUD 和可复用业务 API；客户特定数据、客户独有
规则 / 页面、真实工厂资源、配置、点表、输入、构建产物和密钥仍归消费项目。同步根 / backend / app
边界文档，明确辅助价格属于本轮获批公共模块，不因“业务”二字一概排除，也不将其他客户模块
顺带迁回。本任务不改变 BE003 草案或其状态，不重开通用架构迁移。

## R2-001：冻结三接口与序列化合同

| API（项目 prefix 仍为配置项） | HTTP 200 成功信封内的 data |
| --- | --- |
| GET `/energy/current` | 最新已保存 `PriceRecord`，无记录为 `null`；不返回默认价格、不写入 seed。 |
| GET `/energy?page=1&pageSize=10` | `{ items, total, page, pageSize }`；缺省 page=1、pageSize=20，page>=1、1<=pageSize<=100。无记录 / 越界页 items=[]，total 仍为实际记录数。 |
| POST `/energy` | 新增后完整 `PriceRecord`，一次原子追加三种价格及备注。 |

复用 `common/response.py` 的 `code:200/message:"success"/data` 信封和 `ApiSchema`；允许既有 timestamp
扩展。前端 request 已解包 data；维持分页顶层 fields，不加 `meta`，不改 facade / interceptor。
`PriceRecord` 为 `id`、`electricPrice`、`hydrogenPrice`、`argonPrice`、`electricRemark`、`hydrogenRemark`、
`argonRemark`、`remark`、`operator`、`createdAt`、`updatedAt`；后端内部 / ORM 保持 snake_case。
价格字段最终 JSON 必须为 number，包括 0；Decimal 转 number 限本模块输出 Schema，不能为了本模块
修改全局 serializer。日期沿用目标项目 ISO JSON 序列化；不增加时间格式或时区转换机制。

## R2-002：价格、备注与保存语义

- 三价格全部必填、有限、非负，范围 `0..999999.9999`，内部 / DB 使用 `Decimal` / `Numeric(10,4)`。
  兼容 JSON number 与能无损解析的十进制数字字符串；不接收 bool、空串、非数、null、NaN/Infinity。
  超出四位有效小数或范围返回现有 HTTP 422，不舍入、不截断、不补零；尾随零不改变数值的输入可接受。
  明确的 0 在输入、DB、current、history 和 JSON 输出中保留。
- 单位延续当前价格页：电价 CNY/kWh、氢气 / 氩气 CNY/Nm³，写入模块说明；本轮不新增币种、单位、
  税率、阶梯价或价格换算配置。无硬编码价格默认值，价格 DB 列为非空且不设置隐式业务默认值。
- `electricRemark` / `hydrogenRemark` / `argonRemark` 各最多 500 字符；汇总单数 `remark` 最多 2000
  字符，DB 使用 Text 并有长度约束或等价一致约束。备注可缺省 / null；空字符串归为 null，非空文本
  原样保留为该记录快照，不自动拼接或翻译。前端既有汇总 remark 可直接提交，不新增 `remarks`。
- POST 仅接收三价格和四备注；额外字段包括 id、operator、时间戳返回 HTTP 422，避免静默接受伪造
  元信息。operator 使用认证主体的 username 快照，服务端生成 id，数据库负责 created_at / updated_at；
  不建立新用户 / 角色平台，也不因本轮价格表修改 user 模型。
- 保存成功立即成为可查询历史，current / history 统一按 `created_at DESC, id DESC`。相同时间戳
  有稳定 id 次序；不编辑 / 删除旧记录，不新增生效日、并发覆盖检查或幂等 token。每个成功 POST
  独立追加一条记录；不把两次提交自动合并，亦不承诺并发翻页的全局快照。
- API -> `services/async_energy_price.py` -> `crud/async_energy_price.py` -> AsyncSession；CRUD 不提交，
  Service 控制 commit / rollback，失败无部分写入或伪成功。复用既有异常处理；不新增通用错误平台。
  保存事件记录 actor、record id 和结果，沿现有 JSON Lines 日志；不输出 token、完整请求体或备注。

## R2-003：权限与 schema 边界

两条 GET 仅要求 `energy-price-read`，POST 仅要求 `energy-price-manage`，每条均需现有认证。权限 key
彼此不隐含授予，旧 `auxiliary` key 也不映射为二者。admin 继续按已有 require_permissions guard；
supervisor / operator 及未知角色按现有策略，默认两数组仍不新增授权。测试 fixture 可显式配置角色
授予，保留 operator 原始配置是 supervisor 子集的规则。真实与 example env 均不改，前端 pageId 不
转化为 API grant。关闭模块后的 route / OpenAPI 缺失语义仍需以测试证明。

仅新增一张 `energy_prices` 表，持久化三价格、四备注、操作者和数据库时间；定义必要非负 / 上限 / 长度
约束及 created_at/id 查询索引，与 Schema 对齐。新增 Alembic revision `a6c8e0f2b4d6`，
`down_revision="d4e6f8a0b2c4"`，形成单 root、单 head；upgrade 只建本表及其索引 / 约束，downgrade
只删本表。本轮不改十四表历史 root 原文，也不改已有表或引入任何旧项目 migration。
原静态验收仍验证十四表 root 的操作 / metadata parity；另验证该后继 revision 加一表后，与完整
十五表 metadata 精确对应。不得删除 parity / downgrade / 禁止客户残留断言来使检查通过。

Registry、models import、API 组合 / 启动和 GET 都不得隐式执行 DDL / seed；不新增 Projection、
Worker、Redis、PLC、真实数据导入或价格默认记录。schema-maintenance 仍是通用显式入口，不添加价格
表专有处理；模型由现有 manifest model discovery 自动发现，不需要改其 Service 或 Alembic env。

## r2 精确写入 allowlist

Development 仅写以下文件；新目录中的文件清单不授权任意附加功能：

| 表面 | 允许文件及修改边界 |
| --- | --- |
| 公共模块入口 | `backend/app/auxiliary/__init__.py`、`manifest.py`；`api/models/schemas/crud/services/mocks/seeds` 七目录各自的 `__init__.py`，后两者只保留 import-safe package，不实现 mock / seed provider。 |
| 价格切片 | `backend/app/auxiliary/api/routes.py`（只聚合）、`api/energy_price.py`、`models/energy_price.py`、`schemas/energy_price.py`、`crud/async_energy_price.py`、`services/async_energy_price.py`。 |
| 模块说明与迭代入口 | `backend/app/auxiliary/README.md`、`README.zh-CN.md`、`PLAN.md`、`PLAN.zh-CN.md`、`plans/README.md`、`plans/README.zh-CN.md`；只链接根 BE002 的现有角色文档，不复制第二份 spec，不预建角色证据。 |
| 单表 migration | `backend/alembic/versions/20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py`。 |
| 新增聚焦测试 | `backend/tests/test_energy_price_api.py`、`test_energy_price_service.py`、`test_energy_price_migration.py`，均标注 no_db，不调用真实数据库 fixture。 |
| 必要既有预期 | `backend/tests/test_module_structure.py`、`test_module_registry.py`、`test_openapi_router_tags.py`、`test_celery_retirement.py`、`test_core_migration_baseline.py`；只同步 auxiliary 注册 / 包结构、三个 API、公共价格表后继 migration 的明确预期，保留其他客户模块及退役 runtime 禁止项。 |
| 公共 / 客户边界与索引 | `AGENTS.md`、根 `README.md` / `README.zh-CN.md`、`backend/README.md` / `README.zh-CN.md`、`backend/app/README.md` / `README.zh-CN.md`；只明确公共业务能力 / 客户专属边界、auxiliary 入口及十四表 root + 单表后继的事实，保留其余规则。`CODE_INDEX.md` 只加实际新增源码 / migration 入口。 |
| Development 事实 | `plans/ARCH-BE-002-energy-price-api/tasks.md`，只记录本 r2 实施、DEV self-check、增量 diff 和 handoff。 |

PM 仅写本 spec；Verification 在 developer_handoff 后创建 checklist。主协调者机械同步根 / backend
PLAN pairs 与根 plans catalog 的 BE002 行，其他条目和 BE003 未提交草案保留。Development 不借此修改
索引、其他角色文档、前端、env、组合根、shared common、权限 resolver、数据库基础设施、依赖 / lock、
Docker / CI / INITIALIZATION 或其他业务模块。若真实必需改动超出该清单，先报告证据并回 PM 定范围。

## r2 验收与源码验证闭环

| 标准 | 必需证据 |
| --- | --- |
| AC-r2-001 接口 | 三条实际 ASGI HTTP 路径 / 方法、camelCase 与共享信封通过；current null、空 / 越界列表、分页缺省与边界、价格 JSON number、0、Decimal serialization、备注快照和 server-owned extra 拒绝均有断言，匹配当前前端解包。 |
| AC-r2-002 保存 | 纯规则 / schema 边界含 0、四位小数、最大值与非法价格 / 备注负例；假 session 验证事务成功 / 失败、actor、回滚与无部分写入；真实 SQL statement 的无 DB 编译 / 断言验证稳定排序、分页及参数。不得把 stub 结果称为真实数据库持久化通过。 |
| AC-r2-003 权限 / 注册 | admin 现有行为、sup/op 独立 read/manage 的允许 / 拒绝、未知角色、未认证与 disabled 模块矩阵通过；真实 / example env 不变，源码 enabled 注册三个 API，demo 继续 disabled，其他模块公开面未扩大。 |
| AC-r2-004 Migration | 原 root 文件 hash 不变、十四表 parity / 原 downgrade 保留；新增 revision 实际操作经 recorder 与价格 Model / 完整 metadata 对照；单 root/head、offline upgrade/downgrade SQL、约束与索引通过，未改 schema-maintenance。 |
| AC-r2-005 交接 | 新聚焦 tests、完整 `uv run pytest -q -m no_db`、受影响 Python compileall、文档链接与 `git diff --check` 均通过；双语边界说明一致、增量 diff 限 allowlist、原 r1 与其他工作树改动保留，tasks 如实记录命令 / 退出码、限制与资源。fresh-context Verification 独立给出 verdict。 |

验证在 `/private/tmp/<BE002专属目录>` 的 backend 源码隔离副本执行，排除 `.env*`、logs、运行数据和
产物，使用公开占位配置及项目既有 uv / lockfile / 依赖；禁用 Projection / mock / bootstrap，不安装
Agent 辅助依赖。HTTP 测试使用 ASGITransport、认证 / session dependency overrides，不发真实网络请求；
只运行带 no_db 的项目测试，避免现有 autouse fixture 创建 / 清空 MySQL 测试库。Alembic heads/history
及 upgrade / downgrade `--sql` 仅离线生成到任务 tmp，不执行 online migration。

本轮可完成并验收的是源码、HTTP / Service 隔离合同和静态 / offline migration；真实 MySQL upgrade、
保存 / 查询、重启后现有前端联调与运行状态验证是明确 deferred operational gate，不是本轮必需却未获
授权的通过条件。Verification 按上述证据判定源码 verdict，并列清未验证运行面；不得宣称 live DB、
部署或生产就绪。运行真实 / 可丢弃 MySQL、Docker up/down/build、在线迁移和服务重启另行具体授权。

## r2 风险、回退与交接

新增 source manifest 已启用，未来真实 reload 会暴露路由；未迁移的数据库请求可能失败，因此运行
采用必须先准备 schema 再重启 / 联调。本轮不执行这些操作，也不验证现有进程的重载。新增权限不
自动授权 sup/op，现有前端可见价格页不等于后端能读写；operator 如需保存，由操作者另行显式配置。
DB downgrade 会丢掉价格历史，不作为投运后默认回退；源码回退仅处理本任务增量，数据回退 / 备份
和共享工作树资源删除须独立审查，不能 reset 他人文件。

Development 使用 `backend-arch`（响应、分层、迁移、Registry、认证、日志 / 测试）、
`project-governance` / `aiis`（公共模块边界与文档）、`code-document-indexer`。本轮 API message 沿用
稳定 success key，新增错误只用既有 HTTP / 校验语义；不新增展示文案或修改前端 locale。如需要新增
可见错误 key，再按 `i18n-workflow` 明确翻译 owner，不能顺手重构全局错误显示。
完成后 Development 交精确 r2、完整 tasks、当前 diff / 工作树和源码验证证据，主协调者实际启动
fresh-context Verification；只使用本节验收，不把下方 r1 待确认项继续当成新阻塞。

2026-10-13：Q-001 已由 Human Owner 明确当前仓库 / 可复用业务模块边界；Q-002..005 在其推进 BE002
实施的授权内，按原建议和现有前端 / 旧 Numeric(10,4) 兼容边界具体化为以上合同。无需再次请求同一
目标与开发批准。无最终验收、运行部署、真实 env / DB 操作或 BE003 实施授权；角色仍为 contract_only。

# r1 历史草案（以下原文完整保留）

Task ID: ARCH-BE-002
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending；仅形成后续后端范围草案，待 Human Owner 确认目标消费项目及业务规则，再提交精确实施 Revision 批准

Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 能源单价当前值、历史查询与新增记录的后端契约补齐
Owner: 消费项目的辅助管理 / 能源单价业务 owner，具体项目待 Human Owner 确认
Related Task: ARCH-FE-003
Acceptance Chain Reference: ARCH-BE-002 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-10
Updated: 2026-10-10

# 目标与当前授权

Human Owner 要求将价格问题衍生的后端调整另落 spec，并明确“后端先不动，当前只前端”。本 r1 只保存
后续范围、建议契约与待确认项；没有后端实现、模块启用、权限配置、数据库操作或部署授权。
本任务与 [ARCH-FE-003](../ARCH-FE-003-remaining-module-manifest-adaptation/spec.md) 是非阻塞关联；
该前端任务按自身获批 Revision 完成页面直接消费 auxiliary API，不以本任务完成为其构建 / 验收前提。
前端的隔离 stub 验证不代表这些后端 API 已存在或真实业务已经可用。

# 已核对的现状与归属

- 当前 [auxiliary API](../../frontend-js/src/app/auxiliary/api/index.js) 已声明 GET `/energy/current`、
  GET `/energy`、POST `/energy`；列表参数为 `page` / `pageSize`。完整 URL 由项目 API prefix 提供，
  公共示例为 `/api/v1`，不在模块里重复拼接 prefix。
- [价格页](../../frontend-js/src/app/auxiliary/views/price/index.vue) 使用三种价格、各项备注、汇总
  `remark`、历史 `createdAt` / `operator`。汇总字段是单数 `remark`，不另发明 `remarks` alias。
- [request 拦截器](../../frontend-js/src/utils/request.js) 已将成功信封解包为 `res.data`；页面 / facade
  消费业务对象或分页对象，不能再要求调用方重复解包或执行全局 snake/camel 转换。
- [后端 README](../../backend/README.zh-CN.md) 明确能源业务归消费项目模块。当前 Core 没有 energy
  模块或能源价格表，只有十四表 Core migration baseline；不得以修复前端为由恢复客户业务进 Core。
- 可只读参考旧源码 `/Users/jason/Desktop/DreamCode/vibe-l2-front-end/backend/app/energy/`。
  旧实现有 async 分层、`energy_prices`、`Numeric(10,4)`、`auxiliary` 权限与三条所需接口，但另有
  详情 / 删除 API、无记录时返回硬编码价格、仅按创建时间排序、写入字段默认补零。它是兼容分析材料，
  不是当前已批准业务规则，不整体复制旧模块、迁移链、默认价格、数据或权限。

后续建议将价格持久化和事务归消费项目 `backend/app/auxiliary/` 的能源价格切片，与前端业务 owner
对应；URL 保留 `/energy`。若目标项目已有独立 `app/energy` owner，可在确认其真实边界后沿用，
但一个价格表和事务只能有一个 owner，不同时建立两份实现。本仓库 r1 只承载待办规格；具体目标
仓库 / 目录确认之前不形成 Development 实现 allowlist，也不修改 Core 定位或十四表基线。

# 建议需求（待精确范围批准）

## R-001：仅交付三个接口

| 接口 | 成功业务 `data` | 行为 |
| --- | --- | --- |
| GET `/energy/current` | `PriceRecord` 或 `null` | 返回最新已保存记录；无记录建议返回 HTTP 200、`code: 200`、`data: null`，不写库、不伪造当前价格。 |
| GET `/energy?page=1&pageSize=10` | `{ items, total, page, pageSize }` | 建议缺省 page=1、pageSize=20，page>=1、1<=pageSize<=100；空结果 items=[]、total=0，越界页仍返回空列表和真实 total。 |
| POST `/energy` | 新建后的完整 `PriceRecord` | 一次提交三种价格及可选备注，原子新增一条历史记录；成功提交后该记录可被 current / history 读取。 |

成功响应使用目标项目现有共享 `code/message/data` 信封，兼容既有 timestamp 扩展；不增加第二套
响应基础设施。列表维持顶层 `items/total/page/pageSize`，不在本任务改成 `meta` 嵌套。
输入和输出 Schema 负责 alias；内部 / ORM / 数据库仍使用 snake_case。

`PriceRecord` 包含 `id`、`electricPrice`、`hydrogenPrice`、`argonPrice`、`electricRemark`、
`hydrogenRemark`、`argonRemark`、`remark`、`operator`、`createdAt`、`updatedAt`。
POST 输入仅含三价格和四备注；id、operator、时间来自服务端。operator 从认证主体取得，客户端不能
伪造操作者。三个价格建议输出 JSON number，内部使用精确 Decimal / Numeric；最终 wire 类型及
精度政策须按下方 Q-002 冻结，并验证共享响应序列化后的实际 JSON，不能只看 Schema 注解。

## R-002：零值、校验与历史一致性

- 明确提交的 0 是有效价格，保存 / 读取 / 序列化均保留，不使用 truthiness 回退到默认价格。
  三个价格建议均为必填、有限、非负数；缺失、null、负值、非数、NaN/Infinity 不静默补零或落库。
- 价格 scale、最大值、超精度是拒绝还是舍入、数字字符串兼容、备注长度与空字符串归一化按
  Q-002/Q-003 确认；API 与 DB 约束一致，校验失败不产生部分记录。
- 保存建议采用追加历史；current 与 history 使用同一稳定顺序 `createdAt DESC, id DESC`，相同
  时间戳时仍可唯一确定最新记录。数据库负责持久化系统时间；不由浏览器提供保存时间或硬编码时区。
- Schema 校验失败遵循目标项目现有 HTTP 422 合同；需要业务失败时走统一 BusinessException / 稳定
  errorCode，认证 / 权限 / 系统异常保留现有 HTTP 语义。不把自然语言 message 当客户端判断依据。

## R-003：权限、Registry 与迁移

- 三接口均需认证及显式后端权限，页面 pageId 与 API permission 独立。旧 `auxiliary` 同时覆盖读写
  仅作参考；是否保留该 key 或拆分读写、哪些角色获准保存，由 Q-004 决定，不自动给任何角色加权。
- 复用目标项目现有 admin / supervisor / operator 策略及 operator 子集约束；无权请求不读写价格。
  普通 manifest 只声明 router / model / permission 元数据；disabled 不挂载 route / OpenAPI，
  model metadata 可导入但不创建表。模块开关不是进程内热卸载，启用 / 重启另行授权。
- 持久化模型、Schema 与显式 Alembic revision 同步。接续目标项目现有 migration head，不改写
  本仓库已接受 Core root、不复制其他项目历史、不用 create_all / stamp 代替迁移。import、启动、
  current 查询及 Registry 不得执行 DDL、seed 或默认价格写入。
- API 使用 async Service -> async CRUD -> AsyncSession，Service 持有事务；不引入 Worker、
  Projection、PLC 轮询、缓存或外部设备依赖。日志沿用项目 JSON Lines，保存记录 actor / record id
  与结果，失败可追溯，不输出 token、连接串或完整备注 / 请求体。

# 验收标准与隔离边界

| 标准 | 后续 Development / 独立 Verification 必需证据 |
| --- | --- |
| AC-001 契约 | 三接口真实 HTTP 序列化合同、POST camelCase 输入、record/list camelCase 输出、成功信封及既有前端解包方式匹配；无记录返回、零值、分页边界均有断言。 |
| AC-002 数据一致性 | 追加保存后 current / history 一致；同时间戳稳定顺序；非法输入 / 事务失败无部分写入；operator 不能由请求体伪造；精度边界按最终批准规则通过。 |
| AC-003 权限与模块 | 未认证、未授权、获权各角色及 disabled 模块矩阵通过；权限 key / role grants 与批准结果一致，未修改真实 env 或给前端页面授权赋予后端权力。 |
| AC-004 Schema | Model / Schema / migration 一致；head 图、upgrade / downgrade 的静态 / offline SQL 检查通过；无 import / 启动隐式 DDL / seed，Core 基线未被改写。 |
| AC-005 独立交接 | Development 记录精确批准 Revision、文件增量 diff、实际命令 / 退出码及限制；fresh-context Verification 独立复核并记录 verdict，最终验收由 Human Owner 决定。 |

默认源码验证用项目 uv / lockfile、`no_db` 测试、dependency override / 假 session 和占位配置，
不加载真实 `.env`、不连接现有数据库。上述测试只证明源码合同；真实 SQL 持久化及 migration
upgrade / downgrade 的运行证据需要另行批准、唯一标识的可丢弃数据库目标和清理方案。`TESTING=True`
不是通用隔离保证，不以 SQLite 或 stub 结果宣称 MySQL / 现场库已验证。没有运行授权时，运行验证
保留为明确 gate，不得将缺少必需运行证据记为通过。Docker up/down/build、真实迁移和部署不在 r1 授权内。

# 待 Human Owner 确认与下一 gate

| 问题 | 建议及待确认决定 |
| --- | --- |
| Q-001 目标与归属 | 确认实际消费项目仓库、价格业务 owner，以及 auxiliary 切片或既有 energy owner；如果要将通用价格能力纳入本 Core，须另行批准架构定位变更。 |
| Q-002 金额 / 单位 | 建议三价格必填、0 有效、四位小数、JSON number；确认币种、计量单位、最大值、超精度拒绝 / 舍入及数字字符串兼容。旧 Numeric(10,4) 不自动成为新规则。 |
| Q-003 空值 / 备注 | 确认无记录返回 data:null；确认三项备注及汇总 remark 长度、空字符串策略和保存快照方式。旧默认价格不带入。 |
| Q-004 权限 | 确认读 / 写 key 与 supervisor / operator 矩阵；尤其确认保存是否需独立 manage key。admin 遵循目标项目既有 guard，不以本草案修改 Core 权限实现。 |
| Q-005 生效语义 | 建议保存后立即生效、追加历史、无编辑 / 删除；确认是否存在生效时间、并发覆盖检查或重复提交幂等要求。若有，先扩 Revision，不凭实现者推测。 |

五项确认后，PM 将目标仓库、精确文件 allowlist、最终业务规则和必需验证 gate 写入新 Revision，
交 Human Owner 范围批准；在此之前不启动 Development。本草案不要求暂停 ARCH-FE-003。

# 排除项、风险与回退

本 r1 写入面仅本 `spec.md`；PM 不创建 tasks/checklist 或修改索引。主协调者按草案状态机械同步索引。
后续范围不包含其他 auxiliary 功能、价格详情 / 编辑 / 删除、能耗采集与成本报表、旧库 / 历史数据
迁移、前端二次整改、Core 权限重构、依赖或 Docker 配置、启用服务、真实 DB / 设备操作、发布与部署。

主要风险是旧模块隐含默认价格和宽权限被当成新批准规则，以及 Decimal wire 类型、金额精度或空数据
处理与前端不一致；以确认项和最终 JSON 合同测试收敛。数据库 downgrade 可能删除新增历史记录，
不能作为已投运后的默认回退；实际回退须单独审查数据保留 / 备份及授权。本次文档草案可单独修订，
不撤销共享工作树中其他任务改动。

# Skill handoff 与批准历史

PM 使用 `project-governance`、`aiis`，只读参考 `backend-arch` 的响应、模块、权限与迁移边界。
后续 Development / Verification 必须使用 `backend-arch` 及其 RESPONSE_CONTRACT、LAYERS、
DATABASE_AND_MIGRATIONS、MODULE_REGISTRATION、AUTH_SECURITY、OPERATIONS_TESTING；新增展示错误 key
时按 `i18n-workflow` 约定稳定 key 与翻译 owner；真实结构变化按 `code-document-indexer` 同步索引。
只有获批新增脚本或 Docker 验证时再加载对应 skill，不预设这些工作已获授权。

2026-10-10：PM 依据“后端先不动、当前只前端、后端调整落 spec”的明确请求形成 ARCH-BE-002 r1 draft。
尚无本精确 Revision 的范围批准、Development / QA 证据或 Human Owner 最终验收。角色为 contract_only，
不宣称平台 ACL、自动强制路由或正式团队激活。
