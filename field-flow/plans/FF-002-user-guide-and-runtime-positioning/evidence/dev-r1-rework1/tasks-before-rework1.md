Task ID: FF-002
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: exact approved r1 documentation candidate and bounded macOS arm64 DEV self-check frozen; coordinator must start fresh-context Verification; no QA verdict or Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Field Flow 双语手册、案例教程与 Rust BUILD 文档
Owner: Field Flow
Acceptance Chain Reference: FF-002 r1 scope approval -> Development -> fresh Verification -> Human Owner final acceptance

# FF-002 r1 Development 实施与精确交接

## 1. 批准、角色与交付工作树

Human Owner 原文：“批准 FF-002 r1，按方案完成 Python/Rust 对照使用手册、案例开发教程和 Rust BUILD 说明，完成后按 STD 进入独立 QA。”批准后 spec SHA256=`de9e338f495e1ae756ff50bc12d798edefb1a2f572ec6bc6cd6fb3e150ef3b7c`；原审稿及批准前后对照由主协调器保存。Revision、范围、需求、allowlist、AC与风险未改。

实际选定角色 `development`，执行者 `/root/ff002_development`；读取 `.codex/agents/development.toml`，其中 model/effort 仅为配置证据，不冒称额外底层遥测。`contract_only` 由任务bundle、串行handoff与diff审计形成合同控制，不宣称平台ACL/强制路由。

正式交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，未创建commit、branch/tag、push或release。保留并行dirty，不按whole-HEAD归因。Development写入仅16份授权文档、本tasks及真实证据附件；19份主导航由主协调器机械同步。正式src/tests/config/locales/manifest/lock、FF-001与ARCH历史均未改。

## 2. 实施与文件

已读根AGENTS、canonical workflow、development TOML、根及FF/两工程README/PLAN pair、完整已形成FF-002 spec（开工时尚无tasks/checklist）、相关CLI/config/domain/runtime/app/execution/HTTP/owner/driver/state/audit/fixture、冻结清单/锁与native原包build.rs。无更近AGENTS。

本轮使用 `aiis`、`project-governance`、`rust-runtime`、`plc-point-mapping`、`code-document-indexer`、`i18n-workflow`；`backend-arch`只采用本地执行状态/事务边界，不套FastAPI、ORM、Celery或迁移模板。按需读分层、跨语言结构及日志基线；不写shared skills。

八份新文档：

- `field-flow/USER_GUIDE.md`、`USER_GUIDE.zh-CN.md`：读者路径、目录/方法/单轮对照、共同语义及语言定位。
- `field-flow/field-flow-rust/USER_GUIDE.md`、`USER_GUIDE.zh-CN.md`：独立工程准备、完整分终端两模式教学、真实方法及完整teaching01接线/验证。
- `field-flow/field-flow-python/USER_GUIDE.md`、`USER_GUIDE.zh-CN.md`：独立uv/CPython源码路径、实际对象合同、两模式教学及完整teaching01接线/验证。
- `field-flow/field-flow-rust/BUILD.md`、`BUILD.zh-CN.md`：锁定产品/fixture构建、实际native/动态依赖、三平台限制、状态生命周期及分发gate。

八份必要入口/索引修改：FF README中英pair、Rust README中英pair与CODE_INDEX、Python README中英pair与CODE_INDEX。入口统一Python练手/原型且不打包、Rust长期runtime建设主线；未来不要求所有生产flow双实现。子README过时DEV阶段改为引用FF-001原QA2真实事实，仍待Owner终验。PLAN/catalog归协调器，不由本角色写入。

完整16文件SHA与已拷贝一致性：[candidate-documents.json](evidence/dev-r1/candidate-documents.json)，SHA256=`6217888378795ca536f13079fa65b1c7a1294ea534642f1bc44671cd87627d3b`。文档正式树与私有candidate-documents快照逐字节匹配。教学app/YAML与已编译/导入/运行的私有实现逐字节核对：[tutorial-snippet-consistency.json](evidence/dev-r1/tutorial-snippet-consistency.json)。本tasks的最终hash在非自引用handoff附件和主会话交接中给出。

## 3. 需求与DEV自检覆盖（不是QA）

