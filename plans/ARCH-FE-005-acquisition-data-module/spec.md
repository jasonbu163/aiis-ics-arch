Task ID: ARCH-FE-005
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development 执行已批准的 ARCH-FE-005 r2，按 v2 读合同与 ARCH-ACQ-002 并行
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: JavaScript Web 独立采集数据模块和授权原值查询
Owner: AIIS ICS Architecture JavaScript Frontend
Acceptance Chain Reference: 本规格第 5 至 7 节及 Development Lifecycle Workflow
Depends On: ARCH-BE-012 r4 的 v2 只读合同和现有 dev 独立功能证据
Related Task: ARCH-ACQ-001, ARCH-ACQ-002, ARCH-OBS-001, DAA-010
Created: 2026-11-10 Asia/Shanghai
Updated: 2026-11-10 Asia/Shanghai

# Web 采集数据模块

## 1. 目标与边界

本任务是[项目路线](../ARCH-ACQ-001-acquisition-data-coordination/spec.md)的第 3 项，由本会话协调，按自身范围批准、实施、独立核验与最终验收。为获准的维护人员提供独立一级菜单「采集数据」，下设「实时数据」和「采集历史」。页面读取后端保存的 PLC 原值，按 PLC、DB 和适用的原采集时间组织数据。业务侧设备实时状态和 `monitor` 过程监控按其设备、任务和指标合同管理。 [设备状态与过程监控设计](../ARCH-OBS-001-configuration-driven-equipment-monitoring/spec.md)

本任务范围为 Web 读取、页面授权装配、双语界面和本机列宽偏好。点位、采样设置和投递诊断归 DAA。SMA 接线、业务写入与查询、数据导出、Web 写入、原值保留维护及真实角色授权调整分别另立范围。旧 Projection、旧表和旧快照的清退由 ARCH-ACQ-002 管理。 [旧 Projection 清退](../ARCH-ACQ-002-legacy-projection-retirement/spec.md)

## 2. 开工依据与只读合同

