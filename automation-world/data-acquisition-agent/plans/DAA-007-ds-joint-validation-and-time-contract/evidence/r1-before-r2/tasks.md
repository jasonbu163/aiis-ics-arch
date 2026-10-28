Task ID: DAA-007
Revision: r1
Status: implementation_in_progress
Owner Role: Development
Allowed Writers: Development
Handoff: B0/P1/P2 DEV已完成并冻结候选；待coordinator最终保护审计及Owner手动M01–M09；G1 developer_handoff与独立Verification尚未发生
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: DAA ManagedS7到DS的双实例读取与本地SQLite闭环、必要上海时间合同整改及人工联调手册
Owner: Automation World / Data Acquisition Agent
Acceptance Chain Reference: aiis-ics-arch::DAA-007 r1 PM -> Human Owner scope approval -> Development -> fresh-context QA / Verification -> Human Owner final acceptance

# Development 实施事实

## 批准与交付身份

唯一coordinator `/root`将Human Owner精确批准转交实际Development `/root/daa007_development`，角色为项目`.codex/agents/development.toml`，contract_only。批准原话与spec§10一致：

> 可以，批准 DAA-007 r1，按 spec 完成时间规则整改和联调准备。使用新的隔离 profile，已有 SQLite 配置和历史不动；原生测试由我按试行手册手动执行，只做必要增量验证和独立核验，不重复整套测试，阶段 C 暂不做。

获批草案SHA256 `5ccff5d81eb64c9cad99ed87d360a84e055fe26696056dc1d2bec84933652bf8`；批准登记版spec SHA256 `2976f02121a5f300ba7cbcb09b75f0499b098ad4af09b7993f8878fa9dcff5e5`。仅消费不修改spec，checklist尚未创建。

正式交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `1fa1ce50a521ebd51c2c43389db011a76f2d74bf`，dirty并行工作树。只对spec§6精确32路径及本tasks写入，不把既有DS/FieldFlow/AGENTS增量归为本任务；coordinator负责CODE_INDEX和索引。无源码副本、Git refs、依赖锁、真实env/旧profile/76样本读写、原生窗口或设备操作。

执行产物根E=`/private/tmp/daa-007-r1-exec-e6s14xue`；持久证据V=`/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue`。coordinator的`before-files.json`保存32路径before全文/SHA，`workspace-before-sha256.json`保存2615文件保护审计，`b0-source-inputs.json`保存397 DAA/DS/core输入。上述baseline不改写。Owner联调根E/owner-joint-run的两个profile由coordinator新建且未seed，Development不使用；DEV仅自造测试profile。

## 实施顺序与限制

1. B0：核规划漂移与有限DS采用身份；不将历史QA或DS最终验收移植到本任务。
2. P1：上海集中时间、新空双库v2、锁前RO准入与锁后复核、稳定诊断壳；前端上海秒视图和仅历史表列宽。
3. P2：必要time_contract测试、locked driver check、frontend build、Node TZ/偏好、fmt/locale/docs；不重跑完整B/DS矩阵。
4. 冻结候选后进入`awaiting_owner_native`；Owner按M01–M09执行，M09首次正常退出后先取只读checkpoint，再同profile重开。之后DEV只读对账才能G1交接fresh Verification。

创建本记录时所有测试待发生；当前DEV结果见下，Owner原生与QA仍待发生。遇传输/解码/调度/额外DDL或allowlist变化，停止对应工作返回PM；阶段C排除。

## B0 有限采用与漂移归因

coordinator提供B0 precheck：当时无其他活动DAA执行器、15191/15194/30102/30103无相关监听；该事实仅为执行前快照，Owner启动前仍重核。DS会话最后声明本轮开发停止，等待其Owner终验；Development未向DS会话发消息、未改DS。

采用精确r1批准所列有限DS能力，不等待/代授DS全产品终验。规划227 DS输入中226匹配，唯一漂移`automation-world/device-simulator/src/app/simulator/views/points/index.vue`当前SHA256=`fce5cd7a042be0be487cf93fab1df4a305841eead146450576700ed9eeaf50b7`。DAA158/core12实施前匹配；完整397源输入见V/b0-source-inputs.json。

