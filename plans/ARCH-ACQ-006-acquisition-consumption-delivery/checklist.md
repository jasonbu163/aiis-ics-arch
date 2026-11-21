# ARCH-ACQ-006 r1 独立验证

Task ID: ARCH-ACQ-006  
Revision: r1  
Role: Verification（fresh context）  
Verdict: qa_failed  
Handoff: Development

## 候选与环境

交接清单 SHA-256 为 `c9848d0ec7669666e335a02fb092c1bdf6d36d7bcfb9e220c878b334ee73e39f`。从 tasks.md 的 text 代码块提取原始清单，重算清单及 35 个工作树文件的 SHA-256，35/35 匹配。按 spec §5 复核候选路径，包括公共存储 revision 守卫和已有迁移回归。已发布 plc-facts-v2 JSON 对 HEAD 无差异。共享工作树还有其他任务的改动。

在私有临时副本中使用项目 backend/.venv/bin/python（Python 3.13），排除 .env*、.local、数据库文件、日志、缓存及虚拟环境。隔离 MySQL 8.4.6，角色 qa，127.0.0.1:55794，UUID 28171ac7-e3ea-11f1-b476-8206efe6a29b，数据库时区偏移 +28800 秒。fixture 每次连接核对目标，使用随机 schema；HTTP 通过 ASGI transport。临时源码及字节码由 Verification 回收，实例和私有凭据由协调者回收。

| 独立命令（在副本 backend 下执行 Python 命令） | 结果 |
| --- | --- |
| python -m compileall -q app/plc_facts alembic/versions/20261119_1500_da6c32f8a701_acquisition_consumption.py tests_mysql/test_acquisition_consumption.py tests/test_acquisition_consumption_contract.py | 退出 0，字节码独立存放 |
| python -m pytest -q -p no:cacheprovider tests/test_{acquisition_consumption_contract,plc_facts_v2,acquisition_data_browse,acquisition_source_registry,legacy_acquisition_retirement,generic_task_migration_r3,mapping_migration,equipment_temperature_migration,observation_retirement,business_integration_storage}.py | 188 passed，10 skipped，14.87 秒 |
| python -m pytest -q -p no:cacheprovider tests_mysql/test_acquisition_consumption.py | 4 passed，18.72 秒，退出 0；按 tasks.md 设置 qa 精确目标及确认串 |
| git diff --check；git diff --exit-code HEAD -- 'contracts/published/http-api/plc-facts-v2/*.json' | 两项退出 0 |

## AC 复核与返工

| AC | 已观察到的结果和缺口 |
| --- | --- |
| 01 | 通过。同流第二个请求等待，异流在第一事务释放前提交；延迟采样时间、duplicate 与事务回滚的事实和事件数符合预期。 |
| 02 | 部分通过。独立 MySQL 完成历史截止、过期排除、原三表对账、停写确认守卫、触发器冲突和恢复。实现缺陷见下。 |
| 03 | 部分通过。两种起点、中间过期、清理后 410 和重复创建均有证据。test_origin_retained_now_and_midstream_gap 先 await 完整写入，再 await 创建，再单独写入；未验证规格要求的创建与写入实际重叠。 |
| 04 | 通过。删除源后旧事实仍可读，旧 POST 被拒，重新登记接续流序号；目标换代后既有 pending ID 和游标保留。 |
| 05 | 部分通过。竞争测试得到一项成功、一项 409，旧租约被拒。测试仅对 run-state 注入提交前故障，对创建、续租、pending、目标 POST、ack 注入提交后故障。获取与释放租约的故障重放以及各写操作的双侧故障矩阵未覆盖。 |
| 06 | 部分通过。真实目标回读一条、同字节重试 duplicate、ack 未知后重放均通过。独立核对请求模型限制合同与业务状态，服务核对样本 ID；真实 HTTP 负例仅提交错实例和错 HTTP 状态，缺少其余错误回执后读取 pending 与 cursor 的断言。 |
| 07 | 未通过。tests_mysql/test_acquisition_consumption.py 的 delivery_inputs 直接复制点集、硬编码版本与配置摘要。恢复用例先重建字节，之后才创建内存 SQLite，读取旧配置不会影响重建。不能证明恢复时按原版本生成相同字节，亦未覆盖旧配置缺失仍保持原 pending、目标身份和游标。目标接管、指纹变化与缺口已有部分独立证据。 |
| 08 | 通过。401/403、授权范围、绑定/未绑定目标、五个 GET、v2 工件回归通过。七项消费者操作的发布 paths、components 与 FastAPI 生成结果一致，独立 Schema 定义比对通过。 |

**迁移混合状态检查。** 候选迁移的 _install_guards（第 143 行）只读取 TRIGGER_NAME 和 ACTION_STATEMENT。MySQL 把事件和触发时点独立存储；正文与名称一致而绑定事件不同的已有守卫可以通过该比较。CREATE TRIGGER IF NOT EXISTS 会保留已有定义，因而此类异常状态可能进入后续激活。此结论来自源码审查；本次真实库套件注入的是同事件、不同正文的冲突。Development 应核对各守卫的事件和时点，并在隔离迁移回归中断言错误定义阻止激活且原事实保持。

