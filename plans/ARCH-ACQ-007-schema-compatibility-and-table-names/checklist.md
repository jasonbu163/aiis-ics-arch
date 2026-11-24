Task ID: ARCH-ACQ-007
Revision: r2
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 采集事实运行结构兼容及三表命名
Owner: AIIS ICS Architecture Backend / 采集数据模块 Human Owner
Acceptance Chain Reference: spec.md 第 6 节及 Development Lifecycle Workflow
Related Task: ARCH-ACQ-004 r3, ARCH-ACQ-005 r1, ARCH-ACQ-006 r1, aiis-ics-arch.aw.sma::SMA-008 r3

# ARCH-ACQ-007 r2 独立验证

**Verdict 为 qa_passed。** 本结论仅覆盖指定隔离候选。Human Owner 已随后完成最终验收，见末节。

## 候选与复核命令

在 fresh context 独立读取本次交接。规格 SHA-256 为 `1b4b2b44fc7676831d1332817ded3d215a78b50ab9edd0d8b3b7350a688717b7`，Development 记录为 `228b3064c80b6fdee5df032508b436d9ff90de8aa282950c8bd994c9fb53b55d`。以下命令在 `/private/tmp/arch-acq-007-r2.Oz9DlE` 执行。使用候选源码、项目锁定环境、合成凭据和 ASGI 测试入口。MySQL 启动器内的 fixture 角色名固定为 dev，本轮由独立 Verification 在 Development 释放实例后执行，使用独立 pytest 目录。

| 独立检查 | 观察结果 |
| --- | --- |
| `shasum -a 256 arch-acq-007-r2*`，按清单逐项复算 baseline、candidate、交付工作树对应路径，`git -C baseline apply --check --whitespace=error-all ../arch-acq-007-r2.patch` | 补丁 `48790ed3bac404c0635f3aa8ae46d02106f12baf71eaab1cccc1bbda5ce3f848`，清单 `9b7ffa42564214bb73d098b4993582b7695d49121b81e979bf2e79f21cf230a0`。35 项匹配，正式产品路径仍为基线，补丁可应用。历史迁移差异仅限获准脚本，plc-facts-v2 已发布 JSON 字节一致。 |
| `./offline/run alembic heads`；`./offline/run python scripts/plc_facts_maintenance/main.py --help` | 唯一 head 为 `a1c307f8d2e4`，维护入口显示三个子命令。 |
| `./offline/run python -m pytest -q -p no:cacheprovider --basetemp /private/tmp/arch-acq-007-r2.Oz9DlE/qa-offline -m no_db`，追加 tasks.md「r2 DEV self-check」命令内相同的 14 个测试文件 | 249 passed，3 skipped，18.31 秒，退出 0。两条冻结历史用例及一条有独立 fixture 前置条件的用例跳过。 |
| `./mysql-test/run bd735869-e7ba-11f1-bc50-4a1e65dec043 -p no:cacheprovider --basetemp /private/tmp/arch-acq-007-r2.Oz9DlE/qa-mysql` | 沙箱首次连接被拒，退出 1。针对同一入口放行后，启动器核对 127.0.0.1:33407、指定 UUID、8.4.6、时差 +28800 秒，通过完整 tests_mysql/test_acquisition_consumption.py。19 passed，90.13 秒，退出 0。 |
| `./mysql-test/run bd735869-e7ba-11f1-bc50-4a1e65dec043 preflight-only` | 退出 0。仅余四个系统库，任务临时 DML 账号为零。已通知协调者回收专用实例、卷、凭据和两个 QA fixture 目录。 |

## 验收证据

