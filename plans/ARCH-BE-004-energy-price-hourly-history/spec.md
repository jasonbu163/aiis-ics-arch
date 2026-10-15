Task ID: ARCH-BE-004
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已明确批准 ARCH-BE-004 r2，固定上海时区、暂不允许未来时间并进入 dev；交 Development 按本精确范围实施并创建 tasks.md，随后 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: root
Capability: 带业务记录时间的小时能源价格整组更新、原路径按日查询与只读价格页新增弹窗
Owner: auxiliary 公共能源单价切片及其前端价格页
Depends On: ARCH-BE-002 r3 owner_accepted
Related Task: ARCH-FE-003
Acceptance Chain Reference: ARCH-BE-004 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-13
Updated: 2026-10-13

# r2 范围与状态

本节完整定义当前 r2 获批范围，取代 r1 关于新增 daily 路径、仅服务端当前小时保存、上方可编辑卡片、
dirty 刷新确认和保存后保留原选日的建议；下方 r1 原文完整保留为历史，不作为 r2 实施要求。
草案形成时 Human Owner 仅认可讨论并授权修订 spec；现已明确批准精确 r2 进入 Development，
状态记为 `owner_approved`，真实批准记录见本节末。
BE002 r3 的最终验收不变，BE003、其他任务和现有工作树改动受保护。

## R2-001 时间字段与三接口

保持现有 API prefix、三个路径 / 方法、共享成功信封 `code:200 / message:"success" / data`、原始
JSON number 精度解析和既有鉴权合同；不新增 `/energy/daily`、PUT、PATCH 或 DELETE。
JSON 继续 camelCase，数据库 / 内部继续 snake_case；前端 facade 消费 request 已解包的 data。

| 时间字段 | 含义与控制方 |
| --- | --- |
| observedAt / observed_at | 本次价格的业务记录时刻；POST 可传带时区 ISO 8601，省略或 null 时由 API 层取一次服务器当前时刻。保存为非空规范 UTC。 |
| hourStart / hour_start | observedAt 转业务时区后向下取整到小时的唯一桶键，持久化为 UTC；客户端不可直接写。 |
| createdAt / created_at | 小时行首次创建的数据库时间；同小时覆盖保留。 |
| updatedAt / updated_at | 最后一次成功写入该小时行的数据库时间；历史补录时可晚于 observedAt，不能用于判断 current。 |

一期业务时区固定 `Asia/Shanghai`，不新增 env 或改变全局 DB session / engine 时区。
对外四个时间字段均为带 offset 的 ISO 8601，推荐统一输出 `+08:00`；新表 created_at / updated_at
使用 UTC DB 时间表达式，服务端当前事件时刻使用 aware UTC，均在本模块转换。

业务归桶时区与 wire 的 offset 表示分开：按 IANA `Asia/Shanghai` 解释 picker 选中的民用时间并
确定真实瞬间，前端展示也按该命名时区；wire 仍可用互操作的 `+08:00` 或 UTC `Z` 表达同一瞬间，
不要求输出历史上海的实际 offset。转换不得改变瞬间或丢失秒精度，不能直接给任意历史民用值附
`+08:00`；早期含秒 offset 也不要求传给 JavaScript Date 解析。不新增年份限制或改变可录历史范围。

| API | r2 请求与 data 合同 |
| --- | --- |
| POST `/energy` | 三价格、三项备注、remark 沿用 PriceCreate，新增可选 observedAt。成功整组 upsert 后返回完整 HourlyPriceRecord，新增 / 覆盖均 HTTP 200。 |
| GET `/energy` | 新增可选 date=`YYYY-MM-DD`；保留 page / pageSize、默认 1/20、page>=1、size 1..100；返回 `{items,total,page,pageSize}`。date 存在时 total 为该日实际小时行数，缺省查询全历史。 |
| GET `/energy/current` | 在 observed_at<=本次服务器当前时刻的记录中，按 observed_at DESC、id DESC 取最近一组；没有符合记录返回 null。与 date / updated_at 无关。 |

HourlyPriceRecord 保留 BE002 的 id、三价格、三项备注、remark、operator、createdAt、updatedAt，
新增 observedAt、hourStart。三价格 JSON number 输出，0 有效；完整快照字段不能因覆盖而遗漏。
操作者仍取认证 username；请求禁止写入 id、operator、hourStart、createdAt、updatedAt。

observedAt 仅允许省略、null 或可解析的带时区 ISO 8601 字符串（Z / 显式 offset）；空串、无时区、
非法字符串、日期不存在、错误类型或无法持久化的时间返回 422，不回退为 now。
API 层对每次 POST 捕获一次服务器当前时刻：用于 observedAt 空值兜底及未来时刻校验；
传入 Service 后不得再次取 now 替换业务时间，事务竞争重试不得改变同一请求的小时归属。
前端清空 picker 应发送 null / 省略字段，不能发送空串。

date 缺省表示不过滤；传入时严格单值 `YYYY-MM-DD` 且为合法公历日期，空串、重复 date、错误格式
或非法闰日返回 422。查询按 observedAt 所属业务自然日 `[00:00, 次日00:00)` 转 UTC 后过滤，
排序 observed_at DESC、id DESC（小时倒序）；空日 / 越界页 items=[]，total 仍为筛选后的实际总数。
合法未来日期可以查询空结果，边界日期须安全处理，不因 datetime / DB 范围溢出返回 500。

