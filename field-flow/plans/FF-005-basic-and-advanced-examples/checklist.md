Task ID: FF-005
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner accepted exact FF-005 r1 A on 2026-11-04; coordinator resource closeout recorded: 20 owned generated directories and 18 convenience links removed, 7203 evidence files and 287 exact legacy-prefix resources retained; QA history and unresolved hold_ack limitation preserved
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Owner: Field Flow
Acceptance Chain Reference: FF-005 r1 Owner approval -> Development -> fresh-context Verification -> Human Owner final acceptance

> **当前资源收尾已登记：主协调已回收精确列明的20个自有构建/cache/venv目录及18个便利链接；7203件证据工件和287个精确旧前缀目录保留。详见文末 Resource closeout r1 A。以下“正在盘点/待追加/Owner pending”均保留为原阶段历史，当前Owner验收仍为owner_accepted。**

> **当前最终验收状态：Human Owner 已于 2026-11-04（Asia/Shanghai）明确回复“批准”，精确 FF-005 r1 A 登记为 owner_accepted；依据及边界见文末 Owner acceptance r1 A。下方 QA1/QA2 的 Owner pending 与当时“当前”均为历史时点。资源收尾正在由主协调盘点，尚未登记清理完成。**

> **当前有效判定见文末「QA2：r1 A rework1 当前有效独立结论」：qa_passed，Owner终验pending。以下原QA1正文/失败与证据完整保留，其“本轮/当前”只指QA1时点；原Status=qa_failed及QA->Development handoff不被抹除。**

# FF-005 r1 A 独立 Verification

本轮由主协调交接新的命名 Verification，fresh context 不继承 Development 对话推理。独立读取根 AGENTS、README/PLAN 双语、canonical workflow、verification TOML、FF 与两工程最近 README/PLAN/catalog、完整 spec/tasks、正式实现、原始基线差异与真实自检输出。角色 TOML 配置为 gpt-6.1-sol / max；这是配置证据，不冒充独立可观测的模型运行遥测。本 profile 为 contract_only；串行 handoff、hash/diff 与 checklist 审计是控制，不宣称平台 ACL、强制路由或团队自动激活。

唯一正式写面为本 checklist。没有修改 spec、tasks、实现、测试、配置或导航，没有清理 Development/历史资源。QA 自有根为 `/private/tmp/ff-005-r1-qa-4cpsww4h`；报告/构建/单工程源码副本/新 synthetic 状态均归该根，旧安全回归硬编码前缀产生的确切新增资源另行登记。

## 冻结输入

- 正式树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；working tree，HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。其他模块大量原有 dirty 保留，不作为本任务修复面。
- spec SHA256=`22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8`；tasks SHA256=`3fa591681b27891869df27cbdfb0c3e8762083be870fe18d688b5d601a96c71a`。
- 37 件实现 manifest SHA256=`213cb81ca44cd3e0c1f04774e071f00fa30361ebe41aa8aa69e850b6bfc1e1ab`；51 件完整候选 manifest SHA256=`3bda5ee966a0edc22a005e8c217214b91557651266e9f3b8dfd91d50bef40b41`；开始时全部匹配正式树。
- 主协调 baseline 816 件原 hash、original/ 原 dirty 文件用于当前任务 diff；780 件受保护文件开始时全部相同。FF-004 r1 SHA256=`e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`。
- QA 独立复制 Rust 57 件、Python 62 件自身源码/锁/配置/locale/测试/说明，排除环境、target、状态、日志和真实配置。不是 Development 副本或二进制；复制指纹归自有 qa-copy-hashes.json。

## QA1 已确认失败

F-QA1-001 / P2 / 文档注册事实不一致：两工程 README.md 第 11 行仍写 `Only demo01 is registered`，README.zh-CN.md 第 11 行仍写“当前kind仅demo01”；父对照 USER_GUIDE.md 第 42 行仍写 `The delivered code still accepts only demo01`，USER_GUIDE.zh-CN.md 第 42 行仍写“正式源码仍仅接受demo01”。这六文件都已由本任务触达，末尾新增三个正式基础案例入口；实际 config/runtime 与 examples/config 表已接受 demo01、plc_guard_get_int、get_value_guard_int。读者会得到相互矛盾的正式能力说明，违反 R03–R06/AC09 的真实接线与方法文档合同。QA 未修复；已回报主协调/Development，候选继续冻结。

F-QA1-002 / P1 / Python 新矩阵对强制 driver 回收发生 false positive：`tests/test_basic_examples.py:152` 用带空格字串 `"had_forced_driver_stop": true` 排除强制回收，实际 event_line 输出紧凑 JSON 的 `"had_forced_driver_stop":true`，断言未命中。QA 的 `evidence-python/basic02-execute-unknown-42-None/report.json` 仍标 passed，然而 product.jsonl 第 9–11 行显示原 driver PID 82757 被 SIGTERM 回收、exit_code=-15，并有两条 forced_driver_stop；第 22 行 stop_joined 的 had_forced_driver_stop 为 true。替代 driver 82851 后续正常 join/reap，原 unknown1/GET1/ReadVar11/WriteVar1/002a 与邻接 A5 都保留，但不能把该向量归为无强制回收通过。Development 最终 v3 同场景原输出也显示 PID 63554/-15、forced_driver_stop、had_forced_driver_stop=true，非仅本轮负载差异。此问题违反 R05/R08 与 AC11；tasks 中“最终74场景无强制回收”的事实声明亦不受原输出支持。QA 未修改 harness、向量或受保护 driver；已将精确问题返回 Development，需在原 allowlist 内修复验证断言/故障向量并如实保留失败历史，再另启 fresh QA。

## 环境与执行说明

独立本机 macOS 15.7.7 arm64；rustc/cargo 1.89.0、uv 0.7.8、原有 CPython 3.11.12。原工具链/锁保持，不下载解释器/SDK、不开新协议/端口。已通过正式无 feature Rust release 构建、Rust 独立副本 release 构建、Python 副本 locked sync/compileall、限定 Rust 文件 rustfmt、382 条局部文件链接与中英可执行代码块对称/locale key 对称检查。全部必需检查现已执行并封存，最终 QA1 verdict 为 qa_failed；具体通过项不能抵销下列必需失败。

Python 自有空 cache 的首次 offline sync 因锁定 wheel 缺失 exit1；随后按获批公共依赖准备范围到同一自有 cache locked sync exit0。sandbox 六口 bind 预检 PermissionError，未算产品失败；运行检查通过工具取得已批准 loopback 的执行权限后进行。这不是 qa_blocked 或环境通过的推测。

Human Owner 最终验收：pending。本轮未作资源收尾删除。仅 A；B/C、Windows/Linux、现场/真实 PLC/第三方 HTTP/DS/Backend/真实 DB、托管/长稳/部署/发布均未授予或外推。


## 最终结论、验收口径与边界

**2026-11-04（Asia/Shanghai），FF-005 r1 A QA1 = `qa_failed`。** F-QA1-001、F-QA1-002 均未关闭。没有尚未解除的环境/权限 blocker；失败属于当前候选的文档与测试/证据合同，不记为 qa_blocked。依据为[精确批准规格](spec.md)与[冻结 Development handoff](tasks.md)，不是继承 DEV 的结论。

独立原命令 Rust 全套 exit0、21 个实际 test 项（18 既有 + 3 新增）；Python 全套 exit0、25 个实际 pytest 项（22 既有 + 3 新增）。新增的 6 个测试函数内部共运行 **74 个真实 CLI 场景**，不是 74 个测试函数，也不是旧 QA48 口径。每语言 34 个正常 exit0、3 个预期协议故障 exit1。独立 JSON 解析审计发现 Python unknown 资源项失败，即使原 harness 输出 passed 也不接受其 AC11 结论。

另有 **20 个正常人工 CLI 复演场景**：两个单工程副本 basic01/basic02/basic03 各两模式共12个、teaching01 各两模式共4个、正式树 basic02 各两模式共4个，全部产品/fixture exit0。此处新矩阵74 + 人工20 =94，不把旧回归内部向量或下列22条 CLI 边界命令混入。540个原PID确实消失只证明实际资源已离开；它不能把 F-QA1-002 的 SIGTERM 强收改写为正常退出。

已使用 project-governance、aiis、rust-runtime、plc-point-mapping、i18n-workflow、code-document-indexer，并读取相关语言中立分层/运行日志基线。验证限制保持规格原范围：只有本机 macOS arm64、自有 loopback HTTP/S7、标准 DB1/16字节/INT。没有真实 PLC/第三方 HTTP/DS/Backend/真实 DB/历史迁移、Windows/Linux、托管/容量/长稳、安装/打包/发布/部署、Git refs 或 push。旧 UTC 日历差异明确保留，新 app 未增加时间 producer。QA 不修实现，不修改 tasks/spec/导航，不代替 Human Owner 终验。

## 独立命令、环境、输出与退出码