实际读整个当前points页及HEAD差异，并消费V/ds-direct-scope-and-stop-report.json中Human Owner DIRECT授权与DS停止报告：变化为ConsoleDataTable包装/import、稳定column-key/min-width、固定selection/actions列和操作容器；动作函数/IPC/权限/选择分页无变化。按D03归为纯展示，未扩大协议/依赖/风险。**限制：规划快照仅有SHA，没有该时点SFC全文，不能重建精确planning→current逐行差异**；完整HEAD差异及当前全文支持保守展示归因，不作为当前DS独立QA。历史r5 QA、DS-001与DIRECT仍分别保留。

## P1 实际实现

- `domain/business_time.rs`集中Shanghai固定offset、time_profile、RFC3339规范化、SQLite时间表达式、滚动days cutoff；`local_sample::now`薄转调。单调耗时、序号及旧冻结执行图不改。
- 新空双库完整CREATE v2：metadata/user_version/ledger=2，time_profile固定；samples/payload/manifest=2，配置/context/envelope=1。未给旧库执行DDL/UPDATE/迁移或重编码。configuration.rs既有now调用已随薄转调遵循新合同，无须改该授权文件。
- 锁前preflight核SQLite头（先排除会令RO连接创建sidecar的WAL格式）、RO身份/version/time_profile及原件SHA；无immutable。旧/未知/单库/身份异常在ProfileLock、RW、恢复/迁入/日志/actor之前拒绝。合格/新空取原锁后复核元数据及摘要，版本或有效metadata下的字节漂移均拒绝；锁文件事实与业务库零RW分开。
- 仅允许新合同拒绝转无engine诊断壳；bootstrap保留`time_profile_unsupported:原因`，前端中英说明原配置/历史保留与新隔离profile要求。未新增IPC、capability、自动迁移/清库/换profile入口。
- CycleInput各日历字段先规范；SQL在同轮事务生成一次savedAt供样本、manifest与索引复用。history先规范外部offset并拒非法/逆序，retention沿同合同；原成员、原子提交、pending/reference保护及预算不变。
- stdout FormatTime改Shanghai纳秒；文件at保持既有毫秒，未改日志level/轮转mutex/预算/失败锁存。
- 前端集中上海墙上时间输入/秒视图，终止秒含`.999`；仅历史接入稳定字段本机列宽偏好、min/横滚/恢复。原详情JSON/SHA和其毫秒精度保持。
- 双语README/app/local_store及联调手册同步兼容边界。两条M01命令已填E/owner-joint-run实际路径，DAA清除三项旧进程覆盖。M09先首次正常退出只读checkpoint再同profile重开；没有把人工预期填成pass。

## P2 DEV self-check

以下均在正式交付工作树，未启动产品、原生窗口、S7监听或客户端，未读写Owner profile/默认库。既有`src-tauri/target`作为共享编译缓存复用，不清理、不归本任务独占；前端dist只写E/dev-dist。

| 命令（cwd为DAA根，另注除外） | features / 真实结果 | raw |
| --- | --- | --- |
| `cargo test --manifest-path src-tauri/Cargo.toml --locked --lib time_contract -- --nocapture` | default=[]; local-validation=false; driver=false；exit=0；4 passed; 60 filtered out | E/rust-time-contract-final.log |
| `cargo check --manifest-path src-tauri/Cargo.toml --locked --features rust-snap7-driver` | rust-snap7-driver=true; local-validation=false；exit=0；production build graph clean | E/rust-driver-check-final.log |
| `pnpm build --outDir /private/tmp/daa-007-r1-exec-e6s14xue/dev-dist --emptyOutDir` | frontend TypeScript + Vite；exit=0；build passed; third-party PURE/chunk-size warnings | E/frontend-build-final.log |
| `pnpm exec node --test tests/time-and-history-preferences.test.mjs` | Node/TypeScript + subprocess TZ=UTC,Asia/Shanghai,America/Los_Angeles；exit=0；3 passed | E/node-time-preferences-final.log |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | static；exit=0；passed | E/rust-fmt-final.log |
| `python3 -` | static locale/placeholders/literal keys, doc file links, scoped before delta；exit=0；457 paired keys;195literal references;50links;31 changed /32 allowed;spec unchanged | E/dev-static-final.log |