Human Owner 已明确批准一期仅允许 observedAt<=捕获的当前时刻，未来输入返回 422。
即使以后存在未来行，current 仍必须按截至现在过滤，不提前应用预约价格。

## R2-002 小时整组更新、当前价与并发

本合同的业务小时身份是上海民用日期加小时。夏令时回拨的重复民用小时统一为同一桶：转到
`Asia/Shanghai` 并取整后，以 `fold=0` 规范化整点，再转 UTC 作为 hour_start；observed_at 仍保留
原真实瞬间，不随桶键规范化改写。因此两个 offset 落入同一民用小时仍整组覆盖同一行，每日最多
24 条；这不将业务归桶改成固定 `+08:00`，也不补齐不存在的小时。picker 对重复民用时刻采用同一
确定性选择，不能把不存在的民用时间静默漂移成另一时刻。旧数据归并也须遵循同一小时身份；
实际 MySQL 时间转换与归并核对继续属于既有 operational gate。

- observedAt 决定归桶；例如业务 10:00 首次写入、10:59 再写仍为同一小时，11:00 是下一小时。
  不同 offset 表达的同一瞬间必须归同一桶；23:59:59 / 次日00:00 必须正确分日。
- 同小时无行则新增，有行则覆盖三价格、三项备注、remark、observed_at、operator 和 updated_at，
  保留 id / hour_start / created_at。唯一约束 `uq_energy_price_hours_hour_start` 在 DB 保证一小时一行。
  通过“新增”指定已有小时即可覆盖；向另一小时提交仅写另一个桶，原桶不移动、不删除。
- 按目标 MySQL 原子 upsert / 等价事务实现，不能只靠先查后插或进程锁；Service commit / rollback，
  CRUD 不控制事务。并发同小时按 DB 写入串行顺序整组覆盖，不能拼接两次请求字段或产生重复行。
  数据库唯一键竞争需在同一业务合同内处理；失败不提交部分结果。
- 补写 / 覆盖更早小时不能因为 updatedAt 最新而替换当前价；current 始终按 observedAt 截至现在取值。
  对当前最新小时主动整组覆盖会改变其值和 observedAt，属于该小时覆盖语义，不新增分钟级版本系统。
- 缺小时不补齐、不制造 null 占位行；选日实际 0..24 行。最近已记录价格沿用至下一次有效记录，
  无保存的日可以历史为空但 current 非空；从未记录则 current=null，不伪造默认价。
- BE002 的 Decimal / Numeric(10,4)、0..999999.9999、最多四位有效小数、超精度 422 不舍入、
  JSON number / 无损十进制字符串兼容及原始 number 精度保护、备注长度 / 空串归 null 全部保留。
  不改变单位、汇总 remark 快照、认证 token、read/manage 两独立权限或 admin 现有 guard。

## R2-003 只读卡片与新增弹窗

上方三价格卡片仅展示 current 的值 / 单位 / 备注；移除原编辑控件与原保存按钮，保留刷新。
current=null 时显示未配置，0 正常显示；失败显示既有加载错误并保留可识别的旧值，不伪造成功或默认价。
页面刷新重新读取 current 与所选日期历史；历史日期改变只查询下表，不改变上方 current。

历史标题右侧为日期选择与“新增”按钮。日期默认业务时区今天、不可清空，切日请求
`getPriceList({date:selectedDate,page:1,pageSize:24})`；保留分页响应但 UI 无分页控件，只显示选日
实际行、小时倒序，不下载全历史再前端过滤、不用 slice(24) 掩盖重复行。按 observedAt 显示业务记录
时间，可用 hourStart 展示小时归属；updatedAt 单独标为最后修改时间，不能混淆。

“新增”打开页面内标准表单弹窗：记录日期时间 picker、三价格、三项备注、总备注、取消 / 保存。
日期时间只允许控件选择，不允许键盘手输；可清空，初始为空，不把历史选日自动当作保存时间。
明确提示“留空由服务器保存当前时刻”和“同小时将覆盖整组价格”。非空选择以业务时区解释并发送
带 offset 的 observedAt，不能依赖浏览器本地时区隐式转换；三价格必填，不从历史行隐式提交默认价。
本期没有逐行编辑、移动或删除按钮，不新增编辑模式；remarks / remark 按原长度与空值合同校验。

弹窗行为：

- 保存开始即锁定表单快照与重复提交；校验不通过不 POST，POST 进行中禁用保存及关闭 / 取消，
  失败解除锁定并完整保留输入。取消仅关闭弹窗，不调用 API、不改变 current / 历史；重新新增使用新表单。
- POST 成功即关闭弹窗并提示保存成功；历史筛选切到响应 observedAt 所属业务日期，然后刷新 current
  和该日历史。补历史后的上方仍由 GET current 决定，不能直接把 POST 历史响应覆盖为 current。
- 成功 POST 后任一 GET 失败只提示对应查询失败，不能报保存失败、重开旧表单或自动重放 POST。
  current / history loading、错误和弹窗输入彼此分离；查询失败不能改写未提交弹窗。
- 切日 A -> B、保存后自动切日、手动刷新等请求仅应用最新有效日期的结果 / 错误 / loading 收尾；
  新日期加载时不能把旧日行冒充该日。current 的迟到 GET 不能覆盖更新后的查询结果，卸载后不回写。
  保留普通日期选择，午夜不自动切用户选日；服务器兜底时间以实际保存请求为准。

