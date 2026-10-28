Task ID: FF-002
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 independently passed FF-002 r1 rework1 AC01-AC14 and closed F-QA1-001 with eight real isolated product scenes; QA1 failure/history retained; handoff to Human Owner final acceptance, no release/deployment authority
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: root
Capability: Field Flow 双语手册、案例教程与 Rust BUILD 文档独立核验
Owner: Field Flow
Acceptance Chain Reference: FF-002 r1 scope approval -> Development -> fresh Verification -> Human Owner final acceptance

# FF-002 r1 独立 Verification

当前：QA2由 `/root/ff002_verification_r1_after_rework1` 以新的 fresh context 独立验证 rework1，已形成 qa_passed（见第6节）。下文 QA1 原失败正文、AC表、命令、未运行及资源记录完整保留，描述的是前次时点；本轮独立记录在末尾新增，顶部元数据为当前阶段。

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



---

## 6. QA2：r1 rework1 独立核验与当前 verdict

**2026-10-23（Asia/Shanghai）：`qa_passed`。** 本轮独立通过 AC01–AC14，关闭文档缺陷 F-QA1-001；QA1 的 `qa_failed`、原 AC 表、命令、失败证据、not_run 和资源历史均是前次真实记录，以上正文不改写。其完整原件另存既有 `evidence/dev-r1-rework1/qa1-checklist-original.md`，SHA256=`bb3d6eb203e21e6bbfa4081684b566fd723daa073f2d21c9fd1024786d1b976e`。本轮没有继承 QA1 静态 pass 或 DEV 八场景作为自己的验收结论。

实际命名角色 `verification`，执行者 `/root/ff002_verification_r1_after_rework1`，由唯一 active coordinator `/root` 在新的真实 `developer_handoff` 后以 `fork_turns="none"` 启动。本轮独立读根 AGENTS、README/PLAN 双语、FF/两工程最近 README/PLAN 双语、canonical workflow、verification TOML、完整 spec/tasks/checklist、新旧候选及 diff、实际实现/清单/锁/native/fixture/可用原输出。没有更近 AGENTS。TOML 的 `gpt-6.1-sol / max` 只作配置证据，非额外模型运行遥测；`contract_only` 依靠精确角色、串行 handoff 和 diff/checklist 审计，不宣称 ACL、强制路由或团队激活。

