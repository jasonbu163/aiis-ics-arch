# ARCH-OBS-003 r3 独立验证

Task ID: ARCH-OBS-003  
Revision: r3  
Status: qa_failed  
Owner Role: Verification  
Allowed Writers: Verification  
Handoff: 两项 AC05 实测失败交 Development；ACQ 前驱迁移语义变更交 PM 重新界定 Revision 和冻结基线。

## 结果与复现

2026-11-19，Verification 从 fresh context 独立复制 Development 冻结候选，核对 31 项 SHA-256，清单摘要为 `2383e7658eae02abb756fb3dc5e7a45fb82e6005a5a9aef86aa4fc1c84f60272`。分别在同一专用实例的两个全新随机 schema 上沿历史链升至 da6，用下列两个单独的结构漂移检验 §4.2 条款中的依赖冻结和 §4 第 2 条的结构防护。两个探针均在漂移后调用带正确 UUID、schema 和维护窗口的正常 Alembic upgrade。

| 前驱异常 | 实测 | 源码定位 |
| --- | --- | --- |
| 对 equipment_metric_configs 删除 ck_obs_r10_metric_type，并以原名添加 `CHECK (char_length(value_type)>0)`，取代原来限定 number、boolean、string 的条件 | 升级返回 0，alembic_version 已为 d8；同名约束语义变化应当在破坏性 DDL 前停止 | d8 migration 第 238 行检查约束名和 ENFORCED，缺少谓词核对 |
| `ALTER TABLE metric_ingest_receipts MODIFY target VARCHAR(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL` | 源实际为 utf8mb4_0900_ai_ci。升级仍返回 0，alembic_version 为 d8。target 是回执去重唯一键的第一列 | 第 185 行起的 _receipt_layout 只固定 producer_id、event_id 的排序规则；源与复制表一致仍可能继承漂移 |

## AC 检查记录

| 标准 | 结果与证据 |
| --- | --- |
| AC01 | 原冻结候选在标准空库和非空 da6 迁移通过。MySQL suite 比较表集、主键、业务和采集数据及 FK；异常前驱保护存在上述失败。 |
| AC02 | 非空测试逐行对账回执和引用，包括旧快照、无历史指标事件、样本、多目标同事件与自增水位。通过。 |
| AC03 | 原 c9 源码从 Git 基准 cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81 提取。用真实 MySQL、合成用户和机器身份，经 HTTPX ASGI transport 实际调用应用；新源码重放、变体冲突、撤权、并发及提交故障均通过。 |
| AC04 | 原／新 HTTP 对比覆盖卡片、曲线、历史列表、能耗样本和统计等夹具路径。已完成的证据限于测试实际覆盖，未完成逐端点额外复核。 |
| AC05 | **失败**。标准 suite 中错误身份、名称冲突、异常关联、未知依赖、缺权限、写入竞争及五个中断阶段通过。复制、切 FK、改名、删源及版本登记失败后观察实际状态，恢复隔离 da6 备份，全表对账并重新升级重放通过。上述两个附加反例均误放行。 |
| AC06 | 旧冻结前驱链唯一 head 为 d8，空库、非空 ACQ 六表和三触发器保留路径通过。独立 ACQ da6／d8 行为 suite 在收集时均因缺少应用合成配置退出 2；未证实两版消费路径。本轮因前驱变化停止。正式交付工作树与候选不同，运行中 dev 启用了源码热重载。 |
| AC07 | 已按独立角色核对批准、交接、清单、断言差异和测试输出。r3 变更符合两处现行 metadata 及一处唯一 head 断言的限定。冻结前驱已失效，需重新独立验证。 |

## 环境、命令与停止条件