日期 / 记录时间 / 最后修改 / 新增 / 弹窗 / 覆盖提示与空态等新文案进入 auxiliary zh-CN / en-US，
键对称；沿用 Element Plus、BaseCard、ActionButton、standard-form-dialog 和 theme token，兼容日夜
及窄屏。facade 继续 getCurrentPrice / getPriceList / createPrice，同名诊断 mock 成对维护现有三函数，
形状同步且带明显 mock 标记；不新增 getPriceDaily，不导入真实截图价格。

## R2-004 保留旧数据的后继与回退

仍建议新增 `energy_price_hours`，含非空 observed_at / hour_start、id、三价格、四备注、operator、
created_at / updated_at；旧 `energy_prices` 所有行与 Model 原样保留。仅新增后继 `b8d0f2a4c6e8`，
down_revision=`a6c8e0f2b4d6`，不重写旧两 migration；十六表 metadata parity 与旧十四表子集严格保留。
新 schema revision 只创建小时表、约束和必要索引，不自动迁移真实价格、seed 或修改旧表。

Development 在模块 README pair 交付最小显式归并 SQL / 操作方案与合成数据验证。推荐将经确认
旧时区解释的 created_at 作为旧记录 observed_at，归业务小时后按 `(created_at DESC,id DESC)` 取最后
完整旧快照，保留三价格、全部备注 / actor、其原 created_at / updated_at 含义；新小时 id 不冒充旧 id。
旧原始 append 行全留，普通分页改读小时表，不混入旧表重复记录。

实际执行前独立 gate 确认源 / 目标库、旧无 offset 时间的真实时区、备份及可恢复性、暂停写入窗口、
具体命令和回退责任。预检给出原行数 / 小时数 / 冲突组数 / 异常数及所选旧 id 清单；目标小时表非空
或时间不明时停止自动覆盖，不能猜测或丢弃。导入后核对整组值、时间、小时数及原表校验和未变，
再切新应用；旧表有价格而新表未导入不能报告为原业务没有 current。
这些是受控本地迁移核对工件，不新增审计表、平台或通用脚本框架，不提交真实数据。

回退先停新写入并备份小时表。旧表保留原始历史，但不包含切换后的新写入；回旧应用继续写入需
另行批准转换与核对，不能宣称直接回切数据完整。downgrade 仅会删除新增小时表，须明确丢失新数据；
实际 downgrade / 删除 / 重放仍另 gate。未来同小时被覆盖的旧版本不新增归档，不支持计费重算。

## R2-005 具体实施任务与精确候选 allowlist

Development 按已批准精确 r2 创建 tasks 并依以下分工实施；PM 本轮仅记录批准，不修改实现。

| 实施块 | 交付与候选文件（无目录通配） |
| --- | --- |
| Model / migration | 新增 `backend/app/auxiliary/models/energy_price_hour.py`，修改 `backend/app/auxiliary/models/__init__.py`；新增 `backend/alembic/versions/20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py`。定义 observed_at / hour_start、唯一键、数值 / 备注约束、DB 时间与安全 downgrade 说明。 |
| API / Schema | 修改 `backend/app/auxiliary/api/energy_price.py`、`backend/app/auxiliary/schemas/energy_price.py`、`backend/app/auxiliary/schemas/__init__.py`；observedAt 校验、API 一次取时兜底、date / 分页、原路径与完整输出，保留精确 number 和权限。 |
| Service / CRUD | 修改 `backend/app/auxiliary/services/async_energy_price.py`、`backend/app/auxiliary/crud/async_energy_price.py`；业务归小时 / 整组 upsert、截至现在的 current、date 范围查询、事务与脱敏日志。 |
| 前端 | 修改 `frontend-js/src/app/auxiliary/views/price/index.vue`、`frontend-js/src/app/auxiliary/api/index.js`、`frontend-js/src/app/auxiliary/api/mock.js`、`frontend-js/src/app/auxiliary/locales/zh-CN.json`、`frontend-js/src/app/auxiliary/locales/en-US.json`；只读卡片、选日、新增弹窗、时区编码、保存后切日 / 查询、竞态与双语。 |
| 测试 | 修改 `backend/tests/test_energy_price_api.py`、`backend/tests/test_energy_price_service.py`、`backend/tests/test_energy_price_migration.py`、`backend/tests/test_core_migration_baseline.py`、`backend/tests/test_openapi_router_tags.py`、`frontend-js/tests/module-registry/price-page.test.mjs`；覆盖下表 AC，保留既有回归。 |
| 模块合同 / DEV handoff | 修改 `backend/app/auxiliary/README.md`、`backend/app/auxiliary/README.zh-CN.md`、`backend/README.md`、`backend/README.zh-CN.md`、`CODE_INDEX.md`；创建本任务 `tasks.md`。 |

原 EnergyPrice Model、旧 migrations、manifest、组合根 / Registry、settings / common / auth / database /
schema-maintenance、依赖 / 锁文件、真实 / 示例 env、其他页面、BE002 / BE003 不在修改面。
根、backend、frontend-js、auxiliary PLAN / catalog pairs 由主协调者按事实同步，不创建 frontend-js/plans；
Verification 交接后仅写本任务 checklist。需要其他文件或实质合同变化先回 PM 新 Revision。