正式树仍是 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD=`1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，无新 commit/refs。精确核对：

| 输入 | SHA256 |
| --- | --- |
| approved spec | `de9e338f495e1ae756ff50bc12d798edefb1a2f572ec6bc6cd6fb3e150ef3b7c` |
| rework1 tasks | `eaa5f2c29991af3154d849c0723e24b31568104ac241e8255f0846fa1af0a764` |
| rework1 candidate-documents.json（16份） | `81bf31fdd4f9479c1d3025de7df7f2f5a67001e3921781c1189e291531fcea93` |
| rework1 handoff.json | `71ed9b6e2fbf8a6f4ed3041ffcb553cc757ae73c0d242ffe502a524877522abe` |
| rework1 evidence-manifest.json | `fc96938949fb58006feb2d9745b856eaa75742ed3369dcebaae72c5deb886b04` |

仅四份分语言 USER_GUIDE 相对原候选变化，另外12份相同。正式16份与新候选逐项相等；581份既有FF源码/配置/locale/清单/锁及FF-001/ARCH历史、旧DEV140和返工38份附件均逐字节未变。19份导航由 coordinator 机械同步，QA2开始至终末未变；按原baseline逐行阅读时，根 PLAN/catalog 的并行 DAA-007 行为任务外变化，保留且不归因FF。子PLAN中FF-001真实阶段校正继续指向其唯一bundle，不转成FF-002验收。

适用 shared skills：aiis、project-governance、rust-runtime、plc-point-mapping（仅标准DB INT地址/类型）、code-document-indexer、i18n-workflow；backend-arch仅采用本地状态/事务边界。另读分层、跨语言结构及日志基线；不套FastAPI、Celery、Tauri、Python打包等模板，不改skills。本轮正式写入**只有本checklist**；QA辅助脚本、所有副本/环境/target/新synthetic状态/原输出位于新的独占根 `Q=/private/tmp/ff-002-r1-qa2-1irvf443`。

### 6.1 AC01–AC14 本轮结果

| AC | QA2结果 | 本轮独立依据 |
| --- | --- | --- |
| AC01 | pass | approved spec与新tasks/handoff指纹、唯一FF-002/r1/namespace/root及角色归属一致；批准原文可追溯，未继承FF-001或DS建议的批准/QA。 |
| AC02 | pass | 独立通读八新文档中英正文；7组候选pair章节数与代码块相同，四GUIDE各24块逐字节相同，BUILD1块相同。两语言均在独立复制后以自身manifest/lock/source/config/locale/fixture完成使用与开发，不要求父或兄弟runtime。 |
| AC03 | pass | 总/子指南与入口一致表述Python学习/练手/快速原型、本任务不打包，Rust为长期runtime建设主线；未来不强制所有生产flow双实现。Python正式功能/测试/锁和历史均受hash保护。 |
| AC04 | pass | 独立读两版fixture入口/runtime/native/线程边界，并在8scene实际观察：六固定loopback端口、真实S7 server child、透明proxy、42、Rust cmd-001/source固定/TTL60s，Python fixture-UUID/首flow source/TTL30s，默认input age10s；人工入口无自动测试内部控制面。报告分别protocol.json/report.json，Rust ENTER、Python实际fixturePID的SIGINT正常关闭；均非DS。 |
| AC05 | pass | 自有Rust产品/fixture构建、自有Python锁定环境与6条空cwd无参/中英help、各scene显式init→fixture→真实产品run→inspect→正常停止/检查。8scene均simulated1/write0或confirmed1/write1；16个真实独立zsh落实A/B变量归属，F-QA1-001已关闭，详见6.2–6.4。 |
| AC06 | pass | 独立核对config/domain/HTTP/execution/state/audit/CLI/driver/owner：字段范围/预算/物理重叠、七键严格输入、schema/implementation/mode/instance、T1/T2/T3/unknown、容量/日志轮转、错误码/正常与fault退出说明对应源码；新scene实测JSONL和state。无清库/换ID/改时间/绕过Execution建议。UTC日历差异明确保留为后续gate。 |
| AC07 | pass | 实际读两版demo01/HTTP/domain/Execution/Owner/Stop/state，对照路径、参数、返回、await、错误及owner表；Python按实际duck-typed对象说明，无虚构anchor SDK。读通过Owner，写通过Execution.apply；raw S7/driver/SQL/状态迁移是内部能力。 |
| AC08 | pass | 从手册逐字提取完整teaching01 app、YAML与精确断言接线脚本，只应用到两独立新副本；Rust新产品/fixture编译0、Python自身新env/compile/import/config0，随后两版各dry/execute实际跑通。无额外schema/driver/API/依赖修改；正式源码/配置/locale/锁未动。 |
| AC09 | pass（源码/测试入口核对） | 读Rust runtime/owner与Python runtime/owner的异步flow、完成后interval、每PLC FIFO/常驻driver/session及独立request/sample；读Rust local_protocol.rs三读/慢GET段、Python test_three_read_flows_and_slow_http段：60独立request、同PID/session、慢GET不阻塞独立读、同流max1。未将未注册读流当人工CLI，按spec无需重跑FF-001全矩阵。 |
| AC10 | pass | 自己构建`--no-default-features --bin field-flow`产品与`--features test-fixture --bin ff-fixture`分target release；自己的file/otool确认arm64及五项系统动态库。读current_exe/__driver、include_str locale、bundled SQLite/native build；不存在ff-driver或全静态单文件证明。 |
| AC11 | pass（来源/静态平台边界） | 冻结rust-snap71.142.2/checksum/build.rs、cc1.9.0、native许可头与notices吻合；UnixStream/pre_exec/FD/flock/fcntl/Unix信号阻塞Windows，Linux本轮未测。官方Cargo/Rust target来源只证明工具链选项/层级，不替代目标原生依赖/链接/生命周期证据。 |
| AC12 | pass | 35份范围文档651个活动本地链接/锚点无缺失，无尾空格，范围diff --check0；入口/目录只链接真实角色文件。16候选、581保护文件及原失败/附件均保持；任务外dirty和19导航没有被QA写入。 |
| AC13 | pass | 自己的实际命令/cwd/版本/退出码/失败与资源记录见下；8scene均实际wait/join、48精确PID全absent、6口无listener且按服务规则rebind；必要原输出/ACK/PID与hash在本页持久化。无未授权工具链安装/真实设备或数据/外部动作。 |
| AC14 | pass | 新fresh-context独立形成本qa_passed；保留QA1失败，未静默修手册/实现，未借DEV/前QA替演练。只交Human Owner最终验收；所有未测/后续gate仍明确。 |

### 6.2 环境、实际命令与独立准备

环境：Darwin24.6.0 arm64；zsh5.9；rustc1.89.0 / Cargo1.89.0 / Apple clang17.0.0；uv0.7.8。辅助文本脚本为宿主Python3.9.6，项目行为全部用自己副本中的既有CPython3.11.12。Python实际依赖python-snap7=3.0.0、httpx=0.28.1、PyYAML=6.0.3、pytest=8.4.2。没有下载安装解释器、Rust target、compiler或SDK，没有修改正式锁。

Q/rust-default与Q/python-default分别复制各自单工程，排除target/.venv/dist/cache/运行状态/日志/真实.env；可选父任务导航不作为运行依赖。教学工程为另一个Q/rust-teaching、Q/python-teaching，自身target/env，不借兄弟工程、DEV/QA1环境或服务。Python两环境的sys.executable、field_flow.__file__和tests.fixtures.__file__均重新打印核对属于本副本。公共Cargo package cache只供锁定依赖源码，Python使用Q/uv-cache；未复制DEV的8.8GiB cache。

以下Q为上面真实绝对路径的简写；原始args/cwd/stdout/stderr/exit在Q/commands.jsonl中，场景A/B的完整脚本和原输出在各scene中。

| cwd | 实际命令/动作 | 结果 |
| --- | --- | --- |
| repo | uname -mrs；rustc -Vv；cargo -V；clang++ --version；uv --version；python3 -V；zsh --version；uv python find --help | 均0，版本如上。find语法只读核对为位置REQUEST。 |
| repo | `uv python find 3.11 --no-python-downloads` | 2：默认公共cache的sdists-v9/.git写锁被sandbox拒绝。未写公共cache；同find显式Q/uv-cache后0，找到已有3.11.12。不是自动审批拒绝。 |
| Q/python-default | `uv sync --locked --python 3.11 --no-python-downloads --cache-dir Q/uv-cache` | 首次1，锁定python-snap7下载遇镜像DNS；原输出保留。相同命令经工具auto-review允许require_escalated后0，仅准备声明依赖/本工程环境；无解释器下载或改锁。 |
| Q/python-default | `uv lock --check --python 3.11 --no-python-downloads --cache-dir Q/uv-cache`；同显式uv run打印Python/依赖版本 | 均0，冻结锁及自身解释器成立。 |
| Q/rust-default | `cargo build --locked --release --no-default-features --bin field-flow --target-dir Q/rust-default-product` | 0，31.227s。随后将这个自有target目录移动至Q/rust-demo01-lesson/target-product以对应文档FF_LESSON布局；不借用/重建别人的产物。 |
| Q/rust-default | `cargo build --locked --release --features test-fixture --bin ff-fixture --target-dir Q/rust-default-fixture` | 0，39.108s；同理移到Q/rust-demo01-lesson/target-fixture，产品和feature目标始终分离。 |
| Q | 自己产品`file`、`otool -L` | 0；Mach-O64 arm64；Security、CoreFoundation、libc++.1、libiconv.2、libSystem.B。静态native archive不等于最终全静态。 |
| Q/{rust,python}-empty | 各自实际产品无参、`--lang en-US --help`、`--lang zh-CN --help` | 六条均0，两个cwd保持空；结合CLI早返回源码，无配置/状态/网络IO。自己的Rust fixture --help另0，空cwd不变。 |
| Q/rust-teaching | 手册完整app/YAML写入及逐字block16的app/mod、config kind、runtime派发断言脚本；两条锁定release产品/fixture命令，target-dir分别为Q/rust-teaching01-lesson/target-{product,fixture} | 接线0；产品0/32.860s，fixture0/33.471s。kind/YAML另由真实fixture与产品启动校验，未把编译当配置校验。 |
| Q/python-teaching | 手册完整app/YAML及runtime import/config/dispatch断言脚本；`uv sync --locked --python 3.11 --no-python-downloads --cache-dir Q/uv-cache`；同uv run `python -m compileall -q src`与手册import/load/assert | 全0（sync0.295s、compile0.064s、import/config0.188s）。自身新env，不共享default .venv。 |
| 各新project | `state init --synthetic --mode dry_run/execute --state-dir 新scene/state --instance-id ff-{rust,python}-{demo01,teaching01}`；A/B文档literal块 | init/run/inspect均0；每scene的init/build/env在自身fixture之前，模式/语言/案例串行。QA按scene分别预初始化，文档把两模式一起提前init同样不消耗fixture窗口。没有刷新原ID时间、转换库或隐藏unknown。 |
| 各新project | 实际独立`/bin/zsh -f scene/terminal-A.zsh`及B脚本，向各自read输入真实绝对project/lesson；B真实产品run、sleep2、kill -INT其$!、wait、inspect；A Rust ENTER/Python实际fixturePID SIGINT | 8scene/16shell正常0；不是用短命helper替代产品。16shell环境均移除继承FF_*，见6.3。 |
| 正式树 | 自写static_checks.py（只读）；scoped git diff --check；终末final_audit.py | 35文件/651链接/7pair对称和空白0；16+581+178附件hash、19导航、4副本锁均一致。repo治理checker真实exit1，0 stdout/322 stderr，同旧SHA，未记全仓pass。 |

教学副本逐字app/YAML/接线相等的结果已保存。Rust仅改副本app/mod.rs、config.rs、runtime.rs、新teaching01.rs/YAML及本地README/CODE_INDEX；Python仅改副本config.py/runtime.py、新teaching01.py/YAML及本地README/CODE_INDEX，app/__init__.py未改。没有新增CLI文案或locale key；正式两语言locale的中英键集分别相同，原hash未变。

### 6.3 F-QA1-001 独立关闭、八场景及资源原证据

本轮每scene都用两个真实且不共享变量的`zsh -f`：A前台运行本工程fixture，返回后**紧接**执行手册`FF_FIXTURE_EXIT=$?`及printf，A在前/后均断言FF_PID未定义。B由文档两行read显式读实际project/lesson，自己的`FF_PID=$!`始终留在原B；产品真实wait后，辅助暂停仅等待A正常关fixture，随后回同B运行手册报告/lsof/printf/ps literal块；B前/后均断言FF_FIXTURE_EXIT未定义。没有向A注入FF_PID，也没有在新shell靠继承状态通过。四GUIDE的中英代码块逐字相同，§7明确复用这一路径。

各A原stdout含`fixture exit=0`、`QA_A_PID_UNSET=1`（Python还含fixture_ready）；各B含`runtime exit=0`、原有效`checking runtime PID=...`、`QA_RUNTIME_PS_EXIT=1`、`QA_B_FIXTURE_EXIT_UNSET=1`。每个ps均查询本轮原正整数；其stdout/stderr全空、exit1；无非法PID或权限错误。B的完整stderr为空，runtime stderr也均为空。Rust报告最后无换行时checking文字紧跟JSON末尾，仍解析到相同原PID，不改变检查结果。

以下四类PID分别来自实际A服务listener、B的$!/wait、driver_ready（Rust解析JSON字符串context）、fixture报告native_pid/server_pid；A/B shell由harness实际wait0，runtime由Bwait0，fixture前台由A等待0；server/driver的内部join/reap另有源码/报告/JSONL正常证据。每scene结束后精确ps和lsof，再按服务规则重新bind/listen/close；Rust不加SO_REUSEADDR，Python按自身bind规则加SO_REUSEADDR，不把TIME_WAIT或权限错误当无进程。

| 语言/案例/模式 | inspect counts；WriteVar | fixture/runtime/driver/server PID | A/B shell PID | 正常退出/释放 |
| --- | --- | --- | --- | --- |
| rust/demo01/dry_run | `{"simulated": 1}`；0 | 85724/85740/85742/85734 | 85722/85739 | A/B/fixture/runtime=0；全部absent；`[31102, 31103, 31880]`可重bind |
| rust/demo01/execute | `{"confirmed": 1}`；1 | 85777/85783/85785/85778 | 85775/85782 | A/B/fixture/runtime=0；全部absent；`[31102, 31103, 31880]`可重bind |
| python/demo01/dry_run | `{"simulated": 1}`；0 | 86157/86186/86188/86180 | 86155/86185 | A/B/fixture/runtime=0；全部absent；`[32102, 32103, 32880]`可重bind |
| python/demo01/execute | `{"confirmed": 1}`；1 | 86223/86232/86234/86226 | 86221/86231 | A/B/fixture/runtime=0；全部absent；`[32102, 32103, 32880]`可重bind |
| rust/teaching01/dry_run | `{"simulated": 1}`；0 | 89952/89980/89982/89960 | 89950/89979 | A/B/fixture/runtime=0；全部absent；`[31102, 31103, 31880]`可重bind |
| rust/teaching01/execute | `{"confirmed": 1}`；1 | 90017/90023/90025/90018 | 90015/90022 | A/B/fixture/runtime=0；全部absent；`[31102, 31103, 31880]`可重bind |
| python/teaching01/dry_run | `{"simulated": 1}`；0 | 90069/90080/90082/90074 | 90067/90079 | A/B/fixture/runtime=0；全部absent；`[32102, 32103, 32880]`可重bind |
| python/teaching01/execute | `{"confirmed": 1}`；1 | 90118/90127/90129/90121 | 90116/90126 | A/B/fixture/runtime=0；全部absent；`[32102, 32103, 32880]`可重bind |

inspect原输出（仅紧凑排列，不改原JSON值）：

```jsonl
{"scene":"rust/demo01/dry_run","inspect":{"counts":{"simulated":1},"meta":{"implementation":"rust","instance_id":"ff-rust-demo01","mode":"dry_run","schema_version":1,"store_uuid":"1792757674004-85721-0"}}}
{"scene":"rust/demo01/execute","inspect":{"counts":{"confirmed":1},"meta":{"implementation":"rust","instance_id":"ff-rust-demo01","mode":"execute","schema_version":1,"store_uuid":"1792757676835-85774-0"}}}
{"scene":"python/demo01/dry_run","inspect":{"meta":{"schema_version":1,"implementation":"python","mode":"dry_run","instance_id":"ff-python-demo01","store_uuid":"3bd5bce7710541a58079dcb6cf4365bd","created_at":"2026-10-23T12:15:23.824Z"},"counts":{"simulated":1}}}
{"scene":"python/demo01/execute","inspect":{"meta":{"schema_version":1,"implementation":"python","mode":"execute","instance_id":"ff-python-demo01","store_uuid":"4121d92b3fb14645ba95901d535fd307","created_at":"2026-10-23T12:15:26.680Z"},"counts":{"confirmed":1}}}
{"scene":"rust/teaching01/dry_run","inspect":{"counts":{"simulated":1},"meta":{"implementation":"rust","instance_id":"ff-rust-teaching01","mode":"dry_run","schema_version":1,"store_uuid":"1792757854390-89949-0"}}}
{"scene":"rust/teaching01/execute","inspect":{"counts":{"confirmed":1},"meta":{"implementation":"rust","instance_id":"ff-rust-teaching01","mode":"execute","schema_version":1,"store_uuid":"1792757857159-90014-0"}}}
{"scene":"python/teaching01/dry_run","inspect":{"meta":{"schema_version":1,"implementation":"python","mode":"dry_run","instance_id":"ff-python-teaching01","store_uuid":"49336120723f4cd7ab3da96a2d8b68b5","created_at":"2026-10-23T12:17:39.954Z"},"counts":{"simulated":1}}}
{"scene":"python/teaching01/execute","inspect":{"meta":{"schema_version":1,"implementation":"python","mode":"execute","instance_id":"ff-python-teaching01","store_uuid":"b67709860a6a4b1986465d9727cd35a3","created_at":"2026-10-23T12:17:42.672Z"},"counts":{"confirmed":1}}}
```

四个execute的原协议trace（每scene唯一WriteVar；请求尾部002a，匹配PDU reference、原响应/转发响应相同、正ACK以ff结尾）：

```jsonl
{"scene":"rust/demo01","trace":[{"at_ms":1792757676959,"operation":5,"original_response_hex":"0300001602f0803203000000010002000100000501ff","positive":true,"request_hex":"0300002502f080320100000001000e00060501120a1002000200018400000000040010002a","request_ref":[0,1],"response_ref":[0,1],"sent_response_hex":"0300001602f0803203000000010002000100000501ff"}]}
{"scene":"python/demo01","trace":[{"operation":5,"fault":"","request_hex":"0300002502f080320100000002000e00060501120a1002000200018400000000040010002a","original_response_hex":"0300001602f0803203000000020002000100000501ff","sent_response_hex":"0300001602f0803203000000020002000100000501ff","previous_same_ref":null,"previous_other_ref":null}]}
{"scene":"rust/teaching01","trace":[{"at_ms":1792757857285,"operation":5,"original_response_hex":"0300001602f0803203000000010002000100000501ff","positive":true,"request_hex":"0300002502f080320100000001000e00060501120a1002000200018400000000040010002a","request_ref":[0,1],"response_ref":[0,1],"sent_response_hex":"0300001602f0803203000000010002000100000501ff"}]}
{"scene":"python/teaching01","trace":[{"operation":5,"fault":"","request_hex":"0300002502f080320100000002000e00060501120a1002000200018400000000040010002a","original_response_hex":"0300001602f0803203000000020002000100000501ff","sent_response_hex":"0300001602f0803203000000020002000100000501ff","previous_same_ref":null,"previous_other_ref":null}]}
```

四个dry的fixture WriteVar=0，Rust applied=0；execute Rust applied=1。Python每个execute报告`memory_hex=002aa5a5a5a5a5a5a5a5a5a5a5a5a5a5`，dry全16字节a5；server_exit=0、server_close.exit_code=0、remaining_threads=[]、proxy_threads_joined=1、ports_rebound=[32102,32103,32880]。各stdout与持久runtime.jsonl均为可解析JSONL，含intent/simulated或in_flight/ack及正常driver回收/resources_released/shutdown_complete，无forced_driver_stop/shutdown_incomplete。confirmed仅表示匹配协议ACK和本地提交，不是工艺完成。

Python四个fixture stderr原行保留，不擦除或归为强制cleanup：

```text
Error handling client ('127.0.0.1', 57653): Expected COTP DT, got 0x80
Error handling client ('127.0.0.1', 57678): Expected COTP DT, got 0x80
Error handling client ('127.0.0.1', 57993): Expected COTP DT, got 0x80
Error handling client ('127.0.0.1', 57999): Expected COTP DT, got 0x80
```

这是client正常断开0x80产生的既有server诊断；结合本轮上述server_exit0、无线程、实际join、PID/端口检查判断正常关闭。

终末`ps -p`一次查询全部48个原PID，exit1且stdout/stderr均空；`lsof -nP -iTCP:31102 -iTCP:31103 -iTCP:31880 -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN`同为exit1、双输出空。六口再次按各自规则bind/listen/close成功，自己的路径进程扫描无残余产品/fixture/driver/resource_tracker。没有按名或端口杀占用者，没有forced cleanup冒称正常。

### 6.4 持久指纹、失败与限制

下面hash只核对原输出/候选一致性，不代替本页嵌入的真实结论和必要原证据。Q在Owner gate前仍保留；本页包含必要结论、PID、counts、inspect、ACK和退出/端口证据，不以临时路径作为唯一事实。

| Q相对路径 | SHA256 |
| --- | --- |
| `start-audit.json` | `f8899ea7ff6837005b2d4cc8fc71aefce1995585c0e8f78a0e3145a4a8f39e8c` |
| `static-results.json` | `7d508af699a5f71d19f884377b5f9ed9166b115bb5473a0594d16b91ffee429d` |
| `commands.jsonl` | `fd777a5f734465a8e73d2635c02120276a124113fb3f55cc9af970f3b5b75c5b` |
| `final-audit.json` | `8ff717cf82441c493a638f4ca15eedbac9f73f7602b32b1ba9365324c5e63f9e` |
| `qa_common.py` | `daf26ef053c733647dadf776b2e98162977d2cff7a11c51d63ad15011c07bd9b` |
| `prepare.py` | `bb2115012285696c0b07b9f42d102235fd7add2b15246e3e3b0ec4899427e295` |
| `static_checks.py` | `1d31b3f1caffde576f832cbe83b5522989aa69fb0e64ba6dbf428e30d1674559` |
| `tutorial_prepare.py` | `b25af5ab144c8fcfb5a43ac5fa56ed899ddd8aff47db8f8bfa7d8990f6f1e448` |
| `rehearse.py` | `b2b12d3dbb05d4fbd02f50be100aaabd17bc6dee1da8a3750ec404c649f532af` |
| `final_audit.py` | `a2a96c07bd91fc64a1ff0bad9ad3608691e7a168763375673ede8bb015cded13` |
| `rust-tutorial-equality.json` | `e1624bc3058d64f4e6a74951c4f74f78403f6489efbb9becd23a7f0be7c69cc9` |
| `python-tutorial-equality.json` | `e65262c3921a6d61da18fd59e04e0077a04812da421cb39b8c71254590a763bb` |
| `rust-tutorial-diff.patch` | `9903843cc959b4dd94c462ec8284589a3827fb5db5a842ef4d68584a87941cdd` |
| `python-tutorial-diff.patch` | `410ce1ef403fd8ed704b2fbe8c91efce8ba2438f7330e2106a9afc17b5128c03` |
| `nav19-from-baseline.diff` | `6c5092f5663fdbca4f964e74b1f8755c8b7ceb712ecf0c3e3bbed66e409c2cd2` |
| `python-sync.json` | `44bd1c1932c760837d6ace83a7e4593fd93cf3dbc5e26f9fdc6653001a4e449d` |
| `python-sync-permitted.json` | `007d192a948cdac84cc44774849bb148ef4acdbd72c076a1a657ebceccdd7d38` |
| `python-find.json` | `bb2eb7bd21dc58b1ec36ecee4662f81f93d2ac179e4d662200e34af3c81593f5` |
| `python-find-private.json` | `752d2582bbd785eeadce44e042dcb9926d199563b2ac31dd723eb796d197fa42` |
| `rust-product.json` | `8665056bbaeb7574d615f4fdd4050e265bc727edb30136ad75f933543adc3269` |
| `rust-fixture.json` | `6f5bc2a47f51e9e530adfc5fe31638db0628a4a7958def63d2d1de3ca2b64225` |
| `rust-tutorial-build-product.json` | `3242840f432a6fb3c82ac650ddac8696f591e4ac7abdb90e48b164359fbfbf97` |
| `rust-tutorial-build-fixture.json` | `063cf9377b577bf52ad21c3d1911ad6fa541f3aa7f3b3479cb018f2e50ba6647` |

| scene（Q下） | result.json SHA256 | fixture报告SHA256 | stdout.jsonl SHA256 |
| --- | --- | --- | --- |
| `rust-demo01-lesson/dry-lesson` | `dfb58fba5ed2f7ec1602df2424419fd506a21ce354f1ab95a958177f8626c48a` | `095434d898300cc9bd28f9322464dc7ea61b62164a670ba1e4ddd9db5486a4f8` | `08db867444a9beeaac64a3d2696307a28998e0bf5ff0336d1e12194345ab1211` |
| `rust-demo01-lesson/execute-lesson` | `d36d9cca893b2f317812ae3f31c08c5128ba753ef943074c8e4b862abaaa5a60` | `eed62e9b9e745e64025af72a54a749f4eb5214fad23f33fbf854b905c62e5113` | `b40b013bf5eac99d6e19c00255ecf926fc83e0ebd8a642dc4f58ba61fd18be49` |
| `python-demo01-lesson/dry-lesson` | `a953229df3db737eae070e43fb4a410ac7a9f6e7fe5df8d84de8a0fa45a08aa0` | `a85aae66b5764f4e5cdef0110093f51bb3085104d936a5c2ecf7c75c966a8357` | `1604d206cbb02d35c95c8766d54c18b09677c65a87769fced3b725f7d9d0701f` |
| `python-demo01-lesson/execute-lesson` | `9d4ce00b308734a0853863964992460d8e35bbe99b9db745553edbab86595f12` | `b7a469b982d7cd6a390362df8f7690e91d84ce3e809af64d4d9c3850df516d9d` | `be2df0f1388c6e064f01f9dfa8a68bca593bb07bed95c8d8d4ec7f0875ca9716` |
| `rust-teaching01-lesson/dry-lesson` | `4f6426928ec38b621ad20c354dea284ef56824eab37341a36bd1b485c2e22dd5` | `c9988cbb3d06b9e98b377dac234fb1b5a93f00e2525224274a442f11a93b7779` | `96f23797f02a1c91190bb51116c93269b28b360f9d6504d11a1613a9562d2f75` |
| `rust-teaching01-lesson/execute-lesson` | `9873425d6caec53fe43b74e0af277d05030530fe35bd90e20fa4ede82835b962` | `d58ad3c95253ac2f9a6cc04d44ce68bd569377d8b3b6d15a6e67f52d4bef3805` | `47319a1e6613da39317610a5408d9573b3ad481aa5a2c4e17bab1b374e1e0a45` |
| `python-teaching01-lesson/dry-lesson` | `d4ad16d4457ba3e4a5745e7562211f951e9d5c46996946495b57e7dcf9cd7e3b` | `76a76188f8d61c998d8e26682e26b8d6bb2ddb387bb018409c3b251151cf4bed` | `56b61a5bba264299d651302b8251051393cebc9cfe81c33831b9646c14d53690` |
| `python-teaching01-lesson/execute-lesson` | `c7d4ee5813dda93912ba98a00977e0f198947ba818d17de85bfbab500ac19f6e` | `3d0b7f2958b79625c46401b87d6c8632bd6e5ce976df78ad21cc8bd0bafb7bf1` | `3ff3bc653f854e1cb44cf2d4dd3ffc3ed1223484d168986aac38777b8fc38022` |

原repo治理checker本轮也是exit1，stdout0行/stderr322行，合并SHA256=`df8ce220425c9cbfd25f66a4fe756e916e75a72bf25aaa6fefac942a435ca15c`，与既有基线逐字节相同：318条任务外既有诊断加4条合法子PLAN父spec链接的parser限制。此项不是全仓治理pass；没有改checker、造子bundle或吞诊断。范围内自己的链接/锚点/双语/空白/状态/保护检查独立通过。

本轮准备失败均保留：默认uv find遇公共cache写锁权限错误2，私有cache的第一次锁定sync因DNS失败1；后续同范围require_escalated获准后0，未出现自动审批拒绝。初次复制helper用了过宽state*忽略模式，发现漏了state.rs/state.py后，在任何build/run前从正式树补回原字节并重新核对copy hash；没有修改产品。一次只读native查看猜测了不存在的native/snap7.cpp，改读实际s7_client.cpp及build.rs/manifest/lock完成来源核对。以上是准备/观察helper问题，不抹成首次全绿，也没有污染正式实现或既有执行状态。四Rust初始target移动仅在Q内，原编译输出和路径仍保留。结果记录中的fixture_ready_to_B_s字段实际计量fixture启动至scene末尾，不能用作单独精确就绪延迟测量；原输入时效仍由真实产品验证及成功状态/协议记录证明，本轮未以修改TTL/时间保证成功。

源码/来源交叉核对：Rust commands/config/domain/runtime/driver_process、infrastructure/{http,state,audit,posix,s7_int_pdu}、app/demo01、bin/ff-fixture/fixture；Python同职责模块、owner及tests/fixtures/main/runtime。冻结rust-snap7=1.142.2、Cargo checksum=`8c4d43b3a99825abd300d57a0888eda7b625b7cdbf56ee7766bd02331ac58243`；实际build.rs SHA256=`62aa125e5ecf01b3d2690bd3360b39aa83e525836d7f7d93bddff20b08ed00f7`，cc编native C++ archive、SQLite bundled C编译与实际动态链接相符。wrapper MulanPSL-2.0/native LGPL-3.0-or-later/build.rs GPL-3.0-or-later声明分别保留，不据此授予分发合规。已在线核对官方 [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html) 的bin/profile/features/locked/target说明和 [Rust platform support](https://doc.rust-lang.org/rustc/platform-support.html) 的target层级；没有把工具链支持当本产品跨平台证明。

明确not_run/后续gate：本轮没有重跑FF-001全部故障/崩溃/ACK拒绝矩阵或历史失败preflight，没有Python打包。macOS arm64只证明本次有限本机复演；Windows仍有明确Unix源码阻塞，Linux和macOS x86_64未测。现SQLite日历元数据/JSONL为UTC，与根Asia/Shanghai合同不同，本任务只记录，不改schema/历史/日志或宿主时钟。真实PLC/第三方HTTP、DS/Backend、现场工艺、托管/服务安装、长稳/容量、备份恢复/跨语言迁移、跨主机fencing、unknown人工处置、分发/许可/签名/安装器/发布部署均另gate，没有通过本轮获得资格。

### 6.5 资源、验收审计与handoff

Q拥有四个独立源码副本（两个default、两个teaching）；各Python有自己的.venv，Q/uv-cache为普通声明依赖cache；两个Rust lesson内各有分开的product/fixture target。四lesson下每个dry/execute是独立新synthetic目录，包含state.sqlite/instance.lock/gate/JSONL、fixture报告和完整A/B脚本/原输出；另有空cwd帮助检查、候选/导航快照、辅助脚本及原始命令/hash/diff输出。没有分支/worktree或后台服务。全部48已知PID已正常回收并精确确认absent，六口已实际释放。QA没有清理资源；正常产品自己关闭/删除transient gate属于所验生命周期，不是QA事后强制清理。

Q保留供Human Owner终验与证据/归属核对；终验后由唯一active coordinator核对无运行/后续任务/证据依赖再回收。原DEV根`/private/tmp/ff-002-r1-dev-vncfzod3`、返工根`/private/tmp/ff-002-r1-dev-rework1-6jnwedny`、QA1根`/private/tmp/ff-002-r1-qa-E8j08DYR`与coordinator根`/private/tmp/ff-002-r1-coordinator-k8s3e9_q`均只读保留，不清理FF-001或其他任务资源。未另启停notifier、未发外部邮件、未推送Git或操作Docker/真实配置/数据/设备。

| 验收层 | 本轮真实结论/下一gate |
| --- | --- |
| FF-002 r1 rework1 | 独立QA2 qa_passed，AC01–AC14通过，F-QA1-001关闭；原qa_failed不抹除。 |
| Human Owner最终验收 | **Pending**；由Human Owner决定是否接受这组精确文档与有限本机证据。 |
| FF-001 r4 | 原独立QA2和未完成Owner gate保持；FF-002不代验、不转移其终验。 |
| 平台/现场/托管/长稳/容量/迁移/分发 | 保持上述未测或另立批准gate，无发布部署资格。 |

**QA -> Human Owner：** 精确FF-002 r1 rework1已通过本轮独立QA，提交终验；没有未关闭的本范围实现failure或QA blocker。**QA -> coordinator：** 可按本当前verdict机械同步19导航，保留QA1失败与所有资源/限制；待Owner真实决定后再按canonical workflow审查资源收尾。Verification在本记录形成并完成末次checklist diff/空白审计后停止写入，不代授最终验收。