- 独立 MySQL 8.4.6，+08:00，回环 64865，UUID cb0b6544-e3f0-11f1-afbd-266563b27510，容器 arch-obs-003-qa-op794d。独立临时目录 /private/tmp/arch-obs-003-qa.oP794d。随机 schema 和私有合成凭据仅用于此次验证。
- 使用仓库 backend/.venv 的 Python 3.13.3，在独立副本运行 `python -m pytest -q -p no:cacheprovider tests_mysql/test_observation_receipt_separation_mysql.py`，4 passed，100.23 秒。13 文件定向组首次缺少 settings，补合成 settings 后 148 passed、8 skipped、1 SQLite datetime 警告，12.04 秒；选集见下。Development 自检计数另见 tasks.md。
- 定向组使用 tests/ 下的 test_observation_receipt_separation、test_equipment_observation_r10、test_equipment_observation_r10_flow、test_equipment_observation_domain、test_business_integration_storage、test_generic_task_revision_guards、test_observation_retirement、test_generic_task_migration_r3、test_legacy_acquisition_retirement、test_mapping_migration、test_equipment_temperature_migration、test_acquisition_consumption_contract、test_equipment_observation_r8。每项后缀为 .py。
- `python -m alembic heads` 输出 d8f2a4c6b915 (head)；`python -m app.module_preflight --project-root "$PWD" --check-only` 退出 0。启动 compileall 但未分别记录退出码；文档链接未独立完成复核。
- 前驱文件独立复算 SHA-256。测试副本为 fd28dca872c063f6d9fa1a9ecb146868a5577fd6fd7c0d316bbf90ee8f384703，正式工作树已变为 e2a62bc9518b987bb899e3771956bf1a12413eacb99ded3c6b5cc82628767147。ACQ checklist 为 qa_failed，候选已更改 trigger 的拒绝条件。按 §4.2 停止新增正式测试。PM 确认新 revision 和基线后，Development 应重新交接并包括对上述两个结构漂移的拒绝证明。
- 正式源码整合及 dev 数据库、服务、清理、演示继续等待相应批准。最终验收由 Human Owner 决定。本轮测试只针对旧冻结源。QA 临时目录限返工复查；交接后回收自有实例与临时凭据。

QA 完成记录后已回收上述专用容器及临时卷，删除 QA 专用目录、合成凭据和副本。两项复现条件、候选摘要和全部结果保存在本记录。

## ARCH-OBS-003 r4 独立验证 · 2026-11-19

**Verdict：qa_failed。** AC05 的意外前驱结构保护在非空真实 MySQL 上误放行。提交 Development 返工，最终验收待 Human Owner。

### AC05 失败证据

1. 在专用 MySQL 8.4.6 的随机库 `obs003_e38c64a3a18f4dd1` 上，从 Git `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81` 归档的 c9 backend 提交三个目标的真实 HTTP 写入，升级至冻结的 `da6c32f8a701`。
2. 在原回执表添加 `ALTER TABLE metric_ingest_receipts ADD CONSTRAINT ck_qa_receipt_name CHECK (char_length(event_id) < 100)`。现有夹具数据符合此限制。记录故障注入后全表行、表集和 SHOW CREATE，使用正确的 schema、UUID、窗口确认调用正常 d8 升级。
3. 预期在迁移 DDL 前拒绝。实际 Alembic 退出 **0**，版本变成 `d8f2a4c6b915`，两个目标回执表和五个重命名后的表均已出现。独立 pytest 断言失败，退出 **1**，14.08 秒。回执 event_id 为 VARCHAR(128)，这个前驱额外约束限制了可接受的事件号长度。
4. d8 迁移的 `_receipt_layout` 第 206–229 行只检查回执列及索引，CHECK 的精确集合检查在 `_business_layout` 中，未覆盖旧共用回执表。按规格 §4 第 2 条及 AC05，Development 应核对该表的前驱 CHECK 集合，并保留非空反例与正常前驱的双向证据。前述 r3 同名 CHECK 和单列排序规则反例均已修复。

### 独立运行与其他验收项

