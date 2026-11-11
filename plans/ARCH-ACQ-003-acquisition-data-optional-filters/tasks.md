Task ID: ARCH-ACQ-003
Revision: r2
Workflow Mode: STD
Execution Mode: agent_team_same_session
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Approved Spec SHA-256: 20bfb16926e7c3869e1766478ab60cb88fa061828cf7083a8e13050b46ceb744
Spec with operation authorization SHA-256: 3133b706f2b16ede3ef675399ea138e626b77bdeef8459820369970371e2e5c1

# 实施记录

Human Owner 已批准 ARCH-ACQ-003 r2。Development 于隔离公开源码候选实施；当前正式后端仍连接旧 schema 并自动重载。候选位于 `/private/tmp/arch-acq003-r2-candidate-JhGlNhmC`，排除实际环境文件、运行数据和日志；依赖目录以符号链接复用项目现有锁定环境。交付前须完成候选验证并按获准窗口整合到正式工作树。

## 计划与分工

- 后端事实读写、实例登记、合同和文档：Development 主实施者。
- Web 页面、双语文案及页面测试：Development 前端分工，限规格允许的 Web 文件。
- Alembic 后继和迁移测试：Development 迁移分工，限规格指定的新增文件。
- 精确运行目标、权限和窗口由协调者处理；独立 Verification 在 Development handoff 后开始。

## 当前状态

候选源码、定向离线检查、前端构建与浏览器夹具、任务专属 schema 的真实 MySQL 验证以及正式 dev 的 Alembic 切换和只读复核已完成，现交独立 Verification。Human Owner 最终验收尚未发生。

### 候选范围和数据合同

候选将 `plc_facts_samples_v2` 改名为 `plc_facts_history`，继续每份 PLC/DB 样本一行；`plc_facts_latest_points_v2` 改名为 `plc_facts_latest`，继续每点一行。历史新增可空 `source_type`，`group_id` 和 `config_revision` 可空；新迁移使用 `4e6a8b0d2f14`，原 Alembic 文件未修改。私有配置要求独立 `instances` 登记；DAA 的组和版本必填，外部来源可省略或传 null。原字节摘要、事务回执和按来源代次及序号更新最新值的规则保留。MySQL 对超过 `VARCHAR(8)` 的尾空格输入可能先截断再检查；应用配置严格匹配两种源类型，HTTP 请求不允许提供来源类型。

实时列表新增可独立省略 PLC、DB 和点搜索的分页入口，以及原 latest 的精确 `pointId`；历史范围也支持可选 PLC、DB。授权 PLC/DB 对在 SQL 计数和分页之前约束，实时源分类来自实例登记，历史来源由持久化快照提供。Web 两页默认查询授权范围，并展示 PLC、DB、来源；历史默认最近 24 小时，保留问号帮助与列宽记忆。新增 r2 合同三工件，原三工件保留原字节；历史组、版本和来源允许 null，旧严格读取方需适配。

### 源码和运行验证

- `backend/` 使用候选模块路径、合成环境和 `/private/tmp` 测试目录，`uv run --offline --frozen --no-sync python -m compileall -q app/plc_facts` 通过。执行规格列出的八个后端定向文件：`uv run --offline --frozen --no-sync python -m pytest -q -m no_db tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py tests/test_acquisition_facts_migration.py tests/test_legacy_acquisition_retirement.py tests/test_mapping_migration.py tests/test_equipment_temperature_migration.py tests/test_business_integration_migration.py tests/test_business_integration_storage.py`：142 passed、3 skipped，退出 0。两项分别为历史固定 BE-012 B runner 和 BE-003 旧源码测试；另一项为须显式打开任务 MySQL 的新集成测试，已在真实任务库单独通过。
- 用户随后明确使用现有 dev 库。协调者在 `127.0.0.1:3307` 同一 MySQL 8.4.6 创建本任务独立 `arch_acq003_dev_{upgrade,renamed,altered,guard}` 和 `arch_acq003_qa_{upgrade,renamed,altered,guard}` schema 与各自限定账号；账号访问 `industrial_level_2_system` 均被拒绝。首次授予测试权限因客户端参数格式化拒绝而退出 1，核对后使用参数化 SQL 完成，业务 schema 未改。初次沙箱 localhost 被拒后，以已授权提权通道运行测试。
- 迁移分工通过项目 `uv` 在四个 dev 专属 schema 运行 `tests_mysql/test_acquisition_facts_r2.py`：6 passed，退出 0。覆盖非空前驱升级及数据/键/索引/自增对账、RENAME/ALTER 中断恢复、错误目标、依赖、锁超时及限定来源回填事务回滚。首次真实演练暴露驱动结果转换和字符集排序规则问题，修复后上述结果重跑通过。`dev_guard` 已释放用于协调者备份恢复演练，`dev_upgrade` 已释放并用于本任务集成验证；QA 专属 schema 当时未动。
- 在 `dev_upgrade` 以显式 `ARCH_ACQ003_LIVE_READ_WRITE=ACQ003-ISOLATED` 和私有合成目标环境运行 `tests/test_acquisition_data_browse.py::test_mysql_authorized_ingest_browse_and_cleanup`：1 passed，退出 0。覆盖 DAA/external 提交、相同正文重复回执、遗漏改 null 的 409、身份冒用及无效凭据、迟到水位和缺点补入、单点大小写、REAL 精度、多 PLC 交叉授权分页与字面搜索、历史未记录来源、吊销令牌后读取，以及合成到期数据的 cleanup plan/apply 与字节预算。连接前校验任务账号、专属 schema、server UUID、版本、时区与 revision。
- `frontend-js/` 使用 `pnpm_config_verify_deps_before_run=false pnpm check:modules`、`pnpm_config_verify_deps_before_run=false pnpm test:modules`、以及合成空角色配置的 `pnpm build`：模块检查和构建退出 0，测试 55/55 通过。仅有常规 chunk 大小提示。
- 本任务候选文档的相对链接检查无缺失；被排除在隔离副本之外的现有规格链接以正式仓库目标核对。
- Chrome 157 本机隔离夹具通过中文浅色 1280 和英文深色 390 的两页默认查询、DB 并集和切换、来源及详情、长标识、搜索和 7 天边界。历史标题问号另复验为可见 24×24，hover/focus/触摸均展开时区及保留说明，Escape 可关闭；无 pageerror。截图和夹具位于候选根，测试 Vite/Chrome 已关闭。首次候选 Vite 在共享 node_modules 的 `.vite` 下生成一个自有 deps_temp 缓存，分工已回收该缓存；未停止用户的 5190 进程。

