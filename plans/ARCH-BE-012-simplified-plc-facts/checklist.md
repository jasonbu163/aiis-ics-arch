Task ID: ARCH-BE-012
Revision: r4
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3 的 A 源码验证独立通过。交 Human Owner 审批 B 的具体隔离操作。待两轮 B 证据及独立 QA 结论后进入最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Approved Spec SHA-256: 19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0

# 独立 Verification 第 1 轮

2026-11-10（Asia/Shanghai）。按 `verification` 角色在 fresh context 接收已批准的 [r4 spec](spec.md) 与 [Development handoff](tasks.md)，独立读取候选、diff、合同和测试输出。审查依据为项目 AGENTS、最近作用域文档、Development Lifecycle Workflow、project-governance、backend-arch、backend-script-tooling、i18n-workflow 和 code-document-indexer。角色 model/effort 配置为 `gpt-6.1-sol/xhigh`。

- 正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，候选是当前未提交源码。
- `tasks.md` SHA-256 `e8fcc930c8c58a3b54f96caf7bdc6b69d42459d4c5a28147f165f7e3a826b65d`。[37 项候选摘要](evidence/development-r4-source-hashes.txt)清单 SHA-256 `fbf11ead53653f128865123a9be34c3f7d9ce8df43d63dd1081bd965eeb1abe8`。正式树和隔离副本逐项复核全部一致。
- 合同工件 README EN `3f547862e36668dc819aea4cff46520b02c3ee9c10ce1226ccc9542db97a0334`，中文 `8d1f6044b14fac6d3963971f0aa681ee694c16e3a8afdb174dffe7837cdcfea5`，OpenAPI `6155d860806831624b9e20705e4ffb31a1b2c44b342fa6c96da72f8735dcaa2d`，Schema `77d770ee1f83aa115f43887baed1a6a56e7eaa5afa6e253b590d380f86002df0`，向量 `a7d9fbc43481c6024349cf16ff4fa60498161d423a99a1031ac7c45b4e943412`。
- 受限的正式后端、维护与合同 diff 对应 r4 allowlist。根树有并行未提交工作，Development 前的外部 diff/untracked 比对由协调者核验，本轮按交接逐文件锁定范围，未把整个工作树归入本任务。

## 环境与执行记录

macOS arm64，`uv 0.7.8`，项目锁定环境 Python `3.13.3`、pytest `9.0.2`。隔离副本以 Git 跟踪的公开文件及交接清单构造，排除真实 `.env`、数据、日志及项目 venv。命令在副本 backend 执行，从正式树复用锁定 venv。测试先以 `env -i` 清空继承配置，再装载公开合成环境。独立脚本在导入项目模块前拦截 socket connect/connect_ex/create_connection、SQLite connect、PyMySQL/aiomysql connect、SQLAlchemy Engine connect/raw_connection。仅收集 `no_db`，共享数据库夹具的 `no_db` 分支直接 yield。实际连接尝试均为 0。

```bash
cd /private/tmp/arch-be012-r4-qaA-yo3wd9tt/backend
env -i PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 \
  UV_CACHE_DIR=/private/tmp/arch-be012-r4-qaA-yo3wd9tt/uv-cache \
  uv run --offline --frozen --no-sync \
  --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend \
  python ../offline_qa.py tests/test_plc_facts_v2.py \
    tests/test_plc_facts_migration.py tests/test_plc_facts_maintenance.py \
    tests/test_business_integration_storage.py tests/test_business_integration_migration.py
```

- 定向回归 **80 passed，exit 0，11.50s**。驱动运行 `pytest -q -p no:cacheprovider -m no_db --basetemp=<QA 临时目录>/pytest`。
- 同一 uv/连接保护下运行 `python ../static_qa.py`，exit 0。核对 37 个摘要，编译 20 个 Python 文件，解析 3 个 JSON，检查 15 份 Markdown 的 195 个相对链接。Alembic 静态图唯一 head `2c4e6a8b0d12`，上一 revision `1b3d5f7a9c20`。源码 metadata 77 表，v1 `TABLES` 仍 7 张，F7 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。正常 `create_app(testing=True)` 有 v1 三路、v2 五路和旧 monitor 路由。正式树 `git diff --check` exit 0。
- 同一 uv/连接保护下运行 `python ../probe_qa.py`、`python ../cleanup_probe_qa.py`、`python ../runner_guard_qa.py`，均 exit 0。脚本断言实际缺陷如期复现。ASGI 请求走进程内 transport，清理时钟、SQL 锁读及代理选择均使用合成输入或替身。
- 旧冻结断言独立重跑。基准 HEAD 公开副本在新进程同跑以下两项 **2 passed，exit 0**。候选逐项新进程分别为 **1 failed，exit 1** 与 **1 passed，exit 0**。基准在已创建应用的进程内改 manifest 再创建应用，仍保留缓存的 v1 路由。分别保留为已批准装配变化与基准内存重组行为，不计作候选通过。
  - `tests/test_plc_facts_compatibility.py::test_isolated_owner_has_no_permissions_dependencies_or_projection`。旧断言要求零权限、单 router，r4 明确增加读权限声明和第二 router。候选正常装配仍保留原 v1 三路，新权限不默认发给非 admin。
  - `tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes`。候选新进程禁用检查可通过。组合进程里的缓存行为单独对照基准，基准 F7 与候选一致。
