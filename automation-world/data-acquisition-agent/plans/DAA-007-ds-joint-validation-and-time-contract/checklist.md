Task ID: DAA-007
Revision: r2
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 于 2026-10-30（Asia/Shanghai）明确验收精确 DAA-007 r2；由实际 Verification 仅登记真实决定，原 QA verdict/失败/限制保留；阶段 B 仅在本次受控 DS 联调范围完成，资源由唯一 coordinator /root 另行收尾，阶段 C/自动启动策略/真实现场验证未启动
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA ManagedS7 到 DS 的有限双实例 S7→SQLite 闭环、上海时间、源码开发 profile 与显式运行控制、常驻 YAML 迁入退役
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-007 r2 PM -> Human Owner exact scope approval -> actual Development G1 -> fresh-context QA / Verification -> Human Owner final acceptance

# 独立 Verification 记录（2026-10-30，Asia/Shanghai）

## 1. Verdict 与适用范围

**QA verdict：`qa_passed`，仅限下表所列当前候选与受控本地范围。** 已独立核验当前源码身份、原 Development before/diff/raw、全部归档账本、必要纯检查及本轮完整闭库重开比较。未发现本候选需要返回 Development 修复的可确认实现 failure；当前无未解除的必需验证 blocker。

本结论使用完整证据链，而不是只凭正确最终值：原 r1/r2 精确增量和测试记录、当前逐文件 SHA、Owner 原生报告/截图、独立原字节/成员/序号核查、6 项定向 Rust 与 21 项 Node 用例，以及 QA 阶段先固定完整 8590 样本基线再重开的逐列/原文比较。Owner 原生动作和 QA 直接读得的事实分别标识。

**历史限制未被撤销。** 最早 15:21:50 退出的原 checkpoint 未取得；16:16:48 重开前也没有全部新增 7202 样本的独立 byte checkpoint。15:27 的 8 个 operation 完成事件及 4 个新增 bad 样本与 Owner“只打开查看，没点这些按钮”的报告仍有未明来源冲突。新的可核重开案例证明本次有限 AC14 行为，不追溯证明上述窗口无动作、修复了某个根因，或证明所有未来重开均安全。最终接受时须继续向 Human Owner 呈现这些事实。

## 2. Fresh context、职责与输入身份