PM 使用 project-governance / aiis；Development / Verification 后端遵循 backend-arch 的响应、分层、
数据库迁移、权限与测试规则，前端遵循 frontend-ui FRAMEWORK / DESIGN 与 i18n-workflow，
关键源码 / CODE_INDEX 遵循 code-document-indexer。只读参考
`data-twin-backend/backend/app/dashboard_metrics/services/async_hourly.py` 与同目录 `time_buckets.py`
的 observedAt 归小时 / 时区 / upsert 概念；不复制 sourceKey、scene、sourceVersion / 乐观版本平台、
固定 24 个 null slot、settings 或外部导入依赖，不修改该参考仓库。

## r2 验收与 gate

| 标准 | 必需验证 |
| --- | --- |
| AC-r2-001 输入 / 时间 | 省略 / null observedAt 仅 API 取时一次，非法 / 空串 / 无时区 / 错误类型 422 不 fallback；offset 等价、跨日 / 跨小时、拒绝未来；原始价格精度 / 0 / 备注回归。 |
| AC-r2-002 原子 / current | 同小时同 id / createdAt 整组覆盖、跨小时新增、另一桶不删除旧桶、唯一约束 / 原子 SQL / 回滚；补历史不会按 updatedAt 倒退 current；截至现在无有效价 null、有价沿用且不补小时。 |
| AC-r2-003 原 API / 查询 | 实际隔离 ASGI 恰好原三 API；date 筛选按业务 observedAt、无 date 兼容分页壳、total 正确、空日 / 越界页、合法日期 / 闰日 / 边界 / 参数失败、小时倒序与带 offset 输出；现有 401/403/read/manage/admin/disabled 矩阵保留。 |
| AC-r2-004 页面 | 实际 SFC 验证卡片只读 / 无原保存按钮、日期默认今天 / page1size24 / 无分页、新增 modal picker 不手输可清空、完整价格 / 备注、取消不 POST、失败保留、重复提交锁定、成功关闭并切响应日期 / 刷新两查询、补历史不直接改 current、GET 失败不报 POST 失败、切日 / 保存竞态、双语对称。 |
| AC-r2-005 数据 / migration | 两旧 revision 指纹不变、原表保留、单 root/head、十六表 metadata / 新表 observed_at 与唯一约束 parity、离线 upgrade / downgrade SQL；合成旧历史归并验证 winner、时间解释、原行全留、冲突停止与回退风险。 |
| AC-r2-006 交接 | 隔离公开 fixture 中 backend 完整 `uv run pytest -q -m no_db`、触达源码 compileall、Alembic heads/history/offline SQL；frontend `pnpm check:modules`、`pnpm test:modules`、`pnpm build`；本地 fixture 浏览器核对日夜 / 窄屏 / 弹窗；diff / 新链接 / allowlist 审计并记录真实命令退出码。 |

验证只用合成数据、公开 example 与既有 uv / pnpm 环境，排除真实 env、截图价格、日志和客户导出。
不安装新依赖，不缩套件绕失败；DEV self-check 后交 fresh-context QA，不冒充最终验收。
源码 / no_db / 离线 SQL 为本任务可完成验收面；真实 MySQL 并发 / 持久化、真实历史归并与备份恢复、
时钟 / 时区和运行联调仍为独立 operational gate，fake session 不证明这些结果。真实执行、重启、
容器、部署 / 发布、Git refs / 推送不在本轮授权。

## 批准口径、排除项与修订历史

Human Owner 已批准精确 r2，固定上海时区、当前 / 历史可录但未来 422、实际 0..24 行不补齐、上述
旧历史归并与分页粒度变化按本范围实施。旧无 offset 时间的来源仍需数据执行 gate 确认。
若改为允许未来预约，应先新 Revision 说明生效与 current 规则，不能由实现自行放开。

排除第三方 connector / 价格源、PLC、定时任务 / Worker、auth/token 撤销或权限重构、复杂审计系统、
逐行编辑 / 跨小时移动 / 删除、批量补录平台、计费重算、其他模块、数据库选型迁移及任何真实 DB 操作。
本期允许单次指定历史 observedAt 的整组新增 / 覆盖，不能继续沿用 r1 的“禁止历史补录”作为限制。
风险为时区归桶错误、整小时覆盖丢失后续版本、补历史误当 current、成功写入后的错误提示与请求竞态；
按明确时间 / 唯一键 / 原表保留 / 查询排序 / 独立状态和运行 gate 控制，不扩展新平台。

2026-10-13 r1：初稿包含新增 daily、当前小时写入和上方编辑建议，尚未获批，完整保留于下方。
2026-10-13 r2：根据 Human Owner 认可的最新讨论整理上述三原路径、observedAt、只读卡片与新增弹窗
方案。当时的认可和授权仅用于规格整理，未据此记录 owner_approved、代码实施、QA 或最终验收。

2026-10-13 r2 批准：主协调者转递 Human Owner 明确原话：“批准 ARCH-BE-004 r2，固定上海时区，
暂不允许未来时间，进入 dev。”据此记录 `owner_approved` 并交 Development，实施范围、allowlist、
验收和风险不扩展；r1 历史原文完整保留。此批准不等于 QA 结论、最终验收或真实数据库 / 部署授权，
既有 operational gate 保持。