- 扩展 `python ../offline_qa.py tests/test_plc_facts_*.py tests/test_business_integration_*.py` **539 passed、2 failed，exit 1，348.98s**，连接尝试为 0。失败项是上述旧冻结权限断言，以及候选新增 `tests/test_plc_facts_v2.py::test_normal_app_registers_routes_and_permission`。后者在定向通过，组合顺序下缺失 v1 三路。独立新进程按顺序只跑旧禁用断言、再跑新增装配断言，重现 **1 passed、1 failed，exit 1**。旧禁用测试先装配并缓存关闭 PLC facts 的 router，恢复 manifest 后新增测试仍消费该缓存。候选装配测试应隔离其组合状态。

## A 实现失败与复现

| 编号 | 规格 | 独立证据和结果 |
| --- | --- | --- |
| QA1-01 | R04、R06，AC02、AC04 | [write_sample](../../backend/app/plc_facts/services/async_v2.py#L46) 捕获重复键后先取 DB 时钟再执行 [带行锁身份查询](../../backend/app/plc_facts/crud/async_v2.py#L30)，返回重复成功前不再检查截止。令插入抛重复键、两次时钟读取为 `2027-02-09T10:00:02.119999`，锁读取匹配正文摘要并在 `2027-02-09T10:00:02.120000` 返回。结果为 `200 committed / duplicate`、无本次 commit。该时刻已达样本有效截止，合同要求 410 `expired_unconfirmed`。 |
| QA1-02 | R08，AC05 | 正常 app、无 Authorization 请求 `GET /api/v1/acquisition-data/latest?plcId=PLC-A&dbNumber=21` 为 401。增加同值第二个 `plcId` 后变为 422 `plc_facts_v2.invalid_request`。[路由包装器](../../backend/app/plc_facts/api/v2.py#L24)在登录依赖前拒绝重复参数。R08 对未登录请求规定 401。 |
| QA1-03 | R02、R09，AC01、AC07 | 将公开向量的 REAL 数值改为 JSON 数字 `1.234567890123456789`，该值可解码为有限 binary32。[parse_sample](../../backend/app/plc_facts/v2_domain.py#L139)接受后，历史字典及 typed 点的数值在写数据库前已变为 `1.2345678901234567`。历史 JSON 和 latest 都消费该舍入结果。r4 要求保留 DAA 上报的原数值精度。 |
| QA1-04 | R06，AC04、AC08 | [清理循环](../../backend/app/plc_facts/services/sync_v2_maintenance.py#L33)在取时钟/目标前检查预算，之后直接取带锁候选。替身给出进循环时 1.999 秒、目标核验返回时 2.001 秒，观察到此时仍发起 `candidates(..., lock=True)` 一次，实际清理 0 行。源码还在首次带 `FOR SHARE` 的目标核验之后才设置 InnoDB 行锁等待，并在循环外再次核验和查询最早截止。真实锁等待、元数据等待及命令处理时限尚无 B 证据。 |

## B 计划及入口审查

[tasks.md B 草案](tasks.md#b-隔离运行计划草案)分别列出 MySQL 8.4.6 容器、卷、网络、两个 schema、应用与迁移账户、UUID、loopback 端口和确认串。v2 入口的缺授权变量跳过、轮次/端口/alias/schema 配对、公开副本与默认关闭检查发生在导入数据库模块前。数据库 fixture 在写入前核验实际目标。以下项目影响可执行性或证据完整性。

| 编号 | 证据和待修条件 |
| --- | --- |
| QA1-B1 | [BE-010 runner](../../backend/tests_mysql/test_business_integration.py#L39)在 `1b3d5f7a9c20` 分支只接受 `arch_be010_r2_` 前缀。按 B 计划用 `arch_be012_r4_qa_upgrade` 和配对 ACK，以合成 `profile.json` 调用 `Target()`，在第 39 行、连接前拒绝。计划的两个 schema 均无法在上一 head 通过该 runner。后继分支的 `adoption()` 从 probe 自动生成同 revision 证据，也没有 runner 场景可直接证明旧证据在后继被拒。需准备仍受 UUID/端口/库名保护的两阶段八路复核。 |
| QA1-B2 | 草案先在 71 表采用 v1，再迁至 75 表，缺少在 75 表重新核验并确认三路可用的步骤。v1 运行时比较精确 revision，跳过这一步时，升级至 77 表前证据已失配。还需为正常 FastAPI 入口明确 v1 合成启用/范围/profile/HMAC、v2 enable、reader 角色授权和每个 schema 的进程环境。 |
| QA1-B3 | [B HTTP runner](../../backend/tests_mysql/test_plc_facts_v2.py#L118)只固定 URL，HTTPX 仍默认读取代理环境。离线在合成 `HTTP_PROXY=http://192.0.2.1:9999`、空 `NO_PROXY` 下，`127.0.0.1:18393` 选中 `AsyncHTTPProxy`。没有连接代理。B 需要显式封闭此路径，保证请求及合成凭据仅进入所批准的 loopback 服务。 |
| QA1-B4 | [负载入口](../../backend/tests_mysql/test_plc_facts_v2.py#L385)在积压归零时停止清理调度，即使 30 分钟发送仍在继续。CLI 逐轮 JSON Lines 仅检查最后一行成功，负载总结无行/字节、积压/滞后轨迹，也没有对照未到期行和值及 latest 水位重放。B 草案把剩余故障、并发、清理竞争和降级列为步骤，仍需准备时钟/故障注入、逐步护栏和可复现的断言，确保 AC04/AC08 的清理容量与原值不复现证据。 |

## 验收项和门禁

| 标准 | A 结果 | B 尚需的运行证据 |
| --- | --- | --- |
| AC01 | 400/512/513 点、正文上下限、分块及合法零值/空值有定向离线覆盖。REAL 精度失败 QA1-03。 | 正常 HTTP、两表零写入、两个 DB 与跨 PLC 的独立提交。 |
| AC02 | Service 持事务。正常提交、异常回滚、提交结果不明、同正文冲突检查有替身覆盖。跨截止重复确认失败 QA1-01。 | 独立连接同时看到两表、真实冲突、故障注入与并发重试。 |
| AC03 | 默认关闭、私有配置、按实例摘要及源绑定、版本/目标/时钟核验和按代次/序号的 MySQL upsert 已查。 | 真实旧新并发、重启、代次切换及水位。 |
| AC04 | 自然月/闰年和截止函数、维护计划与 apply 确认、按行版本条件清理已查。QA1-01、QA1-04 失败。 | 真实清理竞争、月末固定时钟、空跑心跳、物理清理和旧数据守恒。 |
| AC05 | 登录、Core 权限键与独立 PLC/DB 读范围，含 admin 显式范围、过期/越界详情及历史查询形状已查。未登录重复参数失败 QA1-02。 | 真实登录、跨权限、排序、分页、过滤和原值对账。 |
| AC06 | 唯一迁移、两表 Model 与 DDL 对照、空/非空降级替身、v1 三路及 71/75/77 profile、BE-010 精确证据匹配已查。 | fresh 和 upgrade 实库，旧 v1/BE-010 值、回执、F7、证据与降级，先解决 QA1-B1/B2。 |
| AC07 | 只有两张新增值表。五条公开路由、三件机器 JSON、双语说明及响应 Schema 对齐有离线覆盖。REAL 行为对照失败 QA1-03。 | 正常 HTTP 与发布工件全矩阵对照。 |
| AC08 | 清理预算失败 QA1-04。负载入口源码限制见 QA1-B3/B4。 | 2×1 Hz、64 点、30 分钟、P95 ≤500 ms、10000 行 15 分钟清理与完整守恒。 |
| AC09 | 候选和规范已锁定，独立 A 测试与失败证据在本记录。 | Development 与另起 fresh-context Verification 分别执行获批 B，并保存脱敏证据供 Human Owner。 |

**Verdict `qa_failed`。** 当前候选返回 Development，保留本轮证据。返工后锁定新的候选及 Development 自检和交接，由另一个 fresh-context Verification 复核。若返工改变范围、允许文件、验收或风险，回 PM 修订并重新批准。B 当前另有操作批准门禁。待计划和入口可执行后，由 Human Owner 单独批准具体 Docker、隔离库迁移/写入、故障、负载和回收动作。A 本轮无真实 DB、Docker、实际迁移、真实 HTTP 外连或现场证据。实际 dev 采用、发布与 DAA-010 独立排期。

## 资源与 Human Owner

QA 资源为 `/private/tmp/arch-be012-r4-qaA-yo3wd9tt`，内含公开候选、基准副本、离线脚本与输出、pytest 和 uv 缓存。验收证据以本文为准，可由协调者在返工/复核不再需要后回收。Development 自有资源见 [tasks.md](tasks.md#a-交接与限制)。本轮只新增本 checklist，未建立分支、worktree 或 commit。

Human Owner 最终验收待定。

# 独立 Verification 第 2 轮

2026-11-10（Asia/Shanghai）。以 fresh context 的 `verification` 角色消费同一已批准 r4 的新 Development handoff。基准 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，正式候选在未提交工作树中。独立核对根与最近作用域契约、生命周期、完整任务 bundle、实现、diff 与已记录的测试输出。复核涉及任务治理、后端分层、维护 CLI、稳定错误键和代码索引。

| 证据 | SHA-256 |
| --- | --- |
| [已批准 spec](spec.md) | `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0` |
| [返工后 Development handoff](tasks.md#qa1-返工-development-自检与-qa2-交接) | `cf2810ed9f7bf667c0582cbd303beb4d43596df72349ff8fab934fa6955b2749` |
| 第 1 轮原始 checklist | `a88457754cf580454703a1b9b60e663e64df03002830c0723145d473f8e77a61` |
| [返工后 37 项候选摘要](evidence/development-r4-qa1-fix-hashes.txt) | `f19a4d0829773cb20243263168a43bdabda4883dacacd8de3870f17e3615325f` |

正式树逐项校验 37/37 通过。临时公开副本的 35 项 backend/contracts 文件也逐项匹配。spec 与共享 `CODE_INDEX.md` 在正式树单独核对。五份合同工件与 QA1 记录的 SHA-256 一致。正式树 `git diff --check` 为 0。范围比对覆盖候选的后端、合同及索引差异，保留共享工作树上的并行改动。

## 环境、命令和结果

macOS arm64，`uv 0.7.8`，项目锁定 Python `3.13.3` 与 pytest `9.0.2`。独立副本为 `/private/tmp/arch-be012-r4-qaA2-UTAzhBSV`，从 Git 跟踪的公开文件和 37 项清单中的 backend/contracts 文件构造。副本无真实 `.env`、私有配置、运行数据或原项目 venv。以 `env -i` 开始，在导入项目模块前用公开合成环境，拦截 socket connect/connect_ex/create_connection、SQLite 三个 connect 入口、PyMySQL 与 aiomysql 驱动和连接方法、SQLAlchemy Engine connect/raw_connection。先定位副本模块，再加载项目测试。检查 `settings`、`app`、`database` 均从副本导入，两次 pytest 记录真实连接尝试 0。

```bash
qa=/private/tmp/arch-be012-r4-qaA2-UTAzhBSV
cd "$qa/backend"
qa_python() {
  env -i PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR="$qa/uv-cache" \
    uv run --offline --frozen --no-sync \
    --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python "$@"
}
qa_python "$qa/guard.py" --basetemp="$qa/pytest-core-safe" \
  tests/test_plc_facts_v2.py tests/test_plc_facts_migration.py tests/test_plc_facts_maintenance.py \
  tests/test_business_integration_storage.py tests/test_business_integration_migration.py
qa_python "$qa/guard.py" --basetemp="$qa/pytest-order-safe" \
  tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes \
  tests/test_plc_facts_v2.py::test_normal_app_registers_routes_and_permission
qa_python "$qa/probe.py"
```

- guard 对 pytest 固定传入 `-q -p no:cacheprovider -m no_db`，先把副本 backend 及 tests 放到导入路径。定向 **88 passed in 10.86s，exit 0**。指定顺序组合 **2 passed in 14.76s，exit 0**。QA1 旧冻结的 `manifest.permissions == ()`、只挂载 v1 的断言与批准的新增合同冲突，保留 QA1 的独立失败记录。QA2 的组合结果覆盖实际装配顺序，不代表旧冻结断言通过。
- 独立探针编译 20 个 Python 文件，解析 3 个 JSON 工件，检查唯一 Alembic head `2c4e6a8b0d12` 直接后继 `1b3d5f7a9c20`，未执行迁移。metadata 为 77 表，旧事实 `TABLES` 为 7，F7 为 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。MySQL 8.4 方言编译检查出现预期 `AS new` 与 `new.instance_id`。探针 exit 0 表示通过其复现断言，其中包含确认下述失败。Markdown 相对链接在写入 QA2 记录前核对 16 个文件、209 条、0 缺失。

## QA1 返工复核

| 项目 | QA2 观察 |
| --- | --- |
| QA1-01 | 原失败关闭。重复键后替身让身份行锁查询跨过截止，在锁返回后第三次取数据库时钟。结果 410 `plc_facts_v2.expired_unconfirmed`，本次 commit 次数为 0。 |
| QA1-02 | 原失败关闭。通过正常 FastAPI 应用和内存 ASGITransport，未登录的普通及重复 `plcId` 请求均为 401。定向回归同时验证已认证请求的重复参数为 422。 |
| QA1-03 | 原输入 `1.234567890123456789` 已保留。解析、存储表示和响应数字 token 对照一致，真实 MySQL 往返待 B。另有独立的 REAL 上界误拒，见 QA2-01。 |
| QA1-04 | 原失败关闭。替身让目标核验返回时为 2.001 秒，带锁候选和积压查询均为 0，`oldestKnown=false`。定向测试另覆盖跨两表查询停止、每批事务设置等待及 2000 行处理限制。真实锁等待、预算、积压和心跳仍须 B 计量。 |
| QA1-B1 | previous/successor 的合成精确成对 guard 和错配端口均有离线覆盖。后继入口已加入对三个 owner 的旧证据拒绝检查。计划所列实际命令仍有 QA2-B1 的导入隔离失败。 |
| QA1-B2 | 计划已写入 71→75 和 75→77 两次 v1 schema-only 再核验、分阶段环境与三路 HTTP 入口。独立用合成时钟运行 `legacy_batch(1)`，旧版 `prepare(BatchIn.model_validate_json(...))` 接受一条 cycle。正式验证须保存 77 表、再核验前以旧 v1 采用证据请求被拒，以及再核验后恢复三路的状态与守恒证据。 |
| QA1-B3 | 源码与离线用例核对 B 的 HTTPX 客户端均显式 `trust_env=False`。合成代理环境下没有代理 mount。丢 ACK 夹具的原始 socket 目标写为 `127.0.0.1` 和已核对端口。 |
| QA1-B4 | 受保护离线替身生成 30 次 tick，并在积压归零后持续记录。源码包含真实 CLI、逐 tick 文件、未到期哨兵、tombstone 重放、故障和降级入口。负载总结留存仍须处理 QA2-B2，实际容量和原值守恒待 B。 |

## QA2 新的失败

### QA2-01　可转为有限 binary32 的 REAL 被拒

R02、AC01、AC07。取公开样例，将 REAL 点的 `value` 换成不加引号的 JSON 数字 `340282356779733661637539395458142568447`。它是 binary32 按最近值舍入的溢出中点减 1。独立本机 `strtof` 直接从该十进制文本转换得到有限的最大 binary32，位型 `0x7f7fffff`。中点 `340282356779733661637539395458142568448` 及其加 1 均得到 infinity。候选先执行 `float(str(value))`，把第一个合法值舍入成精确的溢出中点，然后转 binary32，`parse_sample` 返回 422 `plc_facts_v2.invalid_request`。同样的两级转换还用于持久化和回读的 `real_number`。本次为纯解析和系统数值转换，未使用 DB。复核须覆盖中点前、相等、之后和负值对称边界，并保持有效 REAL 原数字 token。 [值校验](../../backend/app/plc_facts/v2_domain.py#L121) · [内部数值恢复](../../backend/app/plc_facts/v2_domain.py#L210) · [批准的 REAL 值域](spec.md#L47)

```python
import ctypes
import struct

strtof = ctypes.CDLL(None).strtof
strtof.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
strtof.restype = ctypes.c_float
mid = (2**25 - 1) * 2**103
token = str(mid - 1)
assert struct.pack('!f', strtof(token.encode(), None)).hex() == '7f7fffff'
assert float(token) == mid
```

### QA2-B1　B 命令会从正式树解析后端模块

§6、AC06、AC09。以 B 计划的脚本入口形态 `python tests_mysql/<探针>.py` 和 pytest 入口形态 `pytest -q -s --confcutdir=tests_mysql tests_mysql/<探针>.py`，在公开临时副本 backend 下复用锁定环境。用 `importlib.util.find_spec(name).origin` 探测三个模块，两个入口均定位到正式树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend`。该环境的 editable `.pth` 把正式 backend 路径加入 `sys.path`，文件启动时首路径为 `tests_mysql`，计划未将临时 backend 根显式放在正式树之前。`settings.resolve_env_file()` 按其模块文件位置定位 dotenv。因此计划中的实际 BE-010 和 v2 B 入口可能读取正式树的配置并验证另一份代码。探针只查找模块位置，未导入正式 settings 或读任何真实配置。保持相同锁定环境，给脚本命令显式传 `PYTHONPATH=<副本>/backend`，pytest 命令用同一 `PYTHONPATH` 加 `python -m pytest`，两者均解析到副本，exit 0。Development 需在待批准计划中固定隔离运行方式，并在每个子进程加载配置前检查实际模块来源。 [BE-010 命令](tasks.md#L163) · [v2 pytest 命令](tasks.md#L165) · [设置定位](../../backend/settings.py#L17)

### QA2-B2　按计划的成功负载输出缺少汇总证据

AC08、AC09。当前 B 计划使用默认捕获的 `pytest -q`，成功测试的 `load_complete` 标准输出不会写入该命令的普通测试日志。独立持久化的 `cleanup-ticks.jsonl` 记录清理而没有 P95、实际样本分布或发送失败汇总。B 入口和记录步骤须明确持久化脱敏负载总结，包括成功与失败、两 PLC 分布、正文大小、延迟及清理轨迹。未运行真实负载。 [负载总结](../../backend/tests_mysql/test_plc_facts_v2.py#L701) · [运行计划](tasks.md#L165)

## 当前验收和下一门禁

| 标准 | A 证据与未完成的 B |
| --- | --- |
| AC01、AC07 | 双上限、分块、值域、五条路由和合同工件有离线证据。QA2-01 为源码失败。真实 HTTP、两库号及跨 PLC 独立写入和 MySQL 精确 REAL 往返待 B。 |
| AC02、AC03 | 独立替身和旧面检查覆盖提交、未知结果、重复与截止、准入、顺序表达式。真实两表原子性、并发、故障、重启与代次切换待 B。 |
| AC04、AC08 | 原 A 截止及循环预算缺陷复查通过。真实锁、清理、守恒、完整心跳、容量及延迟待 B。QA2-B2 需补全可持久化负载证据。 |
| AC05 | A 鉴权顺序、角色权限和独立范围路径已复核。真实账号、读范围、分页和时间过滤待 B。 |
| AC06、AC09 | A 候选、迁移链、旧 profile 与独立运行已核对。QA2-B1 修复后，按获批精确目标分别运行 Development 与 fresh-context QA 的两轮隔离 B，留存迁移、旧数据及永久回执对账和故障证据。 |

**当前 verdict `qa_failed`。** QA2-01 与 B 交接缺陷返回 Development。返工后须提交同一获批范围内的新候选摘要和自检，再进行独立 A 复核。B 还须单独批准两轮具体容器、库、账号、端口、迁移、写入、故障、负载与回收操作，并实际取得各 AC 所需证据。QA2 没有连接 DB 或 SQLite、启动 Docker、执行 Alembic 迁移、发起真实 HTTP 或触达现场。现有 dev 库采用和 DAA-010 仍各有门禁。Human Owner 最终验收待定。

QA2 自有临时资源为 `/private/tmp/arch-be012-r4-qaA2-UTAzhBSV`，含公开源码、离线脚本、pytest 输出和 uv 缓存。关键证据见本文，协调者可在复核完成且无后续使用时回收。本轮项目写入限于本 checklist，未创建分支、worktree 或 commit。

# 独立 Verification 第 3 轮

2026-11-10（Asia/Shanghai）。以新的 `verification` 角色 fresh context 接收 QA2 返工交接，依据项目 AGENTS、最近作用域文档、Development Lifecycle Workflow、完整任务 bundle、候选 diff、合同和测试输出，复核同一已获 Human Owner 范围批准的 `ARCH-BE-012 r4`。本轮范围为 A 源码验证和 B 入口离线核验。

## 候选和验证环境

正式交付树为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，`main` 基准 HEAD `bcafa89fa31bdf62329bced89baebc193323a739`，候选为未提交工作树。下列摘要均独立比对。

| 输入 | SHA-256 |
| --- | --- |
| [已批准 spec](spec.md) | `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0` |
| [QA2 返工后 Development handoff](tasks.md#qa2-返工-development-自检与-qa3-交接) | `4f411b47bac74b0269f494148e419b1ccabdd7a78917a55786da27d089d51d61` |
| QA3 写入前的 checklist | `432b9366d8cac32b8ebe11269f7760b65181e013734dc771e5eb1c568b3f1415` |
| [37 项候选摘要](evidence/development-r4-qa2-fix-hashes.txt) | `cd77a9ee98b0a6b111ac2ae3132ccb01a7d9b84bad3b959408f17325a4fb23a2` |

`shasum -a 256 -c` 在正式树通过 37/37。后端和合同的 tracked diff 与 untracked 文件共 35 路径，与清单严格一致。相对 QA2 候选，清单内仅 `v2_domain.py`、新版离线测试和两个 B runner 的四个摘要改变，均在 r4 allowlist。五份合同工件摘要继续与第 1 轮一致。`git diff --check` exit 0，16 份 Markdown 的 221 条相对链接路径缺失 0。

macOS arm64，`uv 0.7.8`，Python `3.13.3`、pytest `9.0.2`。用 Git 跟踪的公开文件和当前清单构造 `/private/tmp/arch-be012-r4-qaA3-fltc5j47/source`，隔离副本 backend/contracts 的摘要通过 35/35，排除真实 `.env`、私有配置、运行数据、日志和项目 venv。从正式项目复用已锁定的依赖环境。每次定向执行先 `env -i` 清除继承环境，显式设置副本 `PYTHONPATH`，验证 `settings`、`database`、`app` 导入来源，再载入公开合成环境。审计钩子和连接入口保护阻断 socket、DNS、SQLite、PyMySQL、aiomysql、SQLAlchemy Engine 连接、子进程和正式树源码或 `.env` 读取。

```bash
qa=/private/tmp/arch-be012-r4-qaA3-fltc5j47
cd "$qa/source/backend"
qa_python() {
  env -i PATH="$PATH" PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR="$qa/uv-cache" \
    uv run --offline --frozen --no-sync --project /Users/jason/Desktop/DreamCode/aiis-ics-arch/backend python "$@"
}
qa_python "$qa/guard.py" --basetemp="$qa/pytest-core" \
  tests/test_plc_facts_v2.py tests/test_plc_facts_migration.py tests/test_plc_facts_maintenance.py \
  tests/test_business_integration_storage.py tests/test_business_integration_migration.py
qa_python "$qa/guard.py" --basetemp="$qa/pytest-order" \
  tests/test_plc_facts_compatibility.py::test_disabled_facts_module_only_removes_its_three_routes \
  tests/test_plc_facts_v2.py::test_normal_app_registers_routes_and_permission
qa_python "$qa/guard.py" --probe "$qa/probe.py"
```

- guard 对两次 pytest 固定传入 `-q -p no:cacheprovider -m no_db`。定向 **106 passed in 15.09s，exit 0**。指定顺序的装配组合 **2 passed in 20.87s，exit 0**。两次均为连接及正式配置读取尝试 0。先前扩展运行中旧冻结的零权限和单 router 断言与 r4 批准的装配变化冲突，继续保留其失败记录，本轮没有重跑扩展全量。
- 独立静态探针编译 20 个 Python 文件、解析 3 个 JSON，确认 Alembic 唯一 head `2c4e6a8b0d12` 的直接前驱 `1b3d5f7a9c20`。正常模型装配 77 表，旧事实 `TABLES` 仍为 7，F7 为 `sha256:1ba978ead14cd258b2b8a6d751997bd9c22cd2f55037caf421682ba9da20e0ed`。探针 exit 0，连接及正式配置读取尝试 0。

## QA2 失败的独立复查

| 项目 | QA3 结果 |
| --- | --- |
| QA2-01 | 通过。独立生成正负两侧、整数/定点/指数三种表示的溢出中点前、中点、后共 18 例，用系统 `strtof` 对照。中点前转换为 `0x7f7fffff` / `0xff7fffff`，候选接收并在两类内部存储表示及对外 JSON number 中保留原 token。中点和中点后转换为正负 infinity，候选以 422 拒绝，内部文本恢复也拒绝。QA1 的长小数精度、负零和小指数继续由定向测试覆盖。 [输入判定](../../backend/app/plc_facts/v2_domain.py#L114) · [存储恢复](../../backend/app/plc_facts/v2_domain.py#L218) |
| QA2-B1 | 离线通过。用 `python tests_mysql/qa3_origin_probe.py invalid` 在清洁环境中省略 `PYTHONPATH`，`find_spec` 三项均定位正式树，两个实际入口的来源护栏均在导入项目设置和连接前拒绝。用 `qa_python tests_mysql/qa3_origin_probe.py valid` 固定副本，三个来源均为副本，BE-010 停在刻意缺失的合成 `profile.json`，v2 停在刻意错配的合成目标护栏。两个探针按预期 exit 0，三个项目模块均未加载。另原样取 `tasks.md` 的 `be012_run` 函数，以 `0600` 仅含合成 `APP_NAME` 的脚本运行三处导入预检和无副作用 Python 命令，exit 0。v2 的迁移和维护子进程源码均显式传副本 `PYTHONPATH`。 [BE-010 护栏](../../backend/tests_mysql/test_business_integration.py#L15) · [v2 护栏](../../backend/tests_mysql/test_plc_facts_v2.py#L29) · [计划修订](tasks.md#b-启动方式修订替换前文所有-b-直接启动命令) |
| QA2-B2 | 离线通过。独立探针抽取负载与清理函数，注入合成时钟、HTTP 与清理替身。成功总结实际落盘 570 字节，尝试/成功/失败为 6/6/0，每 PLC 三份 64 点样本、正文大小汇总、P95 与 30 条清理 tick 均可读。给 PLC-B 注入 503 时，异常退出仍落盘 563 字节，尝试/成功/失败为 3/2/1，保留已完成的 1 条清理 tick。两份总结均不含注入的合成凭据标记，重复调用遇现有文件拒绝覆盖。 [清理轨迹](../../backend/tests_mysql/test_plc_facts_v2.py#L656) · [负载摘要](../../backend/tests_mysql/test_plc_facts_v2.py#L692) |

QA1 的已修复行为仍有本轮测试覆盖。重复键等待后按新时钟拒绝过期确认，鉴权先于重复参数校验，REAL 长精度 token 保留，清理预算耗尽后不取带锁候选。装配顺序回归通过。B 的合成目标护栏、v1 两次 schema-only 再核验计划、`trust_env=False` 和 30 条清理轨迹继续有当前源码或离线覆盖。

## 验收映射和交接

| 标准 | A 证据 | B 解除条件 |
| --- | --- | --- |
| AC01、AC07 | 复跑正文/点数双上限、分块、字段和值域、18 个 REAL 边界、五路装配及合同工件。 | 正常 HTTP 与合同对照。验证两表零写入、两库号及跨 PLC 独立提交、MySQL 精确 REAL 往返。 |
| AC02、AC03 | 替身覆盖持久提交后回执、回滚、未知结果、重复确认截止及准入、顺序。 | 在独立连接核验实际原子性，复现并发、丢回执、故障、重启、代次切换与水位。 |
| AC04、AC08 | 截止及预算回归通过。离线正反结果均可落盘，30 条清理轨迹可读取。 | 真实锁竞争、预算、旧数据及原值守恒。每轮 2 PLC 各 1 Hz、每份 64 点、持续 30 分钟，成功 P95 ≤500 ms、10000 行 15 分钟内清理，保存完整脱敏摘要和清理轨迹。 |
| AC05 | 正常 app 进程内覆盖登录优先、独立权限与范围、详情路径及授权边界。 | 真实账号、授权/越权、排序、分页、时间过滤和原值对账。 |
| AC06、AC09 | 候选、迁移图、77 张 metadata、v1 七表/F7 和 BE-010 精确证据回归，两个 runner 的隔离预检通过。 | 各轮分别执行空库全链和合成旧库 75→77、两次 v1 再核验、BE-010 三 owner 旧证据拒绝及八路新证据恢复，完成旧行、永久回执及降级守卫对账。保留命令、目标及脱敏证据。 |

**QA3 判定为 A 独立通过，r4 整体 `qa_blocked`。** 交 Human Owner 审批 [B 计划](tasks.md#b-隔离运行计划草案)及[启动修订](tasks.md#b-启动方式修订替换前文所有-b-直接启动命令)中的两轮具体 MySQL 8.4.6 容器、卷、网络、账号/权限、端口、schema、UUID 核验、迁移/写入、故障、负载和回收操作。批准后由 Development 和另起 fresh-context Verification 分别在各自可丢弃目标执行，并补齐上表证据。Human Owner 最终验收在独立 QA 完成后。现有 dev 库采用、发布、现场与 DAA-010 均依各自门禁。

本轮执行仅限 A 和 B 入口离线探针，连接数据库及 SQLite、Docker、Alembic 迁移、真实 HTTP、真实配置读取均为 0。QA3 自有临时目录 `/private/tmp/arch-be012-r4-qaA3-fltc5j47` 含公开源码、无敏感值的合成环境和离线探针、合成摘要、pytest 输出及 uv 缓存。关键证据已写入本文，协调者可在确认无后续使用时按生命周期回收。本轮项目内只更新本 checklist。


# 独立 Verification：现有 dev 功能验收

2026-11-10（Asia/Shanghai）。Human Owner 本轮授权开启现有 dev 的采集 v2，以模拟样本验证上报、去重回执、最新值与历史查询，后端验收完成后再接 DAA。独立 `verification` 角色在 fresh context 消费 r4 任务 bundle、正式树候选及测试记录。正式树 HEAD 为 `bcafa89fa31bdf62329bced89baebc193323a739`，已批准 spec SHA-256 为 `19adbe990cfcc7faf296e296f476f8cf0440dac1c538c0817629be1c405c76b0`。含 dev 迁移记录的 [Development handoff](tasks.md#实际-dev-库-alembic-迁移记录) SHA-256 为 `181617b2856d94a34c6b6086dae21c03ae4120ca89fe3963852414bbc4c92057`。[最新 37 项候选摘要](evidence/development-r4-qa2-fix-hashes.txt) SHA-256 为 `cd77a9ee98b0a6b111ac2ae3132ccb01a7d9b84bad3b959408f17325a4fb23a2`，`shasum -a 256 -c` 通过 37/37。追加前 checklist SHA-256 为 `788b78b4fffe5b986e5f46046b2cdf9b7e922efe8d4f78d110b487d308b4906a`。

## 环境和方法

在正式 `backend/` 目录使用项目锁定的 Python 3.13.3，以 `PYTHONDONTWRITEBYTECODE=1 uv run --offline --frozen --no-sync python -` 从标准输入执行独立验收探针，退出码 **0**。HTTP 使用已运行的 `127.0.0.1:8000`，HTTPX 禁用代理环境及重定向。独立 SQLAlchemy 连接用 `SET SESSION TRANSACTION READ ONLY` 和 `START TRANSACTION READ ONLY`，确认连接为 `TESTING=False` 的 `127.0.0.1:3307`、MySQL 8.4.6、schema `industrial_level_2_system`，server UUID 匹配指定目标，Alembic 唯一 revision 为 `2c4e6a8b0d12`，实际会话偏移为 +28800 秒。本次预检数据库时间 `2026-11-10T21:56:49.308915+08:00`，模拟实例及 PLC/DB 范围的两表均为 0 行。

范围为模拟 `PLC-BE012-DEV-441247C3 / DB21`、实例 `be012-dev-smoke-441247c3`、代次 `be012-dev-gen-441247c3`。样本正文在发送前以 `0600` 临时文件冻结，原样重传直接读取同一文件，成功后临时正文自动移除。登录及机器凭据只在验收进程内使用。

## 实测结果

| 验收映射 | 观测结果 |
| --- | --- |
| AC01、AC02、AC07 · 新样本及去重 | `POST /api/v1/integration/plc-facts/samples` 发送 `be012-dev-441247c3-102`，HTTP 200 `committed / created`。同字节重传返回 HTTP 200 `committed / duplicate`，独立 SQL 仍见 1 条历史、2 条逐点最新值，历史 ID 为 `1`，落库正文摘要与冻结字节的 SHA-256 匹配。 |
| AC02 · 同身份内容冲突 | 将同 ID、同序号的温度改为 821.5 后发送，HTTP 409，错误键 `plc_facts_v2.sample_content_conflict`。只读对账仍为 1 条历史、2 条逐点最新值，已提交样本和值保持原状。 |
| AC03 · 较旧样本补传 | `be012-dev-441247c3-101` 以较早采集时间、`799.25 / true` 补传，HTTP 200 `committed / created`。补传后逐点 latest 的来源序号仍均为 `102`。 |
| AC05 · 登录和权限 | 现有 admin 与 operator 分别通过 `POST /api/v1/auth/login` 登录，均 HTTP 200。Admin 的 `GET /api/v1/acquisition-data/options` 返回 HTTP 200，仅有该模拟 PLC 的 DB21。同一路由未登录为 HTTP 401，已登录 operator 为 HTTP 403。 |
| AC05 · 最新值 | Admin 的 `GET /api/v1/acquisition-data/latest` 返回 HTTP 200、2 点。两点均来自序号 `102`，`furnace_temp` 为 REAL 数字 `820.5`，`heating_ready` 为 BOOL `false`。对应点观察时间为 `21:56:44.308915+08:00`、`21:56:44.313915+08:00`，来源实例、代次及样本 ID 对账一致。 |
| AC05 · 历史及详情 | Admin 的 `GET /api/v1/acquisition-data/history` 返回 HTTP 200，上海半开区间 `[2026-11-10T21:56:24.308915+08:00, 2026-11-10T21:56:50.308915+08:00)` 内恰有 2 条，页码 1、页长 50、总页数 1。顺序为 `102 → 101`、历史 ID 为 `1 → 4`，样本时刻分别为 `21:56:44.313915+08:00`、`21:56:24.313915+08:00`。 `GET /api/v1/acquisition-data/history/1` 为 HTTP 200，摘要及完整两个原值点与上报相符。 |
| AC02、AC03、AC09 · 独立只读对账 | 按实例及 PLC/DB 双向限定范围，`plc_facts_samples_v2`、`plc_facts_latest_points_v2` 最终各 2 行。两条历史各 2 点，样本 ID、代次、采集时间、正文摘要与两份冻结样本相符，历史 ID 与 HTTP 一致。两条 latest 均为 `102`，原值为 `820.5 / false`。 |

## 判定和交接

**现有 dev 的指定功能验收通过。** 保留该模拟来源的两条历史和两条逐点最新值供 Human Owner 查看。该轮覆盖上述 AC 的功能子集。r4 整体仍为 `qa_blocked`，双轮隔离 B、完整故障和兼容矩阵、清理与 30 分钟容量验证待执行。QA 期间未执行 DDL、直接 SQL 写入、用户创建、样本清理、Docker、后端重启、DAA 或部署。项目文件只追加本 checklist。将本次功能证据交 Human Owner，最终验收待定。