- 实际 Verification：`/root/daa007_r2_verification_1`。由唯一 coordinator `/root` 在实际 G1 `developer_handoff` 后调用新的 `verification`、`fork_turns="none"`；本上下文没有 Development 的对话推理，只消费交接和独立读取的原件。
- 项目 `.codex/agents/verification.toml` 配置为 `gpt-6.1-sol / max`，仅是配置证据，不声称独立观测了平台运行 model/effort。profile 为 `contract_only`；fresh-context、串行交接和 diff/checklist 是合同控制，不宣称 ACL、强制路由或 Agent Team activation。
- 已独立读取根 AGENTS、canonical workflow、角色配置、根/AW/DAA README/PLAN pairs、DAA app/local_store 说明、DS 最近 README/PLAN 与相关指南、**完整当前 spec/tasks**、原 r1/r2 before/diff/候选/raw、当前实现及 Owner/闭库工件。作用域没有更近的 AGENTS。
- 使用 `project-governance`、`aiis`、`rust-runtime`、`desktop-tauri`、`frontend-ui`（适用 FRAMEWORK/DESIGN）、`i18n-workflow`、`plc-point-mapping`、`code-document-indexer`；只用于核验。无 Backend、Celery、打包、根 tools 或新增 lineage 工具范围。
- 正式工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD=`8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，dirty。未创建或采用临时源码副本，未提交、推送、切换 Git refs。

| 输入 | 独立核得 SHA-256 / 结论 |
| --- | --- |
| 已批准当前 spec | `e1838a6af98e0f679b0750b11441c359437200d1a9d11eef618e703d70e1ccc5`；r2/owner_approved，批准草案及 Owner 原话在 spec§1/§10，未改 |
| 实际 G1 tasks | `42e0fe8359945740fa646482c9da60fea0e23d5e3eacceec2588030e1241fc69`；r2/developer_handoff，保留全部原 r1/r2 与补证历史，未改 |
| F/handoff-evidence-manifest.json | `7c3307629534e4dc553b897b1de1254e020618262ce0a93be5539f27d535354e`；36 工件 bytes/SHA 全匹配 |
| F/handoff-source-manifest.json | `f51a8f3c64b59ac927fb8b9dbfd5b41cb80e80282eccb255d03061b117acf206`；541 输入 aggregate=`0b3bc5502023f78004d1d2941e8bbee3fa73655b7e50f162984f5b8fb9a3d4b9`，按排序紧凑 metadata 映射独立重算匹配 |
| coordinator 的 G1 索引 overlay | manifest SHA=`c75b6bf30181494d9d14568a2700d7cddb73749d8e63b7a4e90f63aa74b49ff7`；14 文件均仅精确替换 DAA-007 行。541 内只有 DAA/DS 的 4 个 PLAN 与 F 不同，恰匹配其 before/after；无代码漂移 |
| QA 开始的当前 541 输入 | 含上述 4 个索引 overlay 的 aggregate=`da6ee09a0ae778f62503f99d26d3006aca53fe0005503f8345760504c48f49b3`；验证前后源码输入均未改变 |
| 原 r2 冻结候选 | dev-candidate SHA=`5a2c298727f227b8993085fdd55f8f9159cce712c941f56867e6c28267dadd88`，51 路径 aggregate=`740207f8a547ade835bcc1cfaa5415bc397c17a4dc144312f4c14a91c3638426`；不是当前复合候选的另一名称 |
| T1 原 checkpoint manifest | `d85d4825f9c2af23646261b2aa4b845028366de3f0ec07ea5b28729ef607c6e1`；24 原工件全匹配，没有把 T1 倒称为 15:21 首次退出账 |

独立用 before 全文与原 patch 在内存重建 r1 的 32 路径、r2 的 51 路径，逐文件及 aggregate 与原 candidate 全匹配；实际增量分别为 31/32、32/51。根 AGENTS 只新增获批那一条 Tauri 规则；DAA Tauri 只变 `build.features=[rust-snap7-driver]`。原 r2 `package.json`、Cargo defaults、锁/依赖及驱动/actor/decoder 保护面未借该增量扩大。

原 r2 之后的 DS/core 唯一 UDT 解析、DAA 选中分组/保存后编辑、DAA 只读样本详情及 DS 专用版本管理分别归独立 DIRECT。前三组 37 个已列工件的 SHA 亦匹配；对应 before/patch/report 与当前逐文件来源可追溯。DS 版本功能只作为当前有限联调输入采用，不授予 DS 产品/版本删除/发布功能的新接受，也不把其变化倒记为旧 QA4 或原 r2 测试。原 r5 与 DS-001 的 Owner 接受已读取所属记录；其独立 QA 例外不转移本任务。

## 3. 环境、真实命令与结果

macOS 15.7.7 / Darwin arm64；rustc/cargo 1.89.0；Node 22.19.0；pnpm 11.11.0。辅助 Python 3.9.6 / SQLite 3.43.2 仅为外部只读证据读取器；不是产品 bundled SQLite 3.46.0 的版本证明。没有安装依赖、修改锁、升级工具链、修改宿主时区或用户终端环境。

下文 `Q`、`F`、`T1`、`V1`、`V2` 的绝对持久路径见§7。QA 工件都写 Q；仓内只新建本 checklist。

| 实际 argv | cwd / features / 真实结果与证据 |
| --- | --- |
| `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --no-default-features --lib startup_env` | DAA 根；driver/validation 关闭；exit0，**2 passed /65 filtered**，Q/daa-startup-env.log |
| `cargo test --manifest-path src-tauri/Cargo.toml --locked --offline --no-default-features --lib resident_retirement` | DAA 根；无设备传输；exit0，**3 passed /64 filtered**，含准入 true 的已保存 active 配置两次打开仍停止、0样本，Q/daa-retirement.log |
| 同式 `startup_env` | DS 根；native-s7/test-automation 关闭；exit0，**1 passed /0 filtered**，Q/ds-startup-env.log |
| `pnpm exec node --test tests/time-and-history-preferences.test.mjs tests/point-editing.test.mjs tests/sample-details.test.mjs` | DAA 根；exit0，**21 passed**（3+10+8），Q/daa-node-pure.log；使用真实 TS/SFC 与隔离 IPC double，不是 native/S7 测试 |
| `python3 Q/verify_inputs.py` | 仓根；exit0，F36/T1-24/V1-23/V2-84 工件、原始候选重建、索引单行 overlay、DIRECT 工件及原 13 项 final raw 身份全部成立，Q/input-audit.json |
| `python3 Q/verify_ledger.py` | 仓根；仅读归档原投影/JSONL；exit0，4295轮/8590样本全部重算，0结构差异，Q/ledger-audit.json |
| `python3 Q/verify_static.py` | 仓根；exit0，479 paired keys/占位符、263 common literal references、13文档117本地文件目标、两模板单键、入口/调用图/索引与限定 diff-check 通过，Q/static-audit.json |
| `python3 Q/capture_qa.py before` | 仓根；exit0，16:44:27.993+08 完成；仅明确获准且已关闭的原 DAA 合成 profile，Q/store-before/ |
| `python3 -`（比较 QA before 与 F G1 原件） | 仓根；exit0，两库全表全原列、schema 及 config/runtime/log bytes SHA 均相同，Q/before-vs-G1.json |
| `python3 Q/capture_qa.py after` | 仓根；收到 Owner 精确关闭报告后执行；exit0，16:52:43.341+08 完成，Q/store-after/ |
| `python3 Q/compare_qa_reopen.py` | 仓根；exit0，16:53:46+08 全量业务原列/原文/身份/序号比较通过，唯一允许追加为两条 lifecycle，Q/qa-reopen-comparison.json |

Rust 子进程仅覆盖 `TMPDIR=Q/fixture-temp`、`CARGO_NET_OFFLINE=true`，使用现有共享 target；测试自造的 env/profile 与 Owner profile 分离。**全部为非零过滤用例**。新 lib test 仅保留既有 `empty_for_test` dead_code 告警；未放宽保护或消警。未启动/驱动 DS、DAA 原生、S7 客户端或监听，未运行旧全 B/DS/容量/76样本/完整导入矩阵。

原 V2 84 工件和 13 项 final 的真实 argv/cwd/features/exit/raw SHA 已逐项核准，包括普通 driver check/link、DS native/test-automation check、DAA frontend build、类型、fmt 与静态结果；均保留为 **Development** 证据。原 r1 4 项 `time_contract` raw SHA=`035c51b4321a4369514c55fe4c4534c140e8ef73d3085294cb39ad7a1825ef27`，3 项 Node raw SHA=`f45e4af15e36f95d868c49815f1a7aa4406d348fb113ef013ed45d115d73f5fd` 已匹配。时间/存储/日志核心与原断言未变，历史表后续变化仅为独立只读详情接入；不机械重跑原 Rust 时间/旧全套。当前详情与分组源码的有限 Node 检查已新跑，后续 DIRECT build/隔离 UI 工件单列，不把原 freeze 的 build 宣称为当前全部图的新构建。

保留原 DEV 的编译缺测试 import、旧 seed helper 的 source_identity_conflict、早期格式/static 失败及修正 raw，未用通过覆盖。QA 的探索性辅助脚本曾因 r1/r2 manifest 字段和历史 patch 的 `NEW FILE` 格式不同而中止，修正读取适配后才取得上表最终结果；不计产品失败。第一次 guarded capture 在 `/bin/ps` 被 sandbox 拒绝时即停止，**未开 SQLite**；随后获只读 escalation 后完成 ps/lsof 和 capture。未发生 automatic approval review rejection。

## 4. AC01–AC22 核验

`pass` 均限该行明确的受控证据。Owner 的完成报告/截图不写成 QA 直接操作或直接观测；此前明确未做的 B 异值和 A 恢复由后续独立事实补齐，原记录保留。

| AC | 结果 | 独立核验与证据边界 |
| --- | --- | --- |
| AC01 | pass | 精确批准 spec/tasks SHA、r1 原字节归档、before→patch→候选重建和封闭增量成立；实际角色/交接与单一 coordinator 分开。Q/input-audit。 |
| AC02 | pass（有限采用） | 已读 DS owning acceptance，历史306a/QA4、DS-001及后续 DIRECT 与本 r2 bootstrap 分层；当前541输入/接口/feature已固定。只验证本次所需读链，不重新接受 DS 全产品。 |
| AC03 | pass | `package tauri`→Tauri build.features→Cargo optional driver 接线正确，default=[]；普通 env/读键有限测试通过。Owner 按手册普通命令的报告、真实 s7 原样本及最新同 profile 普通重开相符；实际 env 内容/进程读键未由 QA 窥读，相关启动动作和未设覆盖由 Owner 报告承担。 |
| AC04 | pass | 两库 schema/user_version/time_profile 与 payload2/context1 矩阵直接核得；锁前 RO/锁后复核源码与原4项真实 Stores 测试/raw匹配。legacy 分支零目录/字节变化、锁后漂移可留下锁的区别保留；诊断壳保留具体错误、无业务 engine。未开默认旧库。 |
| AC05 | pass（Owner+原账） | DAA 原配置核双PLC30102/30103、rack0/slot1、Alpha71/4B、Beta88/8B、各6点/类型/地址；DS模型/TSAP/策略按 Owner M02/M06 完成报告，补证图1直接显示 B loaded v18 六个指定值。QA未查询仍运行 DS 的 SQLite，不把 DAA 字节冒称 DS 数据库读证。 |
| AC06 | pass | 当前 draft/revision/context 各 PLC 恰 Fast500两BOOL、Slow1000其余4点，全部启用/地址确认、单一 group、每组跨两DB；无未选声明、UUID/technical name/sourcePath 分工正确。Q/ledger-audit。 |
| AC07 | pass（受控本地） | 全8590 payload origin=s7，逐轮exact成员/两DB/原SHA成立；当前双PLC active版本A Fast94/Slow48 good，B Fast2444/Slow1225 good，各超过2轮。短连续间隔中位数500/999/500/1000ms；B不同值不串A。单点诊断/连接复用由Owner M06报告与同一串行actor/transport源码支持，未由QA新建客户端计数或重跑协议。 |
| AC08 | pass（Owner+原账） | 暂停/恢复与普通UI写由Owner M04/M05报告承担；原S7 good包含ready两态及A同时111/13.25的81个Slow轮，历史原包保留。后续A回到101/12.5按实际版本/运行事实标识，不把早期动态值冒称后期恢复值。未补造准确暂停时刻或同步截图。 |
| AC09 | pass（窄项补证） | 原Owner明确“这里没做”的恢复缺口保留；后续原截图、lost16:15:43.119/restored16:15:58.964及其后36个A good轮闭合。两事件间B **48个已保存**good轮（47个在窗口内开始，1个跨起点），不是新测重启到重连15.845s。失败轮null/bad_read保留，断线不造每tick行。 |
| AC10 | pass | 77109处已列业务/point/read/log日历字段格式核验、事务同savedAt、外部offset规范化与SQL/query/maintenance helper源码及原4项raw成立；stdout新纯检查亦实际输出+08纳秒，文件毫秒。Unix/monotonic/顺序不作日历转换。 |
| AC11 | pass | UI time helper、墙上时间 value-format、终止秒.999、分页/质量条件与原 Stores/新 Node 断言成立；最老pending/陈旧视图使用相同helper。原JSON/SHA保留；Owner M08及最新历史详情正常为原生层报告，非QA驱动界面。 |
| AC12 | pass（工具+Owner报告） | 历史稳定column-key/min/横滚/固定操作列、按app/table/field存本机偏好及reset源码成立，3项时间/偏好与相关SFC纯检查通过；Native拖拽/切页/重开由Owner原M08/M09总体完成报告承担，没有新QA原生鼠标操作证明。后续详情表列宽属独立DIRECT，不归原r2新增表范围。 |
| AC13 | pass | 全4295轮/8590样本原SHA/bytes、context/revision、point定义/exact成员/两DB/manifest引用、pending一对一、sourceSeq与next_seq全部重算0差异，无孤样本/半轮/重复delivery/ACK。并以QA直接闭库投影核F全表相同。 |
| AC14 | pass（QA中补齐） | 原G1只具T1子集及无增长时间线，**不足完整新增行重开前后byte证明**。本QA先直接固定当前全部8590原样本，再由Owner一次同profile无控制重开/正常退出，随后全表全原列比较：配置、payload/manifest/context/SHA/ID/generation/seq/delivery均相同，0新增样本/操作，仅两条正常lifecycle。见§5；没有降低AC或倒补早期窗口。 |
| AC15 | pass | 原13项DEV raw及其候选已审计，当前必要6Rust/21Node和静态/全量RO比较真实通过；编译/原生/DS旧QA不混称。标准启动与模板活动键/本地链接、试行手册的当前状态准确，未重跑旧全矩阵。 |
| AC16 | pass | 实际fresh Verification、当前checklist、QA/DEV/Owner分层、持久证据和资源依赖齐备；只交Human Owner最终决定，不代授B/C或旧任务接受。 |
| AC17 | pass | 普通bootstrap不构造MigrationPaths、engine不调用startup/discover；历史算法cfg(test)。新空v2真实engine空配置/无PLC_1/source/receipt/ETag迁入用例新跑通过，旧locator畸形亦不探测。 |
| AC18 | pass | composable reload/save和配置栏迁入调用/弹窗解绑；summary只读真实SQLite、视图retryAllowed=false，retry立即拒绝。自造receipt/source原串、hash、ETag与save/prune保护有限用例新跑通过；无真实receipt变更。 |
| AC19 | pass | DAA2/DS1 startup用例覆盖优先级、空回退、明确错误不旁建、字面/不可解码/不规则文件；ordinary bool缺失/true允许后续显式动作，false/空/非法/不可解码拒绝，文件残留忽略。active配置准入true仍两次停止/无新样本用例新跑通过。 |
| AC20 | pass | 字面parser、不扫描其他root、不执行shell、不新增依赖/IPC/锁；正式配置只改必需feature。validation mandatory fixture/继承环境/marker/release拒绝与DS test-automation manifest权威源码/原非零raw/编译记录保留；普通默认未逃逸测试边界。 |
| AC21 | pass | 两模板各一个可选profile键；双语README/指南实际优先级、UI+SQLite和显式控制、高级deny/旧键、安装版边界清楚。AGENTS仅一条规则。沿用原Owner合成profile，QA没读写env、切库、seed或批量改其他app。 |
| AC22 | pass（保留历史） | r1归档、r2原失败/候选/角色与当前G1均保留；Owner所报步骤和原账＋必要受影响补证＋本QA完整M09比较形成当前有限闭环。早期非连贯/漏做/未知来源不改写为当时成功；QA豁免未转移，B/C未越级。 |

## 5. AC14 必需证据缺口与本 QA 的精确闭合

开始QA时，F当前原SHA/成员正确、T1原1388样本保留、16:16最后窗口0增长三者仍不能逐字节证明全部新增7202行在重开前后相同。QA将此作为**尚待核验的必需证据缺口**报告 coordinator，没有先发 qa_passed、没有把它改成 deferred gate，也没有修改 spec/tasks/实现。

按 spec D07、R09–R10、AC14，采用同一候选的受影响项补证：

1. Owner此前明确已退出保持关闭后，QA在16:44:27.993+08完成完整 **before**；两库全表原列及 config/runtime/log 原文件SHA均与 F G1相同。固定4295轮/8590样本后才通知 coordinator 可重开。
2. coordinator只 relay一次最短原生步骤：同源码、现有.env、原profile，普通`pnpm tauri dev`；等页面载入、核未连接/未启采/pending8590，查询并打开一个既有样本后正常Cmd+Q。**没有新增60秒固定等待要求**，没有保存、激活、连接测试、诊断、连接、启采、DS或配置动作。全部原生由Owner执行。
3. coordinator转交Owner精确原话：**“未连接未启采、8590、历史详情正常，已退出并保持关闭”**。Q/owner-qa-reopen-confirmation.json如实记录其来源，不冒称QA直接看见原生状态。
4. QA立即重新确认闭库并于16:52:43.341+08完成 **after**。全量比较于16:53:46+08完成。所有业务表全原列相同，配置整文件SHA相同，runtime只新增runtime_events id90/91；原日志字节前缀完全相同，追加start/stop两行。

| 比较面 | 完整 before→after 事实 |
| --- | --- |
| samples / collection_cycles | **8590→8590 /4295→4295**；逐行全部原列、payload/manifest原串、SHA/bytes/point定义完全相同 |
| 配置/身份/上下文 | 两库instance=`99f8a911-3bea-421c-a9d4-75759cb1e296`；全部draft/ETag/revision/source/active/previous/intent/journal/context原列相同；used/active=`c7e027a3-b366-493f-ad29-0cd0c123234e` |
| source generation / next_seq | A=`167e769e-9b6f-4f1c-9b4c-55e133f6d3e9`，seq1..625/next626；B=`1650baae-a148-4d12-9ba2-182dc60425c7`，seq1..3670/next3671；完全不变 |
| delivery/reference/排序 | 8590 pending、0ACK、0reference，sample_order/sqlite_sequence不变；无新增业务样本，最后savedAt仍16:16:11.174+08 |
| 新lifecycle窗口 | runtime_started16:49:50.350+08 / result=stopped；runtime_stopped数据库16:51:57.707+08 /文件16:51:57.706+08 / clean。分别为真实日志生成与事件保存，1ms差异不伪称同一时刻；0 operation_completed/connection事件 |
| config.sqlite SHA | before/after均`3c87ac2ab04ba35fb470ec7caaa6321335539b4105401511b910a7fcbdfb1ec4` |
| runtime.sqlite SHA | before=`b397627f8c844224616874ace793f6b9b5b2c10687fd61d14b2c159cb5c57491`；after=`efc0fcac9ea1ddbdf694c0615d9395c009d60cf1da12dd6e9385dc8f9d73c948`。整文件允许lifecycle写入变化，未要求其假相等 |
| runtime.jsonl SHA | before=`acdc84dc9e22a4028992b567bf6300c737ea042444e0a31e6725c802f51b11de`；after=`cbfdc3a7dcf6390b39a8de288ec81c431b35858fc42f25c659c566d70aa8bbce`，仅上述两行追加 |

两次QA capture均先后检查：ps无DAA、lsof指定profile exit1/无输出；DS PID86440仍运行而未触碰其库。所有祖先/文件非symlink，SQLite头DELETE1/1、无journal/WAL/SHM，末条clean；2秒metadata/bytes稳定后才mode=ro及连接内query_only。两库integrity_check=ok、FK空、schema/user_version2。每次读取前后size/SHA/mtime/ctime/inode/目录完全不变。所有SQL均存各自 readonly-sql.json；无immutable、ATTACH、backup、恢复、DDL/DML、持久PRAGMA、seed/ACK/删除。

本补证在尚未作最终 verdict 的同一fresh QA中完成，不是实现返工或新的Revision；当前spec允许Owner原生和闭库后DEV/QA只读核验。新完整case闭合当前AC14，不补造原15:21/16:16快照，不把T1子集包装成完整before，不消除旧15:27来源未知。

## 6. 保留失败、限制与 Acceptance Audit

- 原15:27:16.769启动之后8条operation_completed、15:28两个新读轮/4个bad样本是真实原件；Owner否认控制点击亦原样保留。源码新建状态停止、只有Action消息更改连接/采集意图，前端mount/watch只有reload/refresh；shutdown join actors再join writer，旧进程在途轮不能解释这些新startedAt。**持久日志缺action/caller/operation ID，当时binary/source运行来源未完整固定，根因仍未知。** 本QA没有给Owner归责，没有确认/修复autostart defect，亦未据最终正态清掉异常。若后续实际复现或需加审计/改actor，由Development/PM按精确范围接续，不能静默扩大本任务。
- 15:21原首次checkpoint和16:16全新增行before仍缺失，T1以前284旧样本亦无完整逐行before；只证明其当前原SHA与T1→F→QA full-before→after保留事实，不声称此前每行从未变动。
- B最初值与A相同、首次M07恢复未做的历史保留。补证B count202/REAL25/BYTE86/120各1179个good点事实，running=true2356；A同期101/12.5/false/18/52。故障后A36个good完整轮的savedAt16:15:59.100..16:16:10.663；startedAt16:15:59.024..16:16:10.581，不能互换时间语义。
- 48个B已保存good轮中，一轮started16:15:43.079、saved16:15:43.178跨lost事件16:15:43.119；A实际bad轮started/finished16:15:43.045、saved16:15:43.117，早于lost日志2ms。该轮两样本null/bad_read保留。15.845s是lost→restored并含DS停机时间，未获精确重启动作时刻；不称重启重连耗时或吞吐/实时保证。
- Owner截图只证明各瞬间，非跨PLC/DB原子快照；Owner总体完成报告承载未逐动作取证的M01/M02/M04–M06/M08/列宽原生操作。当前新native补证只增加停止态、pending与既有详情报告。QA没有native鼠标/双语拖拽、DS库、完整IPC调用追踪、长期运行、实际PLC、安装包或跨平台证明。
- 原DEV `empty_for_test`、第三方PURE/chunk warnings和早期失败保留。当前controller默认停止不等于未来auto-collect/upload方案已批准或实现；本候选不实现该未来方案。

| Area | 当前验收层次 | 下一gate |
| --- | --- | --- |
| DAA-007 r2受控本地闭环/时间/配置/退役 | 当前候选独立QA通过；异常历史及证明限度按上文保留 | Human Owner决定本任务最终接受与上述已知不确定性 |
| DS产品、后续DIRECT版本功能 | 旧r5/DS-001接受及其原QA/例外保持；本QA只有限采用当前DS读链 | 后续DS能力按所属工作流决定，不授予新DS产品接受 |
| DAA-002/003/004等旧任务 | 原bundle的QA/Owner pending不被本任务代验或覆盖 | 各自真实Owner最终决定 |
| 整体Stage B | **仍open**；局部QA不等于整体验收 | Human Owner明确整体B决定及其它必要gate |
| Stage C / Backend / SMA / upload / ACK | 本任务排除，未实现/验证或授权推进 | 稳定后端合同及独立批准 |
| 旧UTC profile迁移、真实配置/PLC/生产、发布/部署/安装版.env | 原件保留；本任务不操作 | 独立批准与目标环境证据 |

## 7. 持久证据、资源与handoff

- `Q` = `/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030`；本次QA独占证据目录。
- `F` = 同一父目录的 `daa007-r2-followup-joint-reconciliation-20261030`；原G1 36工件及coordinator索引overlay，未覆盖。
- `T1` = 同一父目录的 `daa007-r2-m09-first-checkpoint-20261030`；原checkpoint、诊断/Owner报告，未覆盖。
- `V1` / `V2` = 同一父目录的 `daa007-r1-execution-e6s14xue/development` / `daa007-r2-execution-odtninl_/development`；原23/84工件及失败记录，未覆盖。

主要QA附件：[输入审计](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/input-audit.json)、[全量账本](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/ledger-audit.json)、[定向命令及raw SHA](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/focused-results.json)、[静态与环境](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/static-audit.json)、[完整QA重开比较](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/qa-reopen-comparison.json)、[QA证据清单](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r2-fresh-qa-20261030/qa-evidence-manifest.json)。两份完整投影、原JSONL、闭库/文件状态和SQL分别在Q/store-before及Q/store-after；不是供产品启动的runtime数据库副本。清单固定本checklist和QA附件的最终bytes/SHA，清单自身SHA由handoff报告，避免自引用。

Q以及F/T1/V1/V2、独立DIRECT工件和本checklist共同持久保留，Human Owner最终决定/必要复核结束前不回收。原Owner合成profile保留8590 pending及全部历史；真实.env/默认profile/旧76样本完全不动。Q/fixture-temp只有本次辅助编译留下的xcrun_db，其余成功自造fixtures由测试自行收尾；不把共享target/node_modules或DS并行资源算作本QA独占资源。QA未启动需停止的服务、未清理资源；回收仅由coordinator在确认归属、无占用及证据/后续依赖解除后处理。

精确handoff给唯一coordinator `/root`：本checklist的`qa_passed`用于relay Human Owner最终验收；索引只可据此机械同步。无需更多本轮原生测试。没有更改spec/tasks/产品/测试/config/env/profile，也没有利用QA做实现修复；已知历史未知来源仍应随最终交付呈现。

## 8. Human Owner最终验收

**Pending。** Owner的原生操作完成报告与本次QA补证关闭报告不是本任务最终接受，也不是“接受整体阶段B”。本checklist不代录尚未发生的Owner决定，不授予发布、部署、设备、数据库写入、Git/GitHub推送或外发权限。


<a id="owner-acceptance-r2"></a>
## Human Owner 最终验收登记（2026-10-30，Asia/Shanghai）

**当前状态：`owner_accepted`；原独立 QA verdict 保持 `qa_passed`。** 上方 §8 的 Pending、§6 的整体 Stage B open 及相关未授予接受表述均是 QA 交付时点的历史；其当前效力由本节的真实 Owner 决定取代，原文原样保留。

本次由实际 Verification `/root/daa007_r2_verification_1` 按唯一 coordinator `/root` 在当前根会话转交的真实 Human Owner 决定登记。它是验收事实记录，不是新的 fresh-context QA、Development 或本角色代作接受。已完整消费四个 bundle；本任务登记前最新记录为：本轮独立 QA（2026-10-30），当前精确复合候选 AC01–AC22 通过。

Human Owner 原话（四个精确 Revision 的共同最终决定）：

> 验收 DAA-002 r2、DAA-003 r1、DAA-004 r1、DAA-007 r2，确认 DAA 阶段 B 在本次受控 DS 联调范围内完成。已知历史证据限制和来源未明事项按核验记录保留跟踪。请完成验收登记及无依赖临时资源收尾，保留已有 SQLite 配置、历史和联调 profile。阶段 C、自动启动策略及真实现场验证另行推进，本次不启动。

本任务接受范围：接受精确 DAA-007 r2 当前复合候选的受控双实例 DS S7→SQLite、上海时间、源码开发 profile 与显式运行控制、常驻迁入退役范围。原 AC01–AC22 的有限通过及 QA 阶段完整 8590 样本 before→Owner 同 profile 重开→正常关闭→after 比较保持；本次不新增原生/协议/SQL 验证，不替 DS 整个产品或后续版本管理功能授予新验收。

原失败与限制：最早 15:21:50 首次退出 checkpoint、16:16:48 重开前全部新增 7202 行的独立 byte checkpoint 及 T1 以前 284 行完整 before 仍缺失。15:27 的 8 个 operation_completed 与 4 个新增 bad 样本和 Owner 无控制点击报告之间的来源冲突仍未明；日志缺 action/caller/operation ID，不归责 Owner、不宣称已定位或修复根因。后补完整 M09 案例不追溯补造早期窗口证明，所有其他原失败/观察与时间语义限制继续保留。

原 QA 附件关系：原 `qa-evidence-manifest.json` SHA-256 `76dec3d7bce878fa2a3f5ccb53090603ce6ac00e64e2b2d49fb0e4306ebcac16` 保持不改，其 checklist 项固定的是本次登记前全文 SHA `b7fb71d0b49fb6c5c73381bd0b5204f3237f1f997b93df345272b2f0bd2dd188`。新验收附件保存该全文及原 QA manifest，并记录本次 after SHA；当前文件因真实验收登记变化，不据此误报旧 QA 清单损坏。V1/V2/T1/F/Q 等现存持久证据继续保留，本次不重做原核验。

阶段边界：Owner 明确确认 DAA 阶段 B **仅在本次受控 DS 联调范围内完成**。阶段 C、Backend/SMA/上传 ACK、自动启动策略及真实现场验证不由本次接受启动；当前默认停止策略保持，不推断已实施或批准未来自动采集/上传。真实配置/profile 迁入、真实 PLC/生产库/API、安装包/跨平台、发布部署/Git 或外发动作不在本次登记中执行。

资源 handoff：根协调会话 `/root` 另行盘点、归档和收尾，本角色未清理任何资源，亦不声称清理已完成。必须保留已有 SQLite 配置、历史、联调 profile 和现存证据；原文中的旧 PID/临时资源状态仅属其记录时点，不当作当前存活遥测。

登记证据：[验收前 checklist 全文](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa-stage-b-owner-acceptance-20261030/verification/before/DAA-007-r2/checklist.md)、[验收登记证据清单](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa-stage-b-owner-acceptance-20261030/verification/acceptance-evidence-manifest.json)；清单另固定本任务 spec/tasks 全文前像、登记后 checklist 与四文件增量。除顶层 Status/Handoff 和本节追加，原 QA 正文及所有失败历史逐字保持。
