Task ID: DAA-002
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA4 independently closes F-004 on the exact documentation-only r2 handoff; unchanged code, binary and original functional/native evidence are verified by source hashes and raw attachments; hand only to Human Owner final acceptance through coordinator; no Stage C or external action authorized
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-002 r2 第四轮独立核验

## QA4-1. 当前结论与独立性

2026-10-18（Asia/Shanghai），当前独立 verdict 为 **qa_passed**，F-004 已解除，当前无阻断项。通过只覆盖已批准的 DAA-002 r2 受控阶段 B。Human Owner final acceptance **pending**；其此前原生操作回执属于 R19 的实际观察，不能当作终验。本轮不授权阶段 C、Backend/SMA/DS 实施或联调、现场、部署或发布。

实际 Verification 为 `/root/daa_stage_b_r2_verification_4`，唯一 active lifecycle coordinator 为 `/root`。本角色在最新正式 `developer_handoff` 后，以实际 `agent_type=verification`、`fork_turns="none"` 调入全新 context，未继承 Development 的对话推理。独立完整读取根 AGENTS、README/PLAN 双语、canonical workflow、实际 `.codex/agents/verification.toml`，AW/DAA 最近 README/PLAN、app/local_store 说明，以及完整 spec/tasks/QA3（内含 QA2/QA1）、当前差异、必要源码和原始输出。作用域无更近 AGENTS。TOML 的 `gpt-6.1-sol / max` 仅是配置证据；profile 为 `contract_only`，不宣称额外运行遥测、平台 ACL、强制路由或团队激活。

本轮使用 `project-governance`、`code-document-indexer` 核治理/文档配对，按实际源码核对加载 `rust-runtime`、`aiis` 的 BLUEPRINT/CONTRACTS 和运行日志基线。增量只有既有中文说明和 Development 事实记录；未重审未变的 UI/解析/驱动设计或扩大开发表面。仓内仅更新本 checklist；未改 spec/tasks、产品、测试、配置、依赖、CODE_INDEX 或 10 个 coordinator 索引。辅助审计及证据只写自有临时 Q。

旧 QA3 全字节先保存，SHA-256 为 `7cb06996795ff4be3ca4e23ef05e4a4b5a0cd7c3504ee104fbc19c5b7f8c3be7`；本文末完整嵌入，可重建其原 SHA，内部 QA2/QA1 原文也未动。QA1 的 F-001/F-002、QA2 的 F-003、QA3 的 F-004 均仍是各自当时真实的失败，不改写过去。

## QA4-2. 精确输入、完整差异和保护审计

E=`/private/tmp/daa-002-r2-gnwbdg79`；Q=`E/verification4-r2-8tl4shpu`；本轮唯一最新 H=`E/dev/rework-qa3-20261018/final-handoff`。H 为待验证输入，coordinator gate/索引 receipt 仅作来源证据，不作 QA verdict。

| 输入 | QA4 实际核验 |
| --- | --- |
| 批准对象 / HEAD | `aiis-ics-arch::DAA-002 r2`；HEAD `f85bea8bbf36b491968c3dc9a839518a1ed434a8` 保持 |
| 批准 spec | SHA-256 `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a`，20 AC、B0 先行及 R19 原生义务未降低 |
| 当前 tasks | §13/14 `developer_handoff`；SHA-256 `d5847fb57ded32e2419e508d0c47e74ccd3f06a11e7e8e920b19fa5e704a69a6`；DEV 已正式停止写入 |
| H receipt / development manifest | `d607066f96d62b70308c4cdc8ab67662e05671d0480aabe9227e3287793acbe5` / `d8351c25be67114c738d0c927e608d73b7f1a542e222666131d2024566a445d9` |
| 初始完整 diff | 从原始 before 独立重建 626484 字节，SHA-256 `bb667d30e559f0627837fbed21be555683f392db2e89ffb12e3c8a05da41f8d5`，精确匹配 H；78 实际变化、44 新增全文 |
| QA3 至当前两路径 diff | 独立重建 12406 字节，SHA-256 `b913ab6823976fe68147e70d21e87d3134adbb55f914b3467d09ca69937caa7a`；仅 local_store 中文 README + tasks，其余 86 个 DEV 路径不变 |
| 88 文件与副本 | 当前 / 初始 before / H source / QA3-before88 逐项核；all88 aggregate `f6e0409d6e7b5bc6594fa5d254a376ec66c1058b451c5cbb2209cd4a23dc795c` |
| 当前 product87 | aggregate `6739012bd9b81168f8e6dd0d91a7482896c41096b87739ec5c1db8dd443b8dfa`；相对 QA3 只有中文说明变化，非新编译来源声明 |
| 局部说明 pair | 英文 SHA `26c94a601118b8291e8c20f670e3e709f0b3dfb927fc9b8e5ac3edce46271ff0` 保持；中文 SHA `c77d9dd663ed91338c9bc16871094bc863d7e5b3a71cc57811fb80941b9c025b` |
| 未变前端与原生 binary | 57 文件 aggregate `1aef27f7f62495e6e59548f791a25039f6bab80f66399c524afcf366fa9e39c5`；独立 `.app/Contents/MacOS/runtime` SHA `9798b8e128c40c82d6dcd30f51be914086304bb56fd8f3238d02f1cf0e17c2ca`，均逐项核，没有新构建 |
| 历史源码 seal | `5510ff23468b049de4b51bc3cf32bf6ec67b838eb8c0b65da82c936465fc3a41` 保留；它是当时业务源码加文档的集合，不能要求它等于现中文修正后的 aggregate，也不冒称新 binary 来源 |
| QA3 及原始附件 | QA3 manifest SHA `e6c63c7edaf234b77828c49c85a4c92c78839a4e4931a54ec8d12e7eb5ec06af`；168 附件、1336 个旧不可变字节引用全部匹配。H evidence manifest `fddeae8d141362f867abbffce95e198cd8263a717429ee2708e44e953b68e7f9` 的 95 新 + 9 prior，共 104 直接附件逐项匹配 |
| 原文历史 | r1 tasks `7ffdc1600534efe4605ff7a022d9c8bc16a7f68d19748ccb0590cff759d607ef`；QA2 `0ce5221365f7ea4e1f9650f9e3d8052892a2741a7ae96df4c6afd688e88b1f20`；QA1 `8d8112aa26dfef4a5d616e385c8346300182fb08f451679f6711a0930018be4b`，均从嵌入标记独立重建 |
| 保护面 | 1552 个其他原保护文件保持；12 个外来 AW002/DS 文档逐项匹配 temporal seal `3e51200ab13df5a40f6135293591f501a1c25c061dc37b1e17cd1784f1516aa9`（7 旧 + 5 新），单列他任务来源、不认领/回退 |
| 共享索引 / baseline | 四共享根索引过滤 DAA002/AW002/AW004/AW005 行后其他原字节相同；初始 baseline、allowlist、audit-scope.py 保持。10 索引归 coordinator，本 QA 不写 |

原始 `E/audit-scope.py Q/raw-initial-scope.json` 实际 **exit1**：99 总差异中，12 outside 恰为上述已归属外来文档；HEAD 未变。不能将 raw 全局结果写成 exit0。QA4 独立归属审计没有未知越界，没有重 baseline 或扩 allowlist。

coordinator documentation-handoff-gate SHA `09cf4cd64cf1bb9850e15b4cd7847d8ab47f29c48412664ea75d12bfd4ec525a`、机械索引 receipt SHA `0e7d9de717864de7d5643fa11a4d13d59c657f60d537a4f3515fab8e0db30ac3` 及首次旧字段 `KeyError: 'allNewImmutableAttachments'` / exit1 的观察均保留。该 helper 失败没有索引写入或 QA dispatch，其后按实际字段重核；不抹去、不当产品故障。本 QA 初次元数据概览也曾把 list 型 allowlist 当 dict，得到 `AttributeError` / exit1，随后按实际形状读取；只读错误无产品或 profile 变更，记录在 Q/initial-read-helper-error.json。

## QA4-3. F-004 的独立解除依据

适用 [code-document-indexer 配对规则](/Users/jason/Desktop/DreamCode/AI/AIIS/skills/code-document-indexer/SKILL.md:34) 要求同一任务同步既有中英文工程说明，本任务无单语临时例外。本轮完整对读两版正文，并逐项追踪相关代码/原始行为，未把 18 个锚点或 DEV pass 作为充分证据。

- 中文现明确区分：普通存储故障由有界写健康探针与容量健康恢复；日志持久化失败锁存 `log_io_unknown_interval`，修复日志后还须重启。`local_logging.rs` 的 AtomicBool 只在失败置位，health 不自行清除；新 LocalLog 在重启创建。`local_supervisor.rs` 的普通 probe 不能越过该日志 health gate。
- `runtime.rs::cleanup_acknowledged` 对每个完整/ACK/无引用候选，在 DELETE 事务前调用 `admit_maintenance`；后者重读 `capacity` 的主库/journal/config/log/free/旧页界限/全部在途及维护系统预留。`maintain` 在 cleanup 后另调 `reclaim_incremental`，它独立重核再开 `incremental_vacuum(64)` 事务。预算不足延期；先前已提交 cleanup 与后续 vacuum 不被称作整体原子。最多 8 候选 / 64 页，busy/失败 drop 或 rollback；不删 pending。
- `Stores::open` 创建一个 Arc<LocalLog>，StoreHandle 与 Engine clone 同对象；logger 自有 mutex 串行轮转。真实 60 秒 worker 分支直接写其产品日志，未递归 storage.call。稳定 event/process/resource/result/error_code 同时进入 bounded JSONL 与 stdout，只有 append/flush 成功才标 persistence=persisted。日志失败报告 unknown_interval，不能伪造精确起始或用日志代账本。
- `StoreHandle::call(false)`、新轮准入及 worker 维护入口检查日志健康；中文“停止新增写入”指新增准入，不宣称已准入在途和正常关闭协议所有物理写绝对归零。history/config/capacity 仍走 query；Stop/disconnect 走允许的停止分支；shutdown 停 actor 再收 writer。快照和日志查询真实反馈故障。
- QA3 原 stdout/结果中，periodic 3 项、busy 1 项、rotation/context 1 项、保护引用 1 项共 6 项通过。实际产品日志覆盖 cleanup 前拒绝、cleanup 后 vacuum 拒绝、共享读锁 busy、RLIMIT_FSIZE 引发 SQLite IOERR；日志路径冲突产生 unknown_interval，历史/Stop/shutdown 完成。测试源码还明确恢复空间并再推进 61 秒后，查询仍不能重启维护。disconnect 的可用性按同停止分支源码核，不冒称本轮另做已连接 PLC 断连实验。这些是原始行为证据，本轮没有重跑。

中文未改段落的前缀与 SQLite 适用性/硬件限制后缀保持原字节；双库、身份/模式拒绝、激活、原始编码/context、全部容量数字、私有测试 hook 和 ACK 的构建边界与英文一致。2 个本地任务链接存在；两版各 **4 个**官方 URL 顺序/目标一一相同。本轮只核配对及既有来源，不宣称重新联网核验远端可用性或当前 SQLite 发布状态。

**非阻断观察 D-001：** tasks §14 写“five official reference URLs”，实际两版均为 4 个，DEV receipt 的 selfCheck 字段也正确记录 4。没有缺失链接、引用或恢复语义；本 checklist 按实际 4 记录，保留 DEV 原句，不代写 tasks。此计数笔误不改变 F-004 解除条件或 AC20 的实质满足。

## QA4-4. 实际检查、原始证据和本轮未执行项

| QA4 命令 / 核验 | 实际结果与证据 |
| --- | --- |
| `python3 Q/audit-inputs.py` | exit0；完整/增量 patch 独立重建、88 当前与 before/H-source/QA3-source、57 前端/binary、104/168/1336 附件和保护归属，见 input-audit.json 及 input-source/ |
| `python3 E/audit-scope.py Q/raw-initial-scope.json` | exit1；99 差异 / 12 已归属 outside，HEAD 保持；未伪记全局0 |
| `python3 Q/audit-document-and-raw.py` | exit0；完整 pair/18 语义定位及代码控制流、2 local links/4 official URLs、QA3 原输出和冻结 JSON 对账，见 document-and-raw-audit.json；不是产品测试或 live SQL |
| 完整原始行为来源消费 | 已核原 r2 B0 五阶段实际输出、QA2 20 项 stdout 及 4 维护 IOERR/有效 hot journal 恢复、5 激活与 COMMIT 前后轨迹、实际 Snap7 单 client/自定义端口/断连/黑洞/慢读、9 parser 反例、默认/factory/actual release 拒绝、11 历史 + 6 保存函数结果。当前相关源 hash 保持，各原命令/环境/退出码/限制仍归其原执行轮 |
| QA3 静态/构建原输出 | default all-targets、fmt、前端 vue-tsc/Vite 原命令均 exit0，既有 PURE/chunk warning 保留；当前业务/前端字节相同，本轮未重新执行这些命令 |
| checklist/仓库收尾 | Q/closeout.py 只核唯一 checklist 增量、原文重建、输入/保护/HEAD/两版链接与空白；结果和实际退出码封存 closeout-audit.json / verification-manifest.json |

