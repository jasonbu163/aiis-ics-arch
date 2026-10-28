Task ID: FF-002
Revision: r1
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA1 failed AC05 on reproducible cross-terminal PID handling in the four project user guides; return to actual Development for scoped rework, retain this failure and evidence, then start a new fresh-context Verification; Human Owner final acceptance remains pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Field Flow 双语手册、案例教程与 Rust BUILD 文档独立核验
Owner: Field Flow
Acceptance Chain Reference: FF-002 r1 scope approval -> Development -> fresh Verification -> Human Owner final acceptance

# FF-002 r1 独立 Verification

实际角色 `verification`，执行者 `/root/ff002_verification_r1`；由唯一 active coordinator `/root` 在真实 developer_handoff 后，以 `fork_turns="none"` 启动。独立读取 approved spec、tasks、正式文档、实现、diff 与原始证据，不继承 Development 对话推理。`.codex/agents/verification.toml` 的 model/effort 只作配置证据；本 profile 为 `contract_only`，不声称 hard ACL 或底层运行遥测。

正式树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `1fa1ce50a521ebd51c2c43389db011a76f2d74bf`。已核对 spec SHA256 `de9e338f495e1ae756ff50bc12d798edefb1a2f572ec6bc6cd6fb3e150ef3b7c`、tasks SHA256 `78bebeb0823d9682ea0dd1d6c55fdab65dbb0e84c23a875dd887d26811dbe0b0`、16 文档 candidate manifest SHA256 `6217888378795ca536f13079fa65b1c7a1294ea534642f1bc44671cd87627d3b`。

QA 私有根 `/private/tmp/ff-002-r1-qa-E8j08DYR`。正式写入仅本 checklist；辅助记录、副本、环境、target、synthetic 状态只在该私有根。并行 DAA/DS/root dirty 不归本任务；不 reset、不清理任务外资源。19 份主导航的真实阶段由 coordinator 机械同步，不能当实现变更。

已读取根 AGENTS、README/PLAN 双语、FF 和两工程 README/PLAN 双语、canonical workflow、verification TOML、完整 spec/tasks。使用 aiis、project-governance、rust-runtime、plc-point-mapping、code-document-indexer、i18n-workflow；backend-arch 仅限本地状态事务边界，另按需读取跨语言分层、运行日志及资源生命周期 references。未修改共享 skills 或产品。

## 1. QA1 verdict 与失败项

**2026-10-23：`qa_failed`。** F-QA1-001 违反 R04.2 / AC05：四份子工程手册把 runtime PID 仅保存在终端 B，却在明确属于终端 A 的收尾代码块中使用该变量。独立终端 A 中变量为空，`ps` 返回非法 PID，不能按文档完成必需的资源释放核对。不是产品 runtime 缺陷，也不是权限不足造成的推测；已在允许只读进程查询的复现中得到实际退出码 1。