- **对象与环境**。独立源码副本 31 文件清单 SHA-256 为 `5129fa3478f11362ca64ff9f1ed92aded00e30100be1f86b560dd0f53d3cf1f9`，补丁为 `a6cdbb8ae93ac27d653a12b7ad095d0aa70912b567be1fa9403c153b7e84ea9c`。独占容器 `arch-obs003-r4-verification-1649`，回环 55600，UUID `35d5e184-e3f6-11f1-90ea-6a02986ea965`，MySQL 8.4.6、+08:00。仓库 backend 虚拟环境、合成 Settings、独立随机 schema。通过 HTTPX ASGI transport 进入实际应用和数据库。
- **AC01–AC03**。`python -m pytest -q -p no:cacheprovider tests_mysql/test_observation_receipt_separation_mysql.py` 共 **6 passed，148.99 秒，退出 0**。全空历史链与两种默认排序规则（utf8mb4_0900_ai_ci、utf8mb4_unicode_ci）的非空链通过。逐字段对账回执、原 ID、三处业务 FK、五张改名表、采集数据及触发器。三路 POST 原正文与原身份重放、跨目标同号、409、401/403、并发、回滚、提交未知和自增水位通过。
- **AC04**。MySQL 套件比对迁移前后的当前能源价格、实时卡片、历史列表及曲线、能耗统计与样本响应。聚焦回归另覆盖 0、false、空字符串。本轮未另行逐端点比对机器指标发现、管理详情等全部读取面，AC04 完整证据留待复验。
- **AC05 其余项**。上述套件通过两个 r3 原始漂移反例，拒绝时 da6、故障注入后表结构、表集和各行数据均相同。通过权限、占名、未知 target、孤儿、错类、外部依赖、竞争写入及五个中断阶段的拒绝／锁定／备份恢复重放。新增的回执 CHECK 反例独立于这 6 个通过项。
- **AC06**。`python -m pytest -q -p no:cacheprovider tests_mysql/test_acquisition_consumption.py` 在 da6 **9 passed，42.66 秒**；同一文件在 d8 加 `-p pytest_obs003_acq` **9 passed，42.10 秒**。均退出 0，使用任务交接中公开的后继与合成窗口 hook。包括错时点／事件／所属表的同名同正文触发器拒绝、回填、两版本真实采集 HTTP、duplicate、续读、租约、事务与清理。r3 checklist 所列 13 文件聚焦组 **148 passed、8 skipped、1 SQLite 日期警告，15.26 秒**；本次实际选集和计数沿用 r3 独立侧。compileall、alembic heads（唯一 d8）、模块 check-only preflight 均退出 0；7 份变更说明文档内 117 个相对文件链接均能解析。
- **AC07 与交接**。核对 ACQ 返工交接、QA2、冻结 manifest、r4 代码和补丁。只读 integration preflight 显示 OBS 31、ACQ 35、重叠 12、差异 0；正式工作树 git apply --check 通过。当前测试对象为冻结候选，正式源码整合与 dev 切换仍待专门批准。QA 没有更改实现、正式数据库或服务。测试随机库由夹具回收。协调者可在记录本次交接后回收上述专属容器和 `/private/tmp/obs003-r4-independent-1649`；此目录含合成凭据。返工候选须重新交接独立复验。

## ARCH-OBS-003 r4 返工后独立复验 · 2026-11-19

**隔离候选验证通过。整项 verdict 为 `qa_blocked`**。AC06 的正式交付工作树一致性待单独批准的整合窗口。正式 backend 正被 dev 自动重载服务使用。该限制不影响以下隔离测试结果。交接 Human Owner 决定切换窗口及最终验收。