本轮 helper 使用系统 Python 标准库，仅作文件/JSON/hash/文本审计；实际版本和平台记录于 document-and-raw-audit.json。此前功能环境是原始输出中的 macOS15.7.7/24G720、Cargo/rustc1.89.0、pnpm11.11.0，不冒称本轮重跑该工具链验证。没有安装依赖、编译/重建 binary、新 Rust/前端测试、PLC/Snap7 测试、SQL/数据库操作、native/窗口/preview/browser 动作，也没有新 Owner 操作请求。

原生证据本轮仅读不可变 JSON/源码/回执：QA3 frozen snapshot 与最终 Owner / 14:49 新 binary 重开 snapshot 全表相同；从原 sample/manifest/context 字节重新算 SHA，并从已封 transport 夹具大端另解码 **912 个 good 点值**。76 cycle / 76 sample / 76 pending，Test 保留零样本，3 PLC / 24 点，source next=27/51/1，active=used=`add0b620-ebce-4451-a2fa-8c9b7dc83de3`，fingerprint=`e4cd3c37c08643ff353a1c6e3e9bc95299d2d903b7dff28e0b77fdcb65678f1f`。原 closed snapshot 实际 clean_exit=1，再启动只增加事件88 clean-stop / 89 stopped-start；原题干及 Owner“新版停采、Test PLC、历史和详情均正常” relay SHA `0d2567544d0291c763ee88c4710247f156b81474c97879ec8652aadc8227f482` 对应最终9798binary。没有新读 live profile，也没有把 SQL/JSON 当作进程内 connected/desired 实态；可见状态仍归真实 Owner 回执。

旧 §9.3 错误零字节 env 断言/exit1后编排未分支继续、当时缺直接间隙 SQL snapshot，及旧窗口可能自动两 locale HMR 无轨迹，全部保持真实历史。新 278 字节 env/strict helper/closed clean1 只属于后一次真实新源链，不能补造旧事实。首次 F003 compiler101、helper 子 exit 传播修正、默认 cache 写拒绝后的内存解析替代、未启动 candidate、getApp 两次长挂、Codex AX 安全拒绝、49192 自动审核拒绝及未重试/未绕过也均保留。

## QA4-5. 当前 AC01–AC20 映射

以下“通过”只覆盖精确已批受控 B。本轮实际新增验证是文档/来源/差异/冻结附件；AC01–AC19 的未变能力结合当前源 hash 与原始行为/原生链独立核用，**不是本轮 rerun，也不是直接复制前三轮 verdict**。

| AC | QA4 当前结果 | 可核依据与限制 |
| --- | --- | --- |
| AC01 | 通过 | 批准 SHA/B0先行、完整初始及两路径 diff、88 before/current/H-source/r1/QA1–3 原文，1552+12 保护归属；未继承 A/CU 验收 |
| AC02 | 通过 | 未变 bootstrap/模式/旧 IPC/headless guards/profile锁/factory 原源码与拒绝输出；默认 legacy，local 显式门禁，唯一 owner 不调旧 health |
| AC03 | 通过（限定） | 新 r2 B0 实际五阶段：3.46.0/unix/两连接 DELETE/EXTRA3、锁1045ms/interrupt104ms/605752B journal/-9及IOERR778后4/8/8/seq4；旧锁/实际SQL来源未变，不以 r1 WAL probe 代证 |
| AC04 | 通过 | 未变双库身份/schema/WAL/丢库拒绝、短读队列/deadline/join/串行写；原20项结果与后续 busy 回滚/读写推进原证据 |
| AC05 | 通过 | 当前 CAS/derived proof 源码不变，原公开保存/import/确认和 Owner 保存/重读/重开同 ID/ETag 链；Test保留 |
| AC06 | 通过 | parser/full-tree 源未变，flat/nested/数组 golden、9个 file/line/path 拒绝原输出；不冒称全 TIA 编译 |
| AC07 | 通过 | offset/decode/golden 原源及反例，Owner manual0.0/确认/非人工保护链；冻结JSON912点从原fixture另解码，非现场地址校核 |
| AC08 | 通过 | 服务端周期/规模/跨DB/单点单组/跨PLC拒绝源码及原用例不变；native 3PLC/24点、两组1000/500、Test无组零样本 |
| AC09 | 通过 | 当前 token屏障/recovery 源码，5个激活 SIGABRT 原输出/live previous/used 测试；冻结双库两token/context/active-used一致 |
| AC10 | 通过 | actor/共享诊断/endpoint唯一和 managed S7 源未变；真实原 single-client/自定义56032、56034/断连/黑洞499ms、慢读剩400实际200ms；不是DS成品或硬件证据 |
| AC11 | 通过 | 未变公平/非重入/独立周期/deadline/跳tick源与原测试；两PLC26/50轮及暂停稳定链，限额不当现场吞吐 |
| AC12 | 通过 | 全成员/manifest/seq/pending同事务源，原 COMMIT前0/后2pending、有效58880B hotjournal SIGKILL后原4样本保持；无半轮，非断电证明 |
| AC13 | 通过 | 当前原字节/context有界分块源及原测试；本轮冻结JSON重算76原SHA/完整成员/字符串seq/ID/generation/time与912点，fingerprint保持 |
| AC14 | 通过；F-001保持解除 | 交叠shared/hold逐个解除及不完整cycle保护原测试/当前源码、QA3原保护测试；76全pending，产品/validation无ACK/清队列/任意SQL入口 |
| AC15 | 通过；F-002/F-003保持解除 | 当前每DELETE/独立vacuum预算、shared Arc/60s产品JSONL+stdout/unknown latch源；原预算/busy/IOERR/log失败再61s/Stop/history/shutdown及4维护故障原附件成立。本轮未故障注入 |
| AC16 | 通过（受控恢复） | 原产品/维护有效hotjournal重开完整账本；真实最终closed clean1及新9798binary stopped/76原值链，重启不自动连接；旧缺间隙不补造 |
| AC17 | 通过（R19 Owner路径） | 四页真实保存/激活/两PLC/历史、最终分页/modal/picker反向错误恢复/EN深色半屏回执及新binary观察；无QA4点击/新Owner操作，stub与只读视觉仅补充 |
| AC18 | 通过 | DTO/薄IPC/原point键/单1Hz owner/有界读源码和57前端保持；原11历史+6保存函数/实际native链，326/38/87/141 locale/347literal原结果按其源核用 |
| AC19 | 通过（受控验证） | 原 default/actual release compile_error/factory、真实owned Snap7、当前源对应QA3六定向/静态/build及strict新源原生链；无新测试或真实设备/数据库/API |
| AC20 | **通过；F-004本轮解除** | pair完整语义与当前代码/原始日志恢复证据对应；中文恢复边界准确，原数字/硬件限制/2local/4official齐全；33头部/9DAA索引等原结果源未变。当前真实新handoff→fresh QA4→待Owner终验；D-001计数笔误如实记录 |

## QA4-6. 验收审计、资源和最终 handoff

| 表面 | 当前事实 / 下一 gate |
| --- | --- |
| 已验证受控 B | AC01–AC20 通过，F-004解除；源码/功能原证据及本轮文档验证分层记录，QA1–QA3原失败不删除 |
| 当前 failure / blocker | 无；D-001为非阻断计数笔误，无实现返工或新范围要求 |
| Human Owner final acceptance | **pending**；当前仅交 Human Owner 终验，不自行写 owner_accepted |
| legacy / 回退 | 缺省 legacy 保留；local 双库不交旧writer；不授权清pending/重建/真实迁移或现场切换 |
| deferred / out-of-scope | Stage C可靠上传/ACK、Backend/SMA/DS开发或协议联调、真实PLC/TIA/生产DB/API/真实profile/现场、长期硬件负载、系统托管、多平台打包签名、Docker/Git提交/refs/推送/部署/发布均另批 |

SQLite3.46.0 的结论继续限定为已审查 DELETE+EXTRA、unix及受控 SQL；不宣称 WAL 已修复、全面安全或绝对硬件断电耐久。4PLC/500ms为准入边界；无上传器时pending会积累并导致更早停采。日志未知区间需修复与重启，无法伪造精确开始。受控 fixture/native 与原 Snap7 loopback 不证明真实现场或 DAA↔DS成品协议能力。

coordinator 于 15:40:13 UTC 另行只读核 known-owned PID/锁/监听，其 retained-resource-check.json SHA `286af3de6380042335ecf9411a473b040ff26cb32210508cdd024cd1f962e6d0` 确认22594/22593与原Vite族保留、22594持既有profile锁、75323监听127.0.0.1:49190。这是协调只读资源证据，不是QA4自行运行检查或新增功能/数据库/原生验证；无signal/UI/SQL/配置/连接/采样/重启或普通pnpm窗口访问。

本轮只创建 Q 文件/副本，没有产品测试子进程、listener、preview/browser/automation、worktree/分支/ref，也没有信号或资源回收。按 coordinator 及最近 QA3 实际资源审计，继续保留 native22594/父22593、Vite75297/75299/75323/75331和49190、原marked76样本profile、9798独立.app、全部旧故障材料/receipt，以及本轮输入源/diff/hash/原始输出副本。**本轮没有重新 ps/lsof 或 live SQL，不能把上述历史资源快照冒称当前独立观测。** live profile/stdout保持live，frozen快照单独封存；后续只由 coordinator 先核实际归属、后续依赖及证据需要再收尾，不按旧PID盲操作，不清他任务/共享缓存。

Q/verification-manifest.json 封输入、审计结果、完整 source/diff/原附件引用及本 checklist SHA；关键事实、命令/退出码、历史/当前结论和限制已写入本持久事实面，不以可能消失的tmp路径作为唯一解释。本角色封存后停止全部写入。唯一下一 handoff 为 **QA4 qa_passed → coordinator relay → Human Owner final acceptance**；不自动实施C、发信、部署或启动其他流程。

## QA3 原始全文历史

下列 BEGIN/END 标记之间是 QA3 原文件逐字节全文，SHA-256=`7cb06996795ff4be3ca4e23ef05e4a4b5a0cd7c3504ee104fbc19c5b7f8c3be7`。其中内嵌 QA2/QA1 同样保持原字节；旧“当前”、旧路径、PID和失败只属于原执行时点。上方 QA4 才是本轮当前结论，不重写历史。

<!-- QA3_CHECKLIST_VERBATIM_BEGIN -->
Task ID: DAA-002
Revision: r2
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA3 independently closes F-003 and retains functional/native checks, but finds F-004: local_store Chinese README omits the new logging latch/restart boundary required by paired-document governance and R20/AC20; return only this documentation correction through coordinator to Development, then exact new developer_handoff and fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-002 r2 第三轮独立核验

## QA3-1. 当前 verdict 与角色边界

2026-10-18（Asia/Shanghai），本轮独立 verdict 为 **qa_failed，仅文档一致性项 F-004 未满足**。F-003 已由当前源码、生产维护分支定向复测及实际产品日志核验解除；本轮没有发现新的运行/样本故障。旧 F-001/F-002 的修正和原始行为证据继续成立，本轮再定向复核交叠引用保护、维护预算/busy，未将旧 QA verdict 当本轮依据。QA1、QA2 的失败原文均完整保留在本文末；不改成过去通过。

实际 Verification 为 `/root/daa_stage_b_r2_verification_3`，由唯一 active lifecycle coordinator `/root` 在最新正式 developer_handoff 后以实际 `verification`、`fork_turns="none"` 的全新 context 调入。未继承 Development 的对话推理。独立消费根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 `.codex/agents/verification.toml`、AW/DAA及 app/local_store 最近说明、完整 spec/tasks/QA2（含 QA1）、实现、初始与返工完整差异、原始命令输出及原生回执/同库附件。作用域无更近 AGENTS。TOML `gpt-6.1-sol / max` 仅是配置证据；`contract_only` 不表示额外运行遥测、平台 ACL、强制路由或团队激活。

适用 shared skills：project-governance、aiis（BLUEPRINT/CONTRACTS）、rust-runtime、desktop-tauri、frontend-ui（既有 DESIGN/FRAMEWORK 适用部分）、i18n-workflow、plc-point-mapping、code-document-indexer，以及结构/运行日志基线。局部 Rust SQLite/IPC 不扩大成 Backend/Celery/DS/SMA 开发。本 QA 仓内只更新本 checklist；未修改 spec/tasks、产品、测试、配置、依赖、10项 coordinator 索引或其他任务。helper/构建/只读快照仅写自有临时 Q。F-004 不由 QA 修复，也不授权 Owner 最终验收。

## QA3-2. 精确输入、环境和保护审计

E=`/private/tmp/daa-002-r2-gnwbdg79`，Q=`E/verification3-r2-hzwctuer`，唯一最新 H=`E/dev/rework-qa2-20261018/final-handoff`。下表为 QA3 实际逐项核对，H 只是待验证输入。