| 正式文件 | 精确位置与证据 |
| --- | --- |
| [Rust USER_GUIDE](../../field-flow-rust/USER_GUIDE.md#dry-run-lesson) | 第 62 行强调 shell 变量不共享；B 在 81 / 111 行赋值 `FF_PID=$!`；90 / 120 行切回 A 关闭夹具，随后 96 / 126 行直接 `ps -p "$FF_PID"`，没有向 A 传递 PID。 |
| [Rust 中文手册](../../field-flow-rust/USER_GUIDE.zh-CN.md) | 与英文同位置、同命令：62、81 / 111、90 / 120、96 / 126 行。 |
| [Python USER_GUIDE](../../field-flow-python/USER_GUIDE.md#dry-run-lesson) | 第 61 行强调 shell 变量不共享；B 在 82 / 112 行赋值；91 / 121 行切回 A，97 / 127 行使用未传入 A 的 `FF_PID`。 |
| [Python 中文手册](../../field-flow-python/USER_GUIDE.zh-CN.md) | 与英文同位置、同命令：61、82 / 112、91 / 121、97 / 127 行。 |

第 7 节 teaching01 又要求按第 3 节完成精确 PID / 端口检查，因此同样依赖有缺口的收尾步骤。若 A 恰巧残留另一场景的 `FF_PID`，还可能检查错误对象；不能把偶然 shell 状态作为可照做教程的前提。

独立复现（cwd 为 QA 私有根，`/bin/zsh -f`，调用环境移除 `FF_PID`；两个新 shell 不共享状态）：

```bash
# 终端 B 的独立 shell：仅用自身可等待的短命子进程证明变量归属。
sleep 0 &
FF_PID=$!
wait "$FF_PID"
printf "B runtime PID=%s\n" "$FF_PID"
# 返回 0，输出 B runtime PID=50340。

# 新的终端 A shell：按手册收尾块使用尚未赋值的变量。
printf "A FF_PID=<%s>\n" "$FF_PID"
/bin/ps -p "$FF_PID" -o pid=,stat=,command=
# stdout: A FF_PID=<>
# ps 返回 1；stderr 以 ps: Invalid process id: 开始。
```

原始 `ps` 错误尾部含无效 UTF-8 字节，保存的 stderr hex 为 `70733a20496e76616c69642070726f636573732069643a2020b70a`。最终复现记录 `terminal-A-escalated.json` SHA256=`9be885b747e84d06b49285831b378fb3d6c4a057d2236c5db6cb135f876ecda8`。关键命令、变量值、诊断及退出码已在本 checklist 持久化，不以临时文件作为唯一失败证据。

**交回 Development 的关闭条件：** 在四份手册中明确每个检查的所属终端；需要 runtime PID 的命令须在拥有它的终端执行，或明确传入实际 PID 后再检查。保持中英对称、fixture 正常退出方式及退出码核对正确，不把空值/非法参数当 PID 不存在。用两个无共享变量的真实 shell 按修订步骤核对。QA 不修改手册。

发现此必改缺陷后停止本候选的产品运行演练；没有启动 runtime、driver、fixture 或服务，也没有准备项目环境或构建目标。后续仍需新 Development handoff 和新的 fresh-context Verification 完成本 spec 第 8 节全部必要本机复演，不能以本轮静态通过项或 DEV 自检跳过。

## 2. AC01–AC14 独立结果

`pass（静态）` 只覆盖该项要求的文档/源码核对；`partial/not_run` 不表示验收通过。当前整体结论是失败，不是有条件通过。

| AC | QA1 结果 | 独立证据 / 限制 |
| --- | --- | --- |
| AC01 | pass（静态） | 唯一 FF-002/r1、namespace=aiis-ics-arch、classification=root、独立验收链、批准原文及角色归属一致；spec/tasks 精确 SHA 符合交接，不继承 FF-001 或未形成的 DS 建议批准。 |
| AC02 | partial | 八新文档齐备；完整阅读中英正文、四新文档 pair 的结构/代码块/能力/风险/平台说明对称。两子工程有自身完整必需步骤，但跨终端收尾可照做性存在 F-QA1-001，不能判此完整 AC 通过。 |
| AC03 | pass（静态） | 总/子手册与入口一致写 Python 学习/原型且本任务不打包、Rust 长期 runtime 建设主线、不要求未来全部双实现；源码/测试/历史保护 hash 未变。 |
| AC04 | pass（静态） | 独立读取 Rust bin/fixture、Python fixtures main/runtime：真实 server child、HTTP/proxy 线程、六固定端口、DB1/16、42、Rust cmd-001/TTL60s、Python fixture-UUID/首 flow source/TTL30s 与 input age10s、各自正常关闭/报告名均可追溯；人工入口没有自动测试内部控制能力。未做新的协议运行。 |
| AC05 | **failed** | F-QA1-001；独立 shell 的空 PID 和实际 ps exit1 已复现。自身空 cwd 产品帮助、init/dry/execute/inspect/正常退出复演未运行，不以 DEV 报告替代。 |
| AC06 | pass（静态） | 对照两版 config/domain/execution/state/audit/CLI/owner/runtime：字段与预算、物理重叠、分模式/实现/instance/schema、T1/T2/T3、unknown、容量、轮转及故障退出说明符合所读实现；没有恢复绕过写法。UTC 日历限制明确，不改 schema/历史/时间。未新增故障矩阵。 |
| AC07 | pass（静态） | 对照真实 demo01、HTTP、Intent/Clock、Execution.apply、Owner.read/Sample、Stop、inspect/snapshot/log/event 签名、返回、await 与 owner；Python按实际对象说明、不假造注解/anchor SDK；写只能经 Execution，raw/SQL/driver 为内部边界。 |
| AC08 | partial / not_run | 完整 app/YAML、Rust app/mod/config/runtime 和 Python runtime import/config/dispatch 的精确替换均有正式基线对应；无新 locale key，索引更新说明存在。QA 仅建立未修改的独立源码副本；未实际应用/编译/导入/运行教学案例，后续 fresh QA 必须执行。 |
| AC09 | pass（静态） | 独立读两版调度/owner 与 Rust local_protocol、Python test_three_read_flows_and_slow_http 源码：每流 async task、完成后 interval，同 PLC 有界 FIFO/持久 child，HTTP 不预占队列，独立 request/sample。文档明确测试直接调服务，未把未注册读流写成可用 CLI。未重跑旧全矩阵。 |
| AC10 | partial / not_run | Cargo.toml/lock、current_exe/__driver、include_str locale、rust-snap7 build.rs、bundled SQLite 与 notices 的静态核对成立；审核 DEV 原始 file/otool 输出但没有用 DEV 二进制代替自己的 release/fixture 构建及依赖检查，后者未运行。 |
| AC11 | pass（静态来源） | 冻结 rust-snap7=1.142.2/source/checksum/build.rs 与来源一致；核对实际 UnixStream/pre_exec/FD/flock/fcntl/Unix signal，Windows 原样阻塞、Linux未测和跨链 C/C++/linker/SDK需求写清。浏览官方 Cargo build / Rust platform support，未据 target 清单授予平台资格。 |
| AC12 | pass（范围审计） | 16候选逐项与manifest/DEV字节快照相同；581受保护正式文件/FF-001与ARCH历史hash相同。19导航审计仅见17份预期FF-002 phase/真实checklist链接机械差异，其余2份未变；无任务外归因或改动。35范围文档本地链接/锚点无缺失，FF索引双语一致。 |
| AC13 | partial | 真实QA命令/环境/失败/未运行/资源见下文；本轮无服务进程、无新监听或数据库。独立只读观察DEV交接36个已知PID和QA短命helper均absent、六口无listener。DEV实际wait/rebind报告仅作为待审输入，不能替代新的必要产品演练；此AC尚未完整通过。 |
| AC14 | pass（流程控制） | 在实际 fresh context 读取资料并独立得出 qa_failed；仅本 checklist 写入，无静默修复、无Owner验收。返回Development，修订候选再另fresh QA；后续平台/现场/托管/长稳/分发gate保持。 |

## 3. 独立命令、环境与范围审计

环境实测：Darwin 24.6.0 arm64；zsh 5.9；辅助文本/审计 Python 3.9.6；rustc 1.89.0（aarch64-apple-darwin，LLVM20.1.7）、Cargo1.89.0、Apple clang17.0.0、uv0.7.8。没有用 helper Python 执行项目行为；本轮未准备项目CPython环境。DEV 的 CPython3.11.12 与依赖版本属于已审阅的 DEV 原始输出，不声称是本轮新环境结果。

下表 repo 指正式树，Q 指上述 QA 私有根。所有辅助输出只写 Q；命令脚本的真实 args/cwd/退出码及必要原输出在 Q 对应 JSON/文本中。正式结论摘要如下：

| cwd | 实际命令 / 检查 | 结果 |
| --- | --- | --- |
| repo | `git rev-parse HEAD`；`git status --short`；`cat`/`sed`/`rg`读取契约、完整任务/文档及相关源码/锁/fixture/native/notices | HEAD符合；并行dirty已盘点。读取与范围核对未执行产品。 |
| repo | `uname -mrs`；`rustc -Vv`；`cargo -V`；`clang++ --version`；`uv --version`；`uv python find --help`；`python3 -V`；`/bin/zsh --version` | 均0，版本如上。仅读help确认find采用位置REQUEST，不执行下载或安装。 |
| repo | 辅助Python以SHA256逐项核对16文档/快照、581保护文件、spec/tasks；按批准复制两工程到Q，排除环境/target/cache/dist/状态/日志/真实.env | 0，16/16与581/581相等，无正式产品写入；独立副本未运行。`start-audit.json` SHA256=`57c30eabc7b4eb827efca2bd75f1bbce1aac8dcfe95d4439a8e1dcd555f5bb1f`。 |
| repo | `python3 Q/static_checks.py` | 0；35份范围文档共651个活动本地链接均存在，所带锚点存在，无尾空格；7组候选双语pair章节/代码块对称，其中Rust/Python USER_GUIDE各22块、BUILD1块逐字节相同。根README既有树注释中英本就不同，不作失败。`static-results.json` SHA256=`ee6805db2ff0e75337c03613126c5b84001d0350fa699cccabcebab924ac4e7b`。 |
| repo | `bash /Users/jason/Desktop/DreamCode/AI/AIIS/skills/project-governance/scripts/check-governance-bundle.sh /Users/jason/Desktop/DreamCode/aiis-ics-arch field-flow field-flow/field-flow-rust field-flow/field-flow-python` | **1**；stdout0行，stderr322行。stdout+stderr SHA256=`df8ce220425c9cbfd25f66a4fe756e916e75a72bf25aaa6fefac942a435ca15c`，与coordinator before逐字节相同；318任务外既有+4合法子PLAN父spec链接解析限制。不记全仓通过、不造子bundle/改checker。 |
| repo | 辅助Python逐项核对DEV evidence-manifest中的140文件哈希，并核对8场景原始inspect/report与summary | 0，140/140一致；8场景inspect一致，DEV报告显示各dry simulated1/write0、execute confirmed1/write1，Python内存002a。仅为证据一致性复核，不是本轮运行结果。`dev-evidence-review.json` SHA256=`8ec4ae7b272062f8ddd0e6522111a7723c7f187c6b3c629b3e341432eca1e16f`。 |
| Q | 独立 `/bin/zsh -f -c` 两终端变量复现；B自身短命子进程wait，A同文档ps命令 | B0；A变量空，允许只读ps后实际exit1非法PID。最终JSON hash见F-QA1-001。 |
| repo | `/usr/sbin/lsof -nP` 对31102/31103/31880/32102/32103/32880加`-sTCP:LISTEN`；`/bin/ps -p`交接36个精确PID与QA50340 | 三条均1、stdout/stderr为空：无匹配listener/PID。没有按名/端口杀进程，无本轮bind/rebind。`resource-observation.json` SHA256=`0594bdebb38b99967f2ea9eba43736bb9fe09e21124b700e0a77d4c272e0bc28`。 |
| repo | `git diff --check --` 后列16候选+19导航+本checklist | 0；作用域空白检查通过。 |

线上来源仅用于工具链说明：[Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html)、[Rust platform support](https://doc.rust-lang.org/rustc/platform-support.html)。冻结本机 `/Users/jason/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/rust-snap7-1.142.2/build.rs` SHA256=`62aa125e5ecf01b3d2690bd3360b39aa83e525836d7f7d93bddff20b08ed00f7`，与DEV来源记录相同；它编译native archive不能证明最终全静态或跨平台交付。

## 4. 保留的失败、限制与未运行项

DEV失败历史已完整读取，140文件哈希仍一致：DNS/cache权限/锁定wheel缺失、uv包装PID首次SIGINT未收回、TIME_WAIT误探测及文档事实纠正均仍在原tasks/evidence；未把重试或强制cleanup改写成首次正常成功。本轮未修改DEV证据。

QA辅助检查的非产品失败也保留：首次sandbox内ps返回`operation not permitted`（A的变量空值仍可见），随后经工具auto-review允许的同一只读动作复现真实ps exit1；没有自动审批拒绝。首次读取ps原始stderr因无效UTF-8报UnicodeDecodeError，改为保留原始字节/hex/替代解码后完成。一次辅助cat引用了不存在的repository coordinator路径，实际coordinator输出在其私有根，随后读取正确路径；一次evidence manifest辅助校验误用仓库/附件目录基准，纠正为manifest定义的bundle基准后140/140通过，错误辅助结果仍保留。上述不作为产品缺陷。

**not_run：** 本轮未执行Rust release/fixture构建、自己的file/otool、Python uv锁/同步/项目导入、产品空cwd/help、state init、default与teaching01的dry/execute/inspect/正常关闭或重新绑定端口；未写新synthetic数据库。原因是已发现必须返工的正式教程缺陷，结束本失败候选验证并交回Development，避免重复无效候选演练；这些要求仍是最终fresh QA的必需项，没有豁免。未运行项不记pass，也不以FF-001或DEV绿灯补齐。

Windows仍有明确Unix源码阻塞；Linux本轮未测；本轮连macOS产品复演也未完成。没有现场、DS/Backend、第三方HTTP、长稳、容量、托管、备份/迁移、跨主机fencing、分发/许可、签名或发布资格。没有下载解释器/target/compiler/SDK、改锁、Python打包、Docker、真实库/设备操作、系统时间改变、外部邮件、Git refs/push或任务外资源回收。

## 5. 资源与后续 handoff

Q拥有的资源：`rust-default/`、`python-default/`是正式工程未修改的独立源码副本，无`.venv`/target/cache、无运行库；其余为本轮diff/hash/链接/治理/原输出/复现记录及辅助脚本。未启动产品服务、无新监听；唯一短命helper child PID50340已由自身shell实际wait，后续精确ps确认absent。只读核对DEV交接36个已知PID均absent，六固定端口无listener；QA不据此冒称自己已完成产品正常退出/重bind。

Q保留供Development/新fresh QA复核F-QA1-001与本轮范围审计。关键诊断和哈希已进入本checklist；后续由唯一active coordinator在证据/归属/占用/下游依赖核对后处理，QA不回收。DEV根 `/private/tmp/ff-002-r1-dev-vncfzod3` 与 coordinator根 `/private/tmp/ff-002-r1-coordinator-k8s3e9_q`只读使用且原样保留，不清FF-001/其他任务资源；未另启/结束notifier或发送邮件。

**QA -> Development：** 按F-QA1-001修四份授权手册，保留本失败与原证据，更新真实tasks/候选/DEV自检并形成新handoff；不改spec/范围/产品。**coordinator -> 新Verification：** 返工停止写入并真实handoff后另启实际命名`verification`, `fork_turns="none"`，读取原失败及新候选，独立关闭该项并完成本轮未运行的必要演练。当前Verification没有修复或授予通过。只有最终独立qa_passed后，才可交Human Owner决定最终验收。

## Human Owner 最终验收

Pending。QA verdict 仅交接 Human Owner 决定，不替 FF-001 终验、跨平台、现场、托管、长稳、容量、分发、发布或部署证据。