**验证对象与环境。** 依据本任务 r4 返工后的 Development handoff，独立复制冻结候选。31 文件清单 SHA-256 为 `261500f8f13e61848faa103216c58014213e4b7a49a7d5bc04867b5b7da8479c`，补丁为 `72353582063352aa172f3cad69052ab01fc635ccefb727e7921d76933e21de67`，ACQ 35 文件清单为 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`。本轮自有目录 `/private/tmp/obs003-qa-rework.hX4RjI`，MySQL 8.4.6 容器 `obs003-qa-rework-hx4rji`，回环端口 62466，UUID `1403dbd4-e3f8-11f1-a50e-9ef605ec2080`，时区 +08:00。使用仓库 backend 虚拟环境，显式合成 Settings、专用凭据及每例随机 schema。旧 c9 应用取自 `git archive cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81 backend`。

| 验收项 | 实测结果 |
| --- | --- |
| AC01、AC02 | 两种数据库默认排序规则 utf8mb4_0900_ai_ci、utf8mb4_unicode_ci 上的非空 c9 → da6 → d8 均通过。逐表逐行比对五张改名表、任务外业务和采集数据，逐字段比较三路旧回执的拆分结果及原 ID，核对三处实际外键和自增水位。 |
| AC03、AC04 | 每种规则的夹具都记录了 8 份原身份及正文的旧请求、25 份管理员 GET、2 份机器发现 GET。新源码经实际 HTTP 应用入口针对真实 MySQL 逐项比较，包括实时和历史详情、卡片、曲线、能耗统计与配置、原请求重放、401/403、409、跨目标同号及并发去重。 |
| AC05 | r3 同名宽松 CHECK 和 target 排序规则漂移、上一轮 r4 的旧回执额外 CHECK，以及不可见索引、降序索引和不可见列都在迁移 DDL 前拒绝，表集、注入后的 SHOW CREATE 与全部行保持。复制目标上额外 CHECK 在数据复制及 FK 修改前被拒绝，新增空表、旧表 DDL 和行均有断言。复制、切 FK、改名、移除源行、版本登记五类中断分别验证了部分状态、再次启动拒绝、备份恢复及最终重放。 |
| AC06 隔离部分 | 空库历史链、两种非空规则通过。ACQ 六表及三个 trigger 状态保全。对冻结 ACQ suite 分别在 da6 与 d8 运行；同名同正文但时点、事件或所属表错误的 trigger 阻止前驱激活，正常回填、同事务写入、duplicate、续读、租约和清理通过。d8 仅使用已审计的任务专用 pytest hook 设定目标及维护参数。 |
| AC06 正式交付、AC07 | 只读 integration preflight 显示 OBS 31、ACQ 35、重叠 12、差异 0。正式工作树通过 git apply --check --whitespace=error。在独占正式 preimage 副本实际重放补丁后，shasum -a 256 -c 核对 31/31 通过。独立角色已消费返工交接及历史失败记录。正式工作树仍为整合前源码，待批准窗口后核对正式源码、运行入口、数据库和 profile，再按约定处理演示。 |

**命令与结果。** 下列 pytest 使用 `python -m pytest -q -p no:cacheprovider --basetemp=<本轮专用目录>`。

- `tests_mysql/test_observation_receipt_separation_mysql.py` 共 7 passed，184.22 秒，退出 0。
- `tests_mysql/test_acquisition_consumption.py` 在 da6 共 9 passed，46.10 秒；在 d8 加 `-p pytest_obs003_acq` 共 9 passed，46.22 秒。均退出 0。
- 按上述 r3 独立验证列出的 13 文件运行，148 passed、8 skipped、1 条 SQLite datetime 弃用提示，13.95 秒，退出 0。另跑 tests/ 下的 test_plc_facts_v2、test_acquisition_facts_migration、test_acquisition_data_browse、test_acquisition_source_registry 四个 .py 文件，120 passed、2 skipped，5.08 秒。
- `python -m compileall -q app alembic common tests tests_mysql`、`python -m alembic heads`（唯一 d8f2a4c6b915）、`python -m app.module_preflight --project-root "$PWD" --check-only` 全部退出 0。7 份变更说明文档共 117 个相对文件链接均可解析。

本轮结束核对专用服务器仅剩四个系统 schema，已停止并自动回收专用容器。本轮独占临时文件可随记录持久化回收。正式工作树、真实库、dev 进程和演示均维持原状。

## r4 正式 dev 切换后独立验证

**Verdict：`qa_passed`。** 关联 AC06 正式源码、运行验证及 AC07。先前 r4 返工后的隔离验证覆盖其余验收项。Human Owner 最终验收待定。

- 在正式工作树使用 backend/.venv/bin/python、hashlib 和已审阅的 cutover.py 只读函数核验。冻结 manifest 摘要为 `261500f8f13e61848faa103216c58014213e4b7a49a7d5bc04867b5b7da8479c`，正式文件匹配 31/31。全库 dump 253317 字节，SHA-256 为 `25fcec35868de049cd826611daf33c4a23f8c48cdf4580e15f63be91d99bcbd5`。维护脚本和 tasks.md 收录的八份阶段证据摘要全部匹配。
- 在 127.0.0.1:3307 的 industrial_level_2_system 使用 READ ONLY 一致性事务，核对 MySQL 8.4.6、UUID SHA-256 前缀 ac2319a3fdc8、+08:00 和 d8f2a4c6b915。调用 stage_snapshot、verify_acq_preserved、verify_obs_preserved，比对保存的 c9、da6 与现场 d8。63 张业务表全部行指纹、DDL、触发器、回执及序列与 d8 归档一致。五处改名、三条样本外键和拆分约束符合阶段预期；原采集历史 107、最新点值 6、来源 3 得以保全。固定截止回填的 107 个事件逐项匹配原历史，两条流及三个守卫触发器匹配。两张回执表均空，下一 ID 各为 266。两份实际启用的 0600 外部 profile 与各自备份逐字节比对，唯一差异为 schemaRevision 从 c9 改为 d8。
- 运行接口使用 urllib.request 读取 8000 的 OpenAPI，通过既有登录入口取 accessToken，5190 前端入口返回 200。采集 options、latest/browse、使用实际 plcId/dbNumber 的 latest、带上海时区范围的 history 均为 200。11 月 18 日零时至 20 日零时查询返回 total=29。设备、过程和能耗选项均为 200 空列表；管理员实时、过程列表和监控历史返回 200、total=0。指标组、指标配置、卡片及曲线配置均为 200。探索时缺少必填参数的 GET 返回 422；当前无可供关联查询的设备或能耗表计。首次认证探针按 snake_case 读 token 键退出 1，按实际响应 accessToken 重核成功，最终两次端点检查退出 0。
- 正式现场仅验证现存数据和读取路径。原回执为空，旧请求逐 ID 重放、非空拆分及并发行为沿用上节隔离实测。此次未运行真实生产方写入、正式备份恢复或温区 1 演示。交接 Human Owner 最终验收。