下表 `Q=/private/tmp/ff-005-r1-qa-4cpsww4h`，`R=Q/rust`、`P=Q/python`；它们是119件源文件的独立单工程副本。正式 Rust cwd 为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/field-flow/field-flow-rust`。Q/run_job.py 仅用现有文本解释器运行子命令并写命令 argv、cwd、UTC 起止、耗时、退出与原输出到 Q/commands/<label>.json/.log；不替代实际产品。产品 Python 使用已有 CPython3.11.12 与自身锁定 .venv，辅助 Python3.9 不冒充项目环境。

| cwd / 实际命令（Q展开为上述绝对路径） | 结果与原输出 label |
| --- | --- |
| 正式Rust：`cargo build --offline --locked --release --no-default-features --bin field-flow --target-dir Q/formal-product` | exit0；rust-formal-product.log；正式普通产品。初次 login shell 的 Homebrew ps 权限提示未影响 build，后续用非 login shell。 |
| R：同一无feature release命令，target-dir=`Q/copy-product` | exit0，90.13s；rust-copy-product；自己的 source/manifest/lock/native依赖。 |
| R：`cargo build --offline --locked --release --features test-fixture --bin ff-fixture --target-dir Q/fixture` | exit0，135.82s；rust-fixture；与无feature普通产品分开。 |
| 正式Rust：`rustfmt --edition 2021 --check src/app/plc_guard_get_int.rs src/app/get_value_guard_int.rs src/app/mod.rs src/config.rs src/runtime.rs tests/basic_examples.rs` | exit0；rustfmt。没有整树格式化。 |
| R：`cargo test --offline --locked --features test-fixture --target-dir Q/rust-test --no-run` | exit0，104.43s；rust-test-compile。仅编译，不把它算实际测试。 |
| R：`FF005_EVIDENCE_ROOT=Q/evidence-rust cargo test --offline --locked --features test-fixture --target-dir Q/rust-test -- --nocapture --test-threads=1` | exit0，21项；测试运行155.47s；rust-full。3新函数内部37真实CLI场景。 |
| P：`uv python find 3.11 --no-python-downloads --cache-dir Q/uv-cache`；`uv sync --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache` | find0，返回既有3.11.12；sync1，仅因新cache缺锁定wheel，不是产品失败。python-sync.log。 |
| P：`uv sync --locked --python 3.11 --no-python-downloads --cache-dir Q/uv-cache` | 获已批准公共依赖网络执行权限后exit0；python-sync-network.log。仅锁定16包/自身venv/cache，未下载解释器、SDK或安装Agent包。 |
| P：`uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache python -m compileall -q src tests` | exit0；python-compileall。 |
| P：`FF005_EVIDENCE_ROOT=Q/evidence-python uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache pytest -q -s` | exit0，25项，pytest232.24s，含包装233.95s；python-full。3新函数内部37CLI场景。原passed不能覆盖F-QA1-002。 |
| Q：`python3 Q/summarize_matrix.py`（逐JSON解析原74报告/产品日志） | 独立审计exit1，准确命中F-QA1-002；matrix-independent-audit。TTL/计数/内存/身份与其余场景观察完成。 |
| 两教学副本：从各自USER_GUIDE §7逐字提取完整app/YAML/带assert接线脚本，再`zsh -f <wire.sh>` | 两次exit0；rust-teaching-wire.log、python-teaching-wire.log。正式源不增teaching01。 |
| Q/rust-teaching：无feature release产品构建到Q/teaching-product；feature夹具构建到Q/teaching-fixture | 均exit0；rust-teaching-product、rust-teaching-fixture-rebuilt。曾复制本QA自身依赖构建cache，Cargo先判uptodate；QA未把那次当已重建证据，显式`cargo clean -p field-flow --release --target-dir Q/teaching-fixture`仅失效本QA临时包缓存，再由教学源码真实Compiling field-flow，9.59s完成。 |
| Q/python-teaching：同锁定offline sync；`uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache python -c 'from field_flow.config import load; from field_flow.app import teaching01; c=load("config/teaching01.yaml"); assert c.flows[0].kind == "teaching01"; assert callable(teaching01.once)'` | 两次exit0；python-teaching-sync、python-teaching-import。独立venv，未借原版/兄弟进程。 |
| Q：`python3 Q/manual_replay.py <rust或python> <basic01/basic02/basic03/teaching01> [formal]` | 实际10组×两模式=20场景全部0；对应10份manual-*.json/.log及每场景terminal-A/B.zsh/stdout/stderr/report。逐组串行；详见下表。 |
| Q：自身3.11 venv运行`cli_edges.py` | exit0，22条命令全部为预期码；cli-edges。两语言空cwd bare/en/zh帮助0、init0/拒覆盖2、inspect0且文件hash无变化、run缺schema2且不建目录、未知kind/teaching01/非法target/重叠写2且不建状态。 |
| Q：`python3 Q/static_checks.py` | exit0；static.json：冻结51候选的382条局部文件链接无缺失、双语代码块（排除注释语言）对称、locale键对称；git diff --check -- field-flow exit0。已实读内容仍发现F-QA1-001，不能仅靠链接/代码块检查宣布文档正确。 |
| Q：`python3 Q/seal.py` | exit0；seal。51候选/780保护hash、119副本、教学刻意差异、94场景与540确切PID、六口lsof/rebind及本QA可执行入口残余审计；未清理资源。 |

sandbox 首次六口bind预检 PermissionError，运行未被算pass；通过工具取得规格已批准的loopback执行权限后才实际测试。另一次仅QA辅助脚本py_compile预检误用macOS默认全局pycache，权限exit1，没有项目写入；改用内存compile()语法检查0。以上环境/辅助失败没有改源码、放宽TTL、删除负例或冒充项目运行。

## AC01–AC12 独立结论

| AC | 结论 | 独立证据与限制 |
| --- | --- | --- |
| AC01 | pass | exact r1 A批准链、原HEAD、正式无feature release及单工程独立构建/启动均核实；119复制文件与正式源相同，51候选/780保护hash不变。两工程实际非零21/25项测试；公共锁定依赖，无父/兄弟/DS/Backend运行依赖。B/C仍planned。 |
| AC02 | pass | 新app单轮、kind/dispatch最小diff；三case正式YAML均真实CLI load。原demo01/loopback/domain/Flow/Target/Intent算法/Execution/owner/driver/HTTP/state/audit、清单与锁原字节保持。旧严格配置/安全回归及正式CLI新kind非法target/重叠/unknown kind/teaching01拒绝2成立。 |
| AC03 | pass | 各语言4独立scene：42两模式≥11GET，dry simulated1/写0/16×A5；execute confirmed1/写1/002a+14×A5。strict idle另两scene GET≥3/command0/写0/正常0。同原身份/时间不刷新。 |
| AC04 | pass | basic02首先真实ReadVar才GET；execute读A5负值后GET1/写1/confirmed1，之后总读≥11且不再GET写；dry≥11独立读/GET、simulated1/写0。seed=-1/0均两模式，0只读不GET；读协议错误无GET/command/写，原错误传播。 |
| AC05 | pass | basic03 -1/0/101各两模式GET≥3、command0/写0且正常继续；1/42/100各独立两模式只有一次simulated/confirmed，写入对应0001/002a/0064及14×A5。42至少11GET仍一条命令，不靠换ID。 |
| AC06 | pass | 两新case各两模式ready=false/typed非法/纯expires过期。TTL=1000ms>0，8场景首错age2018–2666ms<10000且now≥expires；均原input_stale/原解析错误、零写，不归guard_false。普通skip后续轮次继续，不增长错误/无recovering，代码仍由原runtime归零计数。 |
| AC07 | pass（语义） | 新app所有写只经原Execution；输入原ID/issued/expires在fixture保持。新kind真实ACK丢失后两语言原inspect仍unknown1/GET1/写1/目标42，后十次独立读不重发/不回读升级confirmed。旧TTL/identity/排队/Clock/ACK/restart/audit回归仍过。Python该故障的强收事实属于AC11/F-QA1-002失败，未淡化为正常回收。 |
| AC08 | pass | 实读新增四app无循环/SQL/新连接/自建重试；Python basic02显式接受runtime持有的owner。Rust FIFO/started/clock回归、既有三readers和慢HTTP，以及Python对应并发/排队测试通过；新app不改变同流不重叠/每PLC串行IO。说明明确独立采样、非原子互锁与health非工艺完成。 |
| AC09 | **fail：F-QA1-001** | 新examples/config双语与真实方法/命令、12基础人工场景及反向74矩阵可运行；但六份已触达README/父对照手册仍声称正式仅demo01，与三kind事实矛盾，文档合同未完成。不能用链接检查0或人工运行0代替内容一致性。 |
| AC10 | pass | 两语言teaching01逐字app/YAML/精确接线脚本均适配当前锚点，教学副本编译/导入并各两模式正常0。正式CLI仍拒绝teaching01。教学差异仅Rust3既有接线+2新增、Python2既有接线+2新增；FF-002/FF-004旧bundle完整hash仍在780保护集合中。 |
| AC11 | **fail：F-QA1-002** | 74矩阵均在45/600秒内；正常68场景和额外20人工场景全正常0并有实际wait/join/reap/rebind。Python unknown虽全PID已消失、fixture正常，但原driver82757/-15及had_forced=true违反无强制回收合同，原测试误报passed。故障退出1与正常0保持分开；22真实CLI边界检查通过。 |
| AC12 | **fail：F-QA1-002** | 角色/候选/命令/状态/资源及本独立checklist均如实保留，Owner终验pending；但当前tasks“最终74无强收”与Dev自己final-v3原日志不符，需Development修正事实并保留历史。未改DB/秘密/发布，QA不能替写其权威文档。 |

## 独立真实CLI逐场景结果

下表计数为产品窗口减准备窗口；目标列另含停止产品后的独立16字节核验，后14字节每例均逐一A5。seed准备写/8次读回不混入产品IO。正常exit0与预期故障exit1分别记录；fixture退出均0，各report均记录自身线程/child join及三口实际rebind。**`harness passed`不作为QA verdict**，Python unknown独立资源结果为失败。

| 语言 / scene | GET / ReadVar / WriteVar | command counts | 首INT / 邻接 | 产品/夹具exit | 秒 | 原确切已消失PID | 独立资源项 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rust/basic01-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.259 | 92524,92525,92526 | 符合本scene期望 |
| rust/basic01-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 5.395 | 92430,92431,92432 | 符合本scene期望 |
| rust/basic01-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.343 | 92623,92624,92625 | 符合本scene期望 |
| rust/basic01-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 5.408 | 92557,92558,92559 | 符合本scene期望 |
| rust/basic02-dry_run-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.327 | 92794,92795,92796 | 符合本scene期望 |
| rust/basic02-dry_run-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.341 | 92755,92756,92757 | 符合本scene期望 |
| rust/basic02-dry_run-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.333 | 92760,92761,92762 | 符合本scene期望 |
| rust/basic02-dry_run-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 0.894 | 92829,92830,92831,92832 | 符合本scene期望 |
| rust/basic02-dry_run-value-42-None | 11/11/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 5.384 | 92656,92657,92658 | 符合本scene期望 |
| rust/basic02-dry_run-value-42-Some(-1) | 11/11/0 | `{"simulated":1}` | `ffff` +14×A5 | 0/0 | 5.400 | 92835,92836,92837 | 符合本scene期望 |
| rust/basic02-dry_run-value-42-Some(0) | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 1.358 | 92930,92931,92932 | 符合本scene期望 |
| rust/basic02-execute-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.335 | 93086,93087,93088 | 符合本scene期望 |
| rust/basic02-execute-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.352 | 93047,93048,93049 | 符合本scene期望 |
| rust/basic02-execute-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.340 | 93081,93082,93083 | 符合本scene期望 |
| rust/basic02-execute-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 0.910 | 93121,93122,93123,93124 | 符合本scene期望 |
| rust/basic02-execute-unknown-42-None | 1/11/1 | `{"unknown":1}` | `002a` +14×A5 | 1/0 | 5.740 | 93255,93256,93257,93258 | 符合本scene期望 |
| rust/basic02-execute-value-42-None | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 5.373 | 92935,92936,92937 | 符合本scene期望 |
| rust/basic02-execute-value-42-Some(-1) | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 5.428 | 93127,93128,93129 | 符合本scene期望 |
| rust/basic02-execute-value-42-Some(0) | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 1.365 | 93222,93223,93224 | 符合本scene期望 |
| rust/basic03-dry_run-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.329 | 93600,93601,93602 | 符合本scene期望 |
| rust/basic03-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.368 | 93532,93533,93534 | 符合本scene期望 |
| rust/basic03-dry_run-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.238 | 93565,93566,93567 | 符合本scene期望 |
| rust/basic03-dry_run-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.331 | 93323,93324,93325 | 符合本scene期望 |
| rust/basic03-dry_run-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.331 | 93359,93360,93361 | 符合本scene期望 |
| rust/basic03-dry_run-value-1-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 1.336 | 93395,93396,93397 | 符合本scene期望 |
| rust/basic03-dry_run-value-100-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 1.316 | 93490,93491,93492 | 符合本scene期望 |
| rust/basic03-dry_run-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.313 | 93526,93527,93528 | 符合本scene期望 |
| rust/basic03-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 5.357 | 93400,93401,93402 | 符合本scene期望 |
| rust/basic03-execute-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.373 | 93861,93862,93863 | 符合本scene期望 |
| rust/basic03-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.335 | 93813,93814,93815 | 符合本scene期望 |
| rust/basic03-execute-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.330 | 93851,93852,93853 | 符合本scene期望 |
| rust/basic03-execute-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.349 | 93605,93606,93607 | 符合本scene期望 |
| rust/basic03-execute-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.333 | 93640,93641,93642 | 符合本scene期望 |
| rust/basic03-execute-value-1-None | 3/0/1 | `{"confirmed":1}` | `0001` +14×A5 | 0/0 | 1.338 | 93674,93675,93676 | 符合本scene期望 |
| rust/basic03-execute-value-100-None | 3/0/1 | `{"confirmed":1}` | `0064` +14×A5 | 0/0 | 1.330 | 93774,93775,93776 | 符合本scene期望 |
| rust/basic03-execute-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.330 | 93779,93780,93781 | 符合本scene期望 |
| rust/basic03-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 5.358 | 93681,93682,93683 | 符合本scene期望 |
| python/basic01-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.651 | 80350,80351,80352 | 符合本scene期望 |
| python/basic01-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 6.466 | 80238,80239,80240 | 符合本scene期望 |
| python/basic01-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.733 | 80459,80474,80489 | 符合本scene期望 |
| python/basic01-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 5.756 | 80384,80385,80386 | 符合本scene期望 |
| python/basic02-dry_run-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.832 | 81008,81022,81071 | 符合本scene期望 |
| python/basic02-dry_run-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.939 | 80725,80761,80771 | 符合本scene期望 |
| python/basic02-dry_run-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.794 | 80836,80844,80853 | 符合本scene期望 |
| python/basic02-dry_run-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 2.523 | 81171,81184,81196,81222 | 符合本scene期望 |
| python/basic02-dry_run-value-42--1 | 11/11/0 | `{"simulated":1}` | `ffff` +14×A5 | 0/0 | 7.205 | 81307,81313,81343 | 符合本scene期望 |
| python/basic02-dry_run-value-42-0 | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 2.703 | 81552,81561,81598 | 符合本scene期望 |
| python/basic02-dry_run-value-42-None | 11/11/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 6.348 | 80495,80496,80497 | 符合本scene期望 |
| python/basic02-execute-expired-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.726 | 82022,82032,82077 | 符合本scene期望 |
| python/basic02-execute-idle-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.547 | 81850,81857,81871 | 符合本scene期望 |
| python/basic02-execute-invalid-42-None | 3/3/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.277 | 81934,81940,81944 | 符合本scene期望 |
| python/basic02-execute-read_error-42-None | 0/2/0 | `{}` | `a5a5` +14×A5 | 1/0 | 2.393 | 82263,82291,82318,82350 | 符合本scene期望 |
| python/basic02-execute-unknown-42-None | 1/11/1 | `{"unknown":1}` | `002a` +14×A5 | 1/0 | 10.850 | 82755,82756,82757,82851 | fail F-QA1-002 |
| python/basic02-execute-value-42--1 | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 6.573 | 82438,82456,82482 | 符合本scene期望 |
| python/basic02-execute-value-42-0 | 0/3/0 | `{}` | `0000` +14×A5 | 0/0 | 2.053 | 82718,82720,82724 | 符合本scene期望 |
| python/basic02-execute-value-42-None | 1/11/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 7.005 | 81667,81671,81685 | 符合本scene期望 |
| python/basic03-dry_run-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 3.156 | 83592,83706,83743 | 符合本scene期望 |
| python/basic03-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.454 | 83468,83473,83478 | 符合本scene期望 |
| python/basic03-dry_run-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.499 | 83533,83539,83546 | 符合本scene期望 |
| python/basic03-dry_run-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 1.719 | 82953,82954,82955 | 符合本scene期望 |
| python/basic03-dry_run-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.549 | 82989,82990,82993 | 符合本scene期望 |
| python/basic03-dry_run-value-1-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 2.201 | 83027,83031,83060 | 符合本scene期望 |
| python/basic03-dry_run-value-100-None | 3/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 3.128 | 83296,83313,83316 | 符合本scene期望 |
| python/basic03-dry_run-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.938 | 83384,83386,83423 | 符合本scene期望 |
| python/basic03-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5` +14×A5 | 0/0 | 6.498 | 83066,83104,83109 | 符合本scene期望 |
| python/basic03-execute-expired-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.314 | 84911,84916,84919 | 符合本scene期望 |
| python/basic03-execute-idle-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.801 | 84601,84792,84804 | 符合本scene期望 |
| python/basic03-execute-invalid-42-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.437 | 84848,84851,84859 | 符合本scene期望 |
| python/basic03-execute-value--1-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.647 | 83806,83848,83862 | 符合本scene期望 |
| python/basic03-execute-value-0-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 2.575 | 83961,83983,84000 | 符合本scene期望 |
| python/basic03-execute-value-1-None | 3/0/1 | `{"confirmed":1}` | `0001` +14×A5 | 0/0 | 2.633 | 84107,84119,84129 | 符合本scene期望 |
| python/basic03-execute-value-100-None | 3/0/1 | `{"confirmed":1}` | `0064` +14×A5 | 0/0 | 2.658 | 84372,84408,84416 | 符合本scene期望 |
| python/basic03-execute-value-101-None | 3/0/0 | `{}` | `a5a5` +14×A5 | 0/0 | 3.285 | 84497,84509,84517 | 符合本scene期望 |
| python/basic03-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a` +14×A5 | 0/0 | 6.527 | 84191,84192,84223 | 符合本scene期望 |

- rust：37场景，34正常exit0、3预期故障exit1；场景合计85.280548秒、最大5.739976秒，均小于600/45秒；独立资源失败0个。
- python：37场景，34正常exit0、3预期故障exit1；场景合计134.395441秒、最大10.850140秒，均小于600/45秒；独立资源失败1个。


8个expires隔离场景均原issued/expiry一次生成后不刷新：

| 语言 / scene | TTL ms | 首个input_stale时age ms | 隔离结论 |
| --- | --- | --- | --- |
| rust/basic02-dry_run-expired-42-None | 1000 | 2041 | now≥expires、age<10000；正TTL，仅expires已过期 |
| rust/basic02-execute-expired-42-None | 1000 | 2037 | now≥expires、age<10000；正TTL，仅expires已过期 |
| rust/basic03-dry_run-expired-42-None | 1000 | 2018 | now≥expires、age<10000；正TTL，仅expires已过期 |
| rust/basic03-execute-expired-42-None | 1000 | 2034 | now≥expires、age<10000；正TTL，仅expires已过期 |
| python/basic02-dry_run-expired-42-None | 1000 | 2666 | now≥expires、age<10000；正TTL，仅expires已过期 |
| python/basic02-execute-expired-42-None | 1000 | 2622 | now≥expires、age<10000；正TTL，仅expires已过期 |
| python/basic03-dry_run-expired-42-None | 1000 | 2653 | now≥expires、age<10000；正TTL，仅expires已过期 |
| python/basic03-execute-expired-42-None | 1000 | 2433 | now≥expires、age<10000；正TTL，仅expires已过期 |


本轮两语言unknown的原输入与停止后inspect（没有清库或换身份恢复）：

```jsonl
{"language":"rust","input":{"command_id":"ff005-1793765932250-92428-14","expires_at_ms":1793765992250,"issued_at_ms":1793765932250,"ready":true,"schema_version":1,"source_id":"demo01-feed","value":42},"state":{"counts":{"unknown":1},"meta":{"implementation":"rust","instance_id":"ff-rust-basic02","mode":"execute","schema_version":1,"store_uuid":"1793765932238-93254-0"}},"GET":1,"ReadVar":11,"WriteVar":1,"product_exit":1,"resource_verdict":"expected fault classified without forced stop"}
{"language":"python","input":{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"ff005-command","value":42,"issued_at_ms":1793765593447,"expires_at_ms":1793765623447},"state":{"meta":{"schema_version":1,"implementation":"python","mode":"execute","instance_id":"ff-python-basic02","store_uuid":"20371fe83c544205ace1a65aa85d3928","created_at":"2026-11-04T04:13:13.269Z"},"counts":{"unknown":1}},"GET":1,"ReadVar":11,"WriteVar":1,"product_exit":1,"resource_verdict":"fail F-QA1-002"}
```

真实成功写/typed ACK代表样本（只证明协议ACK与本地confirmed，不证明机器/工艺完成）：

```jsonl
{"language":"rust","operation":5,"original_response_hex":"0300001602f0803203000000010002000100000501ff","positive":true,"request_hex":"0300002502f080320100000001000e00060501120a1002000200018400000000040010002a","request_ref":[0,1],"response_ref":[0,1],"sent_response_hex":"0300001602f0803203000000010002000100000501ff"}
{"language":"python","operation":5,"request_hex":"0300002502f080320100000002000e00060501120a1002000200018400000000040010002a","original_response_hex":"0300001602f0803203000000020002000100000501ff","sent_response_hex":"0300001602f0803203000000020002000100000501ff"}
```


## 人工入口与独立副本证据

准备阶段先完成上述locked build/sync与显式init，随后才起fixture并一次生成原command。基础case的两个`zsh -f`不共享FF变量，逐字提取examples的赋值/启动/停止/inspect/rebind块，分别通过read输入真实绝对路径/case；只有文档允许的副本路径、case与mode替换。Rust product/fixture目录软链接只指向同一QA根已独立建出的target，没有借Development二进制。人工三case不并列写同一target。

teaching01的完整app/YAML/带assert接线脚本逐字来自自身USER_GUIDE；两模式运行复用相同的显式CLI/fixture/原身份路径与新synthetic状态，观察6秒（比旧教程的2秒更长），没有刷新TTL或改产品能力。这里不宣称逐字执行了旧教程每个准备命令或做了FF-002整任务重验。

正式Rust额外用formal-product无feature release和正式basic02.yaml；正式Python额外用本QA own 3.11 venv依赖、`PYTHONPATH=<正式工程>/src`及`PYTHONDONTWRITEBYTECODE=1`，真实加载正式`src/field_flow/cli.py`并从正式cwd使用其fixture源码，没有在正式树sync环境或制造pycache。P/teaching环境各自独立；正式入口检查不能替代前面的独立单工程复制检查，两者都已完成。

| 语言 / 来源 / case / mode | state counts | GET/ReadVar/WriteVar | 产品/夹具/A/B exit | 秒 | 精确已消失PID（shell/产品/driver/native等） |
| --- | --- | --- | --- | --- | --- |
| python/独立副本/basic01/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 6.956 | 98394,98396,98399,98400,98405,98436,98439 |
| python/独立副本/basic01/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.937 | 98552,98554,98556,98557,98563,98566,98568 |
| python/独立副本/basic02/dry_run | `{"simulated":1}` | 12/12/0 | 0/0/0/0 | 6.845 | 98683,98685,98687,98688,98694,98697,98727 |
| python/独立副本/basic02/execute | `{"confirmed":1}` | 1/12/1 | 0/0/0/0 | 6.811 | 98834,98836,98838,98839,98843,98846,98848 |
| python/独立副本/basic03/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 6.882 | 98992,98994,98996,98997,99003,99006,99008 |
| python/独立副本/basic03/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.835 | 99122,99124,99126,99127,99161,99164,99166 |
| python/正式树/basic02/dry_run | `{"simulated":1}` | 12/12/0 | 0/0/0/0 | 6.934 | 863,865,868,869,874,877,879 |
| python/正式树/basic02/execute | `{"confirmed":1}` | 1/12/1 | 0/0/0/0 | 7.024 | 1018,1020,1022,1023,1029,1032,1034 |
| python/教学副本/teaching01/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 6.907 | 99276,99278,99282,99283,99287,99290,99295 |
| python/教学副本/teaching01/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.820 | 99433,99435,99437,99438,99442,99445,99447 |
| rust/独立副本/basic01/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 7.139 | 95950,95952,95986,95992,95995,95997 |
| rust/独立副本/basic01/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.813 | 96106,96108,96109,96112,96115,96117 |
| rust/独立副本/basic02/dry_run | `{"simulated":1}` | 12/12/0 | 0/0/0/0 | 6.716 | 96778,96780,96782,96785,96788,96790 |
| rust/独立副本/basic02/execute | `{"confirmed":1}` | 1/12/1 | 0/0/0/0 | 6.752 | 96917,96919,96920,96923,96957,96959 |
| rust/独立副本/basic03/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 6.718 | 97067,97069,97070,97073,97076,97078 |
| rust/独立副本/basic03/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.721 | 97186,97188,97189,97192,97195,97197 |
| rust/正式树/basic02/dry_run | `{"simulated":1}` | 12/12/0 | 0/0/0/0 | 6.685 | 473,475,476,479,484,486 |
| rust/正式树/basic02/execute | `{"confirmed":1}` | 1/12/1 | 0/0/0/0 | 6.680 | 645,647,648,655,660,662 |
| rust/教学副本/teaching01/dry_run | `{"simulated":1}` | 12/0/0 | 0/0/0/0 | 7.109 | 97348,97350,97358,97364,97367,97369 |
| rust/教学副本/teaching01/execute | `{"confirmed":1}` | 12/0/1 | 0/0/0/0 | 6.695 | 97474,97476,97477,97482,97485,97487 |


全部20个人工场景≤45秒，actual product/fixture wait0，JSONL正常join/reap及shutdown_complete、无forced/fault_cleanup；B在A关闭fixture后继续检查其自己保存的FF_PID与各child原PID，每个ps退出1且stdout/stderr空，kill(0)=ESRCH，各自三口同时rebind。

## 封存、资源依赖与返工handoff

开始与结束的51件冻结候选、37件实现及spec/tasks SHA均相同；780件受保护源/旧bundle/清单/锁hash无差异；Rust57/Python62副本与正式树相同。scope-start/scope-final均unexpected=[]。教学源码差异严格为Rust`src/{app/mod.rs,config.rs,runtime.rs}`与新增teaching01 app/YAML；Python仅config/runtime与新增teaching01 app/YAML；正式teaching01不注册。验证角色配置SHA256=`ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`（仍仅配置证据）。

2026-11-04 12:29:17 +08:00资源封存：新94场景358个去重PID、旧回归输出/新资源182个PID，共540个确切PID全ps1/空输出/空stderr且kill(0)=ESRCH；本QA可执行产品/driver/fixture/双shell路径无运行残余。六口lsof exit1空stdout/stderr，并同时bind/listen/close成功；Rust三口不设REUSEADDR，Python三口沿既有REUSEADDR规则。全部目录/状态/原输入保留；无最终回收动作。F-QA1-002曾被强收的原driver也已消失，原SIGTERM/-15事实保留，不与正常join混同。

Q根保留：普通/正式/fixture/test/教学targets（教学夹具包仅为正确重建失效过本QA缓存）、Rust/Python两个原版与两个教学副本/各自venv、自有uv-cache、evidence-rust/evidence-python、10组manual-*与其新状态、22条edge输出、commands原日志/元数据、原hash/diff、静态与矩阵审计脚本/报告、failure-F-QA1-002.json、sealed-resources.json及qa-start时已有路径清单。没有新Git分支/worktree，没有触碰此前已有/Development仍供证据的临时资源。

旧测试硬编码前缀本轮额外新建95个路径如下：它们是FF-005 QA1自己的新执行资源，不冒称旧任务证据；从执行前清单差集和真实输出确认归属。所有执行前已有同前缀路径保留不动；不能仅凭前缀清理。

```text
/private/tmp/ff-001-r1-r3-rust-ack-rejections-1793765874869-92247-0
/private/tmp/ff-001-r1-r3-rust-audit-queued-1793766018978-94888-54
/private/tmp/ff-001-r1-r3-rust-bad-ref-read-1793765998535-93937-228
/private/tmp/ff-001-r1-r3-rust-bad-ref-write-1793765998679-93937-233
/private/tmp/ff-001-r1-r3-rust-block-boundary-1793766013574-94888-25
/private/tmp/ff-001-r1-r3-rust-capacity-1793766018519-94888-40
/private/tmp/ff-001-r1-r3-rust-child-death-1793766000674-94696-0
/private/tmp/ff-001-r1-r3-rust-concurrent-1793765973192-93937-15
/private/tmp/ff-001-r1-r3-rust-confirmed-then-sink-1793765971514-93933-0
/private/tmp/ff-001-r1-r3-rust-disconnect-1793765996819-93937-193
/private/tmp/ff-001-r1-r3-rust-dry-1793765981652-93937-161
/private/tmp/ff-001-r1-r3-rust-gate-normal-1793765998364-93937-222
/private/tmp/ff-001-r1-r3-rust-immutable-1793766013712-94888-30
/private/tmp/ff-001-r1-r3-rust-int-1793765972443-93937-0
/private/tmp/ff-001-r1-r3-rust-int-readback-1793766012740-94888-0
/private/tmp/ff-001-r1-r3-rust-int-readback-1793766012907-94888-5
/private/tmp/ff-001-r1-r3-rust-int-readback-1793766013079-94888-10
/private/tmp/ff-001-r1-r3-rust-int-readback-1793766013253-94888-15
/private/tmp/ff-001-r1-r3-rust-int-readback-1793766013415-94888-20
/private/tmp/ff-001-r1-r3-rust-lost-ack-1793765981799-93937-166
/private/tmp/ff-001-r1-r3-rust-matched-ack-preflight-1793765998356-93937-221
/private/tmp/ff-001-r1-r3-rust-parent-death-1793766006390-94696-2
/private/tmp/ff-001-r1-r3-rust-queued-expiry-1793766013854-94888-34
/private/tmp/ff-001-r1-r3-rust-queued-stop-1793765997980-93937-215
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-precall-1793766026686-95026-30
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-queued-1793766025794-95026-22
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-state-1793766025803-95026-23
/private/tmp/ff-001-r1-r3-rust-r4-rework-clock-state-1793766026695-95026-31
/private/tmp/ff-001-r1-r3-rust-r4-rework-fifo-1793766021212-95026-0
/private/tmp/ff-001-r1-r3-rust-r4-rework-fifo-state-1793766021222-95026-1
/private/tmp/ff-001-r1-r3-rust-r4-rework-minimum-io-1793766023787-95026-9
/private/tmp/ff-001-r1-r3-rust-r4-rework-started-1793766024050-95026-15
/private/tmp/ff-001-r1-r3-rust-r4-rework-started-state-1793766024058-95026-16
/private/tmp/ff-001-r1-r3-rust-ref-epoch-1793766019217-94888-61
/private/tmp/ff-001-r1-r3-rust-reject-1793765973044-93937-11
/private/tmp/ff-001-r1-r3-rust-reject-bits-1793765876690-92247-46
/private/tmp/ff-001-r1-r3-rust-reject-count-1793765876076-92247-26
/private/tmp/ff-001-r1-r3-rust-reject-count-1793765883755-92247-133
/private/tmp/ff-001-r1-r3-rust-reject-data_length-1793765876374-92247-36
/private/tmp/ff-001-r1-r3-rust-reject-empty-1793765877132-92247-61
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793765877281-92247-66
/private/tmp/ff-001-r1-r3-rust-reject-extra-1793765883901-92247-138
/private/tmp/ff-001-r1-r3-rust-reject-follow_correct-1793765884049-92247-143
/private/tmp/ff-001-r1-r3-rust-reject-function-1793765875928-92247-21
/private/tmp/ff-001-r1-r3-rust-reject-function-1793765883603-92247-128
/private/tmp/ff-001-r1-r3-rust-reject-global0-1793765883163-92247-113
/private/tmp/ff-001-r1-r3-rust-reject-global1-1793765883309-92247-118
/private/tmp/ff-001-r1-r3-rust-reject-id-1793765874869-92247-1
/private/tmp/ff-001-r1-r3-rust-reject-item-1793765883455-92247-123
/private/tmp/ff-001-r1-r3-rust-reject-oldref-1793765882556-92247-91
/private/tmp/ff-001-r1-r3-rust-reject-otherref-1793765882715-92247-97
/private/tmp/ff-001-r1-r3-rust-reject-param_length-1793765876225-92247-31
/private/tmp/ff-001-r1-r3-rust-reject-payload4096-1793765877432-92247-71
/private/tmp/ff-001-r1-r3-rust-reject-payload4097-1793765882115-92247-76
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793765882263-92247-81
/private/tmp/ff-001-r1-r3-rust-reject-ref0-1793765882868-92247-103
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793765882409-92247-86
/private/tmp/ff-001-r1-r3-rust-reject-ref1-1793765883018-92247-108
/private/tmp/ff-001-r1-r3-rust-reject-reserved0-1793765875652-92247-11
/private/tmp/ff-001-r1-r3-rust-reject-reserved1-1793765875789-92247-16
/private/tmp/ff-001-r1-r3-rust-reject-rosctr-1793765875514-92247-6
/private/tmp/ff-001-r1-r3-rust-reject-short_data-1793765876984-92247-56
/private/tmp/ff-001-r1-r3-rust-reject-short_header-1793765876837-92247-51
/private/tmp/ff-001-r1-r3-rust-reject-transport-1793765876522-92247-41
/private/tmp/ff-001-r1-r3-rust-server-absent-1793766019613-94888-66
/private/tmp/ff-001-r1-r3-rust-short-read-1793765999039-93937-240
/private/tmp/ff-001-r1-r3-rust-short-write-1793765999189-93937-245
/private/tmp/ff-001-r1-r3-rust-silent-cotp-1793765996292-93937-189
/private/tmp/ff-001-r1-r3-rust-slow-1793765991463-93937-179
/private/tmp/ff-001-r1-r3-rust-slow-http-1793765973436-93937-79
/private/tmp/ff-001-r1-r3-rust-split-1793765986776-93937-174
/private/tmp/ff-001-r1-r3-rust-stale-1793765996146-93937-184
/private/tmp/ff-001-r1-r3-rust-stale-reference-probe-1793765999697-93937-252
/private/tmp/ff-001-r1-r3-rust-t1-1793765997341-93937-199
/private/tmp/ff-001-r1-r3-rust-t2-1793765997514-93937-204
/private/tmp/ff-001-r1-r3-rust-t3-fail-1793765997689-93937-208
/private/tmp/ff-001-r1-r4-python-absence-alias-b6de7p_h
/private/tmp/ff-001-r1-r4-python-ack-matrix-uwv07517
/private/tmp/ff-001-r1-r4-python-audit-order-2st_qoad
/private/tmp/ff-001-r1-r4-python-audit-stop-n1zbldqp
/private/tmp/ff-001-r1-r4-python-cli-cnc82j45
/private/tmp/ff-001-r1-r4-python-clock-conflict-oenxhu8i
/private/tmp/ff-001-r1-r4-python-concurrency-j8hx1ker
/private/tmp/ff-001-r1-r4-python-connect-queue-1z_ozec1
/private/tmp/ff-001-r1-r4-python-deadline-max_short-twreobdx
/private/tmp/ff-001-r1-r4-python-deadline-slow-wv872lzo
/private/tmp/ff-001-r1-r4-python-deadline-split-85pbkbwn
/private/tmp/ff-001-r1-r4-python-deadline-stale-x84hdqk_
/private/tmp/ff-001-r1-r4-python-gate-rwvkng7g
/private/tmp/ff-001-r1-r4-python-process-death-uolefhsb
/private/tmp/ff-001-r1-r4-python-recovery-yxz0utmp
/private/tmp/ff-001-r1-r4-python-ref-maintenance-eb2ozs1y
/private/tmp/ff-001-r1-r4-python-state-sh3s9h7d
/private/tmp/ff-001-r1-r4-python-values-uibbdav8
/private/var/folders/k5/gb101k5j2nddcgfgrtsn0p300000gn/T/ff-001-r1-r3-cli-1793765970906-93893-0
```

关键临时报告指纹（结论、逐scene核心值及失败已持久写入本checklist，不只依赖临时路径）：

| Q下文件 | SHA256 |
| --- | --- |
| qa-copy-hashes.json | `ea32f82fccd6979d8e8c3396a3083eda322608f9204e7a109e8237234dfd42d0` |
| scope-final.json | `31228573e2be8571598e2e085a94aaefd1dc223dd675ffef48ce68cad7571ca2` |
| matrix-summary.json | `d331d77f42146e92b595ff8e70567e144ef795760195c8bff7641d93a06db8e5` |
| failure-F-QA1-002.json | `3973c754a7ab3fad771c63fe5414f77fa434757152463fe5e0ac66a4bcb6e219` |
| sealed-resources.json | `58a6ff72da2b4d60e65df61bab8cb20d66548dde977291e6be335d5ec4a8ee55` |
| cli-edges.json | `83f30556f5786ea3d4ff40392f6b6ce65ddd8c0e98ef966e4aaf3dd02c9c1f2f` |
| static.json | `0ec13ab6bf4e0ab6521c2ca93144f21547829eaadd274dbe6be5abcb92a4ac41` |


**QA -> Development：** 保留本QA1失败历史与原日志；同r1 A内修正六份旧注册声明，修复Python新harness对JSONL强制回收的结构化判定及符合原合同的unknown故障向量，并如实更新其tasks中被原输出否定的“74无强收”事实。不能借此更改受保护core/旧fixture/锁或把强收降级为正常验收。Development完成新的精确handoff后，由主协调实际另启新的fresh-context Verification，不能用本轮命令exit0替代新QA。

**QA -> Human Owner：** 当前为qa_failed，不进入最终接受；Human Owner final acceptance仍pending。已验证的语义/正常运行事实仅在本轮限定表面成立，不能外推B/C/平台/现场/托管/长稳/发布。原unknown状态与输入/历史继续保留，无自动重发或跨case迁移。

保留资源供Development定位、下一fresh QA交叉核对及Human Owner审阅；QA不清理。后续只有active coordinator在验收/证据归档及真实占用、归属、后续依赖核对后决定可回收项；本failed verdict本身不授权删除历史或旧任务资源。长任务窗口/通知由主协调唯一维护，本Verification未另启计时或外发消息。


---

# QA2：r1 A rework1 当前有效独立结论

**2026-11-04（Asia/Shanghai），FF-005 r1 A QA2 = `qa_passed`，AC01–AC12 均通过。F-QA1-001、F-QA1-002 对当前返工候选关闭。Human Owner final acceptance = pending。** QA1 的 `qa_failed`、原错误日志、PID/SIGTERM/-15、false positive、逐场景表与全部资源历史保留；前文“当前失败/未关闭”等语句只描述 QA1 时点。本轮不是 Owner 最终验收，不记 completed/owner_accepted。

## QA2 独立性、冻结对象与验证策略

主协调在 Development rework1 停写并 `developer_handoff` 后实际新启命名 `verification` / `fork_turns="none"`，本轮未继承 Development 对话推理。独立阅读根 AGENTS、双语根 README/PLAN、canonical workflow、verification.toml、FF/两工程 README/PLAN/catalog、完整 spec/tasks/QA1 checklist、当前实现与原始差异/输出。角色 TOML 为 gpt-6.1-sol/max，仅作配置证据；contract_only 的 fresh context、串行 handoff、diff/checklist 审计不代表平台 ACL 或强制路由。

应用 aiis、project-governance、rust-runtime、plc-point-mapping、i18n-workflow、code-document-indexer，以及语言中立/JSONL/资源归因参考；无 Vue/Tauri/后端改面，不加载相应模板。唯一正式写面是本 checklist；spec/tasks/实现/测试/配置/导航未由 QA2 修改。主协调另负责 12 导航与唯一长任务窗口/通知；QA2 不发送邮件或清理 DEV/QA1/历史资源。

正式工作树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`。QA2 自有根 `Q=/private/tmp/ff-005-r1-qa2-nym8gn9a`，独立 Python 工程 `P=Q/python`。QA1 引用根 `Q1=/private/tmp/ff-005-r1-qa-4cpsww4h`；DEV rework1 根 `W=/private/tmp/ff-005-r1-dev-ovnx25ib/rework1-39nzt0qd`，它们全程只读。