### 候选清单与后续

40 个交付文件及对应基线/候选 SHA 已存入 [脱敏交付清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest.json)，不含真实配置和协调索引。基线快照中前端两个文件的摘要采集与分工并行重叠，已从正式工作树补采并在 [baseline-supplement.json](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/baseline-supplement.json) 标识；正式集成前已逐项核对。三份原 v2 合同和既有迁移冻结摘要也已持久化到该 ignored 证据目录。候选、浏览器夹具、截图及专属测试 schema 当前供独立验证使用；最终接受后由协调者按实际占用清理。

### 3307 dev 切换及初步核对

协调者已用 `dev_guard` 实际恢复原 dev 两表备份，并对账两表各 2 行、原列摘要、建表语句与自增水位。正式切换首轮在发送信号之前发现原 8000/5190 进程已退出，故该轮仅写入私有备份，未写 schema、源码或 profile，也未向任何进程发送信号。再次核对监听、两原表、66 张其他表及备份后，先整合 32 个非 Web 文件，在正式 backend 项目 `uv` 环境执行 `python -m alembic upgrade 4e6a8b0d2f14`，退出 0；再替换 mode 0600 的私有 profile，整合 8 个 Web 文件，以原项目入口恢复 8000 后端及 5190 前端。

两张事实表各 2 行、历史自增水位 5，原列操作证据前后 SHA-256 同为 `34bfc1f0dbe765c4e2f9927ba4a76a0e87fe605d102de6bca87d2d3aef697ef1`；66 张其他表的行数、DDL 与 checksum 一致。旧表名已缺席，旧历史 `source_type` 均保留 NULL，本次没有历史来源回填 DML。正式 40 文件及 13 个冻结文件的 SHA 均与候选/基线相符。新 profile 按已核实的模拟实例登记为 `external`，原凭据、来源和读范围保留。

通过 8000 只读检查原 options/latest/history/detail 四项均为 200，剔除新增 `sourceType` 后与切换前原响应摘要一致；无 PLC/DB 筛选的实时及历史各 2 行，精确点位命中 1 行、缺项 0 行，越权筛选 403。Chrome 独立上下文只读复验中，两页无 PLC/DB 时各发一次首屏查询、各显示 2 行，标题帮助可见；实时显示「外部程序」，历史显示「来源未记录」，详情包含来源实例，默认历史窗口为 24 小时。历史详情首轮私有夹具断言误用精确裸文本，页面实际显示带字段标签的文本；修正夹具后重跑退出 0，没有修改源码。

正式同步 `target_now` 护栏通过。monitor、equipment、performance 三个业务 integration 均仍为 enabled=false、unadopted、空 adoption 文件。DAA、SMA 和业务模块未改。

协调者已将脱敏切换、恢复演练、只读 HTTP/Web、目标护栏、隔离证明和截图共 11 个文件保存到 `backend/data/maintenance-evidence/arch-acq003-r2-dev3307/`；`dev-operation.json` SHA-256 `467b0202905364fbd9d9b3e85afc08e4cd11dfa66f1598ec3912bde1e4296164`。真实私有 profile 和两表备份未复制到仓库，备份存于既有 profile 同级、权限 0700 的任务目录，文件权限 0600，留供验收与恢复。

## developer_handoff