| 输入 | 本轮核验事实 |
| --- | --- |
| 批准对象/HEAD | `aiis-ics-arch::DAA-002 r2`；HEAD=`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，保持 |
| spec | SHA-256 `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a`；最新批准及§1–10有效、§11为r1历史 |
| 当前 tasks | §12 `developer_handoff`，SHA-256 `ffff627350d38a0f58b3824df6e0782f570256486c7c71d82f5a2ceeb9de45fa`；旧等待段不作当前 gate |
| H receipt / manifest | `83446cbdcf0ed034717391c99795f2d28d62d7de076e2a70e19118c31888512c` / `955027892484461c9a9f3511d25bffb7585ee9f6f564567a4750c43d66cd5308` |
| 88路径/current/before/H-source | 全部一致；78实际变更、44新增全文；10个批准产品路径未使用，不把 allowlist 当实际修改清单 |
| 初始完整 diff | QA3独立重建618569字节，SHA-256 `81b22033ec8a1881a2788b37f731914536950157f9b441c911e3ea4eb66b9134`，精确匹配 H |
| QA2返工 diff | 独立重建55292字节，SHA-256 `5afc4177aa221312d7ffc1f1c6a8764493fca6076961c12b9089cf3a8ae72e3c`；11路径=5 Rust+2 locale+3 README+tasks |
| 组成文件 aggregate | all88=`1400b9e9233b7110356aa78801f101330995c3b495d5d2848e6ca1a580f40849`；product87=`9c6e6fcaa93f35bc13a547a22aea4a6c9b6015bdf50351148f111a475768793f` |
| 57前端 | 逐项及 aggregate=`1aef27f7f62495e6e59548f791a25039f6bab80f66399c524afcf366fa9e39c5`；相对旧600c35仅两 locale 增量，未冒称旧窗口无HMR |
| 最终源 / 原生 binary | source-seal SHA=`5510ff23468b049de4b51bc3cf32bf6ec67b838eb8c0b65da82c936465fc3a41`；独立 `.app/Contents/MacOS/runtime` SHA=`9798b8e128c40c82d6dcd30f51be914086304bb56fd8f3238d02f1cf0e17c2ca` |
| native provenance | `f0b4f3331fb258ff6cbf4b9e183fa565113fc02db280190121867e30b8ec9aea`；实际 argv/二进制/显式 factory 对应，未把 target 缓存当正在运行的 `.app` |
| QA2 / QA1 历史 | 原 QA2 SHA=`0ce5221365f7ea4e1f9650f9e3d8052892a2741a7ae96df4c6afd688e88b1f20`；其嵌入 QA1 SHA=`8d8112aa26dfef4a5d616e385c8346300182fb08f451679f6711a0930018be4b`；下方均可重建 |
| r1 历史 | 从 tasks 标记重建 SHA=`7ffdc1600534efe4605ff7a022d9c8bc16a7f68d19748ccb0590cff759d607ef`，保持 |
| 原始附件 | H evidence manifest SHA=`448479d7a126bad665494cb825ebe52b83433215bc9ecfcef615c7fac7d288e2`；384新+12prior直接引用、递归1336个不同附件字节均匹配；历史workspace指纹不当当前附件，live profile/stdout不宣称immutable |
| 保护面 | 1552原保护保持，12外来AW002/DS文档匹配foreign seal `3e51200ab13df5a40f6135293591f501a1c25c061dc37b1e17cd1784f1516aa9`；7旧+5新均单列归属，不回退/认领 |
| 共享索引/初始baseline | 四根索引滤DAA002/AW002/AW004/AW005行后其余初始原字节不变；baseline、allowlist、原审计脚本未改；其余6索引归coordinator |

`Q/audit-inputs.py` exit0；完整独立patch、输入源逐字副本、source manifest、repo-before和1336引用清单在Q。原 `E/audit-scope.py Q/raw-initial-scope.json` 实际 **exit1**，99总差异中的12 outside正是上述已归属外来文档、HEAD保持；没有把raw全局exit1伪记0或重置baseline。Q独立归属审计无未归属越界。

环境：macOS15.7.7/24G720，rustc/cargo1.89.0，pnpm11.11.0。Cargo依锁离线，复用 `E/dev/target` 依赖缓存；Owner运行独立.app副本，编译没有替换它。`Q/run-qa.py` 移除继承 DAA_/DAA002_/VITE_/SQLite/SQLCIPHER/LIBSQLITE3及build override，只提供已封临时TAURI_CONFIG，验证输出写Q，不读取真实env、不安装辅助依赖。

## QA3-3. 实际复测、原始证据与结果

Cargo/pnpm cwd=`automation-world/data-acquisition-agent`；manifest=`src-tauri/Cargo.toml`。完整argv/cwd/环境处理/耗时/真实退出码/stdout/stderr及SHA在Q同名前缀。helper不是DEV结果替代品，原生profile没有故障注入。

| 本轮实际命令/核验 | exit / 实际结果 | Q证据 |
| --- | --- | --- |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib periodic_maintenance -- --test-threads=1 --nocapture` | 0；3 passed、0 failed，0.47s；生产60秒分支私有时钟推进61s，预算两分支/真实IOERR/log不可写 | `periodic-maintenance.*` |
| 同Cargo test过滤 `maintenance_busy_rolls_back_and_releases_worker_for_following_writes` | 0；1 passed，1.18s；真实共享读锁busy、产品持久失败日志、后续读写推进 | `maintenance-busy.*` |
| 同Cargo test过滤 `full_context_is_original_bounded_chunks_and_log_rotation_is_owned` | 0；1 passed，0.80s；原context分块及8文件≤32MiB轮转，每行JSON可解析 | `rotation-and-context.*` |
| 同Cargo test过滤 `acknowledged_overlapping_references_and_incomplete_cycles_are_protected` | 0；1 passed，0.10s；交叠引用逐个解除、不完整单位/原pending保护 | `protected-cleanup.*` |
| `cargo check --offline --locked --manifest-path src-tauri/Cargo.toml --no-default-features --all-targets` | 0 | `default-check.*` |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 0 | `rust-fmt.*` |
| `pnpm build --config vite.validation.config.ts --outDir <Q>/dist --emptyOutDir` | 0；vue-tsc+Vite、1687 modules；既有PURE注释和chunk-size warnings保留 | `frontend-build.*` |
| `python3 Q/audit-f003.py` | 0；5场景的产品日志/结构字段/unknown_interval成立；两自有closed profile复制后ro完整性及10样本/5轮/2pending/4引用和原payload/context SHA逐项成立 | `f003-independent-results.json`、`worker-case-copies/` |
| `python3 Q/audit-native.py` | 0；mode=ro/query_only短读后关闭、双库integrity=ok、全表等于最终Owner快照，76/76/76、912点另解码，实际新closed clean_exit1证据成立 | `native-independent-audit.json`、`native-short-read-snapshot.json` |
| `python3 Q/audit-ui.py` / `audit-ui-source.py` | 均0；541旧registry/checksum保持+7获批新增；4locale pair 326/38/87/141键/占位符与旧值、347literal、33头部、44链接、CODE_INDEX只9条DAA新增 | `ux-*.json`、`ui-source-audit.json` |
| `python3 Q/audit-prior-evidence.py` | 0；独立消费原始B0五阶段/未改表面原输出、维护4故障、实际Snap7和默认release反例，77个DEV路径自QA2未改 | `prior-raw-evidence-audit.json` |
| 已归属PID/锁/49190只读 `ps/lsof` | 0；仅当前native22594/父22593、原Vite75297/75299/75323/75331；锁只归22594、listener只归75323；未发信号 | `resource-audit.json`及`retained-*.stdout` |

本轮没有重复未改UI/解析/Snap7/全套故障测试，也没有新增preview/browser/native操作。旧原始输出在核源/hash后独立消费，不把QA1/QA2的pass/failed结论直接充本轮结果：新B0实际5阶段、QA2的20项原stdout及4维护故障、旧真实Snap7单client/自定义port/坏DB/断连/黑洞/慢read、5个激活SIGABRT轨迹、COMMIT前后/有效hot journal SIGKILL、9解析定位反例、默认/factory/actual release compile_error、11历史函数/6保存函数，以及真实Owner原生链均保留。

真实过程错误继续保留：DEV首次F003测试compiler101、旧run-cargo未传播子exit（本轮读取实际result退出）、Python默认cache写拒绝后内存compile替代、未启动bdce/fa4c候选撤回、§9.3错误零字节env断言exit1后未分支继续及旧间隙SQL快照缺失。本轮不把这些补成过去成功。QA3一次只读脚本搜索遇zsh无匹配glob，随后改用rg文件清单；无产品/测试修改。输入、原始附件和最终scope检查真实结果各自记录。

## QA3-4. F-003解除、旧failure和存储适用性

**F-003当前解除。** `Stores::open`创建一个Arc<LocalLog>，Engine、StoreHandle和worker共享相同对象/轮转mutex；真实60秒分支在`maintain`错误后直接写该logger，不递归`storage.call`。实际profile下`logs/runtime.jsonl`包含`event=maintenance_failed`、`process=daa-local`、`resource=storage_maintenance`、`result=deferred|failed`及稳定`error_code`，stdout只有append/flush成功后才标`persistence=persisted`。预算前拒绝、cleanup后vacuum独立拒绝、读锁busy和RLIMIT_FSIZE=4096引发SQLite journal真实IOERR分别有产品文件记录，原保护/pending/样本字节保持且后续读写成立。

日志不可写用自有runtime.jsonl目录冲突触发：stdout为原事件`persistence=failed`和`local_log_failed/unknown_interval/log_io`，共享latch报`log_io_unknown_interval`；新写入/Start拒绝、采样轮次准入停止。再次恢复空间meter并推进61s后，短读仍不能重启维护写入。历史/配置/容量可读，快照PLC错误和logs查询反馈故障；显式Stop与shutdown实际完成，无递归writer死锁。disconnect走同一允许停止分支，未冒称本轮另做了connected PLC的断连实验。测试恢复自有冲突路径、重开原ledger可读。未知日志区间不伪造精确起点，修复后需restart；已准入在途与新准入区别保留。正常退出的clean_exit写属于关闭协议，不被宣称成所有物理写绝对归零。

**F-001/F-002修正仍成立。** 当前保护测试再实际通过；删除完整/ACK/无引用单位，交叠shared/hold逐个释放后才有资格，不完整轮保留。每个维护DELETE及独立vacuum写前重核当前物理/free、全旧页journal上界、4轮在途、32MiB维护和512MiB系统余量，最多8候选/64页。旧QA2原始四场景分别cleanup/vacuum的真实IOERR及有效hot journal后SIGKILL9→Rust重开/原ledger SHA相同/后续读写维护；峰值79360/9728低于463296/3899096旧页journal界限。没有填宿主盘、手删journal或降EXTRA；本轮不重复这些未改故障场景。

新B0独立复核原始输出为SQLite3.46.0/sourceID `2024-05-23 13:25:27 96c92aba00c8375bc32fafcdf12429c58bd8aabfcadab6683e35bbb9cdebf19e`、unix、双库/多连接DELETE/EXTRA3/page4096/auto_vacuum2/FK1/busy1000；busy1045ms、interrupt104ms、605752字节hot journal SIGKILL与IOERR778恢复后4轮/8包/8pending/seq4保持。r1 WAL探针未替代r2 gate；r1 blocked原文、r2先新B0再产品的事实记录/输出保持。