| 冻结输入 | SHA256 / 核对结果 |
| --- | --- |
| Owner-approved spec r1 A | `22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8`，开始/结束不变；要求、allowlist、12 AC 未变 |
| 当前 Development tasks | `1dcade929dddf7f1091ee1283172f2202eb63d57e7c373dd34089a6eff6f756c`，开始/结束不变 |
| QA1 checklist 原件 | `ce2bb7418d447b2b13c334aed4795e40f27eddf550a3b24a1d31d777b77c4a0d`；Q/checklist-start.md 保留完整原件，前文正文逐字保留 |
| 37 implementation manifest | `58516410099596398e8ae926b5582b91b82a0ae59ce811b32418c033b64ec268`，37/37 正式文件匹配 |
| 51 formal candidate manifest | `fd8c9b89693625c275349d5f05733c6557ed7a4fe5a6e8c5c6099cf5e17568bf`，开始/结束及写 checklist 后均 51/51 匹配；此 manifest 含 spec/tasks，不含独立 QA checklist |
| DEV 119 source-copy manifest | `e6c8e9115b61afac6f75caaf19aba76ada25e3e1251645412acb7e467f789df0`；独立重算正式 Rust57/Python62 源文件均匹配；没有执行 DEV 副本/二进制 |
| FF-004 r1 | `e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`，仍 draft 未批准、未触动 |