| 标准 | 结果 |
| --- | --- |
| AC01 已有库前向升级 | 从同一源码构造含活跃与退役来源代次、历史和最新事实以及消费状态的已布库。前驱 f0a2b4c6d8e1 升级后，九张表的行及索引快照均与升级前一致。临时冲突对象、部分改名和错误触发器阻止切换，正确切换后 history 拒绝直接修改与越权删除。 |
| AC02 无关迁移后的读写 | Alembic 创建与采集独立的表并推进到 eeeeeeeeeeee。旧 profile 文件内容保持逐字节一致。在线 DML 账号完成来源登记、查询和删除，样本创建和 duplicate，latest、history 列表和详情、消费及采集证据读取。维护携实际版本通过。错误 UUID、库名及时钟在实库拒绝，MySQL 版本不兼容由离线用例验证。管理路由使用合成管理员依赖，设备观测自身对无关后继继续拒绝。 |
| AC03 不兼容时拒绝及事务保护 | 六组实库故障分别破坏表、列、类型、唯一索引和 ready 状态。latest 与 POST 均返回 503，检查 history、latest、事件及流无部分写入。在线 DML 账号无 TRIGGER 权限。移除追加守卫或破坏既有事件时，写入或重复请求拒绝，水位保持。 |
| AC04 原有消费和维护语义 | 同流并发、回滚/重试、来源代次失配、租约、pending、ACK、受控清理及过期缺口用例通过。迁移维护端拒绝触发器错表、时点、事件、正文和不可见元数据。维护 CLI 的正确实际版本计划成功、旧版本非零退出。 |
| AC05 空库全链 | 独立随机空库先断言无表，再单次执行 Alembic upgrade 至 a1c307f8d2e4。日志覆盖根节点及 6a8c0e2b4d16 → 7b9d1f3a5c7e，终态旧三名消失，九表齐备、ready=1。已有库场景另核验历史旧名登记表定义及归并行。历史脚本保留原 revision 与前驱，固定定义脱离现役 ORM。全程使用同一候选。 |

## 限制与交接

独立验证未发现阻塞。测试通过 ASGI 与隔离数据库执行。外部报表、客户直查 SQL、表级授权和在途写入仍需目标 Owner 在实际切换前盘点并停写。MySQL DDL 中断须核对实际表名、触发器、版本与备份再决定恢复路径。截至独立 QA 交接，正式采用、真实数据库迁移、服务切换和私有配置变更均未执行。QA 仅提交本清单给 Human Owner。

## Human Owner 最终验收与 dev 采用记录

Human Owner 明确表示「验收 ARCH-ACQ-007 r2」，并授权合入正式代码和使用 Alembic 迁移 dev 库，要求保留数据、保持私有配置原样，8000 由本人启动。依此登记最终状态 `owner_accepted`。原独立 QA verdict 为 `qa_passed`。

以下为协调者的执行记录。正式工作树中补丁涉及的 35 个路径逐项匹配已验证候选的 SHA-256。dev 上 Alembic 从 `f0a2b4c6d8e1` 升至 `a1c307f8d2e4`，退出 0。迁移前后九表行数、校验和、索引及三个触发器对账一致，保留来源登记 3 条、历史事实 108 条、最新点位 8 条。备份位于仓外权限受限目录。私有配置保持原样，8000 未启动。本次登记依据协调者交接，Verification 未连接 dev 库复测。

## dev 环境手动联调记录

2026-11-24（Asia/Shanghai），Human Owner 在 dev 环境手动联调并回报以下结果。此条为操作者现场记录，任务状态沿用 `owner_accepted`，独立 QA 结论沿用 `qa_passed`。

1. DS 的 `DEV-PLC-A` 模拟 DB21。DAA 使用已登记的 PLC 标识 `PLC-DEMO-01`、实例标识 `DAA-DEMO-01` 和来源代次 `g1` 上报，样本 `772d032e-ede2-4727-8e94-b95d7e46724d` 收到 `committed/created` 回执，DAA 显示 `acknowledged`。
2. 在 Web 采集历史中按同一 sampleId 查到该样本，点值和质量与上报一致。
3. 在 Swagger UI 模拟 SMA 查询，调用 `GET /api/v1/acquisition-data/latest`，参数为 `plcId=PLC-DEMO-01`、`dbNumber=21`。响应为 HTTP 200，PLC 标识、实例标识及来源代次均与登记匹配。三个点均关联上述 sampleId，点值和质量一致。

SMA 客户端待其读取功能就绪后另行实测。按 Human Owner 决定保留该来源登记及 DB21 样本。本次仅追加记录，未复跑 QA、连接数据库或操作服务。