实际argv与规划意图的等价边界：Rust命令未额外传`--no-default-features`，已读Cargo.toml确认`default=[]`，driver check仅开启`rust-snap7-driver`且未开启`local-validation`。前端实际用普通vite.config.ts加显式E outDir，未另传validation config；coordinator只读核普通配置已有`envDir:false`，validation配置合并同一Vue/CU并仅补服务端口/默认build outDir，本次实际未启动server且outDir显式隔离。因此记录实际argv及该有限等价依据，不声称逐字执行规划模板，也不为无行为差异flags再重复构建。

`python3 -`静态检查cwd为仓根：locale457键和占位符对称、195 literal common引用可解析；9文档50个本地链接目标存在（不把anchor/按钮操作写成已验）；spec SHA保持批准登记版。主协调另做一次全工作树保护审计，不由本表代替。

4个Rust time_contract测试实际执行非零：自造legacy/unknown/single/identity/WAL sidecar及WAL header前置拒绝、目录/字节不变且无锁；空/合格v2锁后漂移拒绝（含合法metadata下纯字节变化，已形成锁文件）；实际Stores新库矩阵、配置/intent/event时间、sample/manifest/context原字节/SHA、同瞬间offset等价、毫秒闭区间前后、cursor分页/质量筛选、pending保护/acknowledged清理及重新打开；跨日/滚动days和stdout/file精度。测试仅自造数据，不建立DS/S7链。Node3项实际执行，覆盖上海墙上时间、终止秒毫秒、缺失/非法输入、三个TZ结果一致、本机key隔离/最小宽/损坏回退/重载/恢复。

保留限制/警告：lib test有既有受保护`AgentConfig::empty_for_test` dead_code警告；生产driver check无该警告。前端有第三方PURE annotation和chunk-size警告。未通过放宽检查或修改依赖/锁消除警告。没有重跑完整B/DS矩阵，也没有给原生拖拽或S7闭环判pass。

执行工具记录：最初一次detached cargo runner无捕获exit/完成输出，PID随后不存在，不计为测试通过；改用有session/exit的真实定向运行。早期证据helper处理新增路径before=null失败、编辑helper断言在写前失败，随后纠正；不是产品用例失败。初轮通过后，仅对实际变化的helper/schema/前端及新增必要边界断言刷新相应检查，最终raw对应当前候选。

## 冻结候选与实际文件

正式工作树/HEAD同上，无commit/push。32授权路径中31产生本任务增量；唯一不改为`src-tauri/src/infrastructure/local_store/configuration.rs`（已有now薄转调足够）。下列清单只归本次before→after，不归整个dirty HEAD：

- `automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.md`
- `automation-world/data-acquisition-agent/JOINT_TEST_GUIDE.zh-CN.md`
- `automation-world/data-acquisition-agent/README.md`
- `automation-world/data-acquisition-agent/README.zh-CN.md`
- `automation-world/data-acquisition-agent/src-tauri/src/commands/local_acquisition.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/domain/business_time.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/domain/local_sample.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/domain/mod.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_logging.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.md`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/README.zh-CN.md`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/mod.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/runtime.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/schema.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/source_import_tests.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/tests.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/infrastructure/local_store/time_contract_tests.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/lib.rs`
- `automation-world/data-acquisition-agent/src-tauri/src/services/local_supervisor.rs`
- `automation-world/data-acquisition-agent/src/app/README.md`
- `automation-world/data-acquisition-agent/src/app/README.zh-CN.md`
- `automation-world/data-acquisition-agent/src/app/collection/views/storage/index.vue`
- `automation-world/data-acquisition-agent/src/components/console/ConfigRevisionBar.vue`
- `automation-world/data-acquisition-agent/src/components/console/LocalHistoryPanel.vue`
- `automation-world/data-acquisition-agent/src/console/tableWidths.ts`
- `automation-world/data-acquisition-agent/src/console/time.ts`
- `automation-world/data-acquisition-agent/src/locales/en-US/common.json`
- `automation-world/data-acquisition-agent/src/locales/zh-CN/common.json`
- `automation-world/data-acquisition-agent/src/services/localAcquisition.ts`
- `automation-world/data-acquisition-agent/src/styles/app.css`
- `automation-world/data-acquisition-agent/tests/time-and-history-preferences.test.mjs`