| 需求 / AC | 已完成的Development事实与核对依据 |
| --- | --- |
| R01 / AC01,03 | 独立FF-002 r1批准链；Python功能/测试/历史QA保留；Rust主线不等于现已部署；不借FF-001批准/QA或未创建DS建议作本任务事实。 |
| R02 / AC02,12 | 八份新文档+必要入口/索引共16文件；两工程自包含，不以父/兄弟为运行前提。七组双语pair章节数相同、代码块逐字节相等；16文件local links存在、显式anchor存在、无trailing whitespace。 |
| R03 / AC04 | 对应Rust fixture.rs/bin及Python tests/fixtures/runtime.py/__main__.py：真实GET、透传proxy、server child、固定端口、DB1/16、人工与自动测试区别。Rust cmd-001/source固定/TTL60秒，Python fixture-UUID/source首flow/TTL30秒；均默认input age10秒；停止/报告各自准确。 |
| R04 / AC05 | 两工程独立副本；先build/sync/init，再分开新synthetic dry/execute教学。实际副本产品入口、空cwd无参/中英help、state init/run/inspect、SIGINT/ENTER及wait。终端B显式read真实绝对路径，无跨shell未定义变量。 |
| R05 / AC06,09 | 核对typed配置范围、来源七键/类型/时间、ready/queue/IO预算及400ms回收预留、复用HTTP与每PLC持久session、同流不重叠/异流并发、独立采样；解释T1/T2/T3、unknown、审计/容量/退出/UTC限制。既有并发测试仅作源码语义依据，未重跑旧全矩阵。 |
| R06 / AC07 | 实际签名/对象、async/参数/返回/错误/owner方法表；Flow/Plc/Target、GET/Input/Intent、INT read、Execution.apply、Clock/anchor、Stop、inspect/snapshot/log观察均覆盖。写只经Execution，不教Owner/raw/SQL绕过；Python无完整注解或anchor()不虚构SDK。 |
| R07 / AC08 | 完整teaching01 app+YAML、Rust app/mod/config/runtime、Python runtime import/config/dispatch接线；无自动发现。只在私有副本应用，真实产品CLI各两模式运行。无新增locale key故不改locale，说明消费副本索引更新；无通用schema/driver/API扩展。 |
| R08 / AC10,11 | Rust1.89冻结release/no-default-features产品与test-fixture分target；真实current_exe/__driver、include_str locale、rust-snap7 native archive/SQLite及otool依赖；macOS实测，Linux未测，Windows POSIX阻塞；官方primary及原包许可差异可追溯。 |
| R09 / AC12,13 | 581受保护FF源/锁/配置/历史hash零变化；实际命令/原输出/失败/版本/候选/资源持久化。19导航由协调器另冻结，不混入本16文件候选。 |
| AC14 | 本角色只形成developer_handoff；由主协调器必须另启动实际verification、fork_turns=none。其独立verdict及Owner终验均未在此授予。 |

## 4. 真实环境、命令与结果

唯一DEV私有根：`/private/tmp/ff-002-r1-dev-vncfzod3`（以下记D，实际绝对args均在附件）。分别复制到D/rust、D/python；排除target/.venv/dist/cache/状态/日志，保留依赖锁，只读取公开sample配置。辅助文本脚本用宿主现有Python3.9；项目Python行为全部来自D/python/.venv的已有CPython3.11.12。没有借用兄弟或FF-001环境。

环境实测：[environment-build.json](evidence/dev-r1/environment-build.json)：Darwin24.6.0 arm64，rustc1.89.0/Cargo1.89.0，Apple clang17.0.0，uv0.7.8，CPython3.11.12，python-snap7=3.0.0、httpx=0.28.1、PyYAML=6.0.3、pytest=8.4.2。shell无python3.11命令不影响uv找到已有解释器；没有下载安装解释器/target/编译器/系统SDK。

