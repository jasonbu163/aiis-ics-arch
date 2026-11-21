Task ID: ARCH-OBS-005
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: QA2 已通过精确隔离候选，提交 Human Owner 最终验收。正式整合、dev 迁移、服务切换与演示另待确认。

# QA1 独立验证 · 2026-11-20

**结论为 qa_failed。** 登记操作、双目标采样、旧记录保留及隔离迁移已按下表复核。无变化编辑推进了登记的最后修改时间，违反规格 §4 和根契约 §7。正式源码整合、dev 迁移、服务切换和继续演示待 Human Owner 单独确认。最终验收待定。

## 可重复的失败

1. 使用真实管理员在隔离 FastAPI 新建来源 `QA-extra-1795163317705`，名称为 `QA test`，默认启用。创建结果的 `updatedAt` 为 `2026-11-20T16:28:37.719428+08:00`。
2. PATCH 相同名称，HTTP 200。相同业务字段返回的 `updatedAt` 为 `2026-11-20T16:28:37.742548+08:00`。
3. 用独立 SQL 会话读取该登记，确认数据库中的原值为 `16:28:37.742548`。PATCH 相同的 `{"enabled":true}` 仍返回 200，重新查询的数据库值为 `16:30:35.336251`。上述三次均为同一上海自然日。
4. 候选 `backend/app/equipment_observation/services/write_sources.py` 的 `change` 在第 142 行无条件赋值。请 Development 在锁定行上比较已提供字段，验证重复 PATCH 保持时间、真实改名与状态切换推进时间，并保留按来源串行化及删除行为。

## 候选与环境

独立工作目录 `/private/tmp/arch-obs-005-r1.fusgi7bi`，下称 D。QA 候选为 D/qa1-source，基线为 `7d1422523be816233f4e268af73cca365ea34b09`。使用 shasum -a 256 验证 spec、tasks、delta 的 SHA-256 分别为 `cd835e3f4a6fb2414b3819bacd9957a0c8d3e580da031f80f0f005c4fea97347`、`d9b309b4d4bd0ec735997b5c4da4dc68c1fb121ab26fdd2c2e9cf0d92ac6f1cd`、`94fb4004f9593cefefa8c47243d50202a1061aada071567b82f5ab55c36fa882`。Python hashlib 逐项比对 3,743 个前像和 43 个候选文件；git diff 和未追踪文件并集正好 43 个，符合 §8，git diff --check 退出 0。

MySQL 8.4.6 任务容器 `arch-obs-005-r1-qa-fusgi7bi`，回环端口 63996、UUID `69845f90-e4b9-11f1-8650-26f25ffe45ce`，上海时区。空库链、浏览器、并发及补充 SQL/HTTP 测试使用 `obs005_qa_454ee4db1f2e`；非空迁移和采集套件使用各自随机库。浏览器为原生 Google Chrome 和缓存的 Playwright，前后端监听 53584/53583。全程使用专属合成身份，Python 为正式 backend/.venv 的锁定解释器，前端使用已复制的锁定依赖。