基于 C=`/private/tmp/ff-005-r1-coordinator-n1exrlf8` 的 816 件原始 hash、53 有限允许路径与 original/ 原 dirty 基线独立审计：780 保护文件开始/结束保持原字节，scope-start/final 的 unexpected=[]。新 app 单轮、只经原 parser/Execution；config/runtime diff 仅两 kind 与显式 dispatch/原 owner 传参。原 demo01/loopback、domain/Execution/owner/driver/HTTP/state/audit、旧 tests/fixtures、清单/锁/解释器 pin 都保持。Rust config/runtime 虽是本任务既有接线变更，相对 QA1 精确不变。

QA2 新复制 P 的 62 件自身正式源码/manifest/lock/config/locales/tests/docs，排除环境/target/状态/日志/真实配置，创建自身 venv。公共锁定包 cache 只从 Q1 读并复制到 Q/uv-cache，uv 只写自己 cache；不共享环境、不下载解释器/SDK/新 Agent 依赖。CPython3.11.12、uv0.7.8，macOS15.7.7 arm64；import-origin 证实 field_flow 与 tests 实际来自 P。P 62/62 文件与正式源开始/结束相同。

相对 QA1 的实际实现差异仅 11 件：六处注册说明、四份 examples ACK 术语、新 Python test。所有 README/USER_GUIDE/examples/config 文档的可执行 fenced block 与 QA1 完全相同；Rust38件运行相关文件零差异，Python42件相关文件仅新 test 有差异。因此本轮新跑 Python 完整套件，并按精确等价边界引用 QA1 未受影响的独立 Rust 构建/21项/37场景、20个人工/教学场景与22条 CLI 边界命令。引用不是 QA2 新执行，不把 QA1 整体失败改写为通过；QA1 Python unknown 的资源结论被明确排除。