E/dev-candidate.json固定32授权文件SHA及397源输入，implementation aggregate SHA256=`011c3238f02211125b6a3f4c23affc4614bf58cb40188d32c40cf11c600c2486`（排序JSON映射紧凑编码，不含本tasks自引用）。E/dev-task-delta.patch含既有before→after与新增全文，SHA256=`ba1e44b0435f0d8155a8a13a42f5d9f4b5da81c15e8dcab985c7d7881bd3df25`。E/dev-checks.json含每项argv/cwd/features/exit/logSHA和候选关联，SHA256=`abab8b2a43e3a71e13a161ae37f85f5681daa4881be49b182bf30948da4e350d`。以上源码候选已停止写入，coordinator将raw/清单/增量归档至持久证据后执行最终保护审计。

## 当前 gate、资源与后续精确交接

生命周期Status保留`implementation_in_progress`；当前执行gate为`awaiting_owner_native`，**不是developer_handoff/complete/qa_passed**。M01–M09全部not_run；P00启动前Owner端口/窗口核对待执行；实际联调样本/同库账/正常退出证据尚不存在。coordinator最终审计后把已填实手册交Owner，不重复索取范围批准。

Owner run根E/owner-joint-run的ds-profile、daa-profile由coordinator保持新空且未seed；合成env SHA256=`1ffdfe5f5257ac894c4004fecd82425f6b4c3fe7d1f8ad4897412752a293bea8`。DEV测试只在E/dev-test-UUID自造profile，成功后自行清理这些专属fixture；E/dev-dist、日志和manifest保留供证据归档及必要复核，共享target不清理。Owner正常退出前不做联调SQLite查询；之后仅明确绝对路径mode=ro/query_only，无seed/DML/DDL/ACK。

Owner须先完成M01–M08和M09首次正常退出并保持DAA关闭，coordinator/DEV记录首次闭库checkpoint后再通知同profile重开，不重复整套矩阵。第二次正常退出后DEV只读核双库schema/time_profile/身份、两PLC两组各六点、每完整轮成员/两DB/seq/manifest/context/原SHA/pending及重开前后不变事实；无法补证的中间步骤保留缺口。只有这些Owner及同库事实齐备才形成G1精确developer_handoff，交新的fresh-context Verification，之后仍待Human Owner最终验收。阶段C、旧库迁移、真实PLC/生产数据库和发布继续排除。

## Coordinator 持久归档与准备审计（2026-10-23T16:14:30.982+08:00）

coordinator已归档23份真实DEV工件，Development逐份回读核SHA匹配；具体路径与SHA见[归档清单](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue/development/archive-manifest.json)（SHA256=`04da8aa25c9507692dc11730ee3e40b490b448b526758048c495f024e63052f2`）。持久[候选](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue/development/dev-candidate.json)、[DEV检查命令/结果](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue/development/dev-checks.json)、[原before增量与新增全文](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue/development/dev-task-delta.patch)和各final raw log/exit均由该清单逐字节固定，不仅依赖临时路径。原较早检查输出同样保留，最终检查以final文件为准。

仓内[准备候选摘要](evidence/prepared-candidate.json)链接持久[coordinator审计](/Users/jason/.codex/visualizations/2026/10/16/01a143e5-5616-76c0-9df7-13b487bc9c26/daa007-r1-execution-e6s14xue/coordinator-preparation-audit.json)（SHA256=`a3b8a5612e9cccd91899c355d9a639303976cc75f4d3c6600fce8fabdb6db9ef`）。实际核32实现路径与397源输入匹配冻结候选、spec不变；没有未知保护面变化。并行FieldFlow的161份文档/证据变化保留，不归因DAA-007。该审计是coordinator准备/完整性记录，不是fresh Verification或Owner原生实证。

审计时Owner ds-profile/daa-profile仍为空，env SHA匹配；15191/15194/30102/30103均lsof exit1且无输出，无监听。此为准备时快照，不保证未来启动时端口仍空。所有M01–M09仍not_run。E资源保留到Owner运行、只读对账、fresh QA及最终接受后由coordinator核归属/句柄/后续依赖再收尾；共享target、旧库、DS并行资源不回收。本Development现停止全部实现面写入，仅待Owner事实后按批准顺序恢复只读对账及G1交接。