| cwd | 实际命令 / 操作 | 退出与结果 |
| --- | --- | --- |
| D/rust | `cargo build --locked --release --no-default-features --bin field-flow --target-dir D/target-product` | 0，31.75s，原输出rust-product-build.log。 |
| D/rust | `cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir D/target-fixture` | 0，33.60s，原输出rust-fixture-build.log。 |
| D/python | `uv sync --locked --python 3.11 --no-python-downloads --cache-dir D/uv-cache` | 首次1：新cache缺包且镜像DNS受限；最终经auto-review允许的同命令0，仅准备冻结依赖到私有环境/cache。 |
| D/python | `uv sync --locked --offline --python 3.11 --no-python-downloads` | 2：公共cache写锁sdists-v9/.git被sandbox拒绝。未修改公共cache；只读复制正常cache到私有cache后重试。 |
| D/python | `uv sync --locked --offline --python 3.11 --no-python-downloads --cache-dir D/uv-cache` | 1：冻结pytest wheel不在已有cache；网络准备成功后解除。 |
| D/python | `uv lock --check --python 3.11 --no-python-downloads --cache-dir D/uv-cache`；`uv run --locked --python 3.11 --no-python-downloads --cache-dir D/uv-cache python -c ...` | 均0，冻结锁与实际解释器/依赖版本；完整args/stdout见environment-build.json。 |
| D/{rust,python}-empty | 自身已构建product或自身`.venv/bin/field-flow`，分别无参、`--lang en-US --help`、`--lang zh-CN --help` | 六条均0，cwd仍为空，help stdout分别保留。 |
| D/rust, D/python | 自身产品`state init --synthetic --mode dry_run/execute --state-dir 新scene/state --instance-id 匹配ID`；各场景fixture显式config/evidence；产品`run --config ... --state-dir ... [--execute]`；正常停止、实际wait、`state inspect` | 八个独立教学场景，详见下表和commands.jsonl真实绝对args；所有最终正常runtime/fixture退出0。 |
| D/rust | 按手册完整teaching01源码/YAML和rust-wiring.py仅改私有app/mod/config/runtime，再构建上述产品/fixture两个目标 | 两条均0；private源码与文档块相同，真实config由fixture/product load校验。 |
| D/python | 按手册完整teaching01源码/YAML和python-wiring.py仅改私有app/config/runtime；`uv run --locked --python 3.11 --no-python-downloads python -m compileall -q src`；同uv入口`python -c`导入teaching01/load配置/断言kind | 均0；项目解释器是本副本.venv；完整args/stdout见commands.jsonl/python-teaching-*。 |
| D/rust | `file D/target-product/release/field-flow`；`otool -L ...` | 0；Mach-O arm64，Security/CoreFoundation/libc++/libiconv/libSystem真实动态依赖；并非全静态。 |
| 正式树 | scoped静态双语代码块/章节、16文件本地链接/显式anchor/空白、protected hash、拷贝hash | 0；document-checks.json、protected-audit.json和candidate-documents.json；git diff --check scoped exit0。 |

有限实际运行汇总：[rehearsal-summary.json](evidence/dev-r1/rehearsal-summary.json)，逐条命令：[commands.jsonl](evidence/dev-r1/commands.jsonl)。每行各自新synthetic状态、fixture，按语言/模式串行，没有同时writer。

| 语言 | 案例 | dry_run inspect / WriteVar | execute inspect / WriteVar |
| --- | --- | --- | --- |
| Rust | demo01 | simulated=1 / 0 | confirmed=1 / 1 |
| Python | demo01 | simulated=1 / 0 | confirmed=1 / 1 |
| Rust | teaching01 | simulated=1 / 0 | confirmed=1 / 1 |
| Python | teaching01 | simulated=1 / 0 | confirmed=1 / 1 |

Rust报告保留protocol trace/次数/native_pid，Python报告保留memory_hex、server_exit/server_close无线程、proxy join、ports_rebound。execute Python memory前缀002a，尾部a5保留；Rust真实WriteVar/正ACK trace为值42。正常JSONL含intent/ack、driver回收及shutdown_complete；不将confirmed解释为工艺完成。

本轮不重跑FF-001全量故障矩阵/历史失败preflight；不运行Python打包、Docker、真实DB/PLC/第三方HTTP、DS/Backend服务或跨平台构建，不改宿主时钟。

## 5. 失败、修正与诚实限制

完整保留：[failures-and-corrections.json](evidence/dev-r1/failures-and-corrections.json)和各次harness stdout/stderr、准备日志。

- 私有空cache的DNS失败、公共cache写权限失败、复制cache后offline缺锁定wheel均真实保留。仅经auto-review允许的私有uv sync准备冻结依赖后成功；没有拒绝后绕过下载解释器或改锁。
- 首次Python dry场景runtime已正常0/simulated1/write0；helper向uv包装PID发SIGINT后wait10s超时。finally再SIGTERM/wait结束夹具，report server_exit0/无线程/端口rebind。原状态/报告保留，不写成首次全绿；当时uv内部实际fixture父PID未单独采集，已保留此观察限制。后续按文档直接调用本副本`.venv/bin/python -m tests.fixtures`，fixture/server/driver/runtime均记录精确PID及正常wait。最终任务路径进程扫描无残留。
- 第二次Python dry已正常退出，但helper未设SO_REUSEADDR的bind探测遇TCP TIME_WAIT。未重启该场景/未清库；以无listener及与Python夹具相同SO_REUSEADDR重bind核对，并读取原inspect/report恢复完整证据。这是helper断言修正，不是产品清理故障。
- 写教程辅助脚本曾因嵌套heredoc标识冲突在shell解析时报错，未运行/修改正式实现；修正外层标识后完成文档。准备命令核对时发现`uv python find`不支持`--python`，已从最终手册去除，锁定sync/run仍显式选择3.11且禁解释器下载。
- 初稿事实纠正已纳最终文档：Python server也是spawn child而非全部父线程；TTL30秒/Rust60秒；Python Sample无pid；实际全部otool依赖；各工程只提自身锁；具体源码表与Stop/Clock/state合同；完整新副本创建与逐终端运行命令。无正式产品改动。
- Python正常client断开时server可输出`Expected COTP DT, got 0x80`；原stderr保留，结合exit0、server无线程、proxy join、PID和端口判断，未掩盖为无输出。
- 现SQLite日历元数据与JSONL使用UTC，与根Asia/Shanghai合同有差异；Unix ms和monotonic仍按自身语义。仅记录，不暗改schema/历史/日志。Windows有明确Unix源码阻塞，Linux未实测；没有现场、长稳、托管、备份迁移、跨主机fencing、unknown处置或分发合规资格。
- 主协调器治理基线exit1的322条诊断（318任务外既有+4合法父spec链接识别限制）不当全仓通过；本角色不改checker或造子bundle，最终整体输出由协调器/QA记录。