## QA2 实际命令与结果

下表 Q/P/Q1/W 均为上文绝对路径的固定缩写。Q/run_job.py 只编排命令，保存 argv/cwd/UTC 起止/耗时/退出和完整原输出到 Q/commands/<label>.json/.log；辅助 Python 不冒充产品运行。

| cwd / 实际命令 | 真实结果 / 原输出 |
| --- | --- |
| P：`uv sync --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache` | exit0，新建自己 .venv；python-sync；锁定16包，未变 manifest/lock |
| P：`uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache python -m compileall -q src tests` | exit0；python-compileall |
| P：`FF005_EVIDENCE_ROOT=Q/evidence-python uv run --locked --offline --python 3.11 --no-python-downloads --cache-dir Q/uv-cache pytest -q -s` | **exit0，26 passed in 137.93s**；包装138.909414s，python-full；22既有 + 3 CLI case函数 + 1 JSON格式回归，三个 CLI 函数内37真实场景 |
| P：同锁定 offline uv 运行 `python Q/static_and_legacy.py` | 修正 QA 辅助脚本自己的 sys.path 后 exit0；static-legacy-v2；394局部链接全存在、双语代码块/方法表及 locale 递归键对称、六声明准确；新检测分别拒绝 DEV1 和 QA1 原失败日志 |
| Q：`python3 Q/audit_python.py` | exit0；python-matrix-audit；逐原JSONL/37报告/协议trace/状态/内存/ACK/线程与退出独立审计，不能只信 harness green |
| Q：`python3 Q/audit_references.py` | exit0；referenced-evidence-audit；QA1 关键 SHA 全匹配；Rust实际21项（18旧+3新），37场景/85.280548s/max5.739976s，20人工、22 CLI 原始证据/等价复核；**无新 Rust build/测试/人工执行声明** |
| 正式树：`python3 C/audit_scope.py`（起止各一次）；`git diff --check -- field-flow` | 全部exit0、unexpected=[]；scope-audit-start/final、scope-start；780保护hash不变 |
| Q：`python3 Q/seal_resources.py` | 精确 loopback 执行权限下exit0；seal-resources；244精确PID全不存在，六口lsof1/空stdout/stderr且同时 bind/listen/close成功，无自有程序残余 |
| P：`.venv/bin/python -c 'import sys, field_flow, tests; ...'` | exit0；python-origin；解释器 P/.venv/bin/python，field_flow/tests 均为 P 自身源码 |