2026-10-13 r2 同合同澄清：主协调者授权 PM 将上述重复民用小时 / wire 表示解释写入有效段。
依据是原“同业务小时整组覆盖”“每日最多 24 条”和所指参考 helper 的 `fold=0` 归桶方式；这是
既有合同的一致解释，不是新的 Human Owner 业务批准，不扩展 allowlist、AC、日期范围或运行授权。
原“推荐统一 +08:00”保留为 wire 建议，不能据此采用固定 offset 业务归桶；r1 原文保持完整。

# r1 历史草案（以下原文完整保留）

Task ID: ARCH-BE-004
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: pending；仅起草独立跨前后端规格与具体实施任务，等待 Human Owner 批准精确 r1 后进入 Development

Task Namespace: aiis-ics-arch
Classification: root
Capability: 能源单价按小时整组更新、按业务日期查询与价格页日期筛选
Owner: auxiliary 公共能源单价切片及其前端价格页
Depends On: ARCH-BE-002 r3 owner_accepted
Related Task: ARCH-FE-003
Acceptance Chain Reference: ARCH-BE-004 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-13
Updated: 2026-10-13

# 1. 来源、状态与目标

Human Owner 已明确验收 ARCH-BE-002 r3，并说明日期补充是新的想法，要求先接受旧任务再开始新 spec；
随后明确“继续按 STD 起草 ARCH-BE-004 的 spec，先不要改代码”，并要求说明具体实现任务。
PM 已只读确认 [BE002 checklist](../ARCH-BE-002-energy-price-api/checklist.md) 为 `owner_accepted`。
本任务不改写其追加式合同、失败 / 返工 / 验收历史，也不占用 BE003 映射试点。

本次只创建本 spec，不创建 tasks / checklist、不实施代码或迁移。下文是供范围批准的完整推荐方案；
尤其 §8 的时间、兼容与旧数据归并口径尚未获批。批准起草不等于批准实现或操作真实数据库。
已有截图包含真实价格记录；文档和测试只使用人工合成数据，不复制截图数值或客户数据。

目标交互：10:00 保存一组电 / 氢 / 氩价格，10:59 再保存覆盖同一小时，11:00 保存新增下一小时。
历史标题右侧放日期选择，默认今天；下表只显示选日的实际小时记录，最多 24 条，无分页，小时倒序。
上方始终编辑当前价格，历史日期只影响下表，不成为保存日期。

# 2. 推荐业务与时间合同

## R-001 小时与当前价

- 一期业务时区固定 `Asia/Shanghai`，不新增 env 配置，也不采用浏览器 / 操作系统本地时区作业务判断。
- 保存归属服务端接收该请求的时刻：在本模块 API 接收并通过鉴权 / 入参校验后取一次服务端时刻，
  传给 Service，转换到业务时区后向下取整到小时。跨小时等待 / 重试不重新归桶；新 HTTP 请求重新取时刻。
  客户端不提交 date / hourStart / observedAt / operator / id / 时间字段，不允许历史任意补录或未来预约。
- 三种价格、各项备注、汇总 remark 和 actor 每次整组保存，不允许部分价格更新。
  同小时覆盖原行，id / hourStart / createdAt 不变；updatedAt 与 operator 更新为本次成功保存结果。
  跨小时新增；00:00 属于新业务日期，23:59:59 仍属于前一日 23:00 小时。
- `hourStart` 是小时记录的归属键，表示 `[hourStart, hourStart + 1h)` 的最终小时快照；
  `updatedAt` 是最后实际修改时刻。它不是逐次调整日志，也不证明覆盖值从整点起已实际生效。
- 当前价取最新已保存小时的整组值；没有下一次保存时持续沿用最近有效价，不在整点失效。
  不生成空小时、不在 GET 中补行、不运行定时任务；某日无保存可有 0 条历史，但 current 仍可来自此前日期。
  没有任何价格时 current 返回 null，编辑框不填默认价；0 是有效价格。
- 保留 BE002 三价格 `Decimal / Numeric(10,4)`、`0..999999.9999`、最多四位有效小数、原始 JSON
  number 精度保护、超精度拒绝不舍入、备注长度和空串归 null、JSON number 输出的全部规则。
  不改变单位或汇总 remark 的快照语义。

## R-002 原子性、时钟与持久化

新增 `energy_price_hours`，保留 `energy_prices` 全部旧行及其原 Model。小时表拥有独立 id、三价格、
四备注、operator、非空 hour_start、created_at / updated_at；hour_start 存储为规范 UTC 小时瞬间，
数据库唯一约束 `uq_energy_price_hours_hour_start` 保证每小时最多一行，不能只靠先查后插或进程锁。

FastAPI -> async Service -> async CRUD -> AsyncSession；Service 控制事务。使用目标 MySQL 的原子
upsert / 等价数据库事务方案，成功才返回本次完整快照；并发按数据库对该小时写入的串行顺序覆盖，
最后成功写入整组获胜，不能混合两个请求的字段。失败整体回滚，重复键竞争不能暴露为普通 500。
不增加 Redis、分布式锁、幂等平台、版本审计表或客户端自动重放 POST。

hourStart 派生自接收事件；createdAt / updatedAt 使用数据库时间源，新表明确采用 UTC DB 时间表达式，
不改全局 TimestampMixin、engine / session 时区或 settings。API 将新小时记录时间统一序列化为含
`+08:00` offset 的 ISO 8601。运行采用前核对服务端钟与 DB 钟；不能依据无 offset 的旧时间推测其时区。

