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