六口 sandbox bind 首次均 EPERM/exit1（ports-sandbox），记录环境限制，不计产品失败；通过工具申请规格已批准的精确 127.0.0.1 六口权限后实际 preflight exit0（ports-authorized）及上述运行成立。没有换端口或杀占用者。QA 辅助 legacy 脚本首次从脚本目录导入 tests 失败 exit1（static-legacy），只修辅助 sys.path 后v2通过；另一次手动 origin 辅助检查 cwd 误在仓库根也出现 tests 缺失，改从P记录成功。它们未改正式实现或测试，不作为产品失败/取绿。旧协议回归中的既有预期故障/强收与37新场景的零forced分开；原 Server 正常断开 COTP0x80 诊断未吞掉，结合 server_exit0/remaining_threads=[]/真实join及rebind判断资源。

## 两项 QA1 finding 的当前关闭证据

| Finding | QA2 判定 / 精确证据 |
| --- | --- |
| F-QA1-001 | **closed**：六份已触达文档均准确列 demo01、plc_guard_get_int、get_value_guard_int，basic01复用demo01、teaching01仅教程副本、未知kind拒绝/非自动发现。实际 config/runtime 和四app/四YAML/配置表/入口一致；旧六句断言均不存在，394局部链接无缺失，双语方法/代码块对称。源、执行块与QA1正常人工/CLI证据等价，未凭链接检查推断文字正确。 |
| F-QA1-002 | **closed for current r1 A candidate**：新检测按JSON的 event / bool true / driver非0 reaped退出识别强收，紧凑/带空格true、false、无关message、-15都有必要回归。直接读取原DEV final-v3（driver63554/-15）和QA1（82757/-15）日志，整体、forced事件、true旗及非0reap四种子集分别全部被拒绝；各原日志仍有2 forced事件。新37场景所有driver exit0且逐PID threads_joined/remaining_threads=[]，stop_joined真布尔false，零forced事件。tasks顶部明确撤回旧“74无强收”，保留DEV1/QA1历史，当前事实与原输出相符。 |

**尚未解决的旧限制保留：** 旧 `hold_ack` 完全扣留 ACK 曾真实导致 SIGTERM/-15/forced=true；产品/driver/旧 fixture 没有因此修复，本轮没有证明完整 ACK 整包丢失下可正常回收。当前合规向量使用原 `short_data`，在首个正常读后 GET 延迟窗口才截断写 ACK：实际 PLC42、无有效 ACK→unknown。这不是整包丢失，也不把旧失败变成预期通过。两项 finding 对当前候选关闭不抹掉该历史限制。

本轮 unknown 关键持久证据：

```json
{"input":{"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":"ff005-command","value":42,"issued_at_ms":1793768047949,"expires_at_ms":1793768077949},"counts":{"unknown":1},"GET":1,"ReadVar":11,"WriteVar":1,"after_write_successful_reads":10,"memory_hex":"002aa5a5a5a5a5a5a5a5a5a5a5a5a5a5","product_exit":1,"fixture_exit":0,"driver_reaps":[{"pid":32920,"result":"fault_cleanup","exit_code":0},{"pid":32951,"result":"normal","exit_code":0}],"joins":[{"pid":32920,"result":"threads_joined","remaining_threads":[]},{"pid":32951,"result":"threads_joined","remaining_threads":[]}],"forced_events":[],"had_forced_driver_stop":false,"original_response_hex":"0300001602f0803203000000030002000100000501ff","sent_response_hex":"0300001502f0803203000000030002000100000501"}
```

原写ACK22字节，发送21字节且TPKT长度随原fixture调整，最后返回码字节截断；第一个ReadVar返回A5A5/未注入故障，随后仅一次写，十次独立ReadVar均正常返回002a，原库/身份不变、不重发、不回读升级confirmed。首driver fault_cleanup是原协议错误退休分类且exit0/threads_joined；替代driver normal/exit0。产品因unknown保留仍按原故障语义exit1，fixture0，未当正常工艺或普通stop成功。

## QA2 AC01–AC12

| AC | 结论 | 当前独立依据 |
| --- | --- | --- |
| AC01 | pass | r1 A精确批准/工作树/manifest/锁/copy/780保护hash均核实；独立P环境完整26项及CLI启动；Rust未变部分引用QA1自己构建21项/37场景证据，非DEV；B/C仍planned。 |
| AC02 | pass | 仅两新增kind/显式dispatch，三正式配置真实CLI load；旧demo01/loopback/domain/Flow/Target/Intent/Execution/owner/driver/HTTP/state/audit与锁保护不变。既有回归及QA1 22CLI边界支持unknown kind/teaching01/非法target/重叠拒绝。 |
| AC03 | pass | 每语言basic01两模式42/idle：同ID≥11GET仍simulated1/写0或confirmed1/写1/002a+14A5；strict idle无command/写且继续。Python本轮、Rust等价QA1。 |
| AC04 | pass | basic02真实首读A5负值后GET；execute GET1/写1后≥10独立读42，dry≥11读/GET仍simulated1/写0；-1/0两模式及读错零GET/写原错误均核实。 |
| AC05 | pass | basic03 -1/0/101正常skip续轮无command/写；1/42/100独立两模式写精确0001/002a/0064与邻接A5；42同ID≥11GET一次效果。 |
| AC06 | pass | 两新case各两模式idle/typed非法/纯expires过期：原错误、零写、非guard_false。Python四过期向量TTL1000ms，首错age2133–2220ms<10000且now≥expires；Rust原四向量2018–2041ms按QA1不变证据引用。普通skip无错误增长迹象且继续。 |
| AC07 | pass | 原Execution唯一写路径、原ID/issued/expires未刷新，旧TTL/ACK/identity/clock/排队回归通过；当前unknown42/GET1/写1/后十独立读仍unknown1，不提供自动恢复或旁路。旧hold_ack限制保持上述边界。 |
| AC08 | pass | 四新app无循环/连接/SQL/重试；Python明确用runtime现有owner。旧独立flow/同流不重叠/每PLC串行/慢HTTP回归保持；文档明确独立采样、非原子互锁和health非业务完成。 |
| AC09 | pass | 新双语examples/config、自身方法、环境/两模式/观察/停止/失败/可改点完整；六旧声明关闭。执行块精确未变，QA1 12基础人工+4正式树+4teaching场景/22边界逐原证据引用，Python新增37反向真实CLI重新执行。 |
| AC10 | pass | USER_GUIDE/teaching接线可执行块、相关app/config/runtime与QA1逐字节等价；引用QA1独立teaching编译/导入及各两模式真实运行，正式仍拒teaching01。FF-002全bundle/FF-004原hash不变。 |
| AC11 | pass | Python新34正常产品/fixture0；2读错+1unknown产品预期1单列，所有driver exit0/真实线程join、fixture0/实际rebind，零forced。每scene<45s/矩阵98.574276s<600；Rust/20人工/22边界引用精确未变证据。244本轮精确PID消失、六口同时rebind，无残余。 |
| AC12 | pass | tasks当前事实撤回误判并保留全部历史；本新fresh QA如实记录新26项/37场景与引用口径、逐scene数据、指纹/资源/限制和handoff。无产物/SQLite/密钥写正式树，Owner终验pending。 |

## QA2 新 Python 37场景持久结果

以下为本轮实际执行。计数均产品窗口减准备窗口；内存为停止产品后的独立16字节读回，邻接14字节逐一A5。结果/资源由上述独立解析重新断言，不只复制harness passed。34正常exit0、3预期故障exit1，fixture均0。原身份/时间仅一次生成，准备写与独立核验读不混入产品窗口。

| Scene | GET/ReadVar/WriteVar | counts | 首INT+14A5 | 产品/fixture exit | 秒 | 原精确PID |
| --- | --- | --- | --- | --- | --- | --- |
| basic01-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.499 | 31246,31247,31248 |
| basic01-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5`+14A5 | 0/0 | 5.953 | 31151,31152,31153 |
| basic01-execute-idle-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.500 | 31350,31351,31352 |
| basic01-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a`+14A5 | 0/0 | 5.603 | 31251,31252,31253 |
| basic02-dry_run-expired-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.657 | 31728,31729,31735 |
| basic02-dry_run-idle-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.578 | 31484,31485,31486 |
| basic02-dry_run-invalid-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.759 | 31545,31576,31605 |
| basic02-dry_run-read_error-42-None | 0/2/0 | `{}` | `a5a5`+14A5 | 1/0 | 1.375 | 31767,31768,31772,31773 |
| basic02-dry_run-value-42--1 | 11/11/0 | `{"simulated":1}` | `ffff`+14A5 | 0/0 | 5.829 | 31811,31812,31813 |
| basic02-dry_run-value-42-0 | 0/3/0 | `{}` | `0000`+14A5 | 0/0 | 1.831 | 31912,31913,31914 |
| basic02-dry_run-value-42-None | 11/11/0 | `{"simulated":1}` | `a5a5`+14A5 | 0/0 | 5.605 | 31383,31384,31385 |
| basic02-execute-expired-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.878 | 32643,32644,32645 |
| basic02-execute-idle-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.848 | 32566,32567,32568 |
| basic02-execute-invalid-42-None | 3/3/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.826 | 32608,32609,32610 |
| basic02-execute-read_error-42-None | 0/2/0 | `{}` | `a5a5`+14A5 | 1/0 | 1.584 | 32688,32689,32690,32695 |
| basic02-execute-unknown-42-None | 1/11/1 | `{"unknown":1}` | `002a`+14A5 | 1/0 | 5.914 | 32918,32919,32920,32951 |
| basic02-execute-value-42--1 | 1/11/1 | `{"confirmed":1}` | `002a`+14A5 | 0/0 | 5.719 | 32727,32728,32731 |
| basic02-execute-value-42-0 | 0/3/0 | `{}` | `0000`+14A5 | 0/0 | 1.687 | 32906,32907,32908 |
| basic02-execute-value-42-None | 1/11/1 | `{"confirmed":1}` | `002a`+14A5 | 0/0 | 5.677 | 32057,32086,32087 |
| basic03-dry_run-expired-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.562 | 33411,33412,33413 |
| basic03-dry_run-idle-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.561 | 33356,33357,33358 |
| basic03-dry_run-invalid-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.569 | 33403,33404,33408 |
| basic03-dry_run-value--1-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.747 | 33025,33026,33027 |
| basic03-dry_run-value-0-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.768 | 33060,33061,33062 |
| basic03-dry_run-value-1-None | 3/0/0 | `{"simulated":1}` | `a5a5`+14A5 | 0/0 | 2.821 | 33102,33107,33141 |
| basic03-dry_run-value-100-None | 3/0/0 | `{"simulated":1}` | `a5a5`+14A5 | 0/0 | 1.710 | 33285,33286,33287 |
| basic03-dry_run-value-101-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.622 | 33319,33320,33321 |
| basic03-dry_run-value-42-None | 11/0/0 | `{"simulated":1}` | `a5a5`+14A5 | 0/0 | 5.770 | 33148,33149,33150 |
| basic03-execute-expired-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.548 | 33726,33727,33728 |
| basic03-execute-idle-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.568 | 33682,33683,33684 |
| basic03-execute-invalid-42-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.615 | 33691,33711,33721 |
| basic03-execute-value--1-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.530 | 33444,33445,33446 |
| basic03-execute-value-0-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.530 | 33477,33478,33479 |
| basic03-execute-value-1-None | 3/0/1 | `{"confirmed":1}` | `0001`+14A5 | 0/0 | 1.575 | 33510,33511,33512 |
| basic03-execute-value-100-None | 3/0/1 | `{"confirmed":1}` | `0064`+14A5 | 0/0 | 1.569 | 33614,33615,33616 |
| basic03-execute-value-101-None | 3/0/0 | `{}` | `a5a5`+14A5 | 0/0 | 1.566 | 33647,33648,33649 |
| basic03-execute-value-42-None | 11/0/1 | `{"confirmed":1}` | `002a`+14A5 | 0/0 | 5.620 | 33518,33519,33520 |