**交接。** 请 Development 在同一获批范围补齐上述缺口。创建并发用屏障交错持锁写入与消费者创建，验证冻结起点和第一条待消费事件；故障矩阵分别核对重试前后的状态和操作身份；配置恢复应在重启前持久化两个不可变配置版本，重新打开后按 pending 版本重建，再移除原版本验证停在原位置。提交新的候选清单后进行下一次 fresh-context Verification。现有项目数据库、历史、SMA 接入及 Human Owner 最终验收均在本次结果之外。

## QA2 独立复验 · ARCH-ACQ-006 r1 · rework-1

**当前结论为 `qa_passed`，交 Human Owner 最终验收。** 上方 QA1 的 `qa_failed` 对应首轮候选。本轮独立重算 tasks.md 最后一段清单的 SHA-256，得到 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`，35/35 个交付文件一致。基准 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。与 QA1 相比，仅后继迁移和专属 MySQL 测试的摘要改变。运行后再次比对交付清单及副本中的 34 个后端与合同文件，一致。根代码索引中的采集消费入口与实际路径相符。

使用项目 Python 3.13 解释器，从排除环境文件、私有状态、数据库、日志、虚拟环境和缓存的临时副本运行。通过 FastAPI ASGI 和专用 QA MySQL 8.4.6 执行，地址为 127.0.0.1:55794，UUID 为 28171ac7-e3ea-11f1-b476-8206efe6a29b。夹具核验 UUID、8.4 版本与 +28800 秒时差，在随机 QA schema 执行迁移并回收。

| 独立运行 | 结果 |
| --- | --- |
| QA1 表中同一条 compileall 命令，设置仓外字节码目录 | 退出 0 |
| QA1 表中相同十组 pytest 模块，加 TMPDIR=/private/tmp 和 --basetemp 指向 /private/tmp 下的专属目录 | 188 passed，10 skipped，14.71 秒，退出 0 |
| python -m pytest -q -p no:cacheprovider --basetemp 独立仓外目录 tests_mysql/test_acquisition_consumption.py | 9 passed，33.76 秒，退出 0 |
| git diff --check 和 git diff --exit-code HEAD -- 'contracts/published/http-api/plc-facts-v2/*.json' | 两项退出 0 |

首次离线运行因系统默认 pytest 临时目录位于 /private/var 而触发历史守卫，187 项通过、1 项失败、10 项跳过。首次 MySQL 运行将凭据夹具置于临时源码树内，凭据读取守卫正确拒绝，9 项失败。调整测试目录后重新完整运行取得上表结果。

| 验收项 | 实际复核结果 |
| --- | --- |
| AC01 | 同流后写等待、异流先提交、旧采样时间、回滚和 duplicate 对应的事实与事件数均通过。 |
| AC02 | 迁移从 information_schema 复核时点、事件、所属表、正文及守卫名集合。夹具分别注入同名同正文的错误时点、事件及目标表，均保留前驱版本和原三表，阻止激活。停写确认、旧格式插入及越界删除拒绝、部分回填续跑和排除过期历史通过。 |
| AC03 | 两种起点各与两种先持锁者交错，屏障确认另一事务等待。验证冻结水位、重复创建、全序列投递及最终游标。过期排除与清理后 410 用例通过。 |
| AC04 | 已提交事件在删除登记后可读，旧来源新写入被拒。新代次续号，目标接管保留 pending 和游标。 |
| AC05 | 竞争者仅一个获租。创建、运行、暂停、取得、续租、释放、pending、ACK 分别注入 commit 前后故障，读取状态、同身份重试、冲突输入及最终游标校验通过。绑定 POST 另核对故障前后事实数为 0 和 1。 |
| AC06 | 目标收到原字节并提交，重试返回 duplicate，历史及详情回读唯一目标样本。七项错误回执逐项被拒，每次核对 pending 不变、游标为 0、目标仍仅一条。ACK 提交后丢响应可重放。 |
| AC07 | 模拟执行者重启后重新 GET 并打开 SQLite 原配置版本，重新映射点名并生成相同正文。切换版本和删除旧版本分别阻断重建，原 pending、游标及目标 ID 保留。恢复版本后由重建字节重投，历史点名为 zero-mapped。配置库仅保存版本、序列器和映射。 |
| AC08 | Bearer 401、权限及范围 403、绑定目标、未绑定 POST 和原五个 GET 均通过。新合同 paths、components、Schema 和向量通过离线比对，原 v2 JSON 与 HEAD 无差异。 |

本轮无待返工项。测试源副本、测试凭据与 SQLite 工件已回收，专属实例与实例凭据由协调者回收。证据覆盖隔离软件合同；真实环境采用、历史迁移、实际 SMA 对接和部署仍需对应授权与证据。

## Human Owner 最终验收 · 2026-11-20（Asia/Shanghai）

> 验收 ARCH-ACQ-006 r1（rework-1），范围为后端稳定续读游标和投递状态的源码及隔离验证。现有库不执行迁移。

状态为 `owner_accepted`。Human Owner 的决定对应 QA2 通过的历史候选，其 35 文件清单 SHA-256 为 `a984198eaa14266df0a429720158582a4530e733cd83a66c1313a7009082231c`。Verification 登记时从 tasks.md 的 rework-1 原始清单重算摘要，并逐项只读比对当前工作树，23 项匹配、12 项有差异。当前集成工作树未重新验证。本次登记未运行测试、连接数据库或执行迁移。
