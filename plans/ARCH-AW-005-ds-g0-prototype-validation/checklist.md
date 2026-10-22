Task ID: ARCH-AW-005
Revision: r5
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA4 independently closes F-r5-003 and completes all required r5 validation; qa_passed; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# ARCH-AW-005 Verification

当前结论见本文末 r5 QA4；下方完整 r4 及 r5 QA1/QA2/QA3 历史保留其原时点状态，不作为本轮通过。

<details>
<summary>r4 完整历史原文</summary>

<!-- BEGIN R4 CHECKLIST EXACT SNAPSHOT -->
Task ID: ARCH-AW-005
Revision: r4
Status: qa_blocked
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: r4 native gate closed; remaining independent protocol QA not_run after Owner redirected work to product correction; r5 proposal awaits exact approval; no final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# ARCH-AW-005 r4 独立核验

2026-10-21 08:20 +08 补记：现有 qa-0004 三轮正常关闭已核实并封存，AC31 原生门槛闭合，三窗不再是当前 blocker。下文原 checkpoint 正文保留其 00:34–00:40 +08 的0/3时间边界；最新事实、Owner纠偏及剩余未运行项见本文末尾“原生三轮完成后的历史补记”。原32 AC表是该旧时点状态，不回写成当时已通过。全文最初版本 SHA `771ebc885549769d1332588a1b86aa5d1576e5d43389cf45ccea4bc8ca613d66` 已逐字持久保存。

## 验证身份与范围

本记录由主协调在 Development 停写后实际新启动的命名 Verification 创建，fresh context，不继承 Development 对话推理。角色运行配置为 `.codex/agents/verification.toml`（配置 model=gpt-6.1-sol、effort=max；不把配置值宣称为独立观测的运行值）。profile=contract_only；串行 handoff、精确文件与 diff 审计是合同控制，不宣称平台 ACL、强制路由或团队激活。

已独立消费当前根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、最近 AW/DS/R/G0 说明、完整 spec/tasks（含 r3/r2/r1 历史），并审计实现、diff、构建与原证据。适用 skills 为 project-governance、aiis、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow、plc-point-mapping、code-document-indexer；仅用其验证规则，不实施修复。

精确验证输入：

- 批准 spec SHA-256：`4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc`。
- Development tasks SHA-256：`4187f48bcfe555ddf5009be8a7beef02c3b38f921d0d54cc5f900e106b22e701`。
- handoff receipt：`/private/tmp/arch-aw-005-r4-exec/tmp/dev/developer-handoff-receipt.json`，SHA-256 `e02d5df272cfbcfa507e9018b7e316d948c1ca7a408706babf90763898605df2`。
- 正式源码候选：`ba08e83eb3c13ece431c87b304c8bdc2d0e1f8122e24c2477acc2ea9863b9b3e`；180 源文件与 108 只读输入共 288 项，QA 起点逐 SHA 匹配。HEAD 不能单独恢复该脏工作树交付。
- DAA accepted manifest 当前为 60/61 原字节匹配，唯一 CODE_INDEX.md 已批准导航差异单列；不记成 61/61。原 r3/r2/r1 嵌套原文字节恢复 SHA 均匹配。

项目内 QA 只写本 checklist。构建/cache/profile/helpers/raw 只在批准 T 的 qa 角色路径；必要原件持久到批准 A 的 `qa-run-NNNN` 闭集，逐成员 inventory 排除自身。spec/tasks、实现/锁、P 五类工件、DAA/CU/core/004 和根四索引均只读；其他并行 006/007/shared 文档变化按协调分类保留。

## 环境、检查顺序与当前证据