| 验收项 | 本轮证据 |
| --- | --- |
| AC01 | 空库链到 e9；非空 d8 使用旧后端生成样本与回执，包括无引用回执。升级前后 63 张旧业务表的每行和 SHOW CREATE TABLE 完全相同，新登记表为空，错误 UUID 和占用表名均在 DDL 前拒绝。 |
| AC02 | **失败**，两种无变化 PATCH 均改写时间。其他已验点包括空 devices/producers、真实登录增查改启停删、重复／已删除键、大小写、旧行及 profile 碰撞、普通用户拒绝、列宽拖动持久化和重置、中英文及窄屏横向滚动。 |
| AC03 | 两温区四指标的独立双目标槽位、卡片及曲线经真实前端查看。部分实时包产生缺测，部分历史包的 ECharts 及 API 点列保留断点，unknown 样本的 0 值仍可见。另用独立来源验证过期 120 秒的两温区整包返回 stale 且保留 208 和 472；仅 latest 绑定的新指标能写入 0，history 返回 422，GET 对应任务的 history 为 null。 |
| AC04 | 匿名 HTTP 重排等价重放、槽位停用后重放、冲突、5 个并发相同请求、较早实时的 stale 回执、乱序历史、错误介质／大小／时间／类型及 false、空字符串、0 的往返通过。附加 SQL 读数显示，未知指标的 HTTP 422 前后，目标来源的回执、实时及历史条数均为 2、2、0。 |
| AC05 | 停用与删除后的重放、停用可读、恢复写入、删除后 404 和管理员历史记录可见通过。实际 MySQL 行锁以两种顺序验证删除／写入。operator 在两类普通页面可见未删除来源，隐藏删除来源，管理请求拒绝。 |
| AC06 | 旧后端和候选真实旧合同 HTTP 保留 latest/history/energy 的 ID、响应和重放、Bearer、范围及新写入。采集后继的上传、读取、续读、租约、ACK 和保护清理 9 项通过。计划实际创建成功并可列出；实绩人工修改缺失行返回原合同 404，准备已存在的合成实绩后，真实人工编辑返回 updated，重复返回 unchanged，列表保留该记录。 |
| AC07 | 后端相关子集 180 passed、8 skipped。前端生产构建成功，相关观测在真实 Chrome 操作通过。候选和前像的全量 Node 套件均为 90/93；三个同名基线失败见下文。38 个相对文档链接有效。本轮产品缺陷和正式源码后续整合均记录在案。 |

## 实际命令与退出结果

以下命令引用 D 下的专属夹具。qa 前缀的迁移、采集、锁序夹具保留原断言，使用独立 QA 候选、端口、凭据文件和隔离库。另行编写的两项补充探针用于浏览器和 SQL/HTTP 实测。

- `python infrastructure/isolated-stack.py --source "$D/qa1-source" --phase qa --mysql-port 63996 --mysql-uuid 69845f90-e4b9-11f1-8650-26f25ffe45ce`。成功启动，Ctrl-C 后退出 0。
- `bash infrastructure/qa-obs005-run-mysql-dev.sh` 和 `bash infrastructure/qa-obs005-run-dev-acq.sh`。均退出 0；迁移证据在 D/obs003_62ae495ea367431c-migration-qa。
- `OBS005_BROWSER_KEY=QA-Independent node infrastructure/obs005-dev-browser.cjs "$D/obs005_qa_454ee4db1f2e-browser"`、以 QA 候选 backend 为 PYTHONPATH 运行 `python infrastructure/qa-obs005-dev-races.py "$D/obs005_qa_454ee4db1f2e-browser"`，均退出 0。
- `node infrastructure/qa-independent.cjs "$D/obs005_qa_454ee4db1f2e-browser"` 和 `python infrastructure/qa-sql-http.py` 均退出 0，脚本输出可重复的时间缺陷。该退出码表示成功采到证据。
- 后端 source 任务临时合成环境后，以 `PRIMARY_DATABASE=mysql MYSQL_ENABLED=true` 执行 `uv run --no-sync --offline pytest -q -p no:cacheprovider -m no_db`，目标为 equipment_observation 四个测试模块、observation_write_sources、receipt_separation、observation_retirement、equipment_temperature_migration、mapping_migration、business_integration_storage、generic_task_migration_r3、generic_task_revision_guards、legacy_acquisition_retirement、acquisition_consumption_contract。退出 0。首次使用未开启的 SQLite 配置在收集前退出，修正测试环境后产生 180/8 的结果。既有 SQLite datetime adapter 告警一条。
- `pnpm --config.verify-deps-before-run=ignore --config.update-notifier=false build --outDir "$D/qa-build"`，设置合成权限清单及 VITE_API_BASE_URL，退出 0，保留 Vite 块体积提示。在 qa1-source/frontend-js 和 frontend-baseline/frontend-js 分别运行 `node --test tests/module-registry/*.test.mjs`，均退出 1，完全相同的失败为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。

QA Chrome、Vite、Uvicorn 已结束。协调者可回收本轮独占容器。专属临时探针及日志由协调者保留至重验和交付一致性核对完成。未操作 dev 服务或真实库；当前结论仅适用于上述精确候选。