Human Owner 已明确前端可与清退并行。精确 r2 获批后，页面开发和独立核验以 ARCH-BE-012 r4 的 `plc-facts/v2` 读合同及现有 dev 的独立功能证据为依据。Web 开工、独立 QA 和页面交付验收无需等待清退、DAA 上报或 ARCH-BE-012 整体终验。dev 已用合成 `PLC-BE012-DEV-441247C3 / DB21` 通过四条读取检查，核对了 `820.5` 和 `false` 的逐点最新值、序号 `102` 与 `101` 的历史及完整样本详情。ARCH-BE-012 r4 整体仍为 `qa_blocked`，原隔离矩阵和 Human Owner 最终验收待完成。 [后端 r4 规格](../ARCH-BE-012-simplified-plc-facts/spec.md) · [dev 独立功能证据](../ARCH-BE-012-simplified-plc-facts/checklist.md#独立-verification现有-dev-功能验收)

四个浏览器接口均用已有登录 Bearer，成功响应由共享请求设施解包 `code / message / data`。沿用 `/api/v1` 默认 base，facade 使用 `/acquisition-data/...` 相对路径，按下列字段消费，不作大小写转换。 [v2 OpenAPI](../../contracts/published/http-api/plc-facts-v2/openapi.json) · [读接口 Schema](../../backend/app/plc_facts/schemas/v2.py)

| HTTP 接口 | 请求与页面使用的 `data` |
| --- | --- |
| `GET /api/v1/acquisition-data/options` | 无查询参数。`items` 包含 `plcId` 和 `dbNumbers`，提供当前角色可读 PLC/DB 选项。 |
| `GET /api/v1/acquisition-data/latest` | `plcId`、`dbNumber` 必填。`items` 按 `pointId` 排序，消费 `pointId`、`name`、`dataType`、`value`、`quality`、`reason`、`observedAt`。 |
| `GET /api/v1/acquisition-data/history` | `plcId`、`dbNumber`、`from`、`to` 必填。区间 `[from,to)`，`to > from`，跨度最多 7 天。`page` 从 1 开始，`pageSize` 默认 50、上限 100。返回 `items / total / page / pageSize / totalPages`。摘要使用 `id`、`sampleId`、`groupId`、`sampledAt`、`pointCount`，保持后端 `sampledAt` 降序及同时间 `id` 降序。 |
| `GET /api/v1/acquisition-data/history/{id}` | `id` 为摘要返回的正整数十进制字符串，保持字符串精度。返回摘要及 `points`，展示完整样本的点名、标识、类型、值、质量、原因与各点 `observedAt`。 |

**后续正式联调。** 在 DAA-010 获准交付新版上报且联合验证另获批准后，使用受控 DAA 样本对账 DAA 发送、后端接收与页面读取。证据包括候选版本、稳定样本身份、点位、原值、质量、采集时间及 latest/history 结果。该记录独立于本任务的合成 fixture 和 dev 冒烟，由相应联调任务与根路线跟踪。DAA-010 的交接及实施仍由主-DAA 按本身的门禁协调。 [DAA-010 上报改造](../../automation-world/data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md)

## 3. 需求

**R01 模块装配。** 使用 `frontend-js/src/app/acquisition-data/manifest.js` 和 `acquisition-data` 双语 namespace。Registry 装配启用的静态模块，组 `order=100`，两个叶页的 `navigation.order` 分别为 10、20。沿用两级导航、标题、默认入口与路由守卫，保留既有已授权默认入口的优先级。

| 页面 | URL | route name | `meta.pageId` |
| --- | --- | --- | --- |
| 实时数据 / Realtime Data | `/acquisition-data/realtime` | `AcquisitionDataRealtime` | `acquisition-data.realtime` |
| 采集历史 / Acquisition History | `/acquisition-data/history` | `AcquisitionDataHistory` | `acquisition-data.history` |

**R02 登录和两层授权。** 当前登录响应 `data.user` 提供 `id`、`username`、`name` 和 `role`。页面访问沿用 admin 内置权限和 `VITE_SUPERVISOR_PAGE_ACCESS_JSON`、`VITE_OPERATOR_PAGE_ACCESS_JSON` 的显式叶页 grant。无可访问叶页时隐藏模块菜单，未登录沿用登录跳转。业务页 grant 与采集页 grant 分别管理。后端独立判定 `plc-facts-read` 与 v2 `readScopes`，admin 豁免权限键，仍须有对应 PLC/DB 读范围。前端消费后端结果，`apiPermission` 不属于登录或页面访问合同。无效会话为 401 并走现有登录跳转。已登录但缺接口权限、或列表查询 PLC/DB 越范围为 403。合法账号的空读范围返回空选项。不存在、到期或越范围的样本详情统一为 404。实际发放角色权限另行批准。 [登录实现](../../backend/app/user/api/v1/auth.py) · [项目页面授权](../../frontend-js/README.zh-CN.md#项目页面配置)

**R03 数据来源和查询状态。** 两页只通过模块 facade 使用四个 v2 读接口。DB 选项随 PLC 取自 `options`，更换 PLC 时清除旧 DB、列表和详情。更换 DB 或查询区间时重置页码、清除旧结果及详情。切换、权限失效或离开页面后的迟到响应不得复写当前状态。区分未选、加载、空结果、无权限、详情不可用和查询失败，清除不可继续展示的数据并可按有效条件重试。错误在模块内本地化，保持共享认证行为。交付使用正常 HTTP 路径，测试 fixture 仅在隔离验证中使用。旧 raw/latest、机器写入接口和业务 API 不作为数据源。

**R04 实时数据。** 选定 PLC 和 DB 后查询逐点最新值，支持在当前结果中按点名或 `pointId` 查找和手动刷新。表中展示点名（缺省使用 `pointId`）、稳定点位标识、类型、原值、质量与点采集时间。沿用浏览器的 JSON 标量语义，保留 `0`、`false` 和合法空字符串。`quality=bad` 且 `reason=missing` 显示缺测，其余 `bad` 显示坏质量。缺失或不可解析的时间显示缺失状态。`latest` 的当前代次及有效期由后端裁定。首版用 `observedAt` 交代采集时刻，在线或陈旧分级需另有采集周期与新鲜度合同。请求由有效选择和手动刷新触发。

**R05 采集历史。** 按 PLC、DB 和上海采集时间区间查询，初始区间为进入页面时最近 24 小时，默认每页 50 条。保留用户提交的查询区间和后端稳定排序。每行对应一份 DB 样本，显示样本标识、`sampledAt`、采集组及点数。`sampledAt` 是样本中最晚的点采集时间。详情为本页只读视图，仅查询当前结果的样本 ID，展示同一份样本的组及完整点值、质量和 `observedAt`。保留期按后端时钟裁定，页面提示原值最多保留三个上海自然月，查询可见性会在物理清除上限前 24 小时截止，样本以点集中最早截止为准。查询无记录显示空态，详情 404 显示通用不可用提示。

**R06 时间、文案和列宽。** 公共时间工具以 `Asia/Shanghai` 解释输入，向 API 发送带 `+08:00` 的 RFC 3339。界面将后端时间以 `YYYY-MM-DD HH:mm:ss` 显示到秒并保留原始时间字符串。采集时间使用 `observedAt` 或 `sampledAt`，与 `storedAt` 及界面刷新时刻区分。业务文案和授权、失败提示均进入模块双语 locale。实时点位、历史样本和详情点位三张表共用列宽能力。普通数据列支持拖拽、最小宽度和横向滚动，特殊功能列可固定。按应用、表及稳定字段标识保存本机偏好，筛选、翻页、刷新、切页和重开后恢复。每张表可单独重置，失效字段使用默认宽度。沿用当前主题、通用组件和列表布局。 [项目契约](../../AGENTS.md)

## 4. 精确写入范围

以下文件为 r2 审批对象。模块内共用逻辑和详情组件按需拆分，其他新增文件或实质范围变化须由 PM 修订并重新批准。

| 表面 | 允许内容 |
| --- | --- |
| `frontend-js/src/app/acquisition-data/manifest.js`、`frontend-js/src/app/acquisition-data/api/index.js` | Registry 声明与四条只读调用。 |
| `frontend-js/src/app/acquisition-data/views/realtime/index.vue`、`frontend-js/src/app/acquisition-data/views/history/index.vue`、`frontend-js/src/app/acquisition-data/views/history/HistoryDetailDialog.vue`、`frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js` | 两个只读页、可按需拆出的历史详情和两页共用的范围查询。页面样式随组件。 |
| `frontend-js/src/app/acquisition-data/locales/zh-CN.json`、`frontend-js/src/app/acquisition-data/locales/en-US.json` | 对称的模块文案。 |
| `frontend-js/src/utils/date.js`、`frontend-js/src/utils/tableColumnWidths.js`、`frontend-js/src/utils/request.js` | 增加上海时间工具和共用列宽偏好。共享请求只允许按调用关闭全局错误提示以交由页面本地化，维持既有认证、解包和其他调用行为。 |
| `frontend-js/tests/module-registry/acquisition-data.test.mjs`、`CODE_INDEX.md` | 针对本模块的契约和行为回归，索引仅登记本任务新增关键源码。并行任务同时触及索引时由协调者顺序合并各自条目并复核 diff。 |
| `plans/ARCH-FE-005-acquisition-data-module/tasks.md`、`plans/ARCH-FE-005-acquisition-data-module/checklist.md` | Development 及 Verification 按各自门槛写入记录。 |

使用 Vue 3、JavaScript 和 `pnpm` 锁定工具链。现有 Registry、导航、路由守卫、角色配置源与登录机制作为消费依赖。真实 `.env`、权限策略、后端和合同、数据库操作、其他业务模块、包依赖、旧链源码及部署属于任务范围之外。Development 和 Verification 使用 `frontend-ui`、`i18n-workflow`，核对跨端字段、响应和权限时使用 `backend-arch` 的相关约定，实际源码结构变化按 `code-document-indexer` 登记。隔离浏览器 fixture、测试配置和构建产物放本任务临时目录，禁止将登录凭据写入证据。

## 5. 验收标准

| 编号 | 可核对结果 |
| --- | --- |
| AC01 装配与禁用 | 通过 Registry 核对一个组、两个叶页与稳定 pageId。验证原默认入口、只授予其中一页时的菜单与直达、模块禁用后退出菜单、路由、默认入口与文案，以及残留 grant 被校验拦截。 |
| AC02 双层权限 | 浏览器 fixture 覆盖未登录、失效会话、admin 有读范围及空读范围、非 admin 同时有页面 grant 和后端授权、仅有业务页 grant、只有采集页 grant 但无 API 权限，以及有 API 权限但无页面 grant。分别核对菜单、路由和后端拒绝的呈现。模拟越范围 PLC/DB 查询的 403 和越范围、到期及不存在详情的同一 404。实际后端鉴权证据按 AC06 核验。 |
| AC03 实时与切换 | 同一 DB 的正值、`0`、`false`、空串、缺测和坏质量各自正确展示。模拟缺失或异常时间，仍显示缺失状态。验证刷新保留原采集时刻。模拟快速切换 PLC/DB、重复刷新、权限失效及离页，迟到结果不会复现旧数据。 |
| AC04 历史与时间 | 核对初始窗口、后端分页、同时间样本顺序、字符串 ID（含超出 JS 安全整数的值）、`[from,to)`、7 天跨度边界、空结果、完整详情及到期行为。在 `Asia/Shanghai` 和 `America/Los_Angeles` 浏览器时区用相同条件核对请求及到秒显示，保留原采集时间与原精度。 |
| AC05 双语与列宽 | 中英文键结构对称，实际菜单、状态、错误与空态均可解析并切换。桌面和窄屏的日夜模式下控件与数据清晰可读。三张表调整宽度后在适用的筛选、翻页、刷新和重开时恢复，超宽横向滚动。单表重置与过时键回退正确。 |
| AC06 两类读取证据 | 独立浏览器 fixture 覆盖空、拒绝、迟到、异常及代表性值，记录合成数据和实际浏览器请求。关闭 mock，使用获准的 dev provider 与保留的模拟范围，独立核对 options、latest、history、详情的 HTTP 与页面结果，以及现有账号的授权和拒绝。验证接口失败无旧源回退。记录候选、请求、样例时间及脱敏结果。 |
| AC07 源码交付 | 在隔离的公开测试配置下通过 `pnpm check:modules`、`pnpm test:modules`、`pnpm build`。按第 4 节核对交付工作树范围、链接与实际入口，记录命令、环境、退出码及验证限制。 |

## 6. 风险、回退与待确认

- 两类浏览器验证均在无真实 `.env` 的隔离前端副本以 `pnpm dev --host 127.0.0.1` 启动。fixture 使用公开合成页授权配置，dev 冒烟关闭 mock 和演示账号，复用已有登录和保留样本，业务请求限四条读接口。取证时以 dev 独立功能记录中的采集区间为准。环境未就绪或原样本已不可用时先记录 AC06 的实际缺口，等待可读 dev 或另获准的同合同受控 provider。
- v2 dev 证据绑定 Alembic `2c4e6a8b0d12`。若清退候选推进 schema，后继目标的精确匹配及读合同兼容由 ARCH-ACQ-002 交接核验。切换后的 Web 冒烟使用已核验的同合同 provider。实际环境切换及授权变更另行批准。
- 后端合同或角色边界发生实质变化时暂停受影响的接入，交 PM 修订并重新批准。后端未就绪时显示查询失败。源码回退可沿用 manifest 禁用及重新构建，执行前核对活跃角色 grant，按项目正常发布边界处理。

## 7. 批准与交接

| Revision | 日期（上海） | 记录 |
| --- | --- | --- |
| r1 | 2026-11-10 | 起草两页范围，计划等待后端读合同交接并以 DAA 样本做正式链路验收。未获范围批准。 |
| r2 | 2026-11-10 | 依据 Human Owner「前端部分也可以一起并行做了」调整顺序，以 dev 已验证的 v2 读面作为开工依据，固定字段、权限、文件范围及页面验收，正式联调后续单列。 |

### 7.1 r2 范围批准

Human Owner 于 2026-11-10（Asia/Shanghai）批准 `ARCH-FE-005 r2` 精确实施范围。获批审阅稿的 SHA-256 为 `c51d27c11a54de2fa2ec0a031ddecff23ad6b01ccb4017b430fe68e2b7a3cbac`。

> 批准 ARCH-ACQ-002 r2 和 ARCH-FE-005 r2 实施。旧表清退和前端并行做，按规格用 Alembic 清退 dev 库的 9 张旧表，DAA 先不动。

Development 按本 Revision 实施并在 `tasks.md` 记录自检、工作树 diff、证据和资源收尾条件，交接精确候选。fresh-context Verification 在 `checklist.md` 分别登记页面 fixture、dev 实读和后续联调状态，再交 Human Owner 作页面交付最终验收。 [Development Lifecycle Workflow](../../.codex/workflows/development-lifecycle-workflow.md)