总场景耗时 `98.574276s`，最大 `5.952651s`。四过期首错 age(ms)：basic02-dry_run-expired-42-None=2206, basic02-execute-expired-42-None=2220, basic03-dry_run-expired-42-None=2133, basic03-execute-expired-42-None=2134；各自TTL=1000ms、now≥expires、age<10000，未延长TTL或删除负例。

## QA2 结束审计、资源与接受 gate

资源封存时间 `2026-11-04T04:58:11.531441+00:00`（上海12:58:11）：新37场景、旧回归原报告/原stdout及pytest包装记录中244个去重正整数PID，逐个 ps1且stdout/stderr空、kill(pid,0)=ESRCH；没有把权限错误/空PID当释放。产品/driver/fixture先实际wait/join/reap，再检查消失；无Q2可执行程序残余。六口lsof1/空stdout/stderr，31102/31103/31880不设REUSEADDR、32102/32103/32880沿原规则，同时bind/listen/close全部成功；未发送终止信号或回收目录。源候选51/37与780保护hash、P62文件开始/结束一致；QA2唯一正式变更为单独列SHA的checklist，51冻结manifest所含文件全部保持。

Q保留：inputs/spec-start/tasks-start/checklist-start、formal/implementation/source-copy manifest、62文件P副本/自己的.venv与uv-cache、evidence-python 37状态/原输入/JSONL/协议/报告、commands全部原输出/元数据、scope/diffs/静态/legacy/unknown/矩阵/引用/资源审计脚本与JSON；无新Rust target、分支或worktree。Q1、DEV1、W及C仍只读保留。所有关键结论/新逐场景数据/ACK/driver退出/输入/哈希持久写在本checklist，不仅依赖临时路径。

旧pytest硬编码前缀本轮新建18件精确资源如下；这是QA2自己的FF-005新执行资源，不冒充旧任务证据。执行前已存在的同前缀目录未动，不能按前缀批量清理：

```text
/private/tmp/ff-001-r1-r4-python-absence-alias-fos78o7t
/private/tmp/ff-001-r1-r4-python-ack-matrix-lo7i46zt
/private/tmp/ff-001-r1-r4-python-audit-order-6hu5pqi0
/private/tmp/ff-001-r1-r4-python-audit-stop-sununb1u
/private/tmp/ff-001-r1-r4-python-cli-wola1sj_
/private/tmp/ff-001-r1-r4-python-clock-conflict-tc3e47zi
/private/tmp/ff-001-r1-r4-python-concurrency-s5njcz01
/private/tmp/ff-001-r1-r4-python-connect-queue-dpbxxmwy
/private/tmp/ff-001-r1-r4-python-deadline-max_short-5l_p9ouh
/private/tmp/ff-001-r1-r4-python-deadline-slow-r1o1o2zw
/private/tmp/ff-001-r1-r4-python-deadline-split-8fa4ul_4
/private/tmp/ff-001-r1-r4-python-deadline-stale-mlj9jifx
/private/tmp/ff-001-r1-r4-python-gate-0ix86o1f
/private/tmp/ff-001-r1-r4-python-process-death-4oicsw0s
/private/tmp/ff-001-r1-r4-python-recovery-c0xfmn85
/private/tmp/ff-001-r1-r4-python-ref-maintenance-zj7hyh8g
/private/tmp/ff-001-r1-r4-python-state-fk32mclm
/private/tmp/ff-001-r1-r4-python-values-bix0hfuh
```

主协调在Human Owner最终验收后核对归属、实际占用、后续工作和证据依赖，再决定安全回收时点；QA2未删除资源。必要保留目的为Owner审阅和原失败追溯，不将qa_passed本身视为删除权限。

| 验收层 | 当前状态 / 下一 gate |
| --- | --- |
| FF-005 r1 A精确本机synthetic候选 | qa_passed，AC01–AC12通过；Owner final acceptance pending |
| QA1/DEV1旧hold_ack强收与误判 | 历史真实失败保留；旧完整扣ACK资源限制未被修复或重新通过 |
| B/C进阶/C#、FF-003/FF-004 | 后续能力与独立批准；本轮未启动 |
| Windows/Linux、真实PLC/第三方API/DS/Backend/真实DB/历史时间或状态迁移 | 未做/未授权；本轮无相关外部动作 |
| 现场/容量/托管/长稳、安装/打包/发布/部署/Git refs/push | 不由本机QA推定，保持独立gate |
| 既有UTC日历差异 | 按spec保留，新app无时间producer；不宣称+08整改完成 |

**QA2 -> Human Owner：** 精确FF-005 r1 A返工候选独立qa_passed，两项finding对当前候选关闭；请由Human Owner自行作最终验收决定。没有未解决的当前A必需AC或环境blocker。旧完全扣ACK强收边界与全部失败仍诚实保留，不提供现场/部署或业务完成资格。主协调可以仅按本权威事实机械同步12导航；QA2不替写索引或授予Owner接受。

### QA2 关键附件指纹

| Q下附件 | SHA256 |
| --- | --- |
| inputs.json | `1cf1da918126b7cad12a32ef7ed91e9dbf2284fcba9b319a2fef0f352e3c915d` |
| scope-start.json | `1ee5b42a9dd8bf70c9c4d4c15fbc8344c00784fddabde30ab5c02bdb3fc57fca` |
| python-copy-hashes.json | `768a3bd0dd0341c59bd156fa71d256833a2f63216df9b7066ac426fb5da6c756` |
| static-and-legacy.json | `7b60507755d377ed3efb348d5903c27d08e738e2a3f30b13113650ce65631b01` |
| python-matrix-audit.json | `a757477dba85378643e80eb13e5c374c4f23b26490b876c96915f8e5e28e5277` |
| unknown-proof.json | `0e6ef172901fa193931c7fe58f105033e09df1f1625a708fc6e32540f547f56b` |
| referenced-evidence-audit.json | `3721e30e6e890571e0befc67e7b494db42aaa1010f5dd85f65bc95bccbb3d6ad` |
| sealed-resources.json | `68e1671c96735b74a21a1deff9e4395cbf3a7858475c64a175d86c6dddd26e5a` |
| created-temp-directories.json | `93cfaa0bdbd998367469e59bb2d4f87a75f7cea372889d5ccc9981f87db6107a` |
| commands/python-full.json | `1a5738ce8e186a1b85901c1f1d47ef32e424dbfbd856cb02ff720106784b7b34` |
| commands/python-full.log | `cd9d65704ffc6b0b8322d23de1f14658b2cca292fba109e9e9872bd55038bcae` |

verification.toml SHA256=`ac3f369876fb1a2b54e8f78e7c3054b01a8d3b70be66cb0456507ac4a010f67e`，仍仅配置证据。本QA窗口和通知由主协调唯一管理。


---

# Owner acceptance r1 A

## 2026-11-04 Human Owner 最终验收登记

2026-11-04（Asia/Shanghai），Human Owner 在主协调上一条完整交付“FF-005 r1 A 已完成，并通过独立 QA 的全部12项验收，进入你的最终验收”（附 Rust/Python 案例入口与 QA 记录）之后，紧邻回复原话：

> 批准

主协调将该真实决定转交原实际 Verification 角色登记。相邻交付明确指向精确 **FF-005 r1 A / AC01–AC12** 及本 checklist 的 QA2 `qa_passed`，因此本次“批准”绑定为该候选的 **Human Owner final acceptance**；它与 spec 中先前的范围批准是两个不同阶段。Verification 仅记录该已发生决定，没有替 Human Owner 授予验收，也没有重新执行 QA。

| 绑定对象 | 精确依据 |
| --- | --- |
| Task / Revision / slice | FF-005 / r1 / A，仅三个基础案例（basic01复用demo01，basic02/basic03新增）与已批准有界验证/教学说明 |
| 批准规格 | [spec.md](spec.md)，SHA256 `22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8` |
| Development rework1 handoff | [tasks.md](tasks.md)，SHA256 `1dcade929dddf7f1091ee1283172f2202eb63d57e7c373dd34089a6eff6f756c` |
| Owner 决定前的 QA2 checklist | SHA256 `04d41f26a9c19b7f12fc8d2ac61adde7b4e51ddaf41c55576c12b8f4051453c6`，AC01–AC12通过；两项finding对当前候选关闭；QA1失败与旧hold_ack限制保留 |
| 最终验收范围 | 本机 macOS arm64、自有 synthetic loopback HTTP/S7、标准 DB INT 与精确 r1 A候选；不外推现场工艺或业务完成 |
| 当前生命周期 | `owner_accepted`；原 spec的owner_approved、tasks的developer_handoff及前文Owner pending保留各自阶段事实 |

验收不扩大 Windows/Linux、真实 PLC/第三方 HTTP/Backend/DS/真实 DB、外部接口实施或调用、历史时间/状态迁移、现场/托管/容量/长稳、安装/打包/部署/发布/Git refs/push 权限；FF-004 r1、进阶 B、C# C 及其他任务仍按各自独立能力和批准 gate。QA1/QA2全部正文、失败证据和旧 `hold_ack` 完全扣ACK导致SIGTERM/-15/forced的未修限制保持，不将最终验收解释为该旧路径已修复或取得新运行证据。

## Owner acceptance closeout checkpoint

主协调正在按 canonical workflow 盘点本任务临时资源、归属、实际占用、后续依赖和证据保留需求。**此 checkpoint 未登记任何清理完成事实**；确切已回收/保留项、审计路径与指纹将在主协调提供真实结果后，由原 Verification 追加本 checklist。QA本轮没有清理资源，也没有使用任何 DEV/QA 临时环境、运行产品/测试/设备/网络或发送邮件。

本次唯一正式改动为本 checklist 的当前元数据、最新状态提示及本验收登记；既有 QA1/QA2正文逐字保留。文档校验使用系统文本解释器核对三文件 SHA256、正文保留、Markdown局部链接及 `git diff --check -- field-flow/plans/FF-005-basic-and-advanced-examples/checklist.md`，结果均通过。spec/tasks字节保持。12导航由主协调基于本真实Owner记录机械同步，Verification不代写。通知window由主协调唯一管理。

**Verification -> active coordinator：** Owner最终验收决定已登记，当前为FF-005 r1 A `owner_accepted`。仅资源closeout审计记录待追加；本checkpoint停止写入，等待主协调实际资源结果，不预填回收完成。


---

# Resource closeout r1 A