## QA2 独立复核 · 2026-11-20

**qa_passed**。冻结候选 D/qa2-source 的实际时间修复通过；QA1 的失败保留为历史证据。SHA-256 核对 spec、再次交接 tasks、QA1 checklist 和新 delta 分别为 `cd835e3f4a6fb2414b3819bacd9957a0c8d3e580da031f80f0f005c4fea97347`、`7f95477315dcc33c7c7964084a2b7c6400aaf7e472896a404f4434bdf61d32c8`、`27559ef2c086dc4fcae43b8b90fbb6f932cc722e6901610fc5ce006c8a1931cf`、`a46b5778c724154228580f8fa8345d0c605ab7394f0c2cbe50735c0aa3264451`。git rev-parse HEAD 为 QA1 同一基线。hashlib 验证 3743 个前像与 43 项变更组合后的候选文件，逐项比较两份 delta，仅服务与对应测试变化。git diff --check 成功。

专属 MySQL 8.4.6 容器 `arch-obs-005-r1-qa2-fusgi7bi`，127.0.0.1:55456，UUID `288e4156-e4bd-11f1-8b5f-d605d668ebc9`，数据库时差 +08:00。锁定 backend/.venv Python 运行 infrastructure/isolated-stack.py，参数为 `--source "$D/qa2-source" --phase qa --mysql-port 55456 --mysql-uuid 288e4156-e4bd-11f1-8b5f-d605d668ebc9`，空库 `obs005_qa_15922cc06d59` 到 e9f3b5d7c021。真实 Uvicorn/Vite 端口为 56072/56073。以下 QA2 夹具位于 D/infrastructure，浏览器工件目录 B 为 D/obs005_qa_15922cc06d59-browser。

| 验收项 | QA2 实测及结果 |
| --- | --- |
| AC01、AC06 | `bash qa2-obs005-run-mysql-dev.sh` 退出 0。非空 d8 → e9，逐行和 DDL 对比原有 63 张表，旧 latest/history/energy 的重放、读写、认证、范围及失败恢复通过，错误身份及预占表名被拒。工件 D/obs003_5275ca4027f54a6a-migration-qa。`bash qa2-obs005-run-dev-acq.sh` 退出 0，采集 9 passed。真实计划创建与既有实绩检查参见 QA1；本轮补充 Chrome 同时验证计划创建和缺失实绩 404。 |
| AC02 | `python qa2-obs005-rework1-http.py "$B"`、`python qa2-enable.py "$B"` 均退出 0。后者独立 SQL 会话核对真实管理员 HTTP 响应和数据库时间窗。11 月 20 日上海时间，初始、同名、同启用值和两字段均相同的 updatedAt 均为 16:39:45.582922；改名 .629907，停用 .636098，重复停用仍 .636098，再启用 .646973，删除 .653208（同 deletedAt）。createdAt 不变，删除后 PATCH 404。 |
| AC02–AC05 | `OBS005_BROWSER_KEY=QA2-Independent node obs005-dev-browser.cjs "$B"` 及 `node qa-independent.cjs "$B"`（同一键）均退出 0。原生 Chrome 实测列宽拖动、持久化及重置，真实 latest/history、重放、冲突、重复并发、缺测及过期数值、两种数据页、卡片、曲线、启停删除、窄屏英文及普通用户权限。补充夹具验证单目标槽位和另一目标 null。 |
| AC04、AC05 | 以候选 backend 为 PYTHONPATH 执行 `python qa2-obs005-dev-races.py "$B"` 退出 0。实测两个删除/写入锁序、老身份碰撞、profile 冲突拒绝、非法未来时间及类型、false 和空字符串往返。锁内无变化分支在生成响应后 rollback 释放锁，实际变化和删除仍走数据库时钟与提交。 |
| AC07 | 在 qa2-source/backend 加载专属合成环境，以 QA1 的 14 模块运行 `PRIMARY_DATABASE=mysql MYSQL_ENABLED=true uv run --no-sync --offline pytest -q -p no:cacheprovider -m no_db`，187 passed、8 skipped、1 条既有 SQLite datetime adapter 告警，退出 0。前端、文档及迁移在交接清单与冻结源中逐字节相同，沿用 QA1 的生产构建、38 项文档链接和前端 90/93 同名基线失败记录。 |