## 6. 语义与来源核对

- CLI/default dry/state初始化/退出码：Rust commands.rs；Python cli.py（Python启动Failure多为exit2，close fault/unknown为1，不强行统一）。
- 七键/INT/时效/Clock：两版domain；typed YAML范围/物理重叠：两版config。DB1/16/offset0只是当前fixture，非现场合同。
- HTTP有界client与错误key：各infrastructure/http；写唯一入口：services/execution；owner/driver FIFO、会话/时钟/permit/started、停止回收：Rust runtime/driver_process、Python runtime/owner/driver_process。
- 状态T1/T2/T3/immutable/unknown/capacity/time/日志：两版infrastructure/state/audit；读服务示例与并发语义核对既有local_protocol/runtime_regressions测试源码，未新增正式read flow。
- 原native build.rs SHA、Cargo checksum与官方primary URL：[sources.json](evidence/dev-r1/sources.json)。已浏览官方Cargo build与Rust platform support，只说明工具链，不代替冻结native源码或本项目目标验证。

## 7. 资源、保护与handoff

[protected-audit.json](evidence/dev-r1/protected-audit.json)确认协调baseline中的581项FF正式源码/config/locale/依赖锁/旧历史及证据逐字节相同；approved spec仍为本页第1节hash。未向FF-001旧tmp、真实配置/状态或任务外资源写入。

[resources-final.json](evidence/dev-r1/resources-final.json)记录34个最终场景/包装已知PID全部absent，另首次失败scene的原server/driver两个已知PID在failures附件确认absent；任务路径ps扫描无残留，六固定端口31102/31103/31880/32102/32103/32880均无listener、逐一复bind。SO_REUSEADDR对应Python夹具真实规则；未按端口或进程名杀占用者。所有最终scene fixture/runtime均实际wait，报告内部server join/reap亦已核对；SIGINT发送本身不当证据。

本任务自建资源全部位于D：

| 子项 | 归属与用途 | 保留 / 回收条件 |
| --- | --- | --- |
| rust/, python/ | 两语言独立源码副本；仅副本新增teaching01与接线，Python含自身.venv | QA复核及Owner终验后，由coordinator核对归属/占用/后续依赖再回收，不整合教程代码为产品能力。 |
| target-product/, target-fixture/ | Rust无default产品及test-fixture独立release目标 | 同上；非发布产物。 |
| uv-cache/ | 只读复制普通package cache+锁定依赖准备，约8.8GiB；未借兄弟环境 | 同上；无需作为唯一证据长期保存，关键结果已持久。 |
| *demo01* / *teaching01* scene目录 | 新synthetic SQLite/instance.lock/gate/log与夹具报告；原失败场景同样保留 | 不提交DB；Owner终验后核对依赖再清理，不清FF001或现场数据。 |
| *-empty/ | 无参/中英help空cwd核对 | 同上；无配置/状态副作用。 |
| candidate-documents/ | 16份最终正式文档逐字节快照 | QA对照，终验后按证据依赖判断。 |
| helper .py、准备/build/harness日志、root.json | 本角色辅助脚本与失败过程 | 必要脚本/输出已持久到evidence，余项同上。 |

主协调器另建 `/private/tmp/ff-002-r1-coordinator-k8s3e9_q`，保存16/19所有权baseline、581保护hash及批准前后spec；无本角色服务。其归属/验收依赖由active coordinator负责，终验前保留，本角色未清理。没有本任务branch/worktree、外部服务或后台daemon。notifier只使用主协调器已启动窗口，本角色未另开/结束或发送邮件。

**Development -> fresh Verification：** 精确FF-002 r1、上述正式working tree与16文件candidate；请独立读取approved spec、本tasks、正式文档/源码/diff与evidence，按AC01–AC14形成自己的checklist/verdict。特别核对手册可照做、两语言实际差异、案例接线、单工程独立性、未知结果边界、平台/时间限制、失败保留和资源回收事实。19份主导航由协调器另冻结补充。Development写入在此停止；未给QA verdict、未授予Human Owner最终验收。若QA失败，仅原scope新Development turn返工，保留失败，再另fresh Verification。