## 2026-11-04 实际收尾与 checkpoint 关闭

主协调以 active lifecycle coordinator 身份于 **2026-11-04T13:37:54.242728+08:00（Asia/Shanghai）** 完成本轮限定资源收尾。原 Verification 读取并核对其实际结果及 pre/post readiness、保留清单，追加本记录；QA没有执行删除、恢复环境、发信或运行产品/测试/设备/网络。FF-005 r1 A 的 `owner_accepted` 不变，此处关闭前文仍待实际审计的资源 checkpoint，不启动新的 Development/QA 软件周期。

**已回收：20个确切自有生成目录（11个Cargo target、3个uv-cache、6个Python .venv），以及仅指向这些目录的18个便利软链接。** 不按路径前缀清理，不删除源码、原synthetic库、输入、日志、协议或失败证据，不删除分支/worktree，不触及其他任务资源。

以主协调实际报告为操作事实源：`/private/tmp/ff-005-r1-coordinator-n1exrlf8/owner-closeout-result.json`，SHA256 `1b08489a99f898254fbe5f4fa126d3c67d252029a9325771bba720e716343fd2`。Verification本次仅用系统文本解释器读JSON/文件并重算hash/大小、检查路径存在性；没有使用已回收的DEV/QA项目环境。下列路径、数量、归属和结论持久记录，不以临时JSON作为唯一证据。

## 已回收20目录：归属与类别

| 执行归属 | 类别 | 精确路径 |
| --- | --- | --- |
| Development DEV1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-dev-ovnx25ib/fixture` |
| Development DEV1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-dev-ovnx25ib/product` |
| Development DEV1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-dev-ovnx25ib/rust-product` |
| Development DEV1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-dev-ovnx25ib/rust-test` |
| Development DEV1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-dev-ovnx25ib/teaching-product` |
| Development DEV1 | uv锁定公共包cache | `/private/tmp/ff-005-r1-dev-ovnx25ib/uv-cache` |
| Development DEV1 | Python自身venv | `/private/tmp/ff-005-r1-dev-ovnx25ib/python/.venv` |
| Development DEV1 | Python自身venv | `/private/tmp/ff-005-r1-dev-ovnx25ib/python-teaching/.venv` |
| Development rework1 | Python自身venv | `/private/tmp/ff-005-r1-dev-ovnx25ib/rework1-39nzt0qd/python/.venv` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/copy-product` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/fixture` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/formal-product` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/rust-test` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/teaching-fixture` |
| QA1 | Cargo target（产品/夹具/测试/教学构建） | `/private/tmp/ff-005-r1-qa-4cpsww4h/teaching-product` |
| QA1 | uv锁定公共包cache | `/private/tmp/ff-005-r1-qa-4cpsww4h/uv-cache` |
| QA1 | Python自身venv | `/private/tmp/ff-005-r1-qa-4cpsww4h/python/.venv` |
| QA1 | Python自身venv | `/private/tmp/ff-005-r1-qa-4cpsww4h/python-teaching/.venv` |
| QA2 | uv锁定公共包cache | `/private/tmp/ff-005-r1-qa2-nym8gn9a/uv-cache` |
| QA2 | Python自身venv | `/private/tmp/ff-005-r1-qa2-nym8gn9a/python/.venv` |

## 已移除18便利链接

下列均为本任务人工复演目录中的Rust产品/夹具入口链接，目标仅为上表已回收Cargo target；移除链接不修改其余人工原脚本/日志/状态/报告。Development拥有8个，QA1拥有10个，QA2没有此类链接。

| 执行归属 | 精确链接路径 | 原目标 |
| --- | --- | --- |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic01/fixture` | `/private/tmp/ff-005-r1-dev-ovnx25ib/fixture` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic01/product` | `/private/tmp/ff-005-r1-dev-ovnx25ib/rust-product` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-teaching01/fixture` | `/private/tmp/ff-005-r1-dev-ovnx25ib/teaching-product` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-teaching01/product` | `/private/tmp/ff-005-r1-dev-ovnx25ib/teaching-product` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic03/fixture` | `/private/tmp/ff-005-r1-dev-ovnx25ib/fixture` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic03/product` | `/private/tmp/ff-005-r1-dev-ovnx25ib/rust-product` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic02/fixture` | `/private/tmp/ff-005-r1-dev-ovnx25ib/fixture` |
| Development DEV1 | `/private/tmp/ff-005-r1-dev-ovnx25ib/manual-rust-basic02/product` | `/private/tmp/ff-005-r1-dev-ovnx25ib/rust-product` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic01/fixture` | `/private/tmp/ff-005-r1-qa-4cpsww4h/fixture` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic01/product` | `/private/tmp/ff-005-r1-qa-4cpsww4h/copy-product` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-teaching01/fixture` | `/private/tmp/ff-005-r1-qa-4cpsww4h/teaching-fixture` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-teaching01/product` | `/private/tmp/ff-005-r1-qa-4cpsww4h/teaching-product` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic03/fixture` | `/private/tmp/ff-005-r1-qa-4cpsww4h/fixture` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic03/product` | `/private/tmp/ff-005-r1-qa-4cpsww4h/copy-product` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic02/fixture` | `/private/tmp/ff-005-r1-qa-4cpsww4h/fixture` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-basic02/product` | `/private/tmp/ff-005-r1-qa-4cpsww4h/copy-product` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-formal-basic02/fixture` | `/private/tmp/ff-005-r1-qa-4cpsww4h/fixture` |
| QA1 | `/private/tmp/ff-005-r1-qa-4cpsww4h/manual-rust-formal-basic02/product` | `/private/tmp/ff-005-r1-qa-4cpsww4h/formal-product` |

## 保留证据、无运行占用与源码一致性

- **7203件保留工件、38,609,139字节**：主协调before/after清单完全相同，Verification逐条重算全部7203项的SHA256和大小均匹配，差异0；该清单内kind均为file。包括精确已验证源码快照、manifest/锁、raw stdout/JSONL、协议帧/场景报告、原命令身份/输入、unknown原synthetic状态库，以及DEV1/QA1的真实hold_ack强收与误判历史。没有为清理改写旧证据。
- **287个确切登记的旧前缀FF-005新执行目录全部仍在**：DEV1 154 + DEV1另2个CLI临时目录 + QA1 95 + rework1 18 + QA2 18，共287个去重路径。Verification从五份原精确清单重算集合并逐一检查目录存在，287/287；完整路径已分别持久列在tasks及本checklist前文历史清单，不能凭旧前缀批量清理，也不冒充旧任务新证据。
- 初次sandbox的ps spawn为EPERM，**当时未执行清理**；主协调取得同目的精确只读执行权限后，pre-readiness记录ps/lsof均exit0、resource_processes=[]、open_candidate_paths=[]，六口listener检查lsof exit1且stdout/stderr空，确认无占用才实施上表删除。post-readiness同样ps/lsof exit0、无相关进程/打开路径，六口31102/31103/31880/32102/32103/32880无listener；20目录与18链接全不存在。没有发送任何信号或启动产品。这里引用并核对已发生审计，不声称本次又运行ps/lsof、端口bind或产品验证。
- 正式37件implementation与已验证manifest `58516410099596398e8ae926b5582b91b82a0ae59ce811b32418c033b64ec268`逐件hash相同；纯文本scope审计unexpected=[]。spec SHA256 `22636d7248c6d0415b2c4e61c099d0d8c38332a2e75223fcae6780eae7167ab8`、tasks SHA256 `1dcade929dddf7f1091ee1283172f2202eb63d57e7c373dd34089a6eff6f756c`、FF-004 r1 SHA256 `e33aae41d18ba7faad19cb1ed563a19375996bc0f5d23ee7c646d62b2f7b0dc4`保持。C/original与baseline继续保留，无Git refs或分支/worktree删除。

| 保留根 | 归属 / 用途 |
| --- | --- |
| `/private/tmp/ff-005-r1-dev-ovnx25ib`（含`rework1-39nzt0qd`） | DEV1/rework1源码与教学快照、原命令/协议/日志/失败与unknown状态、原handoff/manifest；仅上表生成目录和入口链接回收 |
| `/private/tmp/ff-005-r1-qa-4cpsww4h` | QA1独立源码/教学快照、21/25项与74矩阵/20人工/22边界原证据、F-QA1-002原失败日志与状态、封存结果；原失败不因Owner接受而删除 |
| `/private/tmp/ff-005-r1-qa2-nym8gn9a` | QA2独立源码、26项/37场景原证据、新截断ACK unknown原输入/库/协议、legacy拒绝/等价引用/hash/资源审计；.venv/cache已按表回收，不恢复运行 |
| `/private/tmp/ff-005-r1-coordinator-n1exrlf8` | C/original原dirty基线、816文件hash/53有限路径、批准/导航/通知及owner-closeout审计记录；保持归属与授权追溯 |
| 原五份精确清单中的287目录 | 原旧测试硬编码前缀产生的本任务运行证据；保留状态/失败/日志/报告，前缀不是后续删除授权 |

**保留原因与释放条件：** 旧 `hold_ack` 完整扣ACK强收限制尚未修复，需要原始失败、unknown/协议/状态与精确已验证源码快照追溯。没有现行任务依赖已回收的生成环境/构建cache。后续故障调查如提取并持久化了必要原始证据，再由主协调重新核对归属、实际使用、后续/证据依赖后审计回收不再需要的工件；或按Human Owner明确的清理指示处理。此描述不虚构已获批准的新调查/实现任务，不提供整根或前缀删除权限。

## Closeout审计指纹与最终handoff

| C下真实附件 | SHA256 |
| --- | --- |
| owner-closeout-result.json | `1b08489a99f898254fbe5f4fa126d3c67d252029a9325771bba720e716343fd2` |
| owner-closeout-readiness.json | `bafa99ee2b2b6cdfd829a2d317e8286bd86c34966fcacf627408589fb9266c3a` |
| owner-closeout-post-readiness.json | `bef9b3bad56fb129cace73567c3a1578c5457986ca59c5174be706679876ac6b` |
| owner-preserved-before.json | `ccad54ab6f117e0133add8ca15e84b29be2445ea091b0d65955a94fb5ccbacf2` |

本轮文档/哈希审计通过：上述附件指纹、7203保留项、287目录存在、20目录/18链接不存在、正式37实现/spec/tasks/FF-004 hash、原checklist正文保留、Markdown局部链接和差异空白检查；没有新增软件测试或运行资格。原Owner acceptance checkpoint SHA256 `d324ae53999048fcb97178ecd6a20e04af88ace944748b6068b34d75ce2ce4d9`及其待审计文字完整保留为历史；当前限定资源closeout已完成，需保留的证据及后续释放条件已记录，Owner最终验收仍为 `owner_accepted`。旧hold_ack限制与平台/现场/长稳/部署/发布、外部接口及FF-004/B/C边界不变。

**Verification -> active coordinator：** 本checklist已登记真实资源收尾，当前资源checkpoint关闭。仅本checklist发生正式写入，spec/tasks/源码/导航均未改；主协调据此机械同步12导航至owner_accepted，并维护新的Owner-acceptance通知window。Verification停止写入，不发邮件，不再启动Dev/QA周期。