Chrome 验证和锁检查已结束，Uvicorn/Vite 通过 Ctrl-C 收尾，启动器退出 0。协调者负责专属容器及工件回收。当前通过范围为上述隔离候选；Human Owner 最终验收待定。正式工作树合入及一致性核对、dev 迁移、服务切换和演示均待独立确认。

## 正式 dev 切换后独立复核 · 2026-11-20

**qa_passed**。本节更新页首的历史交接状态。正式工作树、dev 迁移和两个恢复后的服务已完成独立复核，提交 Human Owner 最终验收。隔离 QA1、QA2 的原始结论见上。

- 以 `shasum -a 256` 核对 spec、切换交接 tasks、追加前 checklist，分别为 `cd835e3f4a6fb2414b3819bacd9957a0c8d3e580da031f80f0f005c4fea97347`、`e2f610564aa92212590a020d900df4cbc6eb5ba94cb974ed3d5b904b2670ee67`、`34d6f0eff7df1016d1b08ec399c6abc1392718c50316f494d1b440d76f779f2b`。切换完成记录、前后指纹、源码后像与 HTTP 记录摘要均匹配交接。
- Python hashlib 按冻结的 43 项清单比较 QA2、正式工作树及切换后像。42 个文件的字节和权限与 QA2 一致。并行维护的 CODE_INDEX.md 在切换时为 `183c8437dad559341ceb1697406cbdb0833e3c79dbd21fe9235251215fa79f3f`，现为 `ee876328b0ca06121b7717d81d5305d2ac9817efd93d33e04134584604dfc988`。首次全文件核对捕获此差异，按基线与候选的逐行差异复核，任务新增的全部四行仍在。该差异仅涉及索引。
- 检查维护前 SQL dump 的首尾、完成标记、304040 字节及 SHA-256 `4a945d9c216a8e12bd300c8177151458faa92e969b5e5a138864294a940a8a86`。留存的前后指纹显示 63 张原业务表及触发器、例程、事件一致。两份真实启用的 profile 与备份字节比较仅替换目标 revision，文件权限一致，backend/.env 摘要与切换前一致。备份恢复演练仍未执行。
- 正式 backend/.venv Python 通过 SQLAlchemy 连接 127.0.0.1:3307 的 industrial_level_2_system，使用 `START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY` 后回滚。MySQL 8.4.6，UUID 摘要前缀 ac2319a3fdc8，唯一 Alembic revision e9f3b5d7c021。首次探针假设会话时区为字面 +08:00，实测为 SYSTEM，改以 NOW 与 UTC_TIMESTAMP 比较确认实际偏移为 480 分钟。全部 64 张现有业务表的 SHOW CREATE TABLE 摘要、行数与排序后的逐行摘要均与切换后指纹一致，涵盖设备、过程、采集及回执。新增登记表为空，七个字段、source_key 主键与 storage_identity 唯一索引符合迁移。
- httpx 正式回环验证退出 0。健康检查 200，OpenAPI 含四个新合同路径，匿名列登记 401，通过 Vite 代理查询未知来源 404 且错误码符合合同。阅读认证实现后使用既有管理员登录，登记列表为空，设备、过程、能源消费选项、采集选项及最新数据浏览均返回 200。
- 使用缓存 Playwright 和原生 Chrome，以临时会话登录 5190，访问设备状态的配置管理页并点开“写入登记”，确认表头“来源标识”和“新增”按钮可见，退出 0。浏览器拦截登录之外的非只读请求。lsof/ps 复核 8000 的 run.py PID 75521、子进程 75523 及 5190 的 Vite PID 75570，工作目录分别为正式 backend 和 frontend-js，退出 0。QA 未重启服务，未创建登记或写入样本。真实 dev 的写入行为沿用隔离 QA2 证据。