# 3. 推荐 API 与兼容合同

API prefix、共享 `code:200 / message:"success" / data` 信封及现有鉴权错误合同保持。
模块 Schema 负责 camelCase；前端 request 已解包 data，facade 不再套 / 拆第二层信封。

`HourlyPriceRecord` 包含 BE002 的 id、electricPrice、hydrogenPrice、argonPrice、electricRemark、
hydrogenRemark、argonRemark、remark、operator、createdAt、updatedAt，并新增 hourStart。
hourStart、createdAt、updatedAt 三个时间字段均由服务端决定；不新增可写有效期字段。

| 接口 | 推荐行为与 data |
| --- | --- |
| GET `/energy/current` | 最新小时快照或 null；不受历史选日影响，不补小时。 |
| POST `/energy` | 请求字段沿用 PriceCreate；保存当前接收小时，返回完整 HourlyPriceRecord。同小时更新、跨小时新增均 HTTP 200。 |
| GET `/energy/daily?date=YYYY-MM-DD`（新增） | date 必填；返回 `{date,timeZone:"Asia/Shanghai",items:[HourlyPriceRecord...]}`，按 hourStart DESC，0..24 条，没有 total/page/pageSize。 |
| GET `/energy?page=1&pageSize=20`（保留） | 继续 `{items,total,page,pageSize}`、默认 1/20、size 1..100；数据改为小时表，按 hourStart DESC、id DESC。旧分页形状兼容，追加粒度不兼容。 |

按日接口只接收一个 date：严格 `YYYY-MM-DD` 且为合法公历日期，空值、错误格式、非法闰日、重复
date、携带 page / pageSize 返回 422；合法未来日期没有记录时返回空 items。日期对应业务时区自然日
`[00:00, 次日00:00)`，转换 UTC 边界后查询；极端合法日期须安全处理数据库 / datetime 边界，不能 500。
不通过旧分页接口忽略 date 伪装完成筛选，不在前端下载全历史再过滤或截断 24 条掩盖重复行。

旧分页保留是响应形状兼容，不承诺旧客户端仍能获得每次 POST 的追加记录；旧表不通过普通分页
混入小时表。未修改的调用方须在采用前知晓 POST / 列表粒度变化；不新增 legacy 写 API。

所有 GET 仍要求 `energy-price-read`，POST 仍要求 `energy-price-manage`，两个 key 不隐含授予。
token、认证、admin 既有 guard、supervisor/operator fail closed、模块 enabled 语义保持；不修改真实或
示例 env，不调整页面授权或 API 权限数组，不新增鉴权平台。前端页面可见不代表已获读写权限。

# 4. 前端行为

## R-003 日期历史与编辑隔离

- 仅改现有 auxiliary price 页。历史标题右侧采用 Element Plus 单日期选择器，挂载时默认业务时区
  今天，值为 date 字符串，不用 UTC `toISOString().slice(0,10)` 或用户本地日期冒充业务日期。
  选择器不可清空；切日自动请求 daily，仅显示该日、小时倒序、最多 24 行，无分页控件。
- 历史时间列改为小时归属（显示 HH:00，标题 / 标签经 i18n）；另显示最后修改时间，避免将
  hourStart 当成真实修改时间。电 / 氢 / 氩价格、actor、remark 列继续保留；窄屏允许表格横向滚动。
- 日期变化、历史刷新 / 失败 / 空态不得修改上方价格、备注、未保存标记；历史加载不阻止编辑和保存。
  上方刷新仅重新读取 current；有未保存改动时先确认丢弃，取消保留全部输入。
- 保存锁定本次编辑快照并阻止重复提交，成功使用 POST 返回的完整结果更新当前表单 / 基线；失败
  保留未保存输入。保存始终写服务端当前接收小时，选择过去日期也不改写过去。
  成功后刷新当时仍选中的日期，不自动跳回今天；历史刷新失败单独提示，不能将成功 POST 报成失败。
- current 与 history 使用独立 loading / error 状态；日期快速 A -> B 切换时只接收最新日期请求的
  结果 / 错误 / loading 收尾，不能让 A 的迟到响应覆盖 B。保存触发的刷新与手动切日遵循同一规则。
  current 的迟到响应也不能覆盖新保存或用户未保存输入；页面卸载后不回写状态。
- 日期选择不会随午夜偷偷改变；重新进入页面才重新默认今天，跨午夜保存归新小时且仍保留用户选日。
  需要查看新日时由用户选日。401/403 沿用现有 request 行为，页面不绕过鉴权或伪造成功。
- 新日期 / 小时 / 修改时间 / 丢弃确认 / 空态文案在 auxiliary zh-CN / en-US 保持键对称；沿用
  BaseCard、ActionButton、项目 theme token 与日夜主题，不改共享布局或主题。
  API facade 新增 `getPriceDaily`，既有模块诊断 mock 同名成对，形状一致且带 mock 标记；不用真实价格。

# 5. 旧历史保留、迁移与回退

## R-004 最小后继与数据归并