2026-10-18再核SQLite官方[WAL-reset前提](https://sqlite.org/wal.html#the_wal_reset_bug)、[EXTRA目录同步](https://sqlite.org/pragma.html#pragma_synchronous)、[unix-dotfile修复](https://sqlite.org/releaselog/3_47_0.html)、[partial UNIQUE/WITHOUT ROWID原复现](https://sqlite.org/forum/forumpost/e60e4c295d22f8ce)、[AND投影原例](https://sqlite.org/forum/forumpost/f4878de3e7dd4764)和[hot journal恢复](https://sqlite.org/lockingv3.html#hot_journals)。当前普通rowid/普通列索引/参数SQL、DELETE及unix不具这些对应触发组合；CHECK字面IN不冒称无IN。3.46未修复WAL，DELETE只是排除该前提；日志flush/进程kill不证明断电耐久或SQLite全面安全。

## QA3-5. 原生及历史编排错误边界

R19允许真实Owner操作+同库证据。本轮独立核真实题干/回执及源码/持久副作用：保存重读退出、两modal/下拉/激活、两owned约25秒26/50轮后暂停、最终分页/详情modal/picker反向区间错误清除恢复/EN深色代表窄窗、正常退出与同factory重开。浏览器只读fixture和11/6函数stub只补充UI反例；没有把它们或任何假invoke冒充native。

最终9798…binary的新源Owner原话为“新版停采、Test PLC、历史和详情均正常”，relay SHA=`0d2567544d0291c763ee88c4710247f156b81474c97879ec8652aadc8227f482`，题干仅三台stopped、Test保留、两PLC历史与任一modal、保持窗口。最终reconciliation SHA=`37aa72bce78e59ca8f3104ae75a4f9241b7740c5abb2f9530e9ca132283509fa`。这是观察，不是最终验收。当前短读全表含events与14:54:46快照相同；76cycle/76sample/76pending、3PLC/24点、912good原值按fixture大端BOOL/BYTE/INT/REAL独立核，Test零样本、next27/51/1、active=used=`add0b620-ebce-4451-a2fa-8c9b7dc83de3`，raw fingerprint=`e4cd3c37c08643ff353a1c6e3e9bc95299d2d903b7dff28e0b77fdcb65678f1f`。原payload/manifest/context/hash/ID/generation/seq/时间均保持，SQL不冒称读取了内存connected/desired状态。

本次strict helper SHA=`46dcd524035874822a80af218cfe6a7ba7e733136ef89d9acd680dbb1fca25b9`，源码先核87/57/binary/真实278字节env/fixture/marker/path/旧exit0/PID absent/自然flock，封`clean_exit=1`短读和全ledger核对后才到唯一Popen；异常不能落入启动。preflight SHA=`2a9802edfadad76282f84e079d16051d7f3fc8742ec5b683838cee78c5fc392c`；实际closed snapshot SHA=`4ac19c5e1cfd8f57725965ad6eede8531bcd0f4a153f31f7637cc57638a46ffe`。旧事件88 clean-stop、新89 stopped-start和全原ledger符合。Owner说误关Owned并普通pnpm后要求重开；旧exit0由coordinator实际观察，不改称typed CmdQ。

旧§9.3错误断言0字节env→exit1→编排未判断仍继续的事实完整保留：实际env278字节/SHA=`5fe0fd6b00ec4155e8d8293698c33c7070ba98d4191ea250bdb0bfb148cbe915`与source/旧H/current H相同；工厂在旧I/O前严格校验，fixture无真实transport。它未证明越界产品I/O，但确实丢失当时直接clean_exit1间隙快照；当前新snapshot不能补造旧证据。旧窗口可能自动收到两locale HMR，没有捕获HMR轨迹，不重标旧观察为当前源。

未重试getApp两次长挂、Codex AX安全拒绝或49192自动审核拒绝；不更换入口绕过，不发信号、不操控窗口/改profile/连接/采样/激活/ACK/重开。用户普通pnpm窗口/profile/env完全不在QA访问对象内。

## QA3-6. 当前AC01–AC20独立映射

“通过”仅指获批受控B表面及真实可核证据；不能消除F-004或升级Owner终验。

| AC | QA3结果 | 独立依据/限制 |
| --- | --- | --- |
| AC01 | 通过 | 精确批准/B0先行历史、88当前/初始before/H-source、完整两diff/r1及QA历史/1552保护+12外来归属；不继承A/CU验收 |
| AC02 | 通过 | 当前bootstrap/旧入口guard/profile锁/factory，旧默认/模式拒绝原输出；local唯一owner不调旧health，保存导航不建PLC连接 |
| AC03 | 通过（限定） | 原始r2新B0五阶段、当前541+7依赖/受限SQL/VFS及官方适用性；3.46仍非已修复版本 |
| AC04 | 通过 | 当前队列/查询deadline/join/成对库检查及原QA2 20项输出；本轮busy事务回滚后读写推进，无Owner库修改 |
| AC05 | 通过 | 当前CAS及derived-field保护源码、原公开服务/原生保存重读ID链；当前新binary全配置/opaque ID原值保持 |
| AC06 | 通过 | 未改parser/完整结构源码指纹与flat/nested/数组黄金、9个实际定位反例原始输出；完整结构与enabled分开 |
| AC07 | 通过 | 未改受限offset/decode及独立golden、手工地址持久链，912点从fixture字节另解码；非TIA现场校核 |
| AC08 | 通过 | 当前服务端限额/500ms/跨DB/单点单组/跨PLC拒绝与原测试；native3PLC/24点、Test无组零样本 |
| AC09 | 通过 | token屏障/恢复与原5个SIGABRT阶段、原active/loaded/used/previous测试；新binary同两库context/active/used重开 |
| AC10 | 通过 | 未改managed S7/共享actor源码及真实owned单client/自定义port/断连黑洞慢read原stdout；不是DS或硬件CPU证据 |
| AC11 | 通过 | 未改调度/公平/deadline/跳tick原始用例；native26/50轮及暂停稳定，限额不等现场性能 |
| AC12 | 通过 | 当前全成员事务/seq/pending源码及原COMMIT前0/后2pending、产品hot journal SIGKILL恢复输出；无半轮 |
| AC13 | 通过 | 本轮原context分块/hash测试；76原字节/912原点值/seq字符串/ID/generation/time独立对账 |
| AC14 | 通过；旧F-001保持解除 | 本轮交叠引用/不完整单位反例实际通过；全部原生76pending、产品无ACK/任意SQL/清队列后门 |
| AC15 | 通过；F-003本轮解除 | 生产60秒分支预算前后/busy/真实IOERR均写有界产品JSONL+stdout；日志失败latch/再61s仍停维护/历史Stop退出成立，旧维护恢复证据保持 |
| AC16 | 通过（已测恢复） | 原产品/维护hotjournal恢复证据，当前原生同库完整性/新closed clean_exit1/旧exit0与新stopped、全样本保持；不补造旧§9.3缺失间隙 |
| AC17 | 通过（R19 Owner路径） | 真实四页保存/激活/两PLC/最终历史交互原回执及新binary停采/历史确认；不冒称QA点击、逐IPC抓包或native注入断网/CAS |
| AC18 | 通过 | 当前薄IPC/camelCase/原point键/唯一1Hz owner/有界读及347literal/原11历史+6保存结果；新增故障稳定码双语可解析 |
| AC19 | 通过（受控验证） | 本轮6定向测试/默认编译/前端build，未改真实Snap7/default/release/factory原输出与strict new-native链；无真实设备/API |
| AC20 | **未通过：F-004** | 其他locale/347literal/33头部/44链接/9DAA索引/角色/完整diff均成立；local_store中文pair未同步新的恢复边界，见下一节 |

## QA3-7. F-004：局部中文工程说明缺少新的日志闭锁/恢复边界

范围是批准R20/AC20的文档/实现一致性义务，分类为**必需文档配对缺口**，不是又发现F-003运行失败。

当前 [local_store/README.md](../../src-tauri/src/infrastructure/local_store/README.md) 第21行已新增：共享Arc/轮转mutex、维护失败/延期的产品JSONL与stdout、`log_io_unknown_interval`锁存，日志修复并restart后恢复，历史/config/capacity与Stop/disconnect/shutdown可用。对应 [README.zh-CN.md](../../src-tauri/src/infrastructure/local_store/README.zh-CN.md) 第22行仍为旧描述：“存储失败须有界写健康探针成功且容量恢复后才继续”，没有区分新增日志故障须修复/重启，也没有同步维护写前重核和两阶段延期语义。中文文件自QA2字节完全未变，SHA=`364f702c2f0c527bf328d214f9a8ba24ba7529796cf9716780ab09934518bf49`；英文已改为SHA=`26c94a601118b8291e8c20f670e3e709f0b3dfb927fc9b8e5ac3edce46271ff0`。上层DAA README pair已正确说明新日志边界，不能替代被其明确链接的局部schema/recovery说明同步。

适用 [code-document-indexer/SKILL.md:34](/Users/jason/Desktop/DreamCode/AI/AIIS/skills/code-document-indexer/SKILL.md:34) 明确要求："When editing one version, update its pair in the same task unless the user explicitly says the file is a temporary single-language draft." 当前不存在该局部说明的单语临时例外。这里不要求逐字翻译或增加新设计；缺口是新增恢复条件没有在已有pair中出现。Q/finding-f004.json封精确两版原文、QA2前后hash和skill规则/hash。

**最小解除条件：** Development仅在已经批准的`src-tauri/src/infrastructure/local_store/README.zh-CN.md`同步实际维护准入/独立vacuum重核、共享有界产品日志、日志不可写未知区间锁存/修复重启，以及仍可历史/Stop/disconnect/shutdown的语义。保持现有数字/测试/硬件限制，不改schema/IPC/依赖/运行实现；更新自己的tasks并给精确新diff/源指纹和developer_handoff，coordinator再启动新的fresh-context文档核验。若仅此文档修正，当前binary/UI/业务源和Owner观察按真实未变字节继续核用；无需重复功能套件、重启或让Owner再操作。QA3不代写中文说明。

## QA3-8. 验收审计、资源与下一handoff

| 表面 | 当前事实/下一gate |
| --- | --- |
| 受控功能/原生能力 | 本轮实际通过事实及旧原始证据可核；F-003解除。不会因F-004抹去这些结果 |
| 唯一当前失败 | F-004→coordinator→Development最小文档pair修正→精确新handoff→新的fresh QA；不是扩大产品实现 |
| Human Owner final acceptance | **pending**；当前整体qa_failed，尚未进入最终验收；Owner真实UI观察不等终验 |
| Legacy/回退 | 默认legacy保留，local库不交旧writer；不授权清数据、迁移真实profile、恢复旧备份或现场切换 |
| deferred/out-of-scope | StageC上传/ACK、Backend/SMA/DS协议实现与联调、真实PLC/TIA/生产DB/API/真实profile、长期硬件负载、系统托管、多平台打包签名、Docker/Git refs/commit/push/部署均另批 |

本轮新维护IOERR child已退出；没有新listener、preview/browser/automation、worktree/branch/ref。两关闭marked私有profile及其Q复制、产品log/ledger、完整输入源/diff/hash、原始命令输出和只读native快照保留供返工及下一QA。部分常规测试自行清理其临时目录，关键结果/断言和原始输出已封存；没有清理Owner或其他任务资源。Q/verification-manifest.json列完整本轮输入/产物，不以可能消失的tmp路径作为唯一结论解释。

按coordinator要求保留native22594/父22593、同一marked native-profile、原Vite75297/75299/75323/75331和49190、最终独立.app及全部旧receipt/故障材料/证据；本轮ps/lsof仅核这些已归属资源。live profile/stdout继续是live，不冒封immutable。QA不执行资源回收，不按旧PID盲清理；root按归属/证据/依赖处理后续收尾。本角色在checklist及manifest封存后停止写入。当前结果仅通过唯一coordinator返回Development；最终验证结果仍须交Human Owner决定终验，QA不授予该权力。

## QA2原始全文历史

以下BEGIN/END之间为QA2原文件逐字节原文，SHA-256=`0ce5221365f7ea4e1f9650f9e3d8052892a2741a7ae96df4c6afd688e88b1f20`；内嵌QA1原SHA也保持。旧“当前”、旧源/binary/H/Q/PID与失败均属于各自当时；上方QA3才是本轮时间效力，不回写过去。

<!-- QA2_CHECKLIST_VERBATIM_BEGIN -->
Task ID: DAA-002
Revision: r2
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: QA2 independently closes historical F-001/F-002 on this exact reworked r2, but finds F-003: maintenance failure has stdout warning without the R15 required bounded persistent product log; return through coordinator to Development, then a new exact developer_handoff and fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-002 r2 第二轮独立核验

## QA2-1. 当前结论和归属

2026-10-18（Asia/Shanghai），当前独立 verdict 为 **qa_failed**。QA1 的 F-001（ACK/交叠引用/不完整轮次反例）和 F-002（维护写入当前空间/journal准入与故障恢复）已由本轮源码、实际测试和原始附件验证解除；其原失败结论和证据全文在本文末保留，不改成过去已通过。本轮新增 **F-003：维护失败未写产品自己的有界持久日志**，未满足批准 R15 的失败证据要求。该发现不是数据丢失结论，也不否定已验证的容量、引用保护、事务或恢复结果；整个 B 阶段仍不得记为通过或最终验收。

实际 Verification 为 `/root/daa_stage_b_r2_verification_2`，由唯一 coordinator `/root` 在最新正式交接之后启动的全新 Verification context；未继承 Development 或 QA1 对话推理，未把它们的 verdict/self-check 当本轮权威。已独立读取实际 `.codex/agents/verification.toml`、根 AGENTS、双语 README/PLAN、canonical workflow、AW/DAA及最近目录说明、完整 spec/tasks/QA1 checklist、当前实现、初始完整差异和返工差异及原始证据。作用域内无更近 AGENTS。TOML 的 `gpt-6.1-sol / max` 是配置证据；本 profile 为 `contract_only`，不宣称额外运行遥测、平台 ACL、强制路由或 Agent Team 激活。

采用 project-governance、aiis（BLUEPRINT/CONTRACTS）、rust-runtime、desktop-tauri、frontend-ui（既有 DESIGN/FRAMEWORK 适用部分）、i18n-workflow、plc-point-mapping、code-document-indexer 及适用结构/日志基线，只用于验证。局部 Rust SQLite/IPC 不扩大为 Backend、Celery、DS、SMA、工具或打包开发。

仓内唯一写入为本 checklist；spec/tasks、产品、测试、配置、依赖和10项 coordinator 索引均未由 QA2 修改。所有 helper、编译/故障附件和只读快照归自有临时 Q。没有自修实现；F-003 只交 coordinator 返回真实 Development。

## QA2-2. 精确输入、环境与差异审计

证据根 E 为 `/private/tmp/daa-002-r2-gnwbdg79/`；本轮 Q 为 `verification2-r2-ts37v2i9/`；最新正式 H 为 `dev/rework-qa1-20261018/final-handoff/`。以下指纹均以实际字节核对。H 仅作为待验证输入，QA2 另行重建差异、检查源码和复跑必要行为。

| 输入 | 实际核验 |
| --- | --- |
| 精确批准对象/HEAD | `aiis-ics-arch::DAA-002 r2`；`f85bea8bbf36b491968c3dc9a839518a1ed434a8`，保持 |
| spec | SHA-256 `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a`；§1–10及最新批准有效，§11为r1历史 |
| tasks | `developer_handoff`；SHA-256 `ccc706228c4d0bcfbba9853343238e528c8fcffbc8875d0599d465cb33600589` |
| H receipt | `f4fc8ef029cf0f722b127b134c59c977e5bf03f4223fee17a3309de0c6f1b751` |
| H development manifest | `156a275cccbaf0f9bbd7e8b0cae948d2c4a34105e39b92c360f9f6e8025c0e53`；全部88当前路径、初始before、H/source副本逐项一致 |
| 初始完整全文diff | QA2独立重建583843字节，SHA-256 `bce66141bfaf3a80b623df4cdc0a5a5eb018ec0b44ecacc133112fe6b6204686`，与H patch精确同字节；78实际变化、44新增 |
| QA1返工diff | QA2独立重建59088字节，SHA-256 `3d08d9bf24c5b672b9dc6847206c2ca6978bf81fc3100f9150ebb1560e082880`；8路径=4 store Rust+局部英文README+DAA README pair+tasks，无schema/IPC/依赖/前端变化 |
| 当前source aggregate | H声明的all88=`df97727092179297bb6da0f64c8bbb1491ca819e3f0826262a14873529f25dc4`，product87=`a3c84d7e5e4880697748c29716bf4e7a3acb75116add776e9b0f94827aee8268`；组成文件均独立逐项核对 |
| 前端57文件 | 每项匹配，aggregate=`600c35e30467c367f4d81cc8467e7693e31126fc4189a625d8d1c7de0495a8e7`；未把旧前端构建状态冒称重跑 |
| 新原生源码/二进制 | source-seal SHA `24bc3d6c0fc1adea7d2d5f23787d3c8fb603bd86eb87995a1dc2f027e94822c3`；独立.app runtime SHA `80629d0cd33c7c049179326c8c95ea986185710df642b19a7889f1b06a443158` |
| QA1历史 | 原checklist SHA `8d8112aa26dfef4a5d616e385c8346300182fb08f451679f6711a0930018be4b`，下方全文可重建；QA1 manifest SHA `fb1f246b0d8f2784a4803cd4437efbfce62cc406e582fa0672013b03ff9d5f85`保持 |
| r1历史 | 从tasks原文标记重建 `7ffdc1600534efe4605ff7a022d9c8bc16a7f68d19748ccb0590cff759d607ef`，保持 |
| 不可变附件 | H evidence manifest SHA `23fed0ec8a703ea794039abdb2d7c26fc6cbb9f37855b86fd3756abf42b2fc00`；其266新附件、8个先前manifest引用及递归明确字节引用核到843个不同附件，无摘要不符；历史workspace指纹不当成永久附件，live profile/stdout不作immutable宣称 |
| 保护面 | 1552原保护文件当前保持；11个AW002/DS文档与最新foreign seal `5d40125e262ce2de729acfa14222ddc274816beff27f37fc76fe47dbd19dbd88`相符；四共享索引剔除DAA002/AW002/AW004行后其他初始字节保持；baseline/allowlist未改或扩大 |

环境为 macOS15.7.7/24G720、rustc/cargo1.89.0、pnpm11.11.0。Cargo依锁离线执行；复用 E/dev/target 依赖缓存，由Cargo针对当前源码编译，未覆盖Owner独立.app副本。启动器移除继承DAA_/DAA002_/VITE_/SQLite覆盖和build override，只提供原已封临时TAURI_CONFIG；不输出继承值、不读取真实env、无辅助依赖安装。

## QA2-3. 本轮实际检查及结果

Cargo cwd 为仓内 DAA，manifest 为 `src-tauri/Cargo.toml`。Q/run-qa.py保存完整argv、cwd、环境处理、退出码、耗时和原stdout/stderr。输入/原生审计helper仅读已明确owned资源，输出只写Q；没有运行真实设备/API、Docker、迁移、发布或现有工具服务。

| 实际命令/检查 | 退出码和实得结果 | Q附件 |
| --- | --- | --- |
| `python3 Q/audit-inputs.py` | 最终0；88/source/before、全文patch、返工patch、57前端、843引用及保护面相符 | `input-audit.json`、两份`independent-*.patch`、`immutable-references-verified.json` |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 0 | `rust-fmt.*` |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::tests -- --test-threads=1 --nocapture` | 0；20 passed、0 failed、1 ignored、52 filtered，17.27s。ignored是私有child入口，父测试实际以明确marked tmp参数执行，非省略恢复场景 | `local-store.*`、`qa2-maintenance-results.json`、`maintenance-cases/` |
| `cargo check --offline --locked --manifest-path src-tauri/Cargo.toml --no-default-features --all-targets` | 0，1.67s | `default-check.*` |
| `cargo build --offline --locked --manifest-path src-tauri/Cargo.toml --features local-validation --bin daa-local-validation` | 0，1.04s；当前源码debug CLI | `validation-build.*` |
| `python3 Q/exercise-current-product.py` | 0，4场景：当前CLI裸帮助；COMMIT前/后SIGABRT(-6)重开0/2pending；产品hot journal58880字节、有效magic后SIGKILL(-9)、Rust重开原4样本/账本保持。ACK/清队列/维护/任意SQL命令均拒绝 | `current-product.*`、`current-product-exercise.json`、3个新marked profile/transcript/原journal副本 |
| 当前CLI静态/链接核对 | 0；私有维护child环境键/marker/入口字符串不在validation binary中；bundled amalgamation SHA仍`c01235302fe80da901fb70c7622c39147e29d9f29b7f6eb746b23517f320c90d`；otool无系统SQLite动态链接 | `binary-static-audit.json` |
| `python3 Q/audit-native.py` | 0；mode=ro/query_only短读并关闭，双库integrity=ok，当前全部表等于新源Owner封存，76/76/76和912点独立解码成立 | `native-independent-audit.json`、`native-short-read-snapshot.json` |
| `python3 Q/audit-ui.py` | 0；541旧registry版本/checksum保持、只7个获批新增；4locale pair 325/38/87/141键及占位符对称、旧值保护、44本地链接及r1/spec成立 | `docs-locales-lock.*`、`ux-*-audit.json` |
| `python3 Q/audit-ui-source.py` | 0；真实assembly中347 literal keys双语解析，33新源码中文头部，CODE_INDEX只加9条DAA项 | `ui-literal-heads.*`、`ui-source-audit.json` |
| 已归属资源只读ps/lsof | 0；native40013/父40012、Vite75297→75299→75323→75331保持，40013唯一持profile锁，75323监听127.0.0.1:49190；未发信号 | `retained-processes.log`、`retained-profile-lock.log`、`retained-vite-port.log` |
| 维护失败记录控制流审计 | F-003成立；真实worker失败只有stdout warning，见QA2-7 | `maintenance-logging-source-review.json`和`local-store.stdout` |

Q辅助器的真实过程失败亦保留：初版递归附件核对错误地把历史source-index相对路径及旧workspace tasks指纹当成当前附件，exit1；纠正附件与历史元数据的基址后最终exit0，原两报告保留。首次维护结果提取忽略了test前缀同一行JSON，导致少计一个场景/断言exit1；只修Q解析后核到全部4个子场景，产品测试始终通过。没有因此更改产品、测试或历史附件，也没有把失败断言改记成pass。

没有重复构建未改前端或重跑全部UI/Snap7/解析矩阵。QA2独立消费原始源码、stdout/断点/库状态及当前未改字节：新B0的5阶段原始输出；此前实际Snap7 owned会话、自定义port、断连/黑洞/慢read输出；5个激活SIGABRT阶段原始轨迹；默认/错误模式/factory及actual release compile_error反例；最终前端vue-tsc/Vite、11历史函数及6保存函数原始结果；Owner真实native操作与同库链。这些是既有可核原始行为证据，未被写成本轮重跑或沿用QA1 verdict。

## QA2-4. 两项旧failure解除及存储适用性

**F-001已解除。** 当前 `tests.rs` 的私有种子构造pending、两轮交叠shared/独立hold保护、ACK但expected_samples多于实际包数、普通完整ACK。实际清理先仅删合格轮；解除一个hold后shared仍保护两轮；解除shared只释放无剩余引用的一轮，另一轮仍被hold保留；解除最后hold才释放；不完整轮保持，私有修复完整数后才可释放。每步核原sample/manifest/context字节及摘要、delivery状态和pending；生产/validation无ACK或任意SQL后门。当前整组20项中该反例实际通过，不把QA1缺失测试补称当时已存在。

**F-002已解除。** `mod.rs`真实每60秒worker分支调用`maintain()`；每个合格删除事务前`admit_maintenance()`重读物理主库/既有journal/配置/log/当前free，使用全部旧页journal上界、4轮在途、32MiB维护、512MiB系统余量；cleanup后vacuum前独立重核，vacuum为显式事务。每批扫描最多8cycle、回收最多64页，预算不足延期，事务失败drop/rollback释放；两个阶段不宣称整体原子。

本轮实际测试推进私有时钟至61秒进入同一生产分支，并未声称等了60个真实秒：free=0保留全部；cleanup成功后free降0独立阻止vacuum；读锁使维护busy并回滚，释放后读写推进。cleanup/vacuum分别RLIMIT_FSIZE=0产生真实disk I/O error，恢复限制后原账本及后续写成立；各自有效hot journal后只杀自有child(SIGKILL9)，Rust bundled重开恢复所有pending/交叠引用/不完整cycle/原payload/manifest/context/SHA/seq并继续读写维护。实际journal峰值79360/9728字节，分别小于全旧页上界463296/3899096；不以固定64MiB总reserve替代journal比较，不填宿主盘、不手删journal、不降低EXTRA。

独立复核新B0原始实际SQLite3.46.0、source ID、默认unix VFS、双库/多连接DELETE、EXTRA=3、page4096、auto_vacuum2、FK1、busy1000及锁/恢复/IOERR/interrupt。当前schema普通rowid/普通列索引，参数SQL；静态字面CHECK IN不等于IN子查询。2026-10-18重新核官方[WAL-reset条件](https://sqlite.org/wal.html#the_wal_reset_bug)、[EXTRA同步](https://sqlite.org/pragma.html#pragma_synchronous)、[hot journal恢复](https://sqlite.org/lockingv3.html#hot_journals)、[unix-dotfile修复](https://sqlite.org/releaselog/3_47_0.html)、[partial UNIQUE/WITHOUT ROWID原复现](https://sqlite.org/forum/forumpost/e60e4c295d22f8ce)与[AND聚合投影原例](https://sqlite.org/forum/forumpost/f4878de3e7dd4764)，当前受限SQL/VFS不具对应触发组合。3.46.0仍未修复WAL问题，DELETE只排除其前提；进程kill不是断电证明或全面SQLite安全保证。

## QA2-5. 原生链与编排错误独立评估

R19允许真实Human Owner操作与同库核对。原生自动化getApp长挂、Codex AX安全拒绝及49192审批拒绝均未重试/绕过；QA2没有操作Owner窗口、HMR、连接/采样/ACK、改profile、停进程或重开，也没有新visual server/tab/截图/DOM。此前源码、构建与Owner真实保存/重载、两modal/下拉/激活、两PLC采样暂停/历史、20→10分页/上下页、详情原文/SHA/pending/折叠上下文、datetime反向错误/清除恢复、EN/深色半屏和正常退出链按原始题干/回执及持久副作用独立消费；57前端当前原字节保持，不将stub或只读视觉harness当native。

新Rust binary80629d0c…已在原profile重开，Owner真实回执“停采状态、Test PLC、历史和详情均正常”，对应仅观察三台disconnected/stopped、Test保留、两PLC历史与任一样本弹窗且保持窗口打开。relay SHA `09a77a3b9a0b2d31a0dfa17c598908eda97e0a171ae1ffbe6b5c144d2bb7e457` 与reconciliation SHA `136f4612e8013bef532d42b460c3553e0904b17446be2f153a38b9e67322a69e`已核。当前全部表与12:39:31封存相同：76cycle/76sample/76pending，3PLC/24点，912个good观测逐点按fixture大端BOOL/BYTE/INT/REAL独立解码，全部origin=fixture；Test无样本，next27/51/1，原ID/generation/seq/时间/原sample/manifest/context/SHA保持，fingerprint=`e4cd3c37c08643ff353a1c6e3e9bc95299d2d903b7dff28e0b77fdcb65678f1f`。SQL不读取内存connected/desired状态；该实态来源为Owner观察、stopped事件和源码初态，而非伪造逐IPC线包。

DEV真实编排错误的附件 SHA `e52f8d0f3574a21b5418e8579a96f8e7868c579b5e613f504968ec0c3edb8a29`：前检错误断言empty.env为0字节，实际278字节，原AssertionError/exit1保留；functions.exec未判断exit_code便继续已授权reopen。完整原调用只在DEV会话历史，附件未冒充完整原录；QA2不把该失败补为pass。

QA2核controlled env当前278字节/SHA`5fe0fd6b00ec4155e8d8293698c33c7070ba98d4191ea250bdb0bfb148cbe915`，与当前source fixture、新H和旧H source副本逐字一致；原prepare-native.py SHA`141ff51080fca757d7a03ee6ecf851787ddcb4f38940e4402d97baeebe7f8090`与旧evidence manifest匹配，实际是copy该fixture，无臆造初始profile-env独立seal。transport SHA`ef85384228cafb320b37a248058b74c54d24400d138cd10dc12d64949341f3e2`也保持。launcher核新binary/marker/绝对profile argv/旧PID不存在/自然取得释放既有锁，Rust工厂在旧配置和headless前验证显式路径/允许env键值/无继承DAA，local-validation固定fixture且真实S7 feature排除，无网络fallback。

因此该编排错误在本轮证据下**不另构成产品隔离/恢复阻断**：失败的是不适用的零字节断言，实际必需隔离门槛有另行成立的源码/字节/启动依据，当前全账本无越界变化。但它仍是DEV执行错误，不能掩盖。其直接后果是没有取得旧进程退出至新启动之间的clean_exit=1 SQL快照。可直接核的是旧exit0、事件86 runtime_stopped/clean、自然锁释放、事件87 runtime_started/stopped、新旧全表原值；瞬时clean_exit=1只能按源码与无uncertain_gap事件推断，不能宣称直接观察。未重复重启来补造缺失证据。

## QA2-6. 当前AC01–AC20映射

“通过”只指获批受控B表面及其可核证据，不等于全任务通过、Owner终验或真实现场能力。

| AC | QA2结果 | 本轮独立依据 |
| --- | --- | --- |
| AC01 | 通过 | 精确批准/B0先行、88路径初始全文diff与返工diff、r1/QA1历史、1552保护与11foreign归因；未继承A/CU状态。 |
| AC02 | 通过 | 实际factory/模式/旧入口/锁反例原始输出及当前guards；新CLI公开调用、保存/重开stopped；local owner不调旧health。 |
| AC03 | 通过（限定） | 新B0原始多连接/PRAGMA/锁/恢复、541+7锁对照、当前原生来源及官方SQL/VFS适用性；未宣称3.46已修复。 |
| AC04 | 通过 | 当前20项中双库身份/缺库/损坏/高版本/WAL拒绝、CAS、排队/执行deadline及后续写；当前维护busy回滚/释放亦成立。 |
| AC05 | 通过 | 当前CAS/派生字段防伪测试、QA2当前CLI公开save/import/确认、原生保存重读/正常重开同ID与草稿；新source重开仍保持。 |
| AC06 | 通过 | 当前完整flat/nested/数组黄金、legacy incomplete与拒绝测试；独立读parser及既有9个定位反例原始输出，不把未选字段丢掉。 |
| AC07 | 通过 | 当前offset/类型/地址恶意边界黄金及独立912点解码；Owner人工0.0/确认依据与偏移保护持久链；非真实TIA地址核验。 |
| AC08 | 通过 | 当前规模/500ms/跨PLC/单点单组/预算反例；QA2公开两PLC三DB36点实际激活，原生Test无组无采样。 |
| AC09 | 通过 | 当前live install/previous/used测试、原始5激活SIGABRT轨迹和两库token/context；新binary同active/used重开stopped。 |
| AC10 | 通过 | 当前共享测试/诊断/未知fixture隔离测试及未改真实Snap7四项原始输出：单client、自定义port、坏DB、断连/黑洞/慢读；非DS成品或硬件CPU证明。 |
| AC11 | 通过 | 当前公平组/跳tick/非重入/deadline/其他PLC继续用例；原生26/50轮和暂停稳定账本；限额不是现场吞吐承诺。 |
| AC12 | 通过 | QA2当前CLI COMMIT前0/后2pending、hot journal SIGKILL原4份恢复；当前全成员事务/seq/manifest/错误回滚测试，无半轮。 |
| AC13 | 通过 | 当前原context分块与hash测试、公开详情及正常/异常重开对账；76原样本/manifest/context/时间/代次与912点原值保持。 |
| AC14 | 通过；旧F-001解除 | 新交叠引用逐个解除、不完整ACK单位保护实际通过；当前生产/validation拒ACK/SQL/清pending，全部真实样本pending。 |
| AC15 | **未通过：新F-003**；旧F-002解除 | 当前物理预算/两阶段准入、8cycle/64页、低水位与人工意图、busy/IOERR/维护SIGKILL恢复均通过；R15维护存储失败只有stdout、缺产品持久记录，见QA2-7。 |
| AC16 | 通过（已测恢复） | 当前CLI及维护hot journal重开保原字节/锁、原生正常exit0/clean-stop/锁释放/新source stopped；编排错误及缺间隙快照如实限定，kill不当断电。 |
| AC17 | 通过（R19 Owner路径） | 原始真实四页及最终UI操作链、同库副作用、新source停采/历史回执；未冒称QA2点击或native故障注入，stub仅补充失败/CAS。 |
| AC18 | 通过 | 当前薄IPC/deny_unknown_fields/camelCase/原键、单owner/1Hz cache/有界查询；当前CLI命令反例，未改11历史/6保存函数原始结果和Owner分页/modal/picker对应。 |
| AC19 | 通过（受控验证） | QA2当前20项/构建/CLI故障、未改Snap7和actual release/default反例原始证据、fixture工厂隔离与新源native链。无真实PLC/DB/API。 |
| AC20 | 通过（审计/交接项） | 当前双语键/占位符/347literal/33头部/44链接/9DAA索引和完整差异/角色/资源审计；本文件准确给出失败，不让DEV自检代QA或升级终验。 |

## QA2-7. 新F-003：维护失败缺少产品持久JSON Lines记录

**合同依据：** 批准R15要求采样/存储失败、容量暂停/恢复/缺口产生JSON Lines stdout及有界持久日志；local模式日志固定归profile的logs，不能借旧DAA_LOG_DIR外部路径。适用运行日志基线亦要求维护/外部存储失败留下可追溯结果。该要求不是新增验收范围，也不要求引入ACK、外部日志平台或第二任务系统。

**确切控制流：** 当前 [local_store/mod.rs](../../src-tauri/src/infrastructure/local_store/mod.rs) 274–280在`maintain()`返回错误后只调用`tracing::warn!(event="maintenance_failed", error_code=e)`。当前 [local_logging.rs](../../src-tauri/src/infrastructure/local_logging.rs) 14–26的`LocalLog::new`只设置JSON stdout formatter；有界文件轮转和`runtime.jsonl`写入在同文件`LocalLog::event`，不会自动捕获所有tracing消息。[local_supervisor.rs](../../src-tauri/src/services/local_supervisor.rs)的`LocalEngine::event`才连接该文件写入与runtime_events，而维护worker不走这条路径。`lib.rs` local分支也不会初始化legacy文件sink。

本轮真实60s分支的budget/busy反例确有maintenance_failed stdout，实际cleanup/vacuum IOERR也已证返回storage_error；源码对这些维护错误统一只warn，没有产品文件/账本或现有有界失败状态持久化。E内native-process.log属于DEV启动器捕获stdout，不能替代产品自身profile/logs中的有界持久记录。此发现以当前控制流和原始输出为据，**未**在Owner profile注入故障，**未**声称发生样本删除/损坏或维护预算又失效。Q/maintenance-logging-source-review.json封源码SHA/行片段；本QA没有修代码。

**解除条件：** Development在同r2有限批准路径内，使真实维护失败/延期路径至少按现有产品日志边界留下稳定event/process/阶段或资源/result/error_code的有界持久JSON Lines，同时保留stdout；不开放维护/ACK/SQL产品入口、不改schema/依赖或删恢复材料。定向证据需实际从生产worker路径触发拒绝/busy或受控IOERR，核profile/logs可解析失败记录和后续读写推进，保留原故障/失败历史；不必重跑未改UI/Snap7/解析全套。若产品日志本身不可写，应明确失败/未知区间，不伪报持久成功。再交精确新diff/源码/命令及developer_handoff，由coordinator启动另一次新的fresh-context Verification。若确需改变批准风险/allowlist/验收则回PM，不由QA自修或降低要求。

## QA2-8. 资源、限制与handoff

本轮QA2所有新CLI/维护故障child均已退出；没有新listener、visual server/tab、worktree、branch或ref。Q的3个公开CLI marked profile、4个关闭的维护故障profile及其复制证据、原journal副本、日志/结果/独立patch/原生短读快照、当前CLI副本和共享target缓存继续保留供返工/下一QA。QA不执行资源回收；临时路径之外，本文件已持久记录关键输入、结果、失败和限制。

按coordinator指示保留Owner native40013/父40012、原Vite75297/75299/75323/75331与49190、原marked native-profile和独立.app；QA2只读核归属，不发信号、不动窗口/锁/journal/样本/配置。live资源会随时间变化，不将其误封immutable；后续由coordinator核实际归属、证据与依赖再处理，不能按旧PID盲清理。

默认legacy回退路径保留；不授权真实profile迁移、恢复旧runtime备份、来源切换或数据清空。真实PLC/TIA/硬件吞吐/长期负载、生产DB/API、后台托管/多平台签名打包、Backend/SMA/DS协议联调、Stage C上传/ACK/冻结批次、Docker/Git发布和生产动作仍在范围外。源码/测试/Owner操作都不提供这些权限。

当前handoff是**QA2 qa_failed → coordinator → Development修F-003 → 新精确developer_handoff → 新fresh Verification**。Human Owner final acceptance保持**pending**；真实Owner原生观察不构成终验。QA2未授予最终验收，也未将两项旧failure关闭等同整个B通过。

收尾时独立DS文档又发生真实Owner设计验收后的状态变化：DS spec/checklist与四共享索引DS行改变，首次closeout严格diff断言真实exit1，已保存观察并交coordinator刷新，未回退或认领。最新foreign时间seal为`coordinator-qa2-return-20261018/foreign-refresh/foreign-drift.json`，SHA-256 `b045be30689250ebb1dfdc39cc2d3d08b8a7c27e321d65c193143380a32ff92c`；QA2逐项核11文档及四共享索引副本/当前hash，其他索引内容保持，88DEV/source仍精确。该独立文档验收不提供DS软件实施或DAA通过权限，也不改变初始baseline/DAA allowlist。

## QA1原始全文历史

以下BEGIN/END之间为QA1原文件逐字节原文，SHA-256仍为`8d8112aa26dfef4a5d616e385c8346300182fb08f451679f6711a0930018be4b`。其中“本轮”、旧H/Q、旧PID及未满足项均属于QA1当时；当前时间效力只以上方QA2结论为准。保留它不转移QA权威或回写过去。

<!-- QA1_CHECKLIST_VERBATIM_BEGIN -->
Task ID: DAA-002
Revision: r2
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Independent Verification found F-001 (required protected-cleanup counterexamples absent) and F-002 (maintenance writes bypass current space/journal admission); return exact r2 to Development through coordinator, then a new developer_handoff and fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-002 r2 独立核验

## 1. 结论与验证归属

2026-10-18（Asia/Shanghai），本轮 verdict 为 **qa_failed**。已验证的配置、采集、原子落盘、原生四页和恢复结果保留，但 AC14 的必需反例证据及 AC15 的维护写入准入尚未满足，不能将整个 B 阶段交给 Human Owner 最终验收。

实际 Verification 为 `/root/daa_stage_b_r2_verification`，由唯一 lifecycle coordinator `/root` 在正式 `developer_handoff` 后以新的 Verification fresh context 调入。本 context 不继承 Development 对话推理；独立阅读批准 bundle、当前实现、初始差异和原始输出，未沿用 A/CU/DS 的 QA 结论。已消费实际 `.codex/agents/verification.toml`；其中 `gpt-6.1-sol / max` 是配置证据，不冒称额外运行遥测。本 profile 为 `contract_only`，不宣称平台 ACL、强制路由或团队激活。

QA 仓内只创建本 `checklist.md`；没有修改 spec/tasks、产品、测试、配置或索引，也没有在验证中修复实现。失败只经 coordinator 返回 Development。Human Owner 原生操作回执只作为 R19 允许的观察证据，**不是最终验收**。

## 2. 精确输入、环境与保护面

已完整读取根 AGENTS、双语 README/PLAN、canonical lifecycle workflow、实际 Verification TOML，AW/DAA 最近 README/PLAN、`src/app/README.*`、local_store 说明以及完整 [spec](spec.md) / [tasks](tasks.md)。作用域没有更近的 AGENTS。当前合同是 spec §1–10 与最新批准补记；§11 是 r1 历史。

使用 `project-governance`、`aiis`（BLUEPRINT/CONTRACTS）、`rust-runtime`、`desktop-tauri`、`frontend-ui`（适用 DESIGN/FRAMEWORK）、`i18n-workflow`、`plc-point-mapping`、`code-document-indexer`，并消费适用结构/日志基线。局部 Rust SQLite/IPC 不扩为 Backend/Celery、打包或 tools 开发。

环境：macOS 15.7.7 / 24G720；rustc/cargo 1.89.0；pnpm 11.11.0。项目 Cargo/pnpm 均依既有锁，离线构建；未安装辅助依赖或修改锁。QA 启动器移除继承 DAA/VITE/SQLite 覆盖、TAURI_CONFIG 与 RUSTFLAGS，不输出原值。编译复用仓外 DEV `target/` 依赖缓存，由 Cargo 对当前源重新编译；Owner 实际运行的是独立 `.app` 副本，未被这些编译替换。

| 冻结输入 | 独立核对结果 |
| --- | --- |
| HEAD | `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，保持 |
| 批准 spec | SHA-256 `681b912b9920fa9ecc8ff6c22c23d2e9fb9a4aa31a761589ee1290173846681a`，匹配 |
| 正式 tasks | `developer_handoff`；SHA-256 `6ea1aadec04c18fee639708a39829e567d1540d5809a58c0f100357443a49c7b`，匹配 |
| Developer receipt | `59545b26563de0014ae3504b67d23d5af5a8a1f9daba4ca190474146e9403f99`，匹配 |
| Development manifest | `443d5ea589cf3c8292320b9e2f47edeb3fffb11161467d2a632f16faf2986f64`；88 路径当前字节、初始 before 和冻结 source 副本逐项匹配 |
| 全文差异 | QA 从初始 before 独立重建 542067 字节，SHA-256 `4020cff513ed1ed1dd7e179598f99f40c5e711a5bc3e91c80aa18a89b465283d`，与交接 patch 相同；78 实际变化、44 新增，不将继承 dirty 算本任务 |
| 最终前端 | 57 文件逐项匹配，交接 aggregate `600c35e30467c367f4d81cc8467e7693e31126fc4189a625d8d1c7de0495a8e7` |
| 原生 Mach-O | `.app/Contents/MacOS/runtime` SHA-256 `d04db079168c1be9424c0bbc9437da9adc9ae6b0ff9af681f6a30db855273992`；源码/构建/实际参数与最终 HMR 前端链均可核 |
| 依赖 | 541 个旧 registry package 版本/checksum 保持，仅增加已批准的 7 个必需包；rusqlite 0.32.1 / libsqlite3-sys 0.30.1，旧 ORM/Tauri/Snap7 不升级 |
| r1 历史 | 从 tasks 的原文标记独立重建 SHA-256 `7ffdc1600534efe4605ff7a022d9c8bc16a7f68d19748ccb0590cff759d607ef` |
| 证据附件 | 独立递归核对 403 个补充字节引用，无附件摘要不符；不把历史源码状态当当前源码 |
| 保护审计 | 1552 个原保护文件保持；11 个外来文档为另获授权的 AW002/DS 工作，单列归因；原 baseline/allowlist 未重置或扩大 |

证据根：`/private/tmp/daa-002-r2-gnwbdg79/`；本轮 QA 输出位于 `verification-r2-za4derlf/`（下称 Q）。DEV 最小冻结目录为 `dev/resume-native-final-reopen-20261018/developer-handoff/`（下称 H）。初始 `baseline.json`、`before/`、`allowlist-development.json` 与原审计脚本保留。

coordinator 在 QA 开始后只机械同步 10 个 DAA 索引行至 `developer_handoff / fresh QA running`，receipt SHA `8943721c83662efe0e7002c0568ec7e9b2233db647dd1dd6280c0aa5c333ac34`。它不是 QA verdict。外来 DS spec 在 QA 中继续做 r2 draft 文档自检；`foreign-r2-refresh` seal `81e143de575a9e2de48abbaeb049643562cfba3c9b956c5e4ce9848c8336cc1a` 之后，该已归属路径又变化，QA 实际观察 SHA `e5c92a6fb0ec2b7fbe4086a1dc1d27402c011c07464941363a063a4f364fe4b9`。已即时报告 coordinator；其余外来十文件及本任务 88 路径无漂移。该文档变化不是 DAA 依赖、实施授权或 QA 证据，最终时间性 seal 由 coordinator 刷新。

## 3. 独立命令、实际结果与失败记录

下表 Cargo/pnpm cwd 均为 `automation-world/data-acquisition-agent/`；`--manifest-path src-tauri/Cargo.toml` 指向当前实现。Cargo/Node 使用 Q/qa-run.py 记录完整 argv、环境处理、退出码、时间及 stdout/stderr；其他 Q 脚本保留输入与结构化断言结果。未运行真实 env/profile、设备/API、Docker、现场迁移或发布。

| 实际检查 | 退出码 / 实得结果 | Q 证据 |
| --- | --- | --- |
| `cargo fmt --manifest-path src-tauri/Cargo.toml -- --check` | 0 | `rust-fmt.*` |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib infrastructure::local_store::tests -- --test-threads=1` | 0；16 passed，0 failed，52 filtered，14.48s；当前新增 unknown-fixture 回归也实际执行 | `local-store.*` |
| `cargo test --offline --locked --manifest-path src-tauri/Cargo.toml --lib --features rust-snap7-driver owned_ -- --test-threads=1 --nocapture` | 0；4 passed，5.62s；仅自有 loopback，测试结束关闭 server/socket | `snap7-owned.*` |
| `cargo build --offline --locked --manifest-path src-tauri/Cargo.toml --features local-validation --bin daa-local-validation` | 0；当前 debug CLI 重编译 | `validation-build.*` |
| `cargo build --offline --locked --manifest-path src-tauri/Cargo.toml --no-default-features --bin aiis-data-acquisition-agent --bin aiis-data-acquisition-agent-runtime` | 0；仅静态构建后进行下述拒绝路径，无 GUI 启动 | `default-build.*` |
| `cargo check --offline --locked --manifest-path src-tauri/Cargo.toml --release --features local-validation --lib` | **101，预期拒绝**；精确 compile_error `local-validation is forbidden in release builds`，没有运行 release 程序 | `release-feature-reject.*` |
| `pnpm build --config vite.validation.config.ts --outDir <Q>/dist --emptyOutDir` | 0；vue-tsc + Vite，1687 modules；既有 PURE 注释及 chunk 大小 warning | `frontend-build.*` |
| `python3 <Q>/exercise-runtime.py` | 0；13 场景：裸帮助、4 factory 拒绝、5 激活 SIGABRT 断点、commit 前/后、产品 hot journal SIGKILL 恢复 | `runtime-process-exercise.json`、各自有 profile/transcript |
| `python3 <Q>/exercise-parser.py` | 0；9 反例实际走同 Rust import 服务，均有 file/line/path，未改变已保存草稿或 active | `parser-independent-results.json` |
| `python3 <Q>/exercise-guards.py` | 0；5 参数/模式/旧入口拒绝及 1 个新旧模式同 profile 锁拒绝；各子命令 exit2，全部只用 QA 自有 profile | `mode-guard-results.json` |
| Node 执行 Q 中重定位输出的 `test-history.cjs` / `test-save-candidate.cjs` | 均 0；11 + 6 个生产函数用例，只有 localCall stub；不作为 native/SQLite 证据 | `history-functions.*`、`save-functions.*`、对应结果 JSON |
| `python3 <Q>/audit-native.py` | 0；独立只读 native-profile，双库 integrity ok，76/76/76 与重开原表全同、912 点独立解码 | `native-independent-audit.json`、只读快照 |
| `python3 <Q>/audit-ui.py` | 0；4 locale pair 共 325/38/87/141 leaf keys、占位符/旧值保持，44 本地链接 | `ux-locales-audit.json`、`ux-link-audit.json` |
| `python3 <Q>/audit-ui-source.py` | 0；38 源文件中 347 literal keys 在真实 assembly 双语均解析；33 新源码有中文头部，CODE_INDEX 只增加 9 个 DAA 条目 | `ui-source-audit.json` |
| `python3 <Q>/audit-inputs.py` | 产品/源码/patch/旧依赖/r1/403 附件均通过；**exit1 仅保留已归属的 DS spec 后续 drift**，不能伪记全局 exit0 | `input-scope-audit.json` 与初次/中间报告 |
| 源码预算/反例审计 | 0；生成 F-001/F-002 的精确源码摘要和路径事实 | `findings-source-evidence.json` |

QA helper 的首次差异重建使用 `/dev/null` 新文件头，与 DEV 使用 `baseline/<path>` 的头格式不同；同时第一次库存未滤掉两个已删除 tracked 路径。只修改 QA 仓外 helper 后，完整 patch 字节精确相同、无未知新增。初次 helper 失败报告保留，不算产品故障。后续 exit1 为正在变化的已归属 DS 文档，未改原 baseline 或将其纳入 DAA allowlist。

真实 Snap7 检查使用新随机端口，未重试被拒的 49192 visual server。黑洞连接约 500ms，已连接慢读取剩余预算 400ms 时约 200ms 返回；连续读取 server client_count=1，坏 DB 保持会话，真正断连后完整坏轮和独立退避成立。此为驱动 loopback 证据，不能推广为硬件 CPU 或 DS 成品联调。

QA 自建进程场景通过公开 save → import preview/confirm → offsets preview/confirm → 分组保存 → activate 构造两 PLC/三 DB/36 点，而非伪造 derived fields。五个激活边界以 SIGABRT（-6）终止，Rust 重开 active=loaded 且连接/采集 stopped。轮次 COMMIT 前为 0 包，COMMIT 后为完整 2 个 pending 包/seq1；不存在半轮。另一次实际产品事务 cache_flush 后形成 **58880 字节** hot journal，控制器观察 magic `d9d505f920a163d7`，SIGKILL（-9）后由 Rust bundled SQLite 重开恢复，先前 4 样本和相关全表原值保持；未手工删 journal。全部 QA 子进程已退出。进程 kill 不证明断电耐久。

## 4. 新 B0 与 SQLite 适用性

独立核对新 B0 的解析/native 来源、逐连接 PRAGMA、锁竞争、hot journal、写失败/中断原始输出及实际最终 SQL，而非拿 r1 WAL probe 代替。旧 package 的版本/checksum 全保留；静态 bundled amalgamation SHA `c01235302fe80da901fb70c7622c39147e29d9f29b7f6eb746b23517f320c90d`。新 B0 原输出是 SQLite **3.46.0**、source ID `2024-05-23 13:25:27 96c92aba00c8375bc32fafcdf12429c58bd8aabfcadab6683e35bbb9cdebf19e`、默认 VFS `unix`，两库/多连接实际 DELETE / EXTRA=3、page4096、auto_vacuum2、FK1、busy1000。受控读锁 busy 约1045ms，释放后原子重试；interrupt约104ms后后续写推进；实际 IOERR_WRITE(778) 回滚和重开对账成立。它们是已审查的历史 gate 原始输出，QA 本轮另以当前产品故障场景复核落盘/恢复。

2026-10-18 通过 SQLite 官方资料重新核对：WAL-reset 只影响 WAL 的对应并发条件，3.46.0 **仍未修复**，DELETE 排除该前提；EXTRA 为 DELETE 提交后的目录同步提供额外耐久；unix-dotfile 的 hot-journal 修复不等于默认 unix 同样触发。依据：[WAL §11](https://sqlite.org/wal.html#the_wal_reset_bug)、[synchronous](https://sqlite.org/pragma.html#pragma_synchronous)、[3.47.0](https://sqlite.org/releaselog/3_47_0.html)。

也独立读取官方 [changes](https://sqlite.org/changes.html)、[covering-index 原复现](https://sqlite.org/forum/forumpost/e60e4c295d22f8ce)、[AND 投影原复现](https://sqlite.org/forum/forumpost/f4878de3e7dd4764)。最终 schema 为普通 rowid/普通列索引，固定参数 SQL；无对应 WITHOUT ROWID+partial UNIQUE、view/IN 子查询、布尔聚合投影、FTS/SQL JSON/任意 SQL/自定义 VFS。`CHECK(state IN ('pending','acknowledged'))` 是字面成员约束，不能声称“源码无 IN”。当前真实索引/全扫预期测试通过。以上是受限表面的适用性判断，不是 SQLite 全面安全或硬件同步保证；维护路径缺口见 F-002，不能由 B0 探针豁免。

## 5. 原生证据的独立消费与对账

没有重试 native getApp、Codex AX 安全拒绝或被拒 visual server；没有操作 Owner 窗口、连接、采样、ACK、重开、终止其进程或修改其 profile。R19 明确允许 Human Owner 实际操作与同库证据，故没有因自动化不可用降低必需 native 标准，也没有将 browser/stub 当 native。

独立核对的真实链条：Owner 保存/重载/退出、同 factory 重开草稿；修后两类弹窗/下拉保存与激活；两台 owned PLC 连接/启采/暂停及历史；最终原生 20 条分页/改10、只读详情 modal 原文/SHA/pending/折叠 manifest/context、不可自由输入的 datetime picker 反向区间错误/清空恢复、EN/深色/约半屏可达；最后 Cmd+Q 正常退出后同 factory 重开 stopped，Owner 再确认未连接/未启采与详情正常。

最终操作原话 `以上正常，已正常退出` 的 coordinator relay SHA `c1ff8e89237e5405618a771dbb798133d24c8b6d0adbadf08cf8cd377bc9cd9a`；重开可见状态原话 `均未连接、未启采，历史和详情正常` relay SHA `506c3a2d41a5ed53e06cfa68e9b7aeb5c8a9959d8268cc368a924dd9ed27431c`。题干、最终前端/二进制 fingerprint、原生进程退出和 SQL 证据各自区分，不伪称逐条 IPC 线包抓取。

QA 以另一只读控制进程打开本次明确 owned `dev/native-profile`（mode=ro/query_only，短读后关闭）。控制器自身 Python SQLite3.43.2 **不是**应用原生库来源。当前双库所有表与 Owner 重开后的封存完全相同；正常退出前到重开后，除 clean_exit/生命周期事件外，配置及全部 ledger 原值相同：

- 76 cycle / 76 sample / 76 pending；PLC1 26轮、PLC2 50轮，第三台 Test 保留且无样本。
- 912 个点观测按 fixture 原 DB 字节另用大端 BOOL/BYTE/INT/REAL 解码，全数相等；全部 origin=fixture、quality=good。
- 原 sample/manifest/context 字节 SHA、完整成员、opaque ID、revision、generation、十进制字符串 seq、原时间逐项一致；next_seq 分别27/51/1。
- 原样本 fingerprint `e4cd3c37c08643ff353a1c6e3e9bc95299d2d903b7dff28e0b77fdcb65678f1f`；active=used=`add0b620-ebce-4451-a2fa-8c9b7dc83de3`。
- 正常退出事件#84/clean_exit=1、实际 native exit0/锁自然释放；重开事件#85是 runtime_started/stopped，未新增 uncertain_gap、cycle 或 operation。SQL 不读取内存 connected/desired 状态，后者来源是 Owner 可见回执与源码默认状态。

F-001 未加载/陈旧及 F-002 旧 locale（这里指 DAA-001 历史编号）按当前生产函数/真实 SFC 既有证据及旧字节保护核对；没有冒称本轮在 native 注入 IPC 断网或 CAS 并发故障。本 checklist 的 F-001/F-002 是下节本任务新发现，勿与阶段 A 同号混同。

## 6. AC01–AC20

“通过”只覆盖获批受控 B 表面。DEV 输出仅为验证输入；每项结论结合本轮独立源码/差异/命令、原始证据及 R19 Owner 实际操作链。

| AC | 结果 | 独立结论与证据 |
| --- | --- | --- |
| AC01 | 通过 | 精确批准 SHA、B0 先行历史、88 路径/source/before、完整 patch、旧 r1 和保护面独立对照；无 A/CU 验收继承。 |
| AC02 | 通过 | 6 个默认/模式/旧入口/同 profile 锁反例及严格 factory；local mode 单 active owner、旧 IPC guard/health 隔离；保存和导航不接 PLC。 |
| AC03 | 通过（限定） | 新 B0 原始来源/两连接 DELETE+EXTRA、541+7 依赖、当前 SQL/官方适用性及产品恢复复核；未将3.46写成已修复。 |
| AC04 | 通过（常规读写） | 16 Rust 中身份/缺库/损坏/高 schema/WAL材料拒绝、CAS、排队/执行 deadline、连接释放/后续写及公平队列；维护预算另列 AC15 失败。 |
| AC05 | 通过 | Rust CAS/derived-field 防伪及 QA 公开配置流程；真实 Owner 保存/重读/正常重开同 ID；stale save 返回当前 ETag，不静默覆盖。 |
| AC06 | 通过 | 12叶 flat、7叶 nested/UDT/数组完整结构 golden；QA 再做缺UDT、循环、优化/未知优化、动态/多维/嵌套数组、unsupported、重复字段9反例，file/line/path与active保持。 |
| AC07 | 通过 | 独立 offset golden、BOOL跨字节/偶数对齐、INT/REAL/STRING/NaN/地址溢出；QA公开预览/确认，Owner manual0.0/依据/确认及保护持久链。非现场地址校核。 |
| AC08 | 通过 | 准入边界 Rust 用例、QA 两 PLC/三 DB/36 点跨 DB 组实际激活；native 两组1000/500ms，Test无组无采样；不截断成员。 |
| AC09 | 通过 | QA 五个激活持久断点逐进程 SIGABRT 重开 active=loaded/stopped；原生 token/解释/used 链与现有 previous 回退原始历史保持。 |
| AC10 | 通过 | 共享诊断/连接测试及重复 endpoint Rust 用例；真实 Snap7 owned 单client、自定义端口、坏DB/断连/退避及独立PLC；无第二探针客户端。 |
| AC11 | 通过 | 公平组/500–1000ms/跳tick/完整timeout用例及4个真实驱动loopback；native26/50轮与暂停后稳定账本；不作为硬实时性能承诺。 |
| AC12 | 通过（轮次事务） | QA COMMIT前0/后2pending、全成员/seq/manifest同事务；产品hot journal SIGKILL原4份恢复；既有真实IOERR/背压证据保留。维护故障不被此项代证。 |
| AC13 | 通过 | 当前raw/context分块与hash用例、QA原字节/912点独立解码、字符串seq/identity/generation/时间及正常/异常重开保持。 |
| AC14 | **未通过：F-001** | 76pending/无ACK后门已证；算法确有引用/完整数检查，但规格必需的“已确认仍有引用、cycle不完整”私有反例缺失，不能填pass。 |
| AC15 | **未通过：F-002** | 采样容量/70%迟滞、保守页级reserve、文件/journal/log计量通过；定时清理/增量回收未在维护写前核预算，且对应维护反例/恢复证据缺失。 |
| AC16 | 通过（已测恢复路径） | QA产品hot journal回滚、已提交字节保持及锁/正常退出；Owner最终CmdQ和同factory重开无自动连接。维护路径仍须随F-002补证，进程kill非断电。 |
| AC17 | 通过（R19 Owner路径） | 同最终源原生四页保存/激活/两PLC/历史、最终分页/modal/picker反向错误恢复及EN深色窄窗；stub仅补充冲突/失败保留，未冒称native故障注入。 |
| AC18 | 通过 | deny_unknown_fields/camelCase/原pointId、唯一local时钟/1Hz cache、<=100历史/64游标/原context有界字节；QA11历史函数/6保存函数和实际Rust/native链对应。 |
| AC19 | 通过（受控验证） | QA16 Rust、4实际Snap7、13进程/9解析/6模式反例及构建；actual release compile_error成立，fixture无真实transport/ACK；必需native按R19取得。 |
| AC20 | 通过（交接审计已落实） | 双语/占位符/347 literal keys/33头部/44链接/9条DAA索引/完整diff与角色链已核；本checklist纠正DEV对AC14/15的覆盖声明，Owner终验pending。稳定README仍有“native pending”的旧描述，返工收口时应同步真实状态，不据它抹除实际证据。 |

## 7. 失败与解除条件

### F-001：受保护清理的必需反例证据未交付（AC14；验证义务缺口）

已批准 R14 明确要求 private cfg(test) 覆盖“已确认但仍被引用/所属单位未完整的保留”，AC14 也指明 ACK/交叠引用/不完整 cycle 私有种子。当前 [tests.rs](../../src-tauri/src/infrastructure/local_store/tests.rs) 370–421 只创建10个完整cycle，将最后一轮的2个包改为ack，再确认前面pending不删、合格轮删除；整个测试文件 `sample_references` 和 `expected_samples` 字面引用均为0。本轮独立执行的16项测试通过，不能使从未构造的两种状态成为已验证。

[runtime.rs](../../src-tauri/src/infrastructure/local_store/runtime.rs) 308–330 确有 `samples.len()!=expected` 和 `refs!=0` 的保护。因此本发现**不是**已经证明算法删除了受保护数据，也不是要求实现产品 ACK API。它是明确必需反例缺失，DEV §7“ACK/引用/不完整cycle清理种子已测”的表述超过现有证据。

解除条件：Development 在现有批准 `local_store/tests.rs` 的 cfg(test) 私有新临时库内，实际构造已确认且有保护引用（含交叠引用的解除条件）以及所属cycle不完整的情形，执行真实清理，逐项核对保留/可释放的样本、pending/解释及原hash；保留运行命令/输出并准确更新 tasks。不得为补测试开放产品/validation ACK、任意SQL或清pending入口。

### F-002：维护写入绕过当前空间/journal预算（AC15；实现缺口）

[local_store/mod.rs](../../src-tauri/src/infrastructure/local_store/mod.rs) 270–283：每个 job 后，满60秒即直接调用 `cleanup_acknowledged(days)`，再执行 `PRAGMA incremental_vacuum(64)`。[runtime.rs](../../src-tauri/src/infrastructure/local_store/runtime.rs) 292–352 的清理函数只验证年龄、完整包数、ACK和引用，随后开删除事务；两处均没有调用 capacity/admit 或检查当前 free/journal/reserved budget。

[capacity.rs](../../src-tauri/src/infrastructure/local_store/capacity.rs) 确有按旧主库全部页计算的保守journal上界和32MiB维护reserve；采样/prepare_context也实际使用它。但该计算没有在上述维护写入前被消费/重核。可复查控制流为：一次job（包括只读快照）完成 → 满60秒 → 无条件维护；即便前一个容量快照已报告不可准入，也不会据此拒绝维护。低空间停止新轮次并不阻止这条写路径。R15 要求维护具有journal/空间预算，无法证明时按旧页全量预留或拒绝；现路径未达到该约束。

已核产品kill/IOERR演练覆盖轮次提交，未见维护 DELETE/增量回收阶段的预算拒绝、写失败或强杀后恢复对账；原始 `product-hot-journal` 不能替代这项。此结论基于实际源码路径及缺失的验收证据，**未**通过填满宿主磁盘制造故障，**未**声称已经发生数据损坏。

解除条件：Development 在同r2有限路径内使真实维护入口执行当前物理空间/旧页journal/维护余量准入（预算不足保留材料并拒绝/延期维护），补私有临时库的预算不足、清理/增量回收失败和相应kill/reopen对账；验证pending、被引用/不完整单位与原payload/hash不变，不手删journal、不降低EXTRA。保留精确新的diff、命令和失败历史，再交新developer_handoff。若需改变范围/风险/allowlist则回PM新Revision，不能在本QA中修复。

## 8. 验收审计、限制与资源 handoff

| 表面 | 当前状态 / 下一 gate |
| --- | --- |
| 已验证受控能力 | 上述源码/模式/配置/解析/采集/事务/原生四页/已测恢复结果成立；本任务整体qa_failed，不能将这些局部通过升级为阶段B验收 |
| 未满足项 | F-001与F-002交Development；精确新developer_handoff后由coordinator再启动新的fresh-context Verification，保留本次失败 |
| 原生自动化 | getApp长挂、安全拒绝、visual审批拒绝是已保留工具限制；本QA未重试或绕过；R19实际Owner路径已完成必需native观察 |
| Legacy/回退 | 默认legacy_snapshot保留；local双库不被旧writer/headless读取；不授权现场切换、恢复旧runtime备份或清数据 |
| 延期 / 排除 | 真实PLC/TIA/硬件吞吐/长期负载、生产DB/API、真实profile迁移、系统托管/多平台签名打包、DS协议联调、Backend/SMA、阶段C上传/ACK、Docker/Git发布与生产动作，均仍另批 |
| Human Owner final acceptance | **pending；本次qa_failed尚不能进入最终验收**；实际操作回执不构成终验 |

非本次阻断的结构观察：`tia_source.rs`840行、`local_supervisor.rs`716行、测试文件1266行超过适用拆分评审警戒线；职责仍分别位于parser/runtime/test层。本QA不扩allowlist重构，后续结构评审由Development/PM按实际必要性处理，不把行数单独等同功能故障。

资源：QA新建的marked tmp profiles、故障材料、原始命令输出、独立patch/只读快照及 `<Q>/dist` 全部保留，13场景及解析/模式检查的QA子进程均已退出，owned Snap7 server/socket已关闭。没有新visual server/tab、分支/worktree/ref，没有向共享registry安装辅助依赖。复用target是构建缓存，不替代冻结 `.app`/H 源码证据。

按coordinator要求继续保留Owner fixture-only native96764/父96762、Vite75297→75299→75323→75331及49190、`dev/native-profile`、原日志与所有历史receipt；QA没有给这些进程发信号、打开其窗口、写profile、删锁/journal或重开。它们及Q/H附件仍承担返工/复核证据，不能在当前QA中回收；由唯一coordinator核实归属、后续依赖和证据归档后处理，不按旧PID盲清理。

H的source/manifest/patch、Q中完整输入/输出和原生快照需保留到返工及下一fresh QA完成。关键事实、精确摘要、失败位置、结果及限制已在本文件持久记录；临时路径不是唯一解释。下一gate是Development返工，随后新的独立QA；QA不授予Human Owner最终验收、部署、发布或现场权限。
<!-- QA1_CHECKLIST_VERBATIM_END -->
<!-- QA2_CHECKLIST_VERBATIM_END -->
<!-- QA3_CHECKLIST_VERBATIM_END -->