- 精确范围：Human Owner 批准 ARCH-ACQ-003 r2，包含 2026-11-11 补记的同实例 dev/QA 专属 schema 运行授权；当前规格 SHA-256 `3133b706f2b16ede3ef675399ea138e626b77bdeef8459820369970371e2e5c1`。
- 工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的当前未提交源码。协调者核对 40 个交付文件与隔离候选逐项一致，已有其他并行修改保留；未提交、推送或发布。候选与逐文件摘要见上文清单，QA 应验证正式源码与其一致性。
- 自检：上述 142 passed / 3 skipped 离线、迁移真实 MySQL 6 passed、真实写读和清理综合 1 passed、前端 55 passed/构建及实际浏览器、正式 dev 四类读取与独立浏览器只读核对。历史 BE-012 B 和 BE-003 固定旧源码测试未在新候选中重跑；本任务不把前述独立任务改为最终验收。
- 资源：`/private/tmp/arch-acq003-r2-candidate-JhGlNhmC` 是经验证的公开候选及浏览器夹具；`/private/tmp/arch-acq003-r2-coord-yvB04ebp` 是协调者持有的私有运行材料和临时证据。`arch_acq003_qa_*` 四个空 schema 与独立 QA 账号留给 fresh-context Verification；`arch_acq003_dev_*` 及候选暂留作复核、备份恢复和证据用途。协调者在验证和最终接受后按实际依赖清点并回收本任务资源，持久化脱敏必要证据。当前用户 8000/5190 服务为切换后恢复的项目入口，不属于可随意回收的临时服务。
- 下一步：由新建 fresh-context Verification 检查精确 spec、正式工作树与候选、任务自检和独立 QA schema；依据结果写入 checklist。QA 结论不等同 Human Owner 最终验收，也不启动 DAA。

## QA1 返工与再次交接

独立 [QA1](checklist.md) 于 2026-11-11 对首份 handoff 给出 `qa_failed`，唯一失败项为 AC04 / QA-F01：实时浏览和历史接口在极大有效页码 `page=1000000000000000000000000` 时把超出 MySQL 范围的 offset 送入数据库，返回 503；规格 R06 要求超页返回空项和实际总数。QA1 原记录 SHA-256 `496b901f3f455a2425b38eea64fae5c4b4399d41b3261340930beb7d22c1ef1e`，不覆盖原 verdict 与证据。

在独立公开候选 `/private/tmp/arch-acq003-r2-candidate-qa2-92fLZKdv` 仅修改 `backend/app/plc_facts/crud/async_v2.py` 与 `backend/tests/test_acquisition_data_browse.py`。两种查询均先执行已授权范围计数；若 `(page - 1) * page_size >= total`，直接返回该总数与空列表，不再发送超范围分页 SQL；正常页仍按原条件和排序分页。补充两种接口的空结果、正常页、恰好越界、极大页和 HTTP 信封回归，检查极大页仍有正确 total、page 和 totalPages。

测试先在旧实现重现：定向新用例 7 failed、4 passed；修复后项目环境 `uv run --offline --frozen --no-sync python -m compileall -q app/plc_facts` 退出 0；`uv run --offline --frozen --no-sync python -m pytest -q -m no_db tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py` 退出 0，83 passed、2 skipped。两项跳过分别为固定旧 BE-012 B runner 和须显式授权的真实 MySQL 集成；两者范围与首份交接一致。

QA1 记录完成后，协调者按首份候选原摘要在正式源码中只整合上述两文件，核对 40 个正式交付文件及原 13 个冻结文件。正式 8000 自动重载后，以实际已登录范围只读复验两个接口：极大页均返回 200、`items=[]`、`total=2`；`page=2&pageSize=1` 均返回 200、一项及 `total=2`。证据 [dev-http-qa2.json](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/dev-http-qa2.json) SHA-256 `f11306133bc81c0b1b56f5d489e668d43f457604ccd58dd1f6c0e1e93d25b500`。没有重复迁移、写入 schema/profile 或改动 Web。

重新交付的完整 [40 文件清单](../../backend/data/maintenance-evidence/arch-acq003-r2-dev3307/delivery-manifest-qa2.json) SHA-256 `6ff79de385309b86753d1c549626a503120fd177f315dc836bb6e52afa697a76` 保留 QA1 与新候选逐项摘要。改动文件摘要如下：

| 文件 | QA1 候选 SHA-256 | 返工后 SHA-256 |
| --- | --- | --- |
| `backend/app/plc_facts/crud/async_v2.py` | `6f04c2bded73a61c76f011352316dbc61039a3c6a707ceac3eea50f67153da6c` | `89483004833e50bd72893645e81fa7e2161975a8c3af5c4ee0306039e082442b` |
| `backend/tests/test_acquisition_data_browse.py` | `03a46892f9fc457c4a85a760ad256d5376785dce92388b1e44cd6db7f58a5a23` | `79e605ad7eac8316619c50cec3ec207343972edae58c370a59eebe50618b19e4` |

**Development 重新交接：** 当前正式工作树、上述完整清单、返工候选、自检与 QA1 原证据交新建 fresh-context QA2。两个候选和 QA 专属资源保留供独立验证，回收由协调者按其依赖处理。Human Owner 最终验收仍待 QA2 后独立作出，DAA 未改动。