T=`/private/tmp/arch-aw-005-r4-exec`；A=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence`。

当前 checkpoint：2026-10-21 00:34–00:40 +08。实际环境为 macOS 15.7.7、arm64、Mac16,12、10 logical/10 physical CPU、34,359,738,368 B RAM、内部 SSD。固定 Node 22.19.0、pnpm 11.11.0、Rust/Cargo 1.89.0、CMake 4.0.2、clang 17、SDK 26.1、系统 Python 3.9.6。版本、SDK 路径、sysctl 和经字段裁剪的介质事实在 qa-0001 原命令中；普通 sandbox 的 sysctl 拒绝也保留，精确只读重试成功。

| QA run | 独立执行/审查与实际结果 |
| --- | --- |
| qa-0001 | 固定 spec/tasks/receipt、288 项输入、历史原文恢复、隔离 cache；runtime 54 / desktop 430 / DAA 60 registry 条目均为冻结 548-bank 同 name/version/checksum 子集。bank digest=`cca1d6efbbdd7767a2475f786bf5a67fa64056bca17bff66d4113d4f40615cfa`。只复制原包/索引/source 与 pnpm package content；没有复用 DEV target/binary。 |
| qa-0002 | 正式 D/R/S 的独立 CMake native/reference/probe、Rust release server/probe、真实 DAA harness 构建成功；own QA build/cache/profile。owner_contract 2、ffi_contract 2、clock_contract 1 与 logging lib 1，共 6 项实际通过。新 B0 closed；尚未执行协议矩阵。 |
| qa-0003 | 正式前端 `pnpm install --offline --frozen-lockfile`、vue-tsc/Vite build、Tauri `--no-bundle --features native-s7` build 均 exit0；不生成/注册 `.app`，不签名或打包 installer。 |
| qa-0004 | 新 QA binary 第一窗实际 ready，两项只读 IPC 已发生；0/3 轮正常关闭，人工可见性尚待本次 Owner 回复。仍增长、未封存，详见下节。 |
| qa-0005 | 37 DAA/17 CU 精确来源、UI/host/config 44 项闭包、三项构建 assets、25 个中英文键、15 份文档/113 local links 与 anchors/29 tables、patch dry-run 和 diff whitespace；12 个 C/H 配置边界 no-listener 启动/EOF 退出（有效 exit0，非法 exit2）。不把配置域检查当容量实测。 |
| qa-0006 | 只读核实 189 份 DEV inventory 的完整成员/781,943,025 B；独立解码最终 38 个 DEV 原命令的真实 TPKT/COTP/S7 ACK、1088 B full images 与拒写 image/seq/点版本/时间对账。仅是 DEV 输入审计，不能替代新 QA 协议执行。 |
| qa-0007 | 独立复算上述 38 run 的逐 PID 资源、419,965 条 server stdout/file JSON 顺序一致性、时钟区间、C01 算术/分位数、C04 真实 send 阻塞到 join、C06 stopped 曲线；保存实际新 QA stdout failure 文件字节、8 个 QA helper 源码及保护/活跃窗口 checkpoint 原件。 |
| qa-0008 | 明确复核实际 DAA lock 60 registry 是 active spec §2.6 原静态 66 的子集；6 个未解析条目单列，不将历史静态 67 package 与本次真实 feature/link 图混写。 |

实际主要命令如下；完整 argv、cwd、环境、stdout/stderr、退出码和辅助方法失败均在对应 run 原件中。

```text
cmake -S D/g0 -B T/build/qa/cmake -G "Unix Makefiles" -DCMAKE_OSX_ARCHITECTURES=arm64 ...
cmake --build T/build/qa/cmake --parallel 2
cargo build --offline --locked --release --target aarch64-apple-darwin --manifest-path D/runtime/Cargo.toml --features native-s7 --bins
cargo build --offline --locked --release --target aarch64-apple-darwin --manifest-path D/g0/daa-harness/Cargo.toml --no-default-features --features rust-snap7-driver --bin ds-g0-daa
cargo test --offline --locked --target aarch64-apple-darwin --manifest-path D/runtime/Cargo.toml --features native-s7 --test owner_contract/ffi_contract/clock_contract -- --nocapture
cargo test --offline --locked --target aarch64-apple-darwin --manifest-path D/runtime/Cargo.toml --features native-s7 --lib -- --nocapture
python3 -B D/g0/scripts/build_skeleton.py --project-root D --run-root T --role qa
python3 -B D/g0/scripts/build_skeleton.py --project-root D --run-root T --role qa --native-cycles --b0-run T/runs/qa-0002
python3 -B D/g0/scripts/collect_evidence.py --source-root D/g0 --run-root T --role qa --run T/runs/qa-NNNN --destination A/qa-run-NNNN
```

上表 cargo test 的三个 `--test` 名称分别独立调用；命令展示中的 D/T/A 为已在本记录定义的路径缩写，真实原命令未使用该语法缩写。没有运行 fmt 或声称 fmt 通过。

## 新 B0、来源和八个实际产物

B0 使用 QA own 100 次同 CLOCK_MONOTONIC 夹点，C/Rust 实际双向 int0/37，Tag=20 B / align1 / offsets 0,4,8,12,16，callbacks=104 B / align8 / offsets 0,4,8,16,24,32,40,48,56,64,72,80,88,96。ABI、file/otool/nm/加载路径、release dep-info 与 feature tree 均有原件。不是用 Python 3.9 monotonic 的独立绝对原点比较 native/Rust 值。

未改上游 34 源与受控 34 源成员核对，恰 8 个 native IO/协议/lifecycle 修改文件，完整 patch SHA=`3c3fa385e760f4f9549b14d70545962f0ebebe121d0c4d7401048840fc850ed9`。r3 113 项持久归档成员核 SHA 后，6 个旧 C++ 业务源已退役、不在新 source/link 图。Rust 同一 owner 负责 image/source/CAS/epoch/规则/公平/控制；Tauri 和独立 server 消费同 R 库，未发现第二 image/业务 scheduler。

预算原式 Q=480+256+480+480+512=2208；新 probe Job640 / Connection352 / native worker8736 / worker thread64，另计函数 Answer4096、Tag20、Rust FFI stack2048、map node256，per connection upper=18420≤65536，fixed instance=66592≤1MiB，全局4MiB。Socket/stack/logger/image metadata 单列；B0 不宣称 SO 数值等同所有 kernel 物理内存硬限。FFI stable Arc/Box、packed unaligned read、同步借用、int 异常屏障及真实 pthread/Rust join 调用图已审查；实际 QA W06/W09 生命周期实证仍待 gate。

八个新 QA 文件全部位于 T/build/qa；跨角色 Mach-O 路径/UUID 不同可以导致 SHA 不同，不要求 DEV/QA binary 同 SHA。

| 相对 T/build/qa 的产物 | bytes | QA SHA-256 |
| --- | --- | --- |
| native/libds_g0_native.dylib | 262184 | ca9c4eab9f6e06e2155336cc57735d7aa0541acf64bf542553edd8b777ad1f2e |
| native/libds_g0_reference.dylib | 255048 | 26dc39e3442134c0a44ea69ea55e245e1ed71fa208f4952376d288adf1ef4a49 |
| native/ds-g0-reference | 65696 | 70836d886bfee039f4e7d13c78826ed1d0ff21424a4224c4c902da52eaccf14d |
| native/ds-g0-native-abi-probe | 37272 | 8e67f925796d29f7c8db5a651fab60df23c5e5ed5afb432f5f4c637e8f485035 |
| runtime/aarch64-apple-darwin/release/ds-g0-server | 1077792 | 83df43b88b200e13411e903ef7379aaa7ddb5a081753408fe88dabe9744050eb |
| runtime/aarch64-apple-darwin/release/ds-g0-abi-probe | 510416 | 4b6ebe1bb7162458d075bd42fdf8f0c4df88904075f015fc764e20ac15e398eb |
| daa/aarch64-apple-darwin/release/ds-g0-daa | 577328 | 174778dfa6b08552ad18b26c41faeab61370feb77048dc7f7bbc5a00aebcd332 |
| desktop/aarch64-apple-darwin/release/aiis-device-simulator | 9107584 | b4b7b91d315feda71e4cb6936f3d6ba9c933e3e46e9a722e9f5bafaf43e4b25c |

DAA 五个真实模块和 core 三级相对 path 实际出现在新 release source dep-info；harness 用 `rust-snap7-driver`，没有以 fixture transport 替代。D/source-inputs.json SHA=`1e1ae973328b7a4f1d8611d2596ccb64bd1289c75f4bb8a2c767d59521349c80`。37 DAA 来源 aggregate=`55e84aef4f28029da474c2eecb9e29a8e463e8e92564d4c79b31920bf4c75cac`，17 CU aggregate=`062406ddb19f99d6485a7ee953bc1f8e9e85d752b6d1db961c637713e96a090d`。DAA accepted manifest 始终按 60/61+1 导航例外报告。

## AC31 实际等待点与资源

qa-0004 由上面的 native-cycles 命令启动，unified exec session=`9384`，launcher PID=`16492`，第一窗 PID=`16495`。新 binary SHA 为上表 b4b7…25c，source 为 ba08…9b3e，B0 为 qa-0002。真实 WebView 已发 `ds_get_bootstrap` 与 `ds_get_runtime_snapshot` 各一次；源配置和只读 IPC ready/启动入口对应 stopped。2026-10-20 16:34:36 UTC 的实际 ps 为 launcher/native 两者存活，native 子进程为空，30102/30103/30104 LISTEN 全空；无 QA S7 listener 被启动。

同一时刻附近采样 PID16495 CPU累计22.038259s、RSS75,579,392 B、18 threads、fd45、Mach ports323，monotonic_ns=651726259803000。该活跃窗口仍持续增长，不把这个累计样本当三轮关闭后的资源归零。

主协调在本次第一窗 ready 后已向 Owner 发出新的最小人工观察问题：实际看见三窗，并按每次窗口红色关闭按钮正常关闭。该新问题截至 checkpoint 尚未收到回复，真实正常关闭完成 **0/3**；旧 DEV A67 的“三窗可见/正常关闭”回复不能复用于新 QA binary。CUA 对这个 no-bundle Mach-O 的绝对路径/名称/bundleID 已知无法绑定，未创建 `.app`、用 AppleScript 或其他 UI 控制旁路，也未绕过锁屏。

qa-0004 及 launcher 因该三轮观察有明确依赖而有意保留；不发 TERM，不把等待时间视为输入，不把增长 raw 封成已结束 run。实际 launcher 仍将逐轮采集 CloseRequested/ExitRequested、Rust shutdown/join、code0、CLOCK_MONOTONIC 保守≤5s、owned PID/child/固定端口清空，再创建下一窗；这些尚未发生的结果均 pending。

## DEV 原件复算的可用性及限制

qa-0006/7 证明输入原件完整且可独立解释，不构成 QA 协议执行。最终 DEV 38 个原命令 419,965 条 server JSON 在 stdout/file 的规范化值、顺序、数量完全一致，当前最终 run 未见 evidence_lost/observability_degraded/sampling_error；历史失败另保留。逐 PID 真实起点/首个成功 wait 退出/实际样本和 client、ManagedS7、observer 分列，109 个不足1秒进程的 CPU 为 null、不可评估，不写成0；没有长存活漏采缺口。DS 核心统计用自身样本和单逻辑核 CPU 时间/同域墙钟，未除主机核数。

DEV C01 原测量300s 的16×600=9600请求、4800×(64+8)=345600 B、24000规则机会/0 missed，经原始 write round/slot 与同 client 前序 read 重新取出；C02 replacement 的额外 round99 不计入测量。逐连接最大 p95=0.362458ms/p99=5.08117ms，dispatch p99=0.05ms；原测量299个核心样本的 CPU比=0.08446858、RSS峰6,782,976 B/净增−491,520 B、线程25、fd+Mach83。保留 measurement 控制起止与阶段事件的实际不同时间，未混 Python 绝对原点。

DEV C04 原件存在真实 op3 阻塞、同响应首次 send started_ns→同 connection pthread_join 返回2.005257s，中间另连接2次实际 send 与20次 rule cycle；SO_RCVBUF/SO_SNDBUF 实读8192≤16KiB，TCP_NOOPT/MSS效果、FIONREAD及已广告 credit 各自记录。304次 offered 后实际 send 关闭，握手后 application recv=0；这些 SO 值不被表述为全部 kernel 物理内存硬限。DEV C06 20个 stopped RSS 原曲线与四组中位数重新计算，last5−first5=−507904 B，线程/fd/Mach与B0分项核对。以上均只审查 DEV raw，QA 原样复跑仍未运行。

## 持久证据与闭集 inventory

下列 A 目录已不可变复制，逐成员 bytes/SHA、实际成员集合和 JSONL 重新校验，inventory 排除自身。原命令、环境/失败、build/source/ABI/clock、helper源、raw stdout/stderr、images/wire审计定位均保留；不只留 `/tmp` 路径或 hash。qa-0007/8 的 source-manifest 内保留本次实际 QA helper UTF-8 源码。正式 source 自身仍按交付树与 pins 固定。

| A 子目录 | members | inventory SHA-256 |
| --- | --- | --- |
| qa-run-0001 | 7 | 931972e63ba255097feb4e9dbd256f9f0a7a0c7b2b9785fb7954aafc0ef48c9c |
| qa-run-0002 | 13 | c65e6260a67d94dddf1f8b7ec39ffe01967342719a2d3858f089a62be80842ed |
| qa-run-0003 | 5 | 490ec9fde8071cfe7880f8dc6d9222ff8676baa1ec9230c217ea900e35dab491 |
| qa-run-0005 | 4 | f801de693515e137ffd7d558fec1476bc8f7b4e5a26cdac718d79d0b28107327 |
| qa-run-0006 | 4 | 9e958a65ff92babac41c35ce47bc60e369ad4f1a36c77ca27941805dd2c1cf8f |
| qa-run-0007 | 8 | 3e073bfb69894b36af94b47d708bc31f8c6180b1ddecc9a0dd5da08a1f4ad5ad |
| qa-run-0008 | 5 | 266764a9f6fe99b7661bee8318322b788d60f108ed44cbce425cb89c6a40cf74 |

入口：[新 B0 inventory](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0002/inventory.json)、[逐PID/日志/保护与活跃窗口 checkpoint](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0007/results.jsonl)、[复算与闭集 summary](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0007/summary.json)。P 五 JSON 原件只读，baseline 的 verifiedCandidateSha256 仍 null，DEV candidate/QA pending/Owner pending 没被改写。

qa-0004 仍在 T/runs/qa-0004 增长；A/qa-run-0004 不存在。qa-0007 内只有标注时间点的首窗 IPC/资源/OS 命令快照，不伪称完整关闭证据。其余已完成 run 必要原件均已 A 持久化，T 的 QA build/cache/profile/helpers 与 native 活跃 run 因同版继续/审阅而保留；没有清理自有或他人资源。

## 验收标准

以下是本 checkpoint 的逐项状态，不是整体验收通过。`blocked` 表示该完整 AC 尚缺本次独立执行证据；static/design 子项已通过不补齐协议 gate。

| AC | checkpoint verdict | 证据或尚缺部分 |
| --- | --- | --- |
| AC1 | pass | exact Task/r4/namespace/批准链、历史与当前gate分开；实际新 fresh Verification。 |
| AC2 | pass（B0阶段） | qa-0001/2/3，固定来源/工具链/8 binary/link/ABI/预算闭合；没有先跑协议。 |
| AC3 | blocked | 冻结候选比较/拒绝依据与受控8文件diff可审；最终go/no_go仍待独立矩阵。 |
| AC4 | blocked | QA W01未运行；DEV raw合法写/typed读回审计不是替代。 |
| AC5 | blocked | QA W02/W09拒写与屏障并发未运行。 |
| AC6 | blocked | 六来源真实QA W07未运行；Rust单owner/source/CAS静态与合同测试已审。 |
| AC7 | blocked | QA W03三独立reset/每轮100 BOOL竞争未运行。 |
| AC8 | blocked | QA W04逐负例与合法对照未运行。 |
| AC9 | blocked | QA W05 STRING全包/负例未运行。 |
| AC10 | blocked | QA W06/W08多item部分成功/系统禁操作未运行。 |
| AC11 | blocked | QA C01原30+300s/16会话及同期C02第17条20次未运行。 |
| AC12 | blocked | QA C03原H4/TCP20/绝对期限/idle及C04真实send阻塞未运行。 |
| AC13 | blocked | QA C04全PDU预留/队列/故障/释放和真实SO/credit分列尚缺。 |
| AC14 | blocked | QA C05原60s/F1200 PDU4800items/A、B各120/UI60及三次积压stop/恢复未运行。 |
| AC15 | blocked | 真实DAA feature/link/source已核；QA D01双端口60s/240 db_read尚未运行。 |
| AC16 | blocked | QA D02原TSAP/端口/A误指B/owned冲突/重复start负例未运行。 |
| AC17 | blocked | QA W09/X01三轮屏障、未知回执和stop A期间B实际持续读未运行。 |
| AC18 | blocked | QA C06原160重连/20启停及10s资源/3reset未运行。 |
| AC19 | pass（严格N/A适用性） | 进程内native、无sidecar；X02父子模型严格N/A，native硬崩可影响A/B风险保留；公共stop/cleanup不因N/A免测，仍由其余blocked项承接。 |
| AC20 | blocked | DEV全原件/资源/日志可复算；本次QA全矩阵逐run统计尚无，不转记DEV通过。 |
| AC21 | pass（checkpoint） | 源保护、角色、DEV/QA/Owner层次、fail/blocked/not_run/deferred明确；不越权接受。 |
| AC22 | pass（来源/实际编译闭包） | qa-0001/2/8；60/61+1、实际五DAA模块/core、60⊆66⊆冻结bank与resolved feature/source图分别核实。 |
| AC23 | pass（设计验收） | canonical §13多文件/逐DB UDT/绑定/lineage/CAS/32DB与4096叶；产品D1另批。 |
| AC24 | pass（设计验收） | 受限理论辅助、STRING整DB拒推、完整NameBatch、初值/编码/原v1样例pin；不承诺实机oracle。 |
| AC25 | pass（设计验收） | saved/selected/loaded、九场景typed保值/初始化、停机apply/未知commit/单owner动作路径；D1–D4未冒充产品。 |
| AC26 | pass（source/build/启动血缘） | 180源/108输入与新8产物、D/R/S正式入口及实际native首窗一致；6旧C++业务源已退役。 |
| AC27 | blocked | baseline仍candidate，fresh QA未完成、Owner未接受；DAA应用→SQLite仍另批，B/C边界保持。 |
| AC28 | blocked（全量完成门槛） | 已结束QA闭集和189DEV输入已持久核SHA；native4仍增长、后续独立矩阵原件尚未产生，不能报最终全量证据齐全。 |
| AC29 | blocked | Rust真实调用图/diff/合同测试通过；QA W01–W09/C05 wire对账未运行。 |
| AC30 | blocked | 新ABI/int/Tag/callback/借用/异常预算已核；QA W06/W09实际callback/join/输出预留尚缺。 |
| AC31 | blocked / needs_input | 新native第一窗ready、两只读IPC，实际可见确认及3次正常关闭0/3；不复用DEV人工观察。 |
| AC32 | blocked | r3持久archive/6源退役/100同clock夹点及DEV时钟原件审计通过；本次QA C01/C06与完整原矩阵未运行。 |

## 失败、blocker 与限制

Development 历史失败/blocked、早期候选和 dev151–188 最终自检均保留在原输入中，不能转记成 QA 通过。qa-0005 对旧 A19主题/中英文/刷新观察只在44项UI/host/config来源及新build assets核对后单列审查；不能据此宣称新native三轮可见/关闭，A67属于DEV binary。

本次 QA 方法失败保留：qa-0001 pnpm旧 projects dangling symlink 复制 exit1，改为只复制核对真实 package content；qa-0005 Markdown inline-code/escaped pipe 的列统计 exit1，修正验证器后通过；qa-0006 decoder 首次对冻结Snap7非成功item transport0/DataLength4的无payload error header判断失败，按真实ACK/上游源修正后通过；qa-0007 先把重复wait当进程继续存活、又把C02 replacement额外round99混入C01、checkpoint中误猜并行文档路径，均分别保留 exit1 与原件，改验证方法后实际 exit0。未静默修复实现、依赖或文档；没有发现可据当前已执行面判定的实现failure，未运行面不据此豁免。

保护复核1918 baseline文件：当前12项差异中4项为协调根索引、8项为协调已分类的007/shared文档；DS/spec/tasks/P5/DAA/CU/core/004与receipt12文件、288 frozen inputs未变。8项并行原字节按实际父审计路径保留，不归因DS、不回滚，不用整树dirty否定本任务。

当前外部 blocker 仅为 AC31 新QA三轮人工作证/正常关闭；它按原批准顺序阻止后续全部QA协议矩阵启动。等待期间已完成不依赖关闭的重建、来源/设计/静态、原件/资源/日志审计；尚未产生的协议证据明确not_run。

## QA verdict 与下一 gate

本轮由起始 `qa_in_progress` 收束为 **qa_blocked / needs_input checkpoint**，没有最终 go、qa_passed 或 Owner 接受结论。不能把正常编译、DEV原件复算、两个IPC或等待时长移作三轮正常关闭/独立协议证明。

恢复入口是现存 tool session9384 / launcher16492 / T/runs/qa-0004，先核 pins 和新binary SHA仍精确，接收主协调relay的本次Owner观察，并逐轮等待真实关闭/join/code0/≤5s与PID/固定端口清理原件。不要另启动第二套native三轮，也不要TERM当前首窗。三轮客观事实和新人工观察均闭合后，才从新qa-0002 B0与同源独立QA binary执行原 W01–W09每向量至少三reset、W03每轮100、完整C01–C06/D01/D02/X01原次数与分母；X02只按严格进程内模型N/A。任何真实实现failure返回Development，须新精确handoff与fresh QA，不在Verification修复。

所有适用必证项独立齐全、证据持久和真实资源释放可核后，Verification才可提交QA verdict给Human Owner；QA passed仍待Human Owner final acceptance。

DAA 应用 S7→SQLite 联调仍另批，整体 B 不因本任务关闭；Stage C 不开展。没有真实.env/profile、设备、SQLite/Backend/API、发布/签名、Git refs操作。固定127.0.0.1:30102/30103和仅无listener负例30104，不退102、不扫描/换端口、不SO_REUSEPORT、不killforeign。QA 不清理临时资源；A/T保留供精确继续、Owner审阅及后续另批依赖，由主协调在依赖解除后另盘点。

## Human Owner final acceptance

Pending；本 Verification 不代 Human Owner 作最终验收或风险例外决定。

## 原生三轮完成后的历史补记（2026-10-21 08:20 +08）

本轮只消费已完成的 r4 原生run、实际回接旧session、核源/二进制和结束资源，并封存必要证据；没有创建新窗口、重新三轮启停、人工UI旁路、TERM或旧 W/C/D/X 矩阵，也没有实现产品纠偏。Owner已转向保留Rust与DAA派生正式UI/图标、导入/配置/启停/运行值及测试自动化方向；PM另形成r5 proposal，精确新Revision仍待批准。此方向不被扩成当前Verification实现授权。

### 实际完成与人工观察来源

独立回接原 unified exec session9384，实际返回 exit0，收到原launcher三次 `manual_native_cycle_complete` 及第二/三窗ready记录；并非session失效后的推定wait。原launcher PID16492，使用原B0 qa-0002、正式source candidate `ba08e83eb3c13ece431c87b304c8bdc2d0e1f8122e24c2477acc2ea9863b9b3e`、同一新QA binary SHA `b4b7b91d315feda71e4cb6936f3d6ba9c933e3e46e9a722e9f5bafaf43e4b25c`。

实际 scaffold SHA=`68fbd54f553411d0dd32ba99928d26821f490c92fb0dddc920458bdf020c0807`。逐PID原始日志与scaffold对应：

| Cycle | native PID | 真实正常请求/结束 | 同CLOCK_MONOTONIC的关闭上界 | IPC与清理 |
| --- | --- | --- | --- | --- |
| 1 | 16495 | CloseRequested、ExitRequested、shutdown_joined、真实wait code0 | 251470000ns（251.470ms） | 两只读IPC均发生；ready/退出后固定端口空、无子进程、PID消失 |
| 2 | 11435 | CloseRequested、ExitRequested、shutdown_joined、真实wait code0 | 211383000ns（211.383ms） | 两只读IPC均发生；ready/退出后固定端口空、无子进程、PID消失 |
| 3 | 11462 | CloseRequested、ExitRequested、shutdown_joined、真实wait code0 | 213544000ns（213.544ms） | 两只读IPC均发生；ready/退出后固定端口空、无子进程、PID消失 |

每轮上界从最早真实 Window CloseRequested 到wait完成及OS清理后时点重新相减，分别严格等于上表，均≤5s；不使用等待整段持续时间、Exit fallback或Python3.9独立monotonic绝对原点。`ds_get_bootstrap`/`ds_get_runtime_snapshot` 每PID各一次。events.jsonl与stdout.txt全字节相同，完整JSON逐行可读，stderr为空，未见evidence_lost/observability_degraded。原脚本对native close触发的Rust `desktop_shutdown_joined`、真实wait和owned资源清空已逐项核实；不把此stopped骨架三轮当作未运行的S7 W06/W09 callback/worker lifecycle证据。

Human Owner本次全局观察经主协调relay，原句为：

> 你前面几次的关闭三次窗口的测试都是正常能完成的，你可以看看日志。

该人工补充单列于qa-0009的 `owner_global_observation_relay`，与各PID客观日志分开。它支持此前三窗关闭正常的全局观察，不扩大成每窗主题/语言/刷新重新认证、完整协议QA或Human Owner final acceptance。旧A67人工材料没有被移作新QA三轮；本次结论使用新qa-0004事实与本次Owner补充。原scaffold和脚本summary中的 `human_observations/pending` 是生成当时字符串，保留原字节与SHA，通过本补记关联后续人工来源，不把它继续当当前blocker。

### 精确来源、历史与资源

补记时重新核实正式180源/108只读输入共288项、B0八个binary pins均未变。原r4 spec/tasks/checklist起点副本分别为 `4f1b03ec618bd0a40295bf273339538bc1491f8082380a009449f681ef56c2fc` / `4187f48bcfe555ddf5009be8a7beef02c3b38f921d0d54cc5f900e106b22e701` / `771ebc885549769d1332588a1b86aa5d1576e5d43389cf45ccea4bc8ca613d66`，全UTF-8原文连同helper/source pins持久在qa-0009/source-manifest.json；后续r5嵌入历史或当前spec变化不被误作r4交付来源漂移。P5与实现/锁/DAA/CU/core及根索引没有被Verification修改；并行007/shared字节保留。

2026-10-21 00:18:01 UTC（08:18:01 +08）精确只读 `ps -p 16492,16495,11435,11462` exit1且stdout/stderr空，证明原launcher/三窗PID在该时点均不存在；固定30102/30103/30104 LISTEN检查exit1且空。没有自有原生run继续存活或需等待关闭，不宣称其他用户启动的应用/共享系统服务归本QA资源。

未删除资源。00:20:17 UTC的 `du -sk` 保留事实为 T/build/qa=1403240KiB、T/cache/qa=2528284KiB、T/tmp/qa=188KiB、T/profile/qa=6176KiB；已完成run原件仍在T与A。build/cache/profile/helper保留供r5具体调整与G0清理时按归属/依赖盘点；“调整完成后清理G0”不被QA提前执行为删除。原DEV/他人资源及真实配置/数据未动。

### 新封存闭集及当前结论

qa-0004现在已结束，才首次封存A/qa-run-0004；此前“增长中不封存”的checkpoint保持真实。新增qa-0009保存本次source/bin/逐PID日志复算、实际session回接收据、Owner补充、精确OS/du命令与r4原文快照。两者实际成员集合/每成员bytes/SHA/JSONL均独立复核，inventory排除自身，原七份闭集未改。

| A 子目录 | members | bytes（不含inventory） | inventory SHA-256 |
| --- | --- | --- | --- |
| qa-run-0004 | 9 | 11163754 | 79135a8fa1d3fbfa0dd0df2a53d4bcdadf9783362a2e4578f450544ac55dea0f |
| qa-run-0009 | 5 | 548278 | a6cdd4926e1041a5a99fef2bcc59adbbc3165e62de76e11d8c3acb0f1edaa25c |

入口：[原生三轮原件inventory](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0004/inventory.json)、[三轮scaffold](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0004/scaffold.json)、[本次独立补记/人工来源/资源原件](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0009/results.jsonl)、[补记inventory](/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r4-evidence/qa-run-0009/inventory.json)。

当前AC31原生三轮及同源骨架门槛 **pass / closed**；AC28的本次native必要原件持久化子项闭合。旧AC表在00:40时点的blocked/0/3没有被retrofit。其余独立协议W01–W09、C01–C06（含C02）、D01/D02/X01仍 **not_run**，X02仍仅按进程内模型严格N/A；AC3/4–18/20/27–30/32涉及的完整协议与证据条件不因此通过。

整体r4 QA保持 **qa_blocked / incomplete**，原因是独立协议矩阵尚未完成；Owner转向产品纠偏并要求自动化、调整后清理G0。本次补记按主协调的有限范围指令不追加旧矩阵，后续同类协议回归由r5精确scope承接，未豁免或通过。此状态不是再次等待三窗输入，也不是实现失败结论。旧正文“恢复session后继续原矩阵”的操作入口不作为本次补记执行指令：session9384已真实结束，本次不回启该三轮、不执行旧W/C/D/X。下一活动范围由PM形成精确r5 proposal并等待批准；此补记不授权Development或代替新handoff/fresh Verification。

没有最终qa_passed、G0终验或Owner接受。DAA应用→SQLite联调另批、整体B不因本次native门槛关闭、Stage C不开展；邮件按Owner要求跳过。
<!-- END R4 CHECKLIST EXACT SNAPSHOT -->

</details>

## ARCH-AW-005 r5 QA1（2026-10-21）

**Verdict：qa_failed。F-r5-001 是公开 P5 的工程证据放置缺陷，不是产品 runtime/UI/协议功能失败结论。** 精确 r5 的完整产品 QA 尚未完成，返回 Development 修正交接工件；Human Owner final acceptance pending。没有继承或升级上方 r4 的任何 QA 结论。

### 身份、读取与精确输入

本轮是 developer_handoff 后实际命名 Verification 的 fresh context，不继承 Development 对话推理。已消费根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 `.codex/agents/verification.toml`、最近 AW/DS/runtime/native/tests/fixtures/src-app/plans 说明、完整 spec/tasks/旧 checklist。嵌套历史通过全文段落读取、重复段落逐字对照和 r4/r3/r2/r1 原字节恢复复核，未把历史作为本轮运行结果。实现/脚本、diff、锁及可用 DEV raw 是输入；已发现明确交接失败后停止扩大技术执行，未完成的实现/测试方法审查亦不称完成。

适用 shared skills 已按实际表面读取：project-governance、aiis、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow、plc-point-mapping、code-document-indexer；backend-arch 仅取本地 SQLite/DTO/分层边界。没有初始化、治理 apply 或实现修复。角色 model=gpt-6.1-sol/effort=max 是 TOML 配置证据，不宣称独立观测运行值；profile=contract_only，串行 handoff 与 diff/checklist 审计是合同控制，不宣称 ACL/强制路由。

| 输入 | 本轮独立核对 |
| --- | --- |
| 批准 spec | SHA `67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419`；r5、owner_approved、29R/45AC，Owner 布局纠偏由当前 R27/K08/AC40 承接。 |
| Development tasks | SHA `420361ad132ad7d51b6868a35ad15410acd621f74ffbb048928a28fc6839989a`、developer_handoff。 |
| DEV handoff receipt | `T5/tmp/dev/developer-handoff-receipt.json` SHA `97433e0183eb87935140a3ea154bb214055e3ecdb33ee6dc8b82e71f3b22d7e8`。 |
| 正式源码 | 227 成员，candidate `4d0c3ab8d614a8b0031bfd4e4a3dbc38f48892ecd07f7ddc97d3af773e0e70f0`；起点与停止后逐 SHA 一致，HEAD 不能单独恢复脏树交付。 |
| 其它交接身份 | 22 documents、3 locks、9 DEV 实际 binary/dylib、P5 恰五 JSON 均匹配 receipt；DEV binary 只作输入核对，没有作为 QA 运行产物。 |
| 固定来源 | DAA196 已在 QA 自有 stage 原字节暂存，digest `4751262a5c68aa28f037f9214b43d980587059663e762de096f9b5462bf855e9`；196+108 pin 合并为234个不同成员，均匹配。5图标由冻结输入约束；本次不宣称实际 Dock 呈现。 |
| accepted core/DAA | accepted-source-manifest SHA `8d9d62457baa32aac8134df77773ea5cae23a0401e403ef1d4c267cdafc02ee7`；60/61技术原字节匹配，CODE_INDEX 导航例外单列，不写61/61。core/v1原件只读，不改 expected/oracle。 |
| 旧 QA 原文 | 本次写入前 checklist 全文 SHA `2ba72a739b27a5374e372164eaed656d7956de1f0148be17bafbc2ce14be3e64`；上方 marker 内保持完整原字节，另持久在 A5/qa-run-0003/r4-checklist-before.md。 |

T5=`/private/tmp/arch-aw-005-r5-exec`；A5=`/Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence`；P5=`evidence/r5`。QA 公开只写本文件，私有执行/证据只在 T5 qa 路径及 A5/qa-run-NNNN；spec/tasks/P5/实现/测试/配置不改。

### F-r5-001：公开 manifest 直接嵌入原始 native status

失败位置：[delivery-source-manifest.json](evidence/r5/delivery-source-manifest.json#L301)，JSON pointer **`/nativeStage`**。文件119460 B，SHA `0143e22ce17f10a0a9059e08fd50e6fc4fa89668829df6f137fe1c61129c0c9a`。

规格 §5.2 明确：“A的raw种类……增UI steps/DOM断言……公开P只紧凑事实/hash，不放raw日志/bin/运行DB。”R12 要求“raw持久A5、公开P5仅五索引”；AC28 要求“P5仅5紧凑文件”。当前 `/nativeStage` 与持久 **A5/dev-run-0255/status.json 整个 JSON 对象严格相等**，后者 SHA `dd3d8dc2a61f8f23076abe04ce2493bc734c801de39f78ba1fbe3c0aac19066f`。不是仅引用 path/inventory SHA/有界结果摘要。

| 公开 JSON pointer | 与持久原件的独立对象比较 | 已直接携入公开仓的 raw |
| --- | --- | --- |
| `/nativeStage/cycles/0` | 严格等于 A5/dev-run-0257/status.json；SHA `4d53d8dbfd7682a2c53eb1333a7468ed4a256ae2110c2295f210223a58302e81` | 12个 native_dom_step、32个 WK probe 事件、3个 PID 观察；`steps/2/details` 含整页真实 DOM 文本。 |
| `/nativeStage/cycles/1` | 严格等于 A5/dev-run-0258/status.json；SHA `1783275e02a97c35dcbfef95804171e3250535a7412d886a33d59c4262b471db` | 11个 native_dom_step、13个 WK probe 事件及3个 PID 原观察。 |
| `/nativeStage/cycles/2` | 严格等于 A5/dev-run-0259/status.json；SHA `3ed457b8a9e2dbc3e1e19cd10f53fb5cb318ac4fe6ac2b1bc420f32092f22b6f` | 7个 native_dom_step、5个 WK probe 事件及3个 PID 原观察。 |

合计30个带真实 monotonic_ns/pid/run_id/details 的步骤事件、50个 WK probe 原事件，并含原 `ps` 输出、运行时钟/关闭和资源观察；例如文件第380行是实例页整页 DOM 文本，第550行起为原 WebView PID probe 列表，第1085行起为原 ps 输出。A255/A257–259 inventory及完整成员已独立核集合/bytes/SHA；原件存在且保留，不需要删除或改标签来修复公开边界。

复现命令和方法位于 [QA审计脚本](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0007/audit_handoff_failure.py>)：读取 P5 与 A5/status，作严格 JSON equality，再枚举 raw 字段 pointer；实际最终退出0。机器结果 [finding.json](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0007/finding.json>) SHA `87b0f44f0ebb58840b25da5b5704e85ce9c2456073d371a42c428991b6cd460a`。

**返回 Development 的具体修复要求**：保持 A5 原件、失败历史和原 source/bin/run 标签不变，把 P5 的此类 raw 嵌入改为紧凑摘要与真实 archive/inventory/SHA 引用；检查其它 P5 和生成/交接方法是否再次复制 raw，重新形成精确 DEV handoff。Verification 不代修。纯工件修复不自行扩成产品实现修改或额外窗口重测；本轮尚未执行的原必证 QA 项仍 not_run，后续 fresh Verification 不得用 DEV 原件或本次普通入口替代这些项目。

### 已执行命令、实际时序和停止原因

环境实读 macOS15.7.7/24G720、arm64、10逻辑/10物理核、34359738368 B RAM、Rust1.89.0、Node22.19.0、SDK26.1。完整环境原命令在 A5/qa-run-0007/commands.jsonl；未完成 B0，不称完整工具链/预算/100clock gate 已关闭。首次默认 sandbox 的 pgrep exit3/sysmon unavailable 保留；已批准的精确进程/loopback/native运行使用必要 escalation，没有自动审批拒绝。

1. QA 独立 cache 从冻结包复制：548个 Cargo `.crate` 全部按原锁 checksum 核验；不复制 DEV target 或已解包 Rust source，由 QA Cargo 自行解包/构建。pnpm store 25841个 content 文件/930686460 B 逐SHA512名称核验并二次SHA256核复制，index.db 独立核SHA。没有联网获取新包、安装/升级工具链或改依赖/锁。
2. `/usr/bin/python3 -B scripts/derive_daa.py --project-root <正式D> --run-root <T5> --role qa` exit0，196原字节暂存，不构建/运行DAA。
3. `/usr/bin/python3 -B scripts/run_validation.py --project-root <正式D> --run-root <T5> --role qa --suite all` 实际 session59709/aggregate PID76022；先创建 qa-0004 全候选原字节快照。qa-0005 普通 `pnpm tauri dev` 已在本次 QA 的 Cargo target/cache 从正式源码独立编译并完成，随后自动 watcher 收尾；不是复用 DEV binary。
4. qa-0005 实际 PID76182；新 debug SHA `992bc2437a0e2dc8dfebfce63020521d3993753d53153c547d9b93c0b15d51b0`，nativeFeature=true，int callback0/37/Tag20已由该次启动实际核验；bootstrap/configuration/runtime_snapshot 三正常IPC均ok。新owned SQLite appID0x44535631/user_version1/七表，空配置无S7 listener；Vite只固定15194。run 原 status=pass，launcher code0/remainingPids=[]/五口空；这些事实在发中断前已完成，不回写为未发生。
5. all 随后进入 qa-0006 core；`cargo fmt --check` 真exit0，`cargo test --offline --locked ... --features native-s7,test-automation --lib --tests` 尚未返回完整结果。确认 F-r5-001 后，按精确实际 Python.app argv 核aggregate PID76022并发SIGINT；真实 traceback 在 core subprocess.communicate 收到 KeyboardInterrupt，tool session59709 exit130。core 无完整test结果，不记pass。首次信号helper因误假设 `/usr/bin/python3`显示路径而断言exit1、未发信号；第二次核实际解析路径后才发，方法失败也保留。
6. B0、新release/test build、N1–N3、K07、W/C/D/X没有执行，没有QA S7 listener。未继续已知静态失败下的长矩阵，也未以 TERM/watcher SIGINT 冒充正常Window.close。没有本轮独立的产品布局/DOM/浏览器像素通过结论。

普通入口实际 profile 为 `T5/profile/qa/normal/qa-0005`；store UUID `529ab9c1-9918-4899-b918-d9ddfebdc18d`。本轮只读核实际系统路径 `/Users/jason/Library/WebKit/aiis-device-simulator/WebsiteDataStore/529ab9c1-9918-4899-b918-d9ddfebdc18d` 存在且元数据已持久；不是只凭 DS_PROFILE_DIR 宣称隔离。该普通入口没有完整 WK 全树1Hz资源归属或正常关闭证明，不套 headless C01 RSS阈值，不推断未知费用为0。

nativePatch 两个SHA不是第二failure：正式 `native.patch` 为 `7fafa44ddff8e14ee41c26252855a1b1aca40cf4dcb812db3d52080a53fff3d1`；receipt 的泛称 nativePatchSha256 实际指A256 `vendor-computed-diff.patch`，为 `763ae1ed359139f7451dd0d84e1df5136561afa6b397a2283248c92b5729493b`。独立按8文件分组比较 hunk 字节全部相等，差别为diff文件顺序及 a/b 与 upstream/controlled 头标签。对象命名不够精确的局限已列，不把不同对象误判为实现漂移。

QA 私有辅助错误全部保留：receipt相对 binary path误当绝对路径、pnpm父目录缺失、resume copytree遇既有index、acceptedFiles误当dict、sysctl路径误用。仅修QA验证方法后最终audit exit0；未因此改实现/expected/历史status，未把这些helper失败计为产品失败。

### 45 AC 当前状态

`partial` 表示仅完成该AC的列明子项；`not_run` 是因F-r5-001早停而未执行，不能写pass或deferred。下表没有把任何 DEV self-check转成本轮QA通过。

| AC | QA1状态 | 实际证据/尚缺 |
| --- | --- | --- |
| AC1 | pass（治理） | 精确r5批准/身份、历史及DEV/QA/Owner层次已核；无接受预填。 |
| AC2 | partial | 227source/锁/包、普通入口新build已核；完整B0/实际预算/100clock未运行。 |
| AC3 | not_run | 未完成native有限性/dispatch全调用链独立技术核验。 |
| AC4 | not_run | W01三轮未运行。 |
| AC5 | not_run | W02/W09静默拒写/屏障未运行。 |
| AC6 | not_run | W07六来源/CAS未运行。 |
| AC7 | not_run | W03三轮各100竞争未运行。 |
| AC8 | not_run | W04全负例未运行。 |
| AC9 | not_run | W05 STRING完整/负例未运行。 |
| AC10 | not_run | W06/W08未运行。 |
| AC11 | not_run | C01及同窗口C02未运行。 |
| AC12 | not_run | C03/C04真实send期限未运行。 |
| AC13 | not_run | 全PDU/三层预算/归还未运行。 |
| AC14 | not_run | C05原offered/公平/stop未运行。 |
| AC15 | not_run | 新QA ManagedS7真实编译/240读取未运行。 |
| AC16 | not_run | D02身份/端口/冲突未运行。 |
| AC17 | not_run | W09/X01提交/未知/隔离未运行。 |
| AC18 | not_run | C06原160重连/20启停/3reset未运行。 |
| AC19 | partial / 条件N/A | spec/交付为同进程native、无sidecar；X02仅父子分支条件N/A，硬崩可能波及全DS；共通正常close未验证。 |
| AC20 | partial | 本轮实际起点/ordinary/原件关联已存；全矩阵分母/资源统计未产生。 |
| AC21 | partial | fresh/串行/不代修/无Owner接受成立；完整独立重建与全适用矩阵未完成。 |
| AC22 | partial | accepted60/61+导航例外/196+108pins均核；完整新DAA编译闭包待B0。 |
| AC23 | not_run | 真实多文件重导/UUID业务矩阵未运行。 |
| AC24 | not_run | core v1实际DS消费者/typed完整矩阵未运行。 |
| AC25 | not_run | apply九场景/selected/loaded/unknown未运行。 |
| AC26 | partial | 正式227source/22docs/锁/DEV9产物身份已核；QA产品/test/DAA/B0未全重建。 |
| AC27 | not_run | 有限baseline仍candidate，完整QA未完成。 |
| AC28 | **fail F-r5-001** | P5直接内嵌A255/N257–259原始native status，违反紧凑索引边界。 |
| AC29 | not_run | Rust单owner完整源码/合同/wire联合证明未完成。 |
| AC30 | partial | 普通启动实际int0/37/Tag20；完整新B0/100clock/借用/join wire未完成。 |
| AC31 | not_run | r4原成功保留；本r5独立N1–N3/正常Window.close未运行。 |
| AC32 | partial | r4/r3/r2/r1 spec原文恢复SHA匹配；G0102成员/旧原件迁移与新clock回归未完整独立审完。 |
| AC33 | partial | 本次新空v1/appID/七表/独立profile已实测；全部锁/坏库/未知版本负例未运行。 |
| AC34 | not_run | 真实CAS/容量/失败/unknown整组被中断，未完成。 |
| AC35 | not_run | 重导/core v1/preview矩阵未运行。 |
| AC36 | not_run | manual/coverage/命名/pending矩阵未运行。 |
| AC37 | not_run | 全类型/五规则/policy矩阵未运行。 |
| AC38 | not_run | 九场景实际安装/故障/重开未运行。 |
| AC39 | not_run | K07真实通用多DB/双实例及边界未运行。 |
| AC40 | not_run | 六页八组件/布局/真实DOM/双语主题窄窗未独立复测。 |
| AC41 | partial | normal pnpm tauri dev真实native/SQLite/3IPC/empty stopped，无G0必需键；默认路径及负例等完整门未闭合。 |
| AC42 | not_run | test双gate/实际N1–N3/正常close未运行。 |
| AC43 | not_run | 日志降级/SQL失败完整core结果未取得。 |
| AC44 | not_run | 未完成102成员退役原件/逐项引用/清后产品独立审计；不推断失败或清理完成。 |
| AC45 | fail（handoff gate） | F-r5-001未修；完整QA未完成，不能交Owner最终接受或可联调放行。 |

### K组、原19case与N1–N3

| 组 | 本轮结果 |
| --- | --- |
| K01 | partial：196来源、227交付、普通入口与新owned profile实际完成；其它native/UI/资产呈现未完成。 |
| K02 | partial：新空SQLite身份实际完成；完整CAS/故障/双进程锁测试未完成。 |
| K03 | not_run：core消费者/重导。 |
| K04 | not_run：地址/命名/手工。 |
| K05 | not_run：类型/规则/policy。 |
| K06 | not_run：apply九场景。 |
| K07 | not_run：通用多实例真实wire与容量边界。 |
| K08 | not_run：六页/八组件/布局/DTO完整native回归。 |
| K09 | not_run：原生保存重开及正常退出。 |
| K10 | fail：P5公开raw边界F-r5-001；其它日志/原件/退役子项不推定通过。 |

| 原case | QA1状态与未执行边界 |
| --- | --- |
| W01 | not_run；三次独立reset未开始。 |
| W02 | not_run；原coverage overlay/静默判据未改。 |
| W03 | not_run；原三轮各100竞争未改。 |
| W04 | not_run；原边界/typed/frame负例未改。 |
| W05 | not_run；原STRING8/254完整包未改。 |
| W06 | not_run；原逐item保序部分成功未改。 |
| W07 | not_run；原六来源/普通维护CAS未改。 |
| W08 | not_run；原禁系统操作未改。 |
| W09 | not_run；原屏障/提交未知/join未改。 |
| C01 | not_run；原30s预热+300s/9600请求/345600B未缩。 |
| C02 | not_run；必须C01同16会话窗口，不另造空窗口。 |
| C03 | not_run；原握手/半frame各3次及idle30s未改。 |
| C04 | not_run；原20Hz/256B/最多30s与真实send阻塞/2.5s未改。 |
| C05 | not_run；原60s、A/B各120请求/UI60成功/三次积压stop未改。 |
| C06 | not_run；原160重连/20启停/每次10s/3reset未改。 |
| D01 | not_run；真实DAA五模块/两端点60s/240读取未发生。 |
| D02 | not_run；错TSAP/空口/误端点/冲突负例未发生。 |
| X01 | not_run；原三次及B持续读未发生。 |
| X02 | 条件not_applicable仅父子/sidecar专属分支；本交付同进程native，无崩溃隔离承诺；其余正常退出/资源要求未豁免。 |

N1/N2/N3均 **not_run**。本次未复用 DEV N257–259 或旧 r4 QA 三窗代替本轮独立运行，也未把普通watcher收尾计为正常close；未请求Owner反复关窗。

### 持久原件、资源与foreign边界

每份qa-run已逐成员复制并二次核SHA/bytes，inventory排除自身；没有仅保留临时路径。A3包括本次固定源/doc/P5/receipt/旧checklist、包复制清单及明确coordinator-origin的awake授权/进程/到期、foreign Tool与保护观察输入；它们不是QA verdict。A4保存完整227候选原字节；A5是已实际结束的普通入口raw；A6/A4显式保存aggregate中断原因；A7保存失败严格比对、原DEV status/inventory、原patch对象、真实普通events/ownedSQLite、资源和当前保护核对。

| A5子目录 | members | inventory SHA-256 |
| --- | --- | --- |
| qa-run-0001 | 2 | `16b0d5c3579e516e24a3b6f3cc734c47a28bb539e3b8b9596555eb503c59ae96` |
| qa-run-0002 | 44 | `9d66b21d0828ebcb40b1eec5f2819d9304ec9031a953b3d885f51244116ef5bb` |
| qa-run-0003 | 47 | `e20c42bcd242556a3cde25e8ef21cc020e4fb5371b842db88873d2a254671424` |
| qa-run-0004 | 230 | `711f2d827d01a510b5c0063e4017924334b5d50f571be855ce8e3b770305a34b` |
| qa-run-0005 | 4 | `e17f92564e7950958137f4a374bd87f068629efc752eff5a3980434bb3145934` |
| qa-run-0006 | 2 | `2e46d635051dd5a811a629bf6b7c897240402ab07263be393e3e0ad88f5675d6` |
| qa-run-0007 | 28 | `703541c43adf3a0bf1c1ad76fa3e55fe9cf42933bd4b93b1893b56e0553cbaac` |

最后资源检查2026-10-21 07:36:36 UTC：五个固定端口30102/30103/30104/15194/14194的每个lsof均exit1/stdout/stderr空；精确76022/76045/76182 ps exit1空；精确QA target/命令筛选无匹配，未见QA遗留构建/产品进程。普通入口已观测children在q5结束时逐PID检查退出；共享WK/XPC不冒称自有孤儿或零费用，未知不删。未重新启动/续时caffeinate、解锁或改系统设置；CUA一次实际inventory正常仅证明当时可用，不承诺后续。

T5的stage/qa、cache/qa、build/qa、tmp/qa、profile/qa与runs/qa-*、本次系统UUID store全部保留。用途是DEV返工后的精确复核、未完成QA和Owner审阅；由唯一协调在无运行/后续/证据依赖且持久原件齐全后再按授权决定收尾。QA未删源码、cache/profile、SQLite或系统WebKit目录。未知foreign Tool spec缺失及根四索引并行差异按coordinator-origin材料保留，QA未恢复、删除或认领，不当DS依赖；DS/DAA/core技术pins停止后仍严格匹配。

### QA handoff与Human Owner gate

**qa_failed / F-r5-001返回Development**：修公开证据边界及对应交接方法，保留所有raw和失败状态，再交新的精确receipt；主协调随后必须启动新的fresh-context Verification。当前checklist不是完整r5通过，不标Owner接受，不放行真实DAA应用→DS→SQLite、整体B/C、现场/真实设备、部署发布或Git refs。

最终QA交接回执将保存于 `A5/qa-run-0008/qa-handoff-receipt.json`，包含本checklist最终SHA及保护/封存核验；为避免自哈希环，本文件不内嵌自身SHA或该后续receipt内容SHA。独立verdict只交Human Owner决策，implementation/handoff failure由Development返工；Owner最终接受保持 **pending**。本角色完成记录与收据后停止写入，不代修、不清资源、不外发邮件。

## ARCH-AW-005 r5 QA2（2026-10-21，F-r5-001材料返工后）

**Verdict：qa_failed。F-r5-001 的公开证据放置返工已独立核准关闭；正式 QA core 命令出现新的 F-r5-002，返回 Development。** 本轮没有完整 r5 产品、原生或协议通过结论，Human Owner final acceptance 仍为 pending。旧 r4 与 QA1 的结果只保留其原时点和证据归属。

### 身份、精确输入与执行边界

本轮由唯一协调在 Development 明确停写、停构建和应用后实际新启命名 Verification（`/root/verification_r5_final`），fresh context，不继承 Development 对话推理或旧 QA verdict。独立读取根 AGENTS、README/PLAN、canonical workflow、`.codex/agents/verification.toml`、AW/DS 最近说明、当前 r5 合同/交接与历史记录、P5、原件和相关实现/测试。明确失败后的实现全审和全部必需执行未完成，不记为已完成。role TOML 中 model/effort 是配置证据；profile=contract_only，串行 handoff 与 diff/checklist 审计是合同控制，不宣称平台 ACL 或强制 routing。

实际消费的适用 shared skills 为 project-governance、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow，以及 AIIS、点位和索引规则的适用部分；仅用于核验，不执行治理 apply、安装升级或实现修复。本轮公开写面仅此 checklist，私有原件仅 T5 的 qa 路径与 A5/qa-run-NNNN。未改 spec、tasks、P5、实现、测试、配置、锁或索引。

| 精确输入 | QA2 独立冻结结果 |
| --- | --- |
| spec.md | `67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419`，r5/owner_approved；R27/K08/AC40 的现有布局范围没有新增 Revision。 |
| tasks.md | `ce7c37b106ffe08a259d109d78ac2e1520a23aeca203f1d0897aed1f01913b8b`，developer_handoff。 |
| 新 DEV receipt | `a911d9997c78d7fe0fe6992fc9283f0d5d6fcedaafcd52a8b52594596052308e`；原件在 A5/qa-run-0009。 |
| 正式源码 | 227 成员/candidate `4d0c3ab8d614a8b0031bfd4e4a3dbc38f48892ecd07f7ddc97d3af773e0e70f0`，起点/停止前与 receipt 逐 SHA 一致。 |
| 其它交接 | 22 documents、3 locks、9 DEV 实际 binary/dylib、五个 P5 全部逐 SHA 匹配新 receipt；与旧 A262 receipt 比较，source/documents/binaries 对象均完全相等。DEV bin 未作为 QA 运行产物。 |
| 固定输入 | 正式 checked_inputs 核 spec、source-inputs 及 DAA196/r4Frozen108 合并的 234 个不同来源成员，均匹配。既有 QA cache/stage 保留；本次没有重新安装或从 DEV target 复制产物。 |
| 起点旧 checklist | 全文 SHA `6010a27858b414b8d75d69abd04209dccfc4757e2f71110eec77a38130b1e0eb`，原字节已持久 A5/qa-run-0009/checklist.md；原 r4 marker 内 SHA 仍为 `2ba72a739b27a5374e372164eaed656d7956de1f0148be17bafbc2ce14be3e64`。QA1 正文保留，不回写旧失败。 |

T5、A5、P5 的绝对路径与上方 QA1 定义一致。QA2 起点及 core 后五固定端口每项 lsof 均 exit1、stdout/stderr 空。没有启动 S7 listener、普通入口、原生窗口或浏览器 preview，没有读取真实 DS/DAA 默认 profile/env/DB、操作真实设备、外发消息或改变 Git refs。

### F-r5-001 复核：公开摘要与持久原件边界已关闭

由 QA 自写独立 helper 逐对象检查全部五个 P5，未调用或信任 DEV validator 的 pass。实际复核结果：

| 审核面 | 本轮结果 |
| --- | --- |
| 五对象内容 | 精确文件集合、顶层字段、候选/spec 身份与未填 QA/Owner verdict 均匹配；递归无 steps/details/DOM/events/原始 PID、ps、stdout/stderr、逐秒样本或多行原文嵌入。公开文案中描述资源方法不等于携入原始样本。 |
| 引用 | 67 份 member+inventory 引用及 1 份 inventory-only 引用，共 68 处，逐项重读真实 inventory/member SHA、bytes、路径及非 symlink；另核 260 个 archives inventory SHA、2 个公开 JSON Pointer、45AC/10K 的编号集合和映射 run 存在。 |
| native projection | A255 三轮与 A257–259 原 status 对象逐项核对 result/exit、关闭上界、实际 30 DOM 步骤及 50 WK probe 的计数、三组件成功/不可用样本数、错误和释放统计。公开只保留有界结果/数量及 SHA 引用，不等于完整 raw status。resource-closeout 的摘要与该 projection 一致。 |
| 协议摘要 | 原 38 case-run 的 case/result/duration 与各真实 summary.json 严格相等；W 各三轮、X01 三轮、C02 保留在 C01 原窗口、X02 保留真实条件 N/A 理由。只审核 DEV 记录，没有新执行这些 case。 |
| 历史与生成材料 | A263 旧五 P5、旧 97433e… receipt、A8 QA1 checklist/receipt 均保持真实引用；A265 19 成员的 SHA/bytes 全核，与新 P5/tasks 匹配。原正式 patch 和 computed patch 分别明确命名，没有误报为源码漂移。 |
| 方法负例 | 私有内存中的 whole native status、raw steps、raw ps 三种注入均被 QA helper 拒绝；未写公开 P5。 |

独立原件：[p5-independent-audit.json](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0012/p5-independent-audit.json>)；helper 与真实命令/exit0 同 archive。首次 QA helper 对 X02 漏列允许的 reason 字段而 assert exit1，初稿/命令保留 A11；修正 QA 方法为明确核 reason 与原件严格相等后 exit0。更早只读摘要 helper 对整数 frozenDaaInputs 调用 len 的 TypeError 也如实记录。它们均未改变产品、expected、P5 或历史 status，不是产品 failure。

因此 **F-r5-001 closed（材料边界）**；AC28 的该子项通过。该结果不授予整个 AC28、完整产品 QA、原生行为或协议通过。

### F-r5-002：正式 QA 角色的 core 正例硬编码 DEV 路径身份

位置：[lifecycle_protocol.rs:169](../../automation-world/device-simulator/runtime/tests/lifecycle_protocol.rs:169)，测试 `test_manifest_rejects_parent_escape_symlinks_and_role_mismatch_before_profile_open`。

正式独立命令：

```text
cwd=/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator
/usr/bin/python3 -B scripts/run_validation.py --project-root /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator --run-root /private/tmp/arch-aw-005-r5-exec --role qa --suite core
```

外层实际 exit1，qa-0010。`cargo fmt --manifest-path <D>/runtime/Cargo.toml --check` exit0；`cargo test --offline --locked --manifest-path <D>/runtime/Cargo.toml --features native-s7,test-automation --lib --tests` exit101。这是正常返回的测试失败，没有 SIGINT/TERM 中断。runner 使用本角色 `CARGO_HOME=T5/cache/qa/cargo-home`、`CARGO_TARGET_DIR=T5/build/qa/runtime`、`TMPDIR=T5/tmp/qa`，并令 `DS_TEST_RUN_ROOT=T5/profile/qa/normal/qa-0010`。本轮从正式源真实增量编译 Rust/native 测试，未复用 DEV target。

测试在该 QA root 新建 UUID 子目录，但第167行合法样例固定 `role="dev"`、`runId="dev-9999"`，第169行断言 Manifest::read 成功。[hooks.rs:76](../../automation-world/device-simulator/runtime/src/testing/hooks.rs:76) 正确把允许路径限定为 `profile/<manifest.role>`，该路径因此仍属 qa，不能成为 dev 正例。由第76–78行可推导拒绝码为 test_manifest_role；实际 panic 输出只显示 is_ok 断言，未虚构它打印了该 Err 值。

实际失败 manifest 原件含 `profileDir=T5/profile/qa/normal/qa-0010/d3e6bb99-398c-4ffc-83c3-22a8a44d7760`，与 `role=dev/runId=dev-9999` 同时存在。真实 stdout 显示 **23 tests passed / 1 failed** 后 Cargo 停在 lifecycle_protocol；后续 test binaries 和真实双进程 profile-lock 检查未执行，不能把部分结果写为完整 core 通过。

原件：[commands.jsonl](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0010/commands.jsonl>)、[实际失败样例](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0010/failing-test-manifest.json>)、[F-r5-002 结构化证据](</Users/jason/.codex/visualizations/2026/10/18/01a14e52-eeb4-7c82-bade-bc0a237fa2ff/arch-aw-005-r5-evidence/qa-run-0013/finding-F-r5-002.json>)。A10 另保存完整 227 源快照、inputs、实际外层 argv/exit 与 status。

**返回 Development**：将测试合法/非法角色样例按当前实际 dev/qa root 构造，保持跨角色负例的证明力。不得放宽 Manifest 路径/role 安全校验，不得把 QA root 改成 DEV root、改用 DEV role/target、跳过失败测试或降低门槛。修复后形成新精确 source/receipt，再由新的 fresh Verification 独立重建并完成全套必需验证。QA 没有修复任何实现或测试。该 finding 是验证实现/角色适配缺陷，不推断正式 DS runtime 的隔离保护失效。

### 环境 blocker、实际部分结果与未运行边界

本轮第一次 `cua.getState()` 真实返回 `Native apps: Error: The Mac is locked and automatic unlock could not unlock it. Ask the user to unlock the Mac manually before continuing.`；Chrome inventory 可用不代表 native GUI 可用。原始文字持久于 A9/cua-gui-preflight.json，已立即告协调，没有继续尝试解锁、等待900秒、请求 Owner 反复关窗、续开 caffeinate 或修改系统设置。此环境阻塞与 F-r5-002 独立存在；整体 verdict 由已复现的测试 failure 确定为 qa_failed。

未运行 `--suite all`，因为已知 ordinary/native 依赖的 GUI 不可用；独立不依赖 GUI 的正式 core 在上述真实失败处结束。协调随后明确要求停止扩跑，完成材料审计/失败记录并返回。默认 shell 初始化出现 `/bin/ps: Operation not permitted` 的工具输出只作环境限制，未作为本测试失败根因，也没有自动审批拒绝或提权变更。

本次实际通过子项为 logging lib5、apply/receipt5、clock1、configuration_store4、FFI2、layout_naming3、lifecycle 另3，共23。它们按真实独立测试保留，不扩成完整业务/原生/协议结论。

| AC | QA2 状态 | 实际证据 / 未完成面 |
| --- | --- | --- |
| AC1 | partial | 精确批准/交接身份及当前非终态分层已核，未继承旧 verdict。 |
| AC2 | partial | 源/锁/现有 DEV bin 身份、QA core 编译和 FFI/clock 子测已核；新 B0/release/完整预算未运行。 |
| AC3 | not_run | native dispatch/八文件有限性完整技术复核未完成。 |
| AC4 | not_run | W01 三轮。 |
| AC5 | not_run | W02/W09 静默拒写与屏障。 |
| AC6 | not_run | W07 六来源和 wire/CAS。 |
| AC7 | not_run | W03 三轮各100次竞争。 |
| AC8 | not_run | W04 全负例。 |
| AC9 | not_run | W05 STRING8/254完整包。 |
| AC10 | not_run | W06/W08逐item/系统请求。 |
| AC11 | not_run | C01及同窗口C02。 |
| AC12 | not_run | C03/C04期限和真实send阻塞。 |
| AC13 | not_run | C04完整预留/故障/归还。 |
| AC14 | not_run | C05原分母/公平/stop。 |
| AC15 | not_run | QA真实ManagedS7重建/240读取。 |
| AC16 | not_run | D02端点/TSAP/冲突。 |
| AC17 | not_run | W09/X01取消/未知/隔离。 |
| AC18 | not_run | C06原160重连/20启停/3reset。 |
| AC19 | 条件N/A | 同进程无sidecar，X02仅相应分支N/A；native硬崩可波及全部实例，正常退出未豁免。 |
| AC20 | partial | 当前材料/实际命令和失败原件关联已封存；完整运行分母/资源未产生。 |
| AC21 | fail F-r5-002 | fresh/串行角色成立，正式QA core不能完成；完整独立重建/矩阵缺失。 |
| AC22 | partial | 234固定来源及现有候选身份匹配；本轮完整DAA编译闭包/图标呈现未完成。 |
| AC23 | partial | layout/naming消费者3测通过；完整source_import/重导矩阵未运行。 |
| AC24 | partial | 原v1/四layout oracle消费者子测通过；typed完整矩阵未运行。 |
| AC25 | partial | apply/receipt5测通过；原生UI/全部运行状态联合证据未完成。 |
| AC26 | partial | 正式227source/22docs/9DEV bin身份匹配；QA release/DAA/B0未完成。 |
| AC27 | not_run | baseline仍candidate，完整QA未完成。 |
| AC28 | partial；F-r5-001 closed | 五P5紧凑边界/引用通过，旧原件保留；完整原件/资源/运行证据全门未完成。 |
| AC29 | partial | 部分owner/apply/lifecycle合同测试通过；全调用图与wire联合证明未完成。 |
| AC30 | partial | 本次FFI2/clock1真实通过；完整B0/100探针/borrow/join wire未完成。 |
| AC31 | not_run | 本轮N1–N3/正常Window.close未执行，旧成功保留原来源。 |
| AC32 | partial | 原r4 checklist段及旧QA1原字节保护已核；完整退役/clock影响审计未完成。 |
| AC33 | partial | configuration_store4测通过；真实双进程profile锁未运行。 |
| AC34 | partial | store CAS/rollback/unknown/readonly测试通过；完整角色core gate失败。 |
| AC35 | not_run | source_import完整重导/preview组未运行。 |
| AC36 | partial | layout/naming及namespace/region子测通过，完整组未完成。 |
| AC37 | not_run | typed_rules测试和完整五规则组未运行。 |
| AC38 | partial | apply九场景/故障等5测通过；完整矩阵/原生重开未完成。 |
| AC39 | partial | 无端口拓扑边界/线程准入子测通过；K07真实双实例多DB未运行。 |
| AC40 | not_run | 六页八组件/布局/双语主题窄窗native未执行。 |
| AC41 | not_run | 本轮ordinary入口未执行，未搬用QA1或DEV结果。 |
| AC42 | fail F-r5-002；native not_run | 测试manifest正例角色不适配QA；双gate全组/N1–3未完成。 |
| AC43 | partial | logging5及store故障子测通过；完整产品/资源降级联合组未完成。 |
| AC44 | not_run | 只核P5摘要指向原退役map，102成员迁移/清后完整独立核验未完成。 |
| AC45 | fail | F-r5-002未修，完整QA未完成，不能进入Owner最终接受或联合联调放行。 |

K01 not_run（仅来源身份已核）；K02 partial（store4测，跨进程锁未运行）；K03 partial（layout消费者，重导未运行）；K04 partial（layout/naming）；K05 not_run；K06 partial（apply5）；K07 partial（无端口边界，wire未运行）；K08 not_run；K09 fail F-r5-002/原生not_run；K10 partial（F-r5-001关闭、logging5），不作为整组通过。

原 W01–W09、C01–C06（C02必须C01同一窗口）、D01、D02、X01 本轮全部 **not_run**；X02仍仅同进程条件N/A。N1/N2/N3全部 **not_run**；ordinary、完整core、真实双进程锁、QA release/test重建、B0也未完成。原时长/次数/分母/阈值均未改变，没有将未运行项改成deferred或pass。

### 持久证据、资源和最终handoff

| A5子目录 | 本轮原件 | members | inventory SHA-256 |
| --- | --- | --- | --- |
| qa-run-0009 | 新receipt/P5/spec/tasks/旧checklist、身份/端口/实际Mac锁屏起点 | 12 | `f968d46b05f0c7f02ddae73265ea18652794e094a2f584d80e2f52c846887236` |
| qa-run-0010 | 正式core原命令/真实exit/stdout/stderr、227源、实际失败manifest | 233 | `759d21d34612a89e707831da75ab85e0305ac39a08c054674bf6810e5bf90d1f` |
| qa-run-0011 | 首次QA投影helper与真实方法失败 | 2 | `f84f4bc63d1ef2418053d98269206490f05f32e15808d4ba448dffabbecbba45` |
| qa-run-0012 | 最终独立投影helper、结果、原命令exit0 | 3 | `a30ede1f6b6e2f492ad58a9ff945709bb10d1b917dfa451176598114c78d47d8` |
| qa-run-0013 | 精确F-r5-002/相关源、历史/保护/资源/本checklist最终副本 | 以其inventory为准 | 末次封存时生成，不与checklist循环自哈希 |

以上逐成员复制到持久A5并二次SHA/bytes核对，inventory排除自身。最终 receipt 单独存 A5/qa-run-0014/qa-handoff-receipt.json，固定本 checklist SHA及 A9–13 inventories；不修改已封存成员。原件不只依赖临时T5。

core外层tool session56539已实际退出1，内部Cargo退出101；本轮没有创建ordinary/native/preview/协议launcher或listener。core结束后五固定端口再次均无listener。未把缺少全机PID观测说成系统零进程，未运行或清理共享WebKit/XPC。T5 qa stage/cache/build/tmp/profile、失败测试新UUID目录及全部raw保留，供Development返工/new fresh QA/Owner审阅；不删除证据、缓存、SQLite或历史资源。最终清理仍归唯一协调在实际归属/占用/持久原件/后续依赖核准后按授权执行。foreign Tool/Field Flow及共享索引不认领、不恢复、不删除。

**qa_failed / F-r5-002 返回 Development，经唯一协调串行交接。** 修复后重新handoff给新的fresh Verification，必须按精确修后候选独立完成所有仍必需的构建、B0、ordinary/native和适用协议/产品矩阵；本轮没有降低任何要求。Mac解锁由协调按实际后续执行需要处理，QA未自行解锁/延长awake或要求重复人工关窗。独立验证结果交Human Owner作最终决策，**Owner final acceptance pending**；DAA应用S7→SQLite联合验证另批、整体B/C、真实设备/现场、发布部署、跨平台/L1–L5/8×16和Git refs仍不在本次通过事实内。本角色完成最终receipt后停止写入。


## r5 QA3 — 精确修后独立核验与 F-r5-003 失败交接（2026-10-21）

结论：**qa_failed；F-r5-002 closed，F-r5-003 open，Human Owner final acceptance pending。** 本轮为实际新启动的 `verification_r5_complete` fresh context，profile `contract_only`，只写本 checklist；没有修改实现、测试、spec、tasks、锁或 P5。根治理、最近作用域说明、完整 bundle（含历史）、实现及实际输出已独立读取。QA2 的失败和历史结论保留，未把 Development 日志当成本轮执行。使用 project-governance、aiis、rust-runtime、desktop-tauri、frontend-ui、i18n-workflow、plc-point-mapping、backend-arch、code-document-indexer 的适用验证规则，不实施修复。

精确输入：spec `67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419`；tasks `29789c5d157388140da4ab3c455f3f26172a86ca0d546cfe47eb0efc41313624`；Development receipt `948dd8267e7b2d7c4f54a0899d6f93874b0df4b0fa9819d8c6ff6ad752e51d97`；227 源候选 `9f2f4f7c299d93fdb9f2950e4be7979ca43c3ec21f1fd0ea011de9ac06edfd42`。修后唯一源 delta 是 `runtime/tests/lifecycle_protocol.rs` 的实际 role 推导，生产 Manifest 不变。起止逐 SHA 核对 227 源、22 docs、3 locks、9 DEV binaries、5 P5 均零差异。QA 起点原 checklist SHA `6d28825b59be65761a056a783dc73b4bcc44278a69ba1a7a82ab6aadfa1b4b5f`。五 P5 原字节、spec/tasks/receipt/原 checklist 已持久于 A5/qa-run-0015；F-r5-001 保留 QA2 已关闭的历史结论，本轮未宣称重新完成全部材料投影审计。

本轮在 macOS arm64 使用独立 QA cache/stage/target/profile 与锁内依赖，未复用 DEV target/binary。CUA 点时 preflight 原生 42 apps、无 errors 后执行正式入口（cwd=D，D 为绝对工程路径，T5 如上）：

```text
/usr/bin/python3 -B scripts/run_validation.py --project-root /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator --run-root /private/tmp/arch-aw-005-r5-exec --role qa --suite all
```

| 本轮实际 run | 原始执行事实与边界 |
| --- | --- |
| qa-0015/0016 | 独立身份冻结、CUA preflight、精确 source snapshot。A15 inventory `75106b097670fb4a172cd8078ec4ca23d9436e618d5838f5baa221ef8bc319cc`。 |
| qa-0017 ordinary | 真实 `pnpm tauri dev` pass；新 QA debug binary、独立 SQLite v1 与三项真实只读 IPC，运行时 stopped。watcher SIGINT 收尾，明确不作正常 Window.close 证据。 |
| qa-0018 core | `cargo fmt --check` exit0；`cargo test --offline --locked --features native-s7,test-automation --lib --tests` exit0，33 passed、0 ignored。真实双进程锁：owner exit0、第二 owner exit1 为预期拒绝，DB 不变、独占 reopen。**F-r5-002 以 QA-owned 正式运行关闭**；合法/反角色、parent escape、symlink 原断言保留。 |
| qa-0019/0020 | native 独立重建；新 B0 closed（5 headless binaries、ABI、100 clock、退出值 0/37、预算/日志原结果均在 build-manifest 与 commands）。另有普通及验证桌面产物；本表不把构建当 GUI 证明。 |
| qa-0021/0022/0023 | 真原生 N1/N2/N3 各自原始 suite result=pass，steps 分别12/11/7，原生 IPC/SQLite/S7/正常关闭及 WK 原资源原件保留。完整独立资源分母、阈值复算因 F3 停止而未完成，不据此授予全部原生 AC/K/resource 最终 pass。 |
| qa-0025 | K07 实际 pass；A DB71/88/109，B DB94/130；B 连续6次读，真实 cleanup clean/evidence_complete。 |
| qa-0026–0052 | W01–W09 每例3轮，各原 summary pass 且 cleanup clean/evidence_complete；各轮命令、wire、events、资源与 inventory 独立持久。 |
| qa-0053 | C01 已启动，发现 F3 后行政中断；C01/C02 **incomplete**，无成功 summary/正常终结证明，不计 pass。 |
| qa-0054 | F3 helper 源码/二进制/真实链接与运行命令、stdout/stderr、SQLite 原件与8份不可变保存 revision、输入止点 SHA、实际停止/资源证据及本轮 run 索引。 |

**F-r5-003（open，产品实现 failure）**：spec §3.3（当前 spec:123）、R23/K03、AC35 要求 DB 号变化使受影响点的初值/策略确认失效。独立 helper 仅链接本轮 QA core 已构建的冻结 runtime/serde/native，经过真实 `Manifest::read` 和 `App`/ConfigurationService/SQLite/import/layout/naming/compile/apply 调用链：先完整确认并 apply DB71，再以完全相同源字节及 lineage、相同 DB/point UUID，只将绑定号改为72。重导后只重新确认地址和名称，**没有再提交 confirm_points**；旧 initial/policy confirmation 仍保留，compile 接受，真实 apply 返回 `committed=true, receiptState=known, result=loaded`，真实 Rust owner DB 列表 `[72]`。helper 未启动监听，`shutdownJoined=true`。这不是仅据局部代码推断，也不是 DAA 应用到 DS SQLite 联调。

最小调用链：`runtime/src/services/source_import.rs:223–276` 克隆同路径旧 point，仅类型变动重置 point confirmations；DB address/names proof 会清除。`runtime/src/services/configuration.rs:57–145` 及 `runtime/src/domain/layout.rs:90–99,295–303` 的初值/策略签名不含 DB 号/地址，故旧确认通过；真实 apply 继续接受并加载。完整 helper、原命令 exit0/stdout/stderr 与不可变 revision 字节可复查，动态复现仅覆盖 DB71→72；地址/长度/改名/结构/类型其它变体本轮没有追加运行，不将其推断成动态已证失败。

A54 finding `finding.json`；helper SHA `ad89cefa28512bb6a3d90865507d36acd958557790dd97e9cf13ea9204b7ae27`，helper binary `ae9c6414b59b6e5c887e61710f9039b96227f9478bf784de92e08b3a3028f5aa`，实际 QA runtime rlib `72c9e7ecfd5a37627d97b119b53d55603d1c01760ce916bdcab450e8c45edce2`，对应 native `4390c038d324b9f0facc40ba203b91093a69134c3777c1ea99f74c88ba9e0869`。A54 25成员 inventory `9519a9bb72fb684a43142b8593a4653c0ec5be7c3ff22e53484a2bc0a144266e`。封存辅助首次误按列表读 receipt.binaries 而 exit1 的历史也如实保留；按真实 dict schema 只修正收尾读取后完成，不修改冻结脚本或测试。

未完成边界：45 AC / K01–K10 / 原19 case **整体未通过**；AC35 失败，AC36 相关确认/apply 门槛受影响，其余只保留上述已运行范围，不继承旧 DEV 或 QA 的 pass。C01/C02 interrupted；C03–C06、D01/D02、X01/X02 本轮 not_run（不把 X02 未执行写成已确认 NA）。完整产品矩阵、原生资源复算及其它未复核项继续 incomplete。原生/六页自动场景已真实运行，未因本发现重做 UI 或新增功能。DAA–DS SQLite 联调另批，Stage C、真实设备、部署发布、Git refs 均未开展；未发送邮件或对外消息。

收尾：先核精确 argv，再暂停 aggregate 防止进入后续项，之后只对自有当前 C01 PID24945 与 aggregate PID15255 发 SIGINT，并 SIGCONT aggregate；tool session90919 实际 exit130（KeyboardInterrupt），不伪装成正常关窗或原套件退出成功。原 C01 summary/cleanup 缺失如实保留，行政说明独立写入，不补造。最终独立 ps 未见本轮自有 DS/test/reference/launcher，五固定端口30102/30103/30104/15194/14194 的 lsof 均 exit1、stdout/stderr空；没有杀外来 PID、延长 caffeinate、改系统设置或要求 Owner 重复关窗。T5 自有 cache/stage/target/profile/helper/raw 与 WK 独立 store 保留，供必要返工与证据依赖；不删除 G0、数据库、缓存或原件，不触碰并行变化。

A15–A54 均已持久封存，逐成员 inventory 排除自身；最终 A5/qa-run-0055/qa-handoff-receipt.json 固定本 checklist SHA 与完整 A15–54 inventory/成员索引，无自哈希循环。本轮唯一项目写入为此 checklist 的头部交接/当前结论及追加 QA3；r4、QA1、QA2 历史正文保留。**返回实际 Development 作原 r5 最小修复，经唯一 coordinator 串行交接；Verification 不修实现，不授予 Owner 最终验收。最终 receipt 后停止写入。**


## r5 QA4 — 最终独立核验（2026-10-21）

**qa_passed；F-r5-003 closed；Human Owner final acceptance pending。** 实际 fresh-context `verification_r5_acceptance` 独立读取治理、完整 bundle、正式实现/diff/原始输出，按适用 shared skills 只验证。此次唯一项目写入为本 checklist；未修改实现、测试、spec、tasks、锁、P5 或配置，没有新增验证矩阵。此前 QA1–3、r4 与 Owner 人工三窗原文保留；本结论不搬用 DEV 或旧 QA 的执行结果。

精确输入：spec `67155fe4fca3068ef8e616dcf0ade69a5cdc614e7175a2f1ef4c6bf98f935419`；tasks `bc063bb940787f5aefc52db58235fd55a56046b69c3b20de374b583c85edb854`；DEV receipt `b58bbe2b65bb515337996a3923ef6a9b19588a99a517a1fe1577a6111088a48e`；正式 227-source candidate `306a09d5317931482a59f45da5eafcb9d3ee739199799f475ade1891fb0b00b4`。相对 QA3 仅 configuration service 与 source_import 回归测试两源变化；225 其它源、22 docs、3 locks、234 固定输入原字节保持。QA 起止核对零差异，五 P5 原字节固定于 A5/qa-run-0057/P5，未被本轮改写；其既有 QA3 状态待协调在本 handoff 后同步。当前旧 checklist SHA `b1d6d7c4a1081c7a2f06691c5a007e03b4029e6b0740206dab84d6dd4abcfa0d` 与 QA3 历史原件保护。

正式入口（cwd=D；D/T5/A5 沿用上文绝对路径），从同一正式源码以 QA 自有 cache/stage/target/profile 重建；没有使用 DEV binary/target：

```text
/usr/bin/python3 -B scripts/run_validation.py --project-root /Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/device-simulator --run-root /private/tmp/arch-aw-005-r5-exec --role qa --suite all
```

首次 aggregate qa-0058 / ordinary qa-0059 遇实际锁屏、缺三 IPC，行政 SIGINT 后 exit1，原件保留且不计 pass。经 Owner 一次解锁及本轮最多60分钟 awake 授权、实际 CUA 新 preflight 后，按同入口分别 `--suite core`、`--suite build`、`--suite native`、`--suite protocol` 完成尚欠阶段；各正式阶段外层 exit0，未重复已完成项或改变原断言/次数/时长/阈值。默认 ps 的 EPERM 采用精确已授权升级；未因锁屏修改产品。

| 实际 QA run | 结果及证据 |
| --- | --- |
| 0060 core | fmt exit0；offline/locked Cargo native-s7,test-automation lib/tests exit0，34 passed、0 failed/ignored；真实双进程同 profile 锁争用，第二 owner 预期 exit1、原 DB 不变、独占 reopen。 |
| 0061 ordinary | 实际 `pnpm tauri dev`、native default、清 DS_G0_*、新空 SQLite v1/appID/7表及 bootstrap/configuration/snapshot 三 IPC；默认 stopped、无 listener。watcher SIGINT 收尾不作为 Window.close 证明。 |
| 0062 / 0064 | 独立 product/test desktop 与 headless/native/真实 ManagedS7 重建；B0 closed 后才监听。非 test 产品拒测试参数 exit2 为预期。九新产物完整路径/SHA/bytes 见 A108/audit/qa-output-nine.json。 |
| 0065 N1 / 0066 N2 / 0067 N3 | 各 pass、进程 exit0，真实 native DOM/IPC/SQLite、保存重开、启停和值、真实 Window.close；steps 12/11/7，normal close 63.045/108.462/83.850ms，均远小于5s。无行政中断/残留/锁占用。 |
| 0063 F3 独立实证 | QA 自编 helper 仅链接本次 QA 固定库；真实 Manifest→App→SQLite/import/layout/naming/compile/apply/owner，反例阻断、确认后成功、历史 revision 回滚成功，退出0并 joined；没有监听。 |
| 0068 / 0069–0107 | protocol aggregate exit0；K07 pass；原19 case 全部判定完成（X02 条件 N/A），确定性向量及 X01 各3轮，C02 与 C01 同窗口；详下表。 |

F3 修复独立闭合：DB71 完整确认并 apply 后，相同源字节/lineage/DB 与 point UUID 仅改 DB72，旧初值/策略的候选值保留而确认失效，preview 零持久写；仅重确认布局/名称且**未调用 confirm_points** 时，compile 报 initial_unconfirmed/policy_unconfirmed，真实 apply 拒绝 configuration_blocked，owner 仍 `[71]`。显式确认初值/策略后实际 committed/known/loaded、owner `[72]`；当前 draft 仍72时加载不可变历史71版合法回滚、owner `[71]`，不错误用当前 draft 取消历史确认。A63 保存 helper 源/命令/二进制、SQLite 与9份 revision 原字节；34测另覆盖长度/地址/结构失效、未改 DB/显示兼容。独立调用图审核确认每 DB 物理上下文只比较一次，正常 prepare/实际 import/layout preview 取消受影响确认，历史 apply 编译独立保存版；没有 schema/UI/API 绕过或额外框架。

B0/架构结论：Rust 保持唯一 image/规则/CAS/配置 owner；Snap7 仅8个受控 IO/lifecycle 源改动，34个其它上游源原字节保持。C↔Rust 实际 int0/37、Tag20/align1/offset0/4/8/12/16、callback104/align8、同步 borrow/Arc 与真实 pthread/Rust join、100个同 CLOCK_MONOTONIC 夹点成立；连接18420B、native fixed66592B、Q2208B 与原预算闭合。DAA196派生、5图标、shared core0.1.0/v1、5真实 ManagedS7 模块及 feature/local-validation 边界保持；没有 DAA app 运行或 SQLite 联调。22 docs/146局部链接、双语键/插值/调用、既有布局/几何等待与 bounded UTF8 错误回传检查通过。

| 原 case | 本轮独立结果与 run |
| --- | --- |
| W01 / W02 / W03 | pass：0070–72 / 0073–75 / 0076–78；W03 每轮100次同 byte 竞争。 |
| W04 / W05 / W06 | pass：0079–81 / 0082–84 / 0085–87。 |
| W07 / W08 / W09 | pass：0088–90 / 0091–93 / 0094–96。 |
| C01 / C02 | pass：0097，同一16会话窗口；30s warm +300s measure、9600/9600请求、345600B、额外20次拒绝不抢占。 |
| C03 | pass：0098，55.939s；H限额、绝对握手/半 frame 期限各3次及30s idle。 |
| C04 | pass：0099，19.566s；三层 reservation、队列边界与真实 send 阻塞；首次发送至同连接 join 2.004109s。SO实际≤16KiB，304 offered 至真实关闭，原最多30s/600次未改。 |
| C05 | pass：0100，77.566s；60s正常段 F1200 PDU/4800items、A120/B120/UI60全部完成，逐类/逐连接 RR 与3次积压 stop/恢复。 |
| C06 | pass：0101，224.588s；160重连、20启停×stop后10s、3reset；transport/callback/worker/timer/queue/reserve归零与重绑。 |
| D01 | pass：0102，61.844s；真实 ManagedS7 两模块共240次 db_read、marker与修改值匹配，原 RemotePort/TSAP。 |
| D02 | pass：0103；错 TSAP/空口/误指另一实例各3次、冲突/重复 start，B继续、无扫描或回退102。 |
| X01 / X02 | X01 pass：0104/0105/0106，正常/故障 stop/单close及B隔离；X02 0107 实际判定 not_applicable：同进程无 sidecar，native 硬崩可能影响两实例，不宣称崩溃隔离。 |

原件独立复算：420791条 stdout/file JSON 逐值同序、15079个真实 S7 ACK 解码、284个完整1088B image、100对拒绝前后 bytes/hash/seq/metadata 不变。C01 每连接最大 p95=1.30342ms/p99=4.76187ms，queue p99=.928ms，24000规则到期/0missed；299个核心采样，平均单核CPU8.987%、RSS峰20152320B/净增−212992B、线程26/句柄87，原100%/512MiB/64/1024及净增16MiB阈值不变。C06 stopped B0 RSS17121280B，末5中位数−首5=1212416B，小于8MiB且各次≤B0+16MiB。完整 offered/拒绝/超时分母、逐连接分位数、RR与1Hz进程资源原件见 A108/audit/protocol-independent-audit.json；短命 CPU 不可评估项保持 null，不记0。

原生资源独立结论：只读固定 test-only WK getter 在主线程借用真实 WKView，无任意 selector；实际 WebContent/GPU PID、owned storeUUID Networking 与 POSIX 后代取并集去重。N1/N2/N3 各组件有效采样31/11/5，采样错误与 terminalUnavailable 均0；真实 close 后实际 host code0、所有所属 WK PID 精确 ps exit1 全空及 SQLite 独占 reopen。主进程 RSS峰96370688/100171776/98729984B，WebContent/GPU/Networking 各峰单列 A108/audit/native-resource-peaks.json；没有相加为同时峰值，也不套 C01 headless512MiB阈值。终端 ESRCH 规则仍要求正常 close→desktop_exit→host code0≤100ms→精确 ps exit1 全空，未吞错误伪0。

45项验收按当前原 spec 判定均 **pass**（AC19 的 X02 以原条件 N/A 满足；Owner接受仍待定），证据映射如下；每项内容仍以 spec 原文为准，无删减原门槛：

| AC | 当前独立证据 |
| --- | --- |
| AC01 / AC02 / AC03 | 精确审批/历史冻结 A57；QA own normal/build/B0 A60–64；8受控 native 与 int/ABI 审查 A108。 |
| AC04 / AC05 / AC06 | W01、W02/W09、W07三轮及 core owner/typed/apply/真实 UI；完整 image 与唯一 commit 复算。 |
| AC07 / AC08 / AC09 | W03×100×3；W04全负例；W05 STRING8/254 原包，均真实 ACK/不变 image。 |
| AC10 / AC11 / AC12 | W06/W08部分成功与拒绝；C01/C02同窗口；C03/C04真实期限与释放。 |
| AC13 / AC14 / AC15 | C04全阶段 reservation/实际阻塞；C05逐项RR/低频完成；D01真实240次 ManagedS7。 |
| AC16 / AC17 / AC18 | D02原负例；W09/X01取消/未知/单close；C06完整次数/10s采样与趋势。 |
| AC19 / AC20 / AC21 | X02条件 N/A/硬崩边界；A69–107全 raw 与 A108复算；fresh QA 与 Owner 分层。 |
| AC22 / AC23 / AC24 | 234 pins/DAA196/5模块/core固定；source_import与F3；layout/naming/typed黄金断言。 |
| AC25 / AC26 / AC27 | apply九场景/真实SQLite/重开与owner；正式源与9新产物；协议 baseline仍candidate/联调排除。 |
| AC28 / AC29 / AC30 | 五紧凑P5引用/持久raw/失败史；唯一owner调用图+core/wire；新ABI/100clock/borrow/join。 |
| AC31 / AC32 / AC33 | 新ordinary/N1–3真实 close；r4历史/G0原件及clock；新空SQLite/真实跨进程锁/坏库失败。 |
| AC34 / AC35 / AC36 | SQLite CAS/immutable/未知/只读；重导/core/F3关闭；手工DB/点/完整布局/命名/阻apply。 |
| AC37 / AC38 / AC39 | typed/5规则与W07；apply故障/保值/回滚+N重开；K07非41/57双实例多DB及8/32/4096/64KiB边界。 |
| AC40 / AC41 / AC42 | N1–3六页DOM→IPC→SQLite/owner/双语主题窄窗；ordinary默认入口；test双gate/产品拒测试参数。 |
| AC43 / AC44 / AC45 | logging降级5测与B0压力/SQL故障；102旧G0原件及135迁移引用/清后正式重建回归；本handoff与边界/保留项。 |

K01–K10 均 **pass**：K01=A61/62/64+派生pin；K02=A60真实SQLite/跨进程锁；K03=A60 source_import+A63 F3；K04=A60 layout/naming+N；K05=A60 typed_rules+W07；K06=A60 apply+N+A63历史回滚；K07=A69真实A71/88/109与B94/130隔离及B连续6读+core容量边界；K08=A65–67全部真实DOM/IPC场景；K09=A62非test/双gate与A65–67保存重开/正常退出；K10=A60/B0 logging+A108原件/P5/退役审查。不存在待补必需 case 或新的产品 finding。

持久封存：A56 方法失败、A57精确输入、A58/59锁屏中断、A60–107全部本轮原命令/真实exit/bytes/SQLite/resources、A108独立审查/helper及方法修正历史均保留，inventory排除自身。A57 inventory `66bbebd4e1243b465f9a80890a50353420a9ab08ff45b0d1ec971d55831db200`；A63 21成员 `1ad9bd50ac23af0b3fee9f372bfcb596fc9a12ad6f19428ee4510cfedcc5a40c`；A108 26成员 `6325640198948ee8619d3f6d4207c40dbc089a21ea38772dfc5c4256b0496a5c`。最终 A5/qa-run-0109/qa-handoff-receipt.json 固定本 checklist SHA、A56–108 inventories、全部9个QA产物身份、五P5输入SHA与资源事实；A109含本 checklist 最终副本及 coordinator-origin awake授权/启动/撤销/关联stderr原件，避免自哈希循环。首次 freeze/独立解码/动态i18n前缀等 QA helper 方法错误均保留原件，仅修私有 helper，没有更改项目方法、测试或判据。

失败史与限制：DEV N285 同源/同binary几何20s等待超时、TERM收尾的失败仍完整保留，N286为未改源码/driver/阈值的单次重试成功，根因未知；本轮 QA 三个 N 全通过，不将 DEV 写成连续无失败或已证瞬态。G0已退役102路径的原件1635298B与迁移闭合核对通过，不再次删除。默认数据目录只有 API/解析事实；实际原生使用新 owned profile，未触真实默认用户库。macOS15.7.7 arm64/Mac16,12，10核/32GiB；Rust1.89/Node22.19/pnpm11.11与锁固定。没有跨平台、完整L1–L5/8×16长负载、真实PLC/DAA app→SQLite/阶段C/发布部署或Git refs能力声明。

所有实际测试结束后已立即通知协调；协调按 Owner 授权核完整 PID/argv/lstart 后精确撤销本轮 awake，随后 ps exit1 全空；这是 **coordinator-origin** 事实，未捕获子进程退出码，不宣称 exit0，QA未再启动awake。QA于10:23:44UTC的最终实际观察：自有 DS/test/launcher匹配为空，30102/30103/30104/15194/14194逐口 lsof exit1且 stdout/stderr空；原生每轮真实正常 close/DB释放另有原件。QA own stage/cache/targets/profiles/SQLite/WK stores/raw全部保留供协调按实际依赖收尾，未杀外来进程或删除资源。foreign Tool/共享并发变化保留且不归因本任务。**本轮 qa_passed 交 Human Owner 最终验收，Owner final acceptance pending；最终 receipt 封存后停止所有写入。**