建议新增后继 `b8d0f2a4c6e8`，down_revision=`a6c8e0f2b4d6`，仅创建小时表、必要约束 / 索引；
不改十四表 root 或 BE002 migration，不 rename / truncate / drop / update `energy_prices`，不把客户
数据写入 revision。完整 metadata 从十五表增为十六表，旧十四表子集断言保持严格。

Schema revision 不自动归并现场历史。Development 在模块 README pair 交付独立、显式执行的归并
SQL / 操作方案和合成数据验证；本期不新增通用维护平台、后台 job 或迁移脚本框架。真实执行需后续
独立 gate 明确库 / 表、旧时间来源、备份位置、写入暂停窗口、命令和回退责任人。

推荐旧数据归并规则（待批准）：

1. 以经确认的旧 created_at 时区解释每条原始保存时刻并归业务小时；同小时取
   `(created_at DESC, id DESC)` 第一行，整组复制价格 / 备注 / actor，不平均、不逐字段拼接。
   hourStart 为小时键，createdAt / updatedAt 保留所选原始快照时间含义；新 id 不宣称等于旧 id。
2. 原表所有行原样留存，作为完整历史归档与审计源；归并只生成新小时视图，不消灭其他旧行。
   归并预检需给出原行数、小时组数、冲突组数、无效 / 无法解释时间数及每小时所选旧 id 的清单。
   这些是受控本地审计工件，不是新审计系统，不提交真实数据。
3. 采用前先备份并验证可恢复性，暂停旧 / 新价格写入；小时表已有数据则停止自动覆盖，先核对冲突。
   对空小时表显式导入后，核对小时数、整组三价格 / 备注 / actor、时间、原表行数与校验和未变化。
   时间不明、无效行或冲突未经处理时停止归并，不静默丢弃或猜测。
4. Schema 准备和旧历史导入核验完成后才能切换新 API；普通 GET / POST、Registry、启动或页面打开
   都不能触发归并。旧表有数据但新表未准备时，不能把新 current=null 宣称为原业务没有价格。

回退先停新写入、备份小时表。旧表可恢复原追加历史读取，但不包含切换后的新小时写入；若需回到
旧应用继续写入，必须显式批准将小时快照转为旧格式并核对，不能直接切回宣称数据齐全。
新 revision downgrade 仅可删除小时表，必须警示其新数据会丢失；实际 downgrade / 删除 / 重放仍另行
批准，旧表始终不删除。历史小时内未来覆盖的旧版本本期不额外保存，不支持任意历史恢复或计费重算。

# 6. 具体实施任务与候选 allowlist（批准后执行）

以下是本 spec 的实施分工，不是已发生的 tasks / self-check。Development 批准后创建所属 tasks，
按以下顺序细化；实现方案若需要其他文件或改变合同，先回 PM 新 Revision。

| 实施块 | 具体交付 | 精确候选文件 |
| --- | --- | --- |
| Model / migration | 新小时 Model、唯一约束、UTC DB 时间与数值 / 备注约束；独立后继、原表保留、十六表 parity | 新增 `backend/app/auxiliary/models/energy_price_hour.py`；修改 `models/__init__.py`；新增 `backend/alembic/versions/20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py` |
| API / Schema | daily 日期校验、HourlyPriceRecord；保留旧分页壳；服务端接收时刻、原始数字精度与原 guard | `backend/app/auxiliary/api/energy_price.py`、`schemas/energy_price.py`、`schemas/__init__.py` |
| Service / CRUD | UTC 归小时、current / daily / 兼容分页、唯一键原子整组 upsert 与回滚；脱敏保存事件 | `backend/app/auxiliary/services/async_energy_price.py`、`crud/async_energy_price.py` |
| 前端 | facade / 成对 mock、日期选择、小时 / 修改时间列、dirty 确认与独立请求状态 / 竞态防护 | `frontend-js/src/app/auxiliary/api/index.js`、`api/mock.js`、`views/price/index.vue`、`locales/zh-CN.json`、`locales/en-US.json` |
| 回归测试 | 固定时钟边界、原始 JSON、鉴权、SQL / 事务 / migration、页面实际 SFC / 异步竞态与双语 | `backend/tests/test_energy_price_api.py`、`test_energy_price_service.py`、`test_energy_price_migration.py`、`test_core_migration_baseline.py`、`test_openapi_router_tags.py`；`frontend-js/tests/module-registry/price-page.test.mjs` |
| 模块合同 / 交接 | 更新小时 / 兼容 / 迁移 / 回退说明与合成数据 SQL 方案；源码索引真实新入口；DEV handoff | `backend/app/auxiliary/README.md`、`README.zh-CN.md`、`backend/README.md`、`backend/README.zh-CN.md`、`CODE_INDEX.md`；本任务 `tasks.md` |

表中缩写的相对路径均延续同一格首个完整目录；不是目录通配授权。原
`backend/app/auxiliary/models/energy_price.py`、两份旧 migration、manifest / 组合根 / Registry / settings /
common / auth / database / schema-maintenance、依赖与锁文件、真实 / 示例 env 均不在实施修改面。
不为本任务创建 frontend-js/plans。根、backend、frontend-js 与 auxiliary 的 PLAN / catalog pairs
由主协调者按角色事实机械同步；PM 本轮只写本 spec，Verification 交接后只写本任务 checklist。

必要 skill：PM 用 `project-governance` + `aiis`；Development / Verification 后端使用 `backend-arch`
及 RESPONSE_CONTRACT、LAYERS、DATABASE_AND_MIGRATIONS、AUTH_SECURITY、OPERATIONS_TESTING；
前端使用 `frontend-ui` 的 FRAMEWORK / DESIGN、`i18n-workflow`；新源码 / CODE_INDEX 用
`code-document-indexer`。若后续确需新增维护脚本，先修订 allowlist 并使用 `backend-script-tooling`。

# 7. 验收与证据边界

| 标准 | 必需证据 |
| --- | --- |
| AC-001 小时 / 当前价 | 注入固定钟验证 10:00 新增、10:59 同 id 整组覆盖、11:00 新行、23:59 -> 00:00 跨日；current 跨无记录日沿用，空表 null、0 / 精度规则不退化。 |
| AC-002 API / 权限 | 实际隔离 ASGI 覆盖四接口、camelCase / offset / JSON number、daily 日期合法性 / 闰日 / 未来空日 / 边界 / 参数拒绝、0..24 倒序、兼容分页；独立 read/manage、401/403/admin/disabled 仍有效。 |
| AC-003 原子 / 事务 | 实际 SQL 编译断言唯一 hour 键与原子 upsert；同小时整组覆盖、失败回滚、重复请求无重复行的聚焦测试。fake session 不冒充真实 MySQL 并发证明。 |
| AC-004 数据 / migration | 单 root/head、旧两 revision 指纹不变；recorder / metadata 十六表 parity、新表完整约束、离线 upgrade/downgrade SQL；合成旧历史验证同小时 winner、原行全留、时区转换、冲突阻断与回退警示。 |
| AC-005 页面 | 实际 SFC 测试默认业务今天、日期仅影响下表、最多 24 行无分页、hourStart / updatedAt 区分、dirty 刷新确认、保存当前小时、历史失败不改表单、A/B 迟到与保存 / 切日交错；双语键对称。 |
| AC-006 完整交接 | 公开隔离副本中 backend 完整 `uv run pytest -q -m no_db`、触达源码 compileall、Alembic heads/history/offline SQL；frontend `pnpm check:modules`、`pnpm test:modules`、`pnpm build`；diff / 新链接 / 精确 allowlist 审计。记录命令、退出码、限制，不能以聚焦通过绕过完整套件失败。 |

测试只使用合成价格与公开 fixture，排除所有真实 env、客户截图 / 数据、日志和导出；复用 uv / pnpm
及已有依赖，不安装 Agent 辅助依赖。前端用隔离的公开配置构建；浏览器检查采用本地 fixture 验证
日夜主题、桌面 / 窄屏日期控件与表格，无真实 API 写入。DEV self-check 后必须 fresh-context QA。

源码 / no_db / 离线 SQL 可在本任务完成并进入最终验收；真实 MySQL 唯一约束竞争、真实数据归并、
DB 时钟 / 时区、运行前后联调为独立 operational gate，不将无授权操作做成源码验收的假通过或必做项。
运行采用前必须独立完成这些验证与数据保留核验；源码通过不等于部署或真实数据已转换。

# 8. 待 Human Owner 批准的少数口径

| 项 | 本 r1 推荐 | 批准含义 / 未定风险 |
| --- | --- | --- |
| Q-001 时间与小时含义 | 固定 Asia/Shanghai；服务端接收点归小时；小时最终快照与实际 updatedAt 分开 | 10:59 覆盖 10:00 桶，不提供分钟级生效历史；需接受该一期口径。 |
| Q-002 缺小时与当前价 | 仅保存时创建小时；无保存不补行，最近价持续沿用 | “每小时一份”解释为每小时最多一份，不能保证每日恰好 24 条。 |
| Q-003 兼容与旧数据 | 新增 daily；旧分页壳保留但读小时粒度；原 append 表原样归档，同小时选最后旧快照 | 旧客户端追加语义发生变化；旧 created_at 的真实时区须在数据执行 gate 明确，不能由本草案猜测。 |

其余按上述最小方案一并供批准；现在不额外询问或执行。若 Owner 选择自动补齐、客户传时刻、历史
任意补录、其他兼容策略或逐次修改可恢复，则 PM 先形成新 Revision，不能由 Development 推断。

# 9. 排除项、风险与历史

排除第三方 connector / 价格源、PLC、定时任务 / Worker、鉴权撤销或权限重新设计、复杂审计系统、
历史任意编辑 / 删除 / 补录、费用计算与历史计费重算、其他 auxiliary 页面、BE003、数据库选型迁移、
真实 env、真实 DB / 备份导出执行、容器操作、服务重启、部署、Git refs / 推送与资源清理。

主要风险为时区误归桶、同小时覆盖的分钟级信息不再留存、兼容调用方认知不一致、归并误判和迟到
请求覆盖页面。对应以显式时间合同、唯一键原子整组操作、旧表完整保留与审计核对、分离的运行 gate、
前端请求序列和 dirty 防护控制。不给未来小时覆盖增加额外版本系统；旧原始历史仍可追溯。

2026-10-13：确认 BE002 r3 已获最终验收后，建立独立 ARCH-BE-004 r1 draft；已只读核对当前
auxiliary 三 API、append Model / Service、价格页及现有测试入口。编号 / 目标目录此前空闲，BE003
保留。本轮仅形成 PM 规格与实施分工，未运行开发测试、未修改实现、未获得 r1 实施批准。
