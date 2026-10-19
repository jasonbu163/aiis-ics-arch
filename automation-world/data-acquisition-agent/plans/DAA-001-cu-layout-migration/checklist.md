Task ID: DAA-001
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner accepted exact DAA-001 r1 on 2026-10-17 after independent QA2 qa_passed; acceptance-only checklist closeout, coordinator to synchronize indexes; no additional tests, Stage B specification only and implementation still requires exact approval
Workflow Mode: STD
Execution Mode: agent_team_same_session

# DAA-001 r1 返工后独立 Verification（QA2 当前）

**当前状态：owner_accepted；QA2 独立 verdict：qa_passed。** F-001、F-002 已由本轮实际隔离交互独立确认关闭，AC01–AC13 在已批准阶段 A 表面通过。产品 failure：无；未解决 blocker：无。**Human Owner 已于 2026-10-17 最终验收 DAA-001 r1。** 不表示 B/C、原生、现场或部署通过。

第1–6节保留 QA2 形成时的独立验证、证据及 handoff；其中 qa_passed、Owner pending 和下一终验 gate 属于当时状态。当前真实最终验收与本次仅文档收尾见第7节。附录A保留 QA1 `qa_failed` 的完整原文，包含当时的两个失败、命令、37项观测、31次invoke/15次被阻断health、保护审计和资源事实；原文不改写为通过。历史文件 SHA-256 为 `ec61c104a638b2fa0cb0a121ff41620d7954a827816909b2e88e22b3695c29fa`，可按附录标记提取原字节校验。

## 1. 本轮角色、读取与精确输入

2026-10-17（Asia/Shanghai），主协调 `/root` 在 Development 再次停止实现写入并形成新 `developer_handoff` 后，实际调用新的 `verification`、`fork_turns=none`，本轮角色为 `/root/daa_stage_a_verification_recheck`；调用记录为证据根 `qa-recheck-dispatch.json`。未继承 Development 对话推理。独立读取根 AGENTS、README/PLAN pair、canonical workflow、verification TOML、AW/DAA/CU最近 README/PLAN、DAA src/app README pair、完整spec/tasks/QA1 checklist、before/current实现、4535行完整实施diff及最小返工diff、D03/D04、DEV和QA1可用输出；作用域内未发现更近 AGENTS。

采用 project-governance、aiis/CONTRACTS、frontend-ui DESIGN/FRAMEWORK适用规则、i18n-workflow、desktop-tauri、code-document-indexer，仅用于验证。`contract_only`；TOML的gpt-6.1-sol/max是配置证据，不冒称观测到运行模型/effort、平台ACL、强制路由或完整团队激活。唯一仓内文档/源写入是本checklist；执行标准构建更新了忽略的DAA/dist生成产物，没有修实现、改spec/tasks/测试/配置/10索引。通知窗口由root统一管理。

证据根 `/private/tmp/daa-001-r1-resume-feckufum/`；本轮新证据独立保存在 `qa-recheck/`，不覆盖 `dev/`、`qa/`、`dev-rework/`。本文件保留关键事实与指纹，临时目录不是唯一结论依据。

| 输入 | 本轮独立重算SHA-256 / 事实 |
| --- | --- |
| 已批准spec | `ce9887b1c1d054384db2f03bac2bb9ddcbc78d480c6469510306feae2ae0c0e4`；同一aiis-ics-arch::DAA-001 r1、R01–R10/AC01–AC13/59精确路径 |
| 当前tasks全文 | `64665ac5570b9654ffcef57a6c82eec244fb2792d79ec3ac13be1d976b5060ff`；§7为返工当前权威，§1–6及旧SHA表为第一次handoff历史 |
| 新handoff-receipt.json | `6fee697969921c1f628518cbf9654ba48688f4fc5ad8791fbb53e798df2ea8de` |
| 新47路径file-manifest.json | `bd37edb0204f56cd880ee17ec104747eddb8855dc182643a4d605f411d611526` |
| D03→当前完整implementation.patch | `aa156608452a15cf4818742ec1816df21ed063ef85b7dd457dc470599f44fd9b`；4535行，独立重建逐字节一致，含未跟踪新增全文 |
| QA1→当前rework.patch | `a6442790bb984012c9436c687031c52c57559eb00d2c0849ee1af62c4b0a607f`；独立重建逐字节一致 |
| CU-008 r1 spec / tasks | `0577e02e9067f5564c2c3896cba6f657c3517ab0dc41d211c6b105ab3832e4d5` / `63bb3926a7990f810b82a23cbbf8cb64904ca7277e67241ae09fe67abc1b50ed` |
| CU-008 QA/Owner checklist | `7e8790d6f215df4c871d6157aec0babf98259671165441d1153547c5713f9199`；§7真实owner_accepted原话及§5的17项源码表保持 |
| HEAD/工作树 | `f85bea8bbf36b491968c3dc9a839518a1ed434a8` / `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD仅上下文，无commit/ref发布 |

47路径的原D03 before、QA1字节、当前after及实际源码逐项吻合；DEV原22附件、返工20附件、QA1失败原文三份副本均重算一致。QA1→当前只有四实现文件和tasks变化，其余42实施路径完全不变。四个当前实现SHA：composable=`f45290a54f75272a90de3cffc2b2161c1eef8a257b6e137eed210bf972aef568`；status view=`b961345419733ec541f8554d8f933a77f44244d4496b95fc3e3183e85b136058`；collection zh=`8ec4506068b65befa5267a8525232ff7f4267bfc12164d6080d6ef4b77e6323a`；en=`812736f644da45decb784c7058e93bc2056a0925c5dc6144ed1e6465ccc3aec9`。

## 2. F-001/F-002 本轮实际复核与关闭

| 原失败 | QA2亲自操作、实际结果 | 当前判定 |
| --- | --- | --- |
| F-001 首次失败误称最近快照 | 全新隔离页面`?scenario=refresh-reject`，先guard、唯一get_runtime_snapshot({}) reject、再mounted；无此前成功快照且无health。实际显示“快照尚未加载，当前为占位状态。”及sanitized fixture IPC rejected错误，刷新按钮重新可用。随后显式mixed刷新成功，raw/latest/sample=12；再reject保留12并显示“刷新失败，以下保留最近快照，数据可能已陈旧。”，busy再次释放。不是通用模糊提示。 | closed；first-reject.json/.dom.txt/.png、loaded-mixed.json、success-then-reject.json/.dom.txt |
| F-002 gateDetails五项对象被标题覆盖 | 实际展开门禁详情，中英文均显示collection/write/loop/database/readOnly五项原说明；collector=control-agent-plc、driver=fixture、interval=3000 ms正确插入，无collection.gateDetails.*裸key；语言切换及展开不增加调用。静态逐项确认两语言对象与原D03五说明完全相同，summary使用独立gateDetailsTitle，原五detailKey调用保持。 | closed；gates-zh/en.json/.dom.txt、gates-en.png、audit.py及static-results.json |

来源选择修复只调整snapshotLoaded与refreshError的判断顺序；标题修复只改summary key并恢复原对象。完整差异未见删除调用消除警告、重命名旧业务为新功能或增加副作用。

## 3. 环境、安全与本轮命令

宿主macOS/zsh，实际Node v22.19.0、pnpm11.11.0；D04的17公共源逐项匹配上游已接受表及当前源，7项DAA自有依赖resolved path/version/package SHA吻合。无安装/升级，CU cardPaddingPx=18保持。

浏览器当前inventory重新提供IAB 3，本轮使用其两个新临时tab，不读取无关用户tab。原生Mac锁定的inventory提示未阻断DOM浏览器能力。实际App加载前独立审阅并在qa-recheck克隆serve.mjs/guard.ts与serve-built.mjs：source由guard先安装纯内存IPC回执及fetch/XHR/WebSocket/EventSource/beacon阻断，再动态import实际main；两服务均CSP connect-src none。built在HTML head最先注入阻断，只服务本轮DAA/dist静态白名单。未裸开真实App，未读真实env/profile或启动原生runtime。

| 命令/方法（默认cwd仓根） | 实际结果 |
| --- | --- |
| 标准库输入SHA/47before-QA1-current/patch重建脚本 | exit0；20返工附件、22初次附件与QA1失败全文吻合；identity-scope.json、reconstructed.patch、reconstructed-rework.patch |
| `python3 /private/tmp/daa-001-r1-resume-feckufum/qa-recheck/audit.py` | exit0；59allowlist/47DEV/58累计差异/1555保护、17CU/7依赖、314双语键与占位符、232源码引用（含5个detailKey及3合法namespace前缀）、无缺失/对象形态变化/成员删除；最终52本地链接、2锚点及围栏通过；原五说明精确恢复 |
| `pnpm build`，cwd=automation-world/data-acquisition-agent | exit0；现有脚本vue-tsc --noEmit及Vite1679模块，2.32s；标准构建刷新DAA/dist，三产物与dev-rework/dist逐字节一致；build.log/build-result.json |
| `node .../qa-recheck/serve.mjs` | 默认sandbox listen EPERM/exit1；相同已批准loopback隔离动作经require_escalated成功，session33840/PID19922/25199；没有auto-review拒绝 |
| `node .../qa-recheck/serve-built.mjs` | 空闲端口核对后经同一批准loopback边界启动成功，session28787/PID20621/25200；只服务刚更新DAA/dist |
| CUA实际渲染、点击、DOM、截图及标准库轨迹断言 | 11项本轮source观测+独立dist四页；断言exit0，interaction-assertions.json。实际source仅4个snapshot及2个PLC-B单次读、2次被截断health；built仅一次被截断health，所有业务外发为0 |
| `git diff --no-index --check <dev-rework>/before <dev-rework>/after` | exit1、无空白错误输出；两侧有真实差异，不误写exit0 |
| 形成checklist后标准库final-document-audit与全文空白检查 | exit0；当前AC01–AC13/pass、QA1原文提取SHA、47实施未变、Owner pending及文档自身检查通过；新增全文no-index空白检查exit1/无诊断（真实差异） |
| 两own session发送Ctrl-C；`lsof -nP -iTCP:25199 -iTCP:25200 -sTCP:LISTEN` | 各exit130；随后lsof exit1无输出；CUA两个自建tab关闭，IAB inventory=[] |

构建保留原PURE annotation与>500kB chunk提示，没有改分包/依赖。工具辅助问题：一个summary被native AX呈现为button但Playwright button locator无匹配，按实际summary重新定位；一个不支持的heading level筛选被忽略而触发strict定位失败，改用已见h1后完成。均发生在helper定位，不计作产品通过或产品失败。最终audit脚本将恢复对象断言放在退出前执行，实测exit0；未把未执行断言当证据。

标准构建当前产物：`dist/index.html`=`72e5f0f776c7eef1eca171fd31e8102d9e4d13c065ae579a0704536ae13fd187`；`assets/index-Cf3NtaIk.js`=`8e1cd6c1287395e3c66ed65385137af5c074c4b5179aed6c6afff55fe54607f0`；`assets/index-D9OrVbmu.css`=`142c37160d709c33ffb53640ba54579f32c2907bfc307b34705e89c8ccef4c52`。不会再由旧dist预览QA1失败版本。

## 4. AC01–AC13 当前独立判定

本轮以完整当前实现/diff、原独立QA实证及精确字节链作判断。QA1的37观测不是本轮重跑；四修复之外未变的行为以原实际DOM/trace/assertions、当前源码核对及本轮必要代表复测共同支持，未仅继承DEV自检或CU通过结论。

| AC | 当前结果 | 证据与范围 |
| --- | --- | --- |
| AC01 | pass | D03写前库存1614、原before、1658模块build及挂载前guard→snapshot→blocked health→mounted→PLC-A单次读轨迹可对读；原dirty保留，环境EPERM与产品失败分开，不冒称本轮重做写前构建 |
| AC02 | pass | CU-008精确批准/独立QA/Owner接受真实，D04的17公共源与上游表、7依赖重算吻合；DAA采用公共二级Sidebar，无私有替代 |
| AC03 | pass | 当前两公共alias、dedupe/fs/types、EP→CU→宿主CSS与八组件/展示类型消费符合；无CU私有导入/在线前置/源码副本/第二主题。标准build后只服务自身dist，四页实测可达，仅自身JS/CSS请求 |
| AC04 | pass | 两一级及四leaf身份/标题/父组准确，配置中心仅父组；本轮source/built四页实际可达，完整授权诊断view/locale未变且仍在工作台。键盘/隐藏恢复/窄窗为QA1原实证，相关接线字节保持 |
| AC05 | pass | §4.2逐项对照完整diff/current：摘要、逐台读取/直库、all确认、latest组、一次读、授权及旧policy均保留；F-002五说明已实测恢复。原四逐台/all命令参数、partial/blocked/failed/reject证据与未变控制函数相符，本轮PLC-B单次读及all-stop取消/外部headless说明再确认 |
| AC06 | pass | App唯一composable/根owner、一次mounted刷新，无新timer。实际选B→points→读样本→第2页→storage→中英/明暗→points保持B、fixture_point_5及结果；trace不变，sizes10回第一页。旧选择重置/操作中跨页重复控制的QA1实证与未变逻辑保持 |
| AC07 | pass | F-002中英五detailKey及参数真实可解析，314键/占位符和232引用全通过。daa偏好及首启规则源码保持，无cu.*访问或html/body公共覆盖；本轮theme/locale、EP分页、message/dialog作用域通过 |
| AC08 | pass | F-001首刷未加载/曾成功后stale分支实际区分；built无桥明确browser fallback。四页现有能力/旧直库/只读策略及未接入说明准确，无假保存/连接/单点测试/上传/日志/容量/SQLite；旧policy/rawHotRetentionDays的可配置语义未被新三自然月规则替换 |
| AC09 | pass | 两原失败闭合，首刷与后续reject均有error并释放busy、保留可重试。原read三结果、gate关闭、控制blocked/partial/accepted-failed/reject、重复busy及全体确认实证对未变路径仍适用；本轮一次读成功与全体取消再次成立 |
| AC10 | pass | QA1实际1280/960×640/390×720中英明暗/长文案/局部滚动/两反馈区实证与相同布局/CSS字节保持；当前代表工作台截图可审。实际sizes在daa-feedback/light、message在daa-feedback/dark、确认dialog在显式dark scope，无未主题化脱出；未新增尺寸矩阵 |
| AC11 | pass | 本轮独立标准vue-tsc/build、自建source/built实际交互及命令次数/参数断言完成；业务外发0、挂载前拦截可证明。浏览器与原生证据分开，native具体deferred不阻塞此浏览器UI合同 |
| AC12 | pass | 59精确路径、46实施+tasks、2合法删除/3新源码+tasks全文、1555保护及协调行/CODE_INDEX唯一DAA行审计通过；当前locale无缺失和结构删除，README pair/链接/锚点/围栏一致。批准spec历史theme源链接单列，不修冻结spec |
| AC13 | pass | 本次精确新tasks/receipt/patch及返工记录真实；串行新命名fresh Verification形成当前qa_passed，仅写本checklist，不修实现/代授Owner。QA1失败全文和证据保留；下一gate仅Human Owner final acceptance |

## 5. 代表实测、差异与证据沿用审计

本轮11项source记录位于`qa-recheck/interactions.json`。首次reject只有1次snapshot/0health；mixed成功后为12/12/12；再reject只有snapshot新增、原12保留；两语言展开五详情轨迹完全不变。手动切mixed并再次刷新后四页/选B不自动读；两次实际样本读均精确`read_plc_samples_once_for_plc({plcKey:'PLC-B'})`。分页、storage往返、主题/语言切换和取消all-stop后总计严格为4 snapshot+2 sample，2 blocked health，无控制命令。实际10条分页显示fixture_point_0…9且第1页；消息/弹窗/sizes实测scope见第3–4节。

独立静态产物四页轨迹完全相同，仅首次被阻断`http://127.0.0.1:8000/health`；静态请求清单仅`/`、自身Cf3NtaIk.js、D9OrVbmu.css和favicon.ico(404)，无CU HTTP或业务请求。代表[当前工作台截图](/private/tmp/daa-001-r1-resume-feckufum/qa-recheck/workbench-current.png)为本轮实际页面，不是DEV图或native证据。

独立审阅QA1的37项原观测及原断言，其中31invoke含16snapshot、5单次读、10控制；四逐台参数、all空参数、busy/双击/切页、failed/partial tone、read三状态、空/无桥/关闭门禁、键盘/窄窗与tooltip均有实际DOM/trace证据。当前42实施路径（含两删除的持续缺失）与其输入相同；四返工实现文件的完整差异仅F-001/F-002。当前build的CSS SHA亦与QA1相同。该证据链允许只定向复测缺陷及相关代表路径，不无故重跑全部37项；不将旧失败证据称为新成功。

相对D03库存累计58变化=47DEV+10root机械索引+1QA checklist；1555 allowlist外源库存原字节保持。10索引排除DAA-001行后其余全文相同，CODE_INDEX排除唯一DAA行后其余相同。root复核期间机械索引记录developer_handoff/QA复核中有独立coordinator-rework-handoff.json/.diff，非DEV越界。两删除仅gates/manifest.ts及旧theme.css；新增三源码和tasks全文均进patch。受保护facade、locale loader、ConsoleTableShell、Rust/Tauri/Cargo、package/lock、CU/backend/SMA/CA/tools、已接受设计及其他任务未变。该source库存不审计真实ignored运行数据，未读真实env/profile。

现役文档本地链接通过；spec对旧theme.css的链接是批准时写前事实且同spec授权删除，单列为历史已删除源链接。QA2没有修改PM文件。原DEV/QA产物均保留，不删除证据。

## 6. 限制、资源与验收审计

| 项目 | 当前事实/下一gate |
| --- | --- |
| 阶段A CU接入及既有功能兼容 | QA2 qa_passed；交Human Owner最终验收 |
| F-001/F-002 | 本轮独立实测closed；QA1原失败仍在附录A |
| 可选native UI smoke | deferred：当前浏览器伪桥不能证明原生WebView挂载前全面截断IPC/health；真实snapshot可能触DB且runtime保护，因此未启动Tauri。R09明确该具体延期不阻塞浏览器UI交付 |
| B/C/现场/生产 | 新长连接/配置保存/双SQLite/上传API、真实PLC/DB/业务API、headless长稳、后台托管、原生生命周期/跨平台/打包签名分发、部署/生产切换、Git refs/推送未验证且不获本结论授权 |
| Owner最终验收 | pending，由Human Owner真实决定；QA不代授 |

本轮source服务25199/session33840/PID19922、built25200/session28787/PID20621均已Ctrl-C退出130，lsof无监听。两个自建IAB标签已关闭，未设置viewport override，最终IAB inventory为空；未停止用户/他人服务、清理偏好或profile。qa-recheck的脚本、构建日志、11观测/DOM/截图、断言及审计保留；仓内DAA/dist为标准当前生成产物。原dev/qa/dev-rework及root证据也保留供终验追溯，由coordinator之后按依赖盘点，不由本轮回收。无新分支/worktree/commit或跨用户chat消息；未另开notifier。

## 7. Human Owner final acceptance

**当前状态：owner_accepted。** 2026-10-17（Asia/Shanghai），Human Owner 对精确 `aiis-ics-arch::DAA-001 r1` 明确最终验收，由唯一 coordinator `/root` 传递的用户原话为：

> 可以，验收 DAA-001 r1。接下来先出阶段 B 的实施 spec，明确范围、实施顺序和验收标准，批准后再改代码。

本次由最新实际 QA2 Verification `/root/daa_stage_a_verification_recheck` 仅记录已经作出的真实 Human Owner 决定，更新本 checklist 的当前 Status、Handoff、效力说明及本终验节。保留 QA2 `qa_passed`、AC01–AC13、F-001/F-002 关闭证据、全部命令/结果/限制和 R09 可选 native deferred；QA1_VERBATIM_BEGIN/END 间完整原文字节不变，提取 SHA-256 仍为 `ec61c104a638b2fa0cb0a121ff41620d7954a827816909b2e88e22b3695c29fa`。这是 acceptance-only 文档收尾，没有追加测试、构建、启动、浏览器操作或实现重审，没有修改 spec/tasks/索引/源码，也没有更新其他临时 receipt。

本次写前 checklist SHA-256 为 `02d5135b418eba4863562032de6e0c8fc896e3519d1fcab6e3e7d2036e98768f`，与 coordinator 的 `/private/tmp/daa-stage-b-spec-zd359myi/baseline.json` 一致。原 `/private/tmp/daa-001-r1-resume-feckufum/` 继续承担阶段 A 审计证据和阶段 B 基线用途，全部保留；原测试服务器/浏览器已关闭，依据 QA2 既有收尾记录，本次未重开、重查或回收资源。未另开通知窗口，协调索引由 coordinator 据本真实终验机械同步。

本终验只接受阶段 A 的 CU 公共 UI 接入及既有功能兼容。用户对阶段 B 的授权仅为先起草实施 spec，批准精确范围后才可改代码；本记录不授权阶段 B 实施，也不解除原生延期 gate，不授权生产、真实 PLC/数据库/API、现场操作、部署、发布或 Git 推送。其他角色独立起草阶段 B，本角色不覆盖或清理其内容。DAA-001 r1 的 Human Owner 最终验收 gate 已完成，本次记录后停止写入。

### QA2 时 handoff 原记录（历史）

**pending。** 精确handoff为aiis-ics-arch::DAA-001 r1、第1节spec/tasks/receipt/manifest/patch字节与当前QA2结论。只交唯一coordinator `/root` 转交Human Owner作终验及10索引机械同步；若实现字节再变，本结论不自动覆盖新输入。QA通过不等于Owner接受、原生/现场操作或部署。

## 附录A：QA1 qa_failed 完整原文（历史，原字节保留）

以下标记间内容为QA1原文；其中状态、未解决失败、Owner pending及资源描述只代表第一次handoff时事实，当前效力见上文QA2。提取两标记之间的原始UTF-8内容，SHA应为`ec61c104a638b2fa0cb0a121ff41620d7954a827816909b2e88e22b3695c29fa`。

<!-- QA1_VERBATIM_BEGIN -->
Task ID: DAA-001
Revision: r1
Status: qa_failed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Independent Verification found F-001 and F-002 in the exact Development handoff; return failures through coordinator /root to Development, then require a new exact handoff and new fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session

# DAA-001 r1 独立 Verification

**本轮 verdict：qa_failed。** 已实际复现两项 UI 回归：首次快照失败误称保留最近快照；采集门禁的双语说明对象被折叠标题覆盖，展开后出现五个裸 key。本轮未修改实现，修复后必须重新交接并启动新的 fresh-context Verification。构建通过和其余交互通过不能抵消这两项失败。

## 1. 角色、批准依据与精确输入

2026-10-17（Asia/Shanghai），实际命名 Verification `/root/daa_stage_a_verification` 在 Development 停止实现写入并交接后启动。主协调的 `qa-dispatch.json` 记录 `role=verification`、`fork_turns=none` 和成功调用。本轮未继承 Development 对话推理；独立读取根 AGENTS、README/PLAN 双语、canonical lifecycle workflow、实际 verification TOML、AW/DAA/CU 最近 README/PLAN、DAA `src/app/README.*`、完整 [spec.md](spec.md) / [tasks.md](tasks.md)、实现、完整 4479 行 patch、before/after、新增全文与可用 DEV 输出。未发现更近 AGENTS。

采用 project-governance、aiis、frontend-ui 的 DESIGN/FRAMEWORK 适用规则、i18n-workflow、desktop-tauri、code-document-indexer，只作验证。本 profile 是 `contract_only`；TOML 的 `gpt-6.1-sol/max` 仅为配置证据，没有宣称独立观测到运行模型/effort、平台 ACL、强制路由或完整团队激活。本轮唯一仓内写入是本 checklist，未修改 spec、tasks、实现、测试、配置或协调索引，也未另开通知窗口。

| 输入 | QA 独立重算 SHA-256 / 事实 |
| --- | --- |
| 已批准 DAA-001 r1 spec | `ce9887b1c1d054384db2f03bac2bb9ddcbc78d480c6469510306feae2ae0c0e4`；D01 原话和批准历史保留 |
| 精确 Development tasks | `55c038f0e21e8d859879664dfcd767636107937dc289a2f885c3fe759edd222b`；`developer_handoff` |
| DEV handoff receipt | `511c4b3aa314347b7db0a471bc1902228b56bdbcee11cd61c64d7bfe9921ee40` |
| 47 路径 before/after manifest | `ece44ba7fe4f1cf7cdae0a756d168dc901c85b39cc2e7b915e0ea021e55a3f88` |
| 完整实施 patch | `73baf05a5001f44c194dba8156d2a3aad9199a80bfa6a62f415c8d546bbac44d`；独立从原字节重建后完全相同，包含新增 tasks 全文 |
| CU-008 r1 spec / tasks | `0577e02e9067f5564c2c3896cba6f657c3517ab0dc41d211c6b105ab3832e4d5` / `63bb3926a7990f810b82a23cbbf8cb64904ca7277e67241ae09fe67abc1b50ed` |
| CU-008 QA / Owner checklist | `7e8790d6f215df4c871d6157aec0babf98259671165441d1153547c5713f9199`；§7 保存 2026-10-17 真实 `owner_accepted` 原话 |
| HEAD / 工作树 | `f85bea8bbf36b491968c3dc9a839518a1ed434a8` / `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD 仅上下文，本轮无 commit 或发布 ref |

DEV 的 22 项 receipt 附件、47 路径 before/after/current 字节和 3 个最终 dist 文件全部重算吻合。D04 的 17 项 CU 公共文件与上游已接受清单和当前实际源逐项相同，7 项 DAA 自有依赖的 resolved package 路径、版本和 SHA 相同；完整清单持久记录在 tasks §3，不以 CU 自身 QA 替代本轮 DAA 集成验证。公共 `cardPaddingPx=18` 保持，公共样式没有被本地常量替代。

证据根为 `/private/tmp/daa-001-r1-resume-feckufum/`；DEV 证据冻结于 `dev/`，本轮独立附件位于 `qa/`。本文件保存命令、结果、失败复现和关键指纹，临时路径不是唯一结论依据。

## 2. 实现失败及 Development 返工条件

### F-001：首次快照失败把初始占位称为最近快照

位置：[useControlAgentConsole.ts](../../src/console/composables/useControlAgentConsole.ts) 第 71–76 行；本轮文件 SHA 为 `183d62357dbda60c674620f44e7b6892c41f8b9cf9544cdc5b1913b0588bd077`。

隔离新页面以 `?scenario=refresh-reject` 首次载入。guard 在 App 前安装，轨迹严格为 `guards-installed -> get_runtime_snapshot({}) reject -> mounted`；没有此前成功快照，也没有 health 调用。页面显示错误并释放刷新 busy，但来源文案是“刷新失败，以下保留最近快照，数据可能已陈旧。”，下方实际是 `fallbackSnapshot` 的初始实例及四个 0，占位来源提示不再出现。截图与 DOM 亲自核对；不是从关键词扫描推断。

根因是 `snapshotSourceText` 先判断 `refreshError`，尚未判断 `snapshotLoaded=false` 就选择 `common.feedback.stale`。这违反 R06/R07、AC08/AC09 的未加载/fallback 来源真实性要求。

对照病例：先成功取得夹具快照（raw/latest/sample=12），再令刷新 reject，原成功数据保留、来源为 “Refresh failed. The last snapshot is retained and may be stale.”，刷新按钮恢复可用；这条已有成功快照的 stale 路径正确，不应被返工破坏。

返工验收：没有成功快照时明确显示未加载/初始占位来源并保留失败反馈；确有最近成功快照时继续显示陈旧提示、保留数据并释放 busy。不得只换成一条对所有状态都模糊的通用文案。附件：`qa/first-refresh-reject.json`、`.dom.txt`、`.png`、`qa/success-then-stale.dom.txt` 及 `interactions.json` 对照条目。

### F-002：采集门禁说明的双语对象被标题字符串覆盖

位置：[中文 locale](../../src/app/collection/locales/zh-CN.json) 和 [英文 locale](../../src/app/collection/locales/en-US.json) 第 48 行、[采集视图](../../src/app/collection/views/status/index.vue) 第 11 行，以及根 composable 第 243–286 行。

原 `collection.gateDetails` 是包含 `collection/write/loop/database/readOnly` 的对象；本轮两语言都改成了“采集门禁详情”/“Collection gate details”标题字符串。根层仍用 `detailKey` 查找这五个子键并插入 `collector/driver/interval`。实际展开工作台“采集门禁详情”，中英两种语言均显示：

```text
collection.gateDetails.collection
collection.gateDetails.write
collection.gateDetails.loop
collection.gateDetails.database
collection.gateDetails.readOnly
```

旧读取门禁、写库边界、周期/启动模式、数据库和只读模式说明丢失，collector/driver/interval 原有上下文也没有正确呈现。两语言结构对称不代表键可解析；DEV 的 literal-only 检查没有覆盖此处 `t(item.detailKey, ...)`。这违反 R04/R06、AC05/AC07；AC12 的完整文案解析检查也未通过。

返工验收：保留原五项说明及其参数，折叠标题使用不冲突的键；展开后中英文均可读、无裸 key，功能归位不能丢失既有诊断。不得通过删除详情调用来消除告警。本轮触达 locale 的额外结构检查只发现这两处对象→字符串，原成员删除仅这五项；未发现其他形态回归。附件：`qa/gate-details-en.dom.txt`、`qa/gate-details-zh.dom.txt`、`qa/gate-details-zh.png`、`qa/static-results.json`（含原说明对象）。

## 3. 环境、安全隔离与实际命令

宿主为 macOS / zsh；实际 `node --version` 为 v22.19.0，`pnpm --version` 为 11.11.0。沿用项目锁定依赖，无安装或升级。Vue 3.5.38、Element Plus 2.14.2、icons 2.3.2、vue-i18n 9.14.5、Vite 5.4.21、TypeScript 5.9.3、vue-tsc 2.2.12 与 D04 相符。

浏览器用实际 CUA/IAB，未使用 terminal Playwright、没有安装辅助依赖。启动前独立审查 DEV 的 `serve.mjs/guard.ts/serve-built.mjs`，仅在仓外 QA 目录复制为本轮夹具并增加首刷失败/长文本病例。source 夹具以 CSP `connect-src 'none'`、fetch/XHR/WebSocket/EventSource/beacon 阻断及纯内存 IPC 回执先于实际 main 挂载；只允许本机静态源码。built 夹具在 HTML head 最先注入阻断，无原生桥，只服务本轮 dist 白名单。未直接打开无 guard 的真实 App。

| 命令 / 方法（除标注外 cwd 为仓根） | 真实结果 |
| --- | --- |
| QA 标准库 SHA / before-after / inventory 脚本 | exit 0；59 allowlist、47 DEV、22 附件、3 dist、17 公共源、7 依赖一致；`qa/identity-scope.json`，独立重建 patch 完全一致 |
| 审阅 DEV `baseline-build.log`、原 UI DOM/截图/trace、before 原源码 | 修改前 build 为 1658 模块成功日志，旧 UI/旧动作/挂载前 guard 轨迹与原源码一致；与修改后证据分开。此为审阅 D03，不冒称 QA 重做修改前构建 |
| `pnpm --dir automation-world/data-acquisition-agent build --outDir /private/tmp/daa-001-r1-resume-feckufum/qa/dist --emptyOutDir` | exit 0；既有脚本执行 vue-tsc 和 Vite，1679 模块，2.50s；输出只在 QA tmp，3 产物 SHA 与冻结 DEV dist 完全相同；`qa/build-result.json` |
| `node /private/tmp/daa-001-r1-resume-feckufum/qa/serve.mjs` | 默认 sandbox listen 返回 EPERM/exit 1；相同已批准 loopback 隔离动作经 require_escalated 成功，session 74874 / PID 4062 / 25196；无 auto-review 拒绝 |
| `node /private/tmp/daa-001-r1-resume-feckufum/qa/serve-built.mjs` | 空闲端口核对后，以相同批准边界 require_escalated 成功；session 22503 / PID 7231 / 25197；服务 QA 自身 dist |
| CUA 实际渲染/点击/键盘/viewport/DOM/截图 | 37 项独立记录；下节列结果，F-001/F-002 均实际复现；不是 DEV 自检复述 |
| QA 调用轨迹断言脚本 | exit 0；确认 guard 顺序、有限命令集、参数、取消、重复点击与无导航额外调用；`qa/interaction-assertions.json` |
| `python3 /private/tmp/daa-001-r1-resume-feckufum/qa/audit.py` | **exit 1（真实 F-002）**：309 键/占位符对称，232 源码键引用含 3 个合法状态 namespace 前缀；五个 detailKey 缺失；精确差异/保护/文档检查通过。不得写成静态全通过 |
| `git diff --no-index --check <DEV>/before <DEV>/after` | exit 1、无空白错误输出；两侧有真实差异，未误报为 exit 0 |
| 停止两个 QA own exec session：Ctrl-C | 各 exit 130；随后 `lsof -nP -iTCP:25196 -iTCP:25197 -sTCP:LISTEN` exit 1/无输出 |

构建中原有 PURE annotation 与 >500kB chunk 提示保留；没有为提示扩张依赖/分包或验证范围。QA helper 曾把合法 namespace 前缀当叶键、把批准 spec 的历史 theme 源链接当新失效链接，已按真实结构分类后重做；五个真正缺失键仍保留为失败。浏览器的一个 label locator、动画关闭期间的定位和一个 helper JS 拼写失败均在读新状态后处理，没有计为产品通过证据。一次只读 DOM 环境不提供 localStorage 对象，未据此推断偏好值；偏好规则由保护源码及真实切换/重载行为核对。

## 4. AC01–AC13 独立结果

| AC | 结果 | 证据与边界 |
| --- | --- | --- |
| AC01 | pass | D03 的原字节、dirty 库存、构建及原 UI/IPC 隔离轨迹可对读；未以修改后截图代替修改前。原状态保留，环境 EPERM 与产品缺陷分开 |
| AC02 | pass | CU-008 r1 独立批准/QA/Owner 接受真实；17 源和 7 依赖重算吻合 D04；DAA 直接消费其二级合同，无私有菜单替代 |
| AC03 | pass | 八公共组件实际由薄适配渲染，两 alias、dedupe、fs/types 和 CSS 顺序符合；旧 theme 删除且不再导入。独立 build 与只服务自身 dist 的四叶页实际可用，无 CU 在线 HTTP/私有入口/依赖目录前置 |
| AC04 | pass | 仅 workbench 和 configuration 两一级，后三个稳定 leaf；标题、选中、父展开、键盘及窄窗实际一致。原完整授权诊断仍在工作台 details，无第五主页面 |
| AC05 | **fail F-002** | 主动作/策略/样本/授权等已归位，但五项旧采集门禁说明丢失。四逐台命令、all 确认、status/affected/gateErrors 和 headless 边界的实际对账通过，不能据此宣称整个旧→新映射无丢失 |
| AC06 | pass | App 唯一 composable，单首次 refresh；导航/折叠/主题/语言/分页不增加调用。选中 PLC、分页与反馈跨页保留，换 PLC 按原规则重置；delayed 双击并切页仅一条控制。无新 timer |
| AC07 | **fail F-002** | daa 偏好/首启规则保留，CU/EP locale、theme/dialog/message/tooltip/sizes scope 实测通过；html/body 无旧公共主题覆盖。但展开详情在两语言均出现五个裸 key |
| AC08 | **fail F-001** | 三配置页能力说明、browser fallback、自检边界、旧 policy 语义正确，无假表单/上传/SQLite/日志。首次请求失败却误称最近快照，来源真实性不通过 |
| AC09 | **fail F-001** | accepted/blocked/partial/failed/reject、busy 复原、读一次三种结果、read/write 关闭及空态均实测；有成功快照后 stale 正确。首次失败来源仍不符合本 AC 的完整错误状态要求 |
| AC10 | pass（布局/可达范围） | 1280 宽窗反馈 496px+496px 并列；960×640 堆叠、页面宽 960；390×720 中英明暗页面宽 390、菜单 client/scroll=389，末项可点，长文本及表格局部滚动可达。样本 sizes 真选 10/page 后 10 行且回第一页，弹层未脱离主题；裸 key 另计 F-002，不以布局通过掩盖 |
| AC11 | pass（本轮验证能力） | QA 独立 vue-tsc/build、实际 source/built 浏览器与调用断言完成；业务外发 0。构建成功不意味着交付通过；原生证据按 R09 具体延期，见第6节 |
| AC12 | **部分通过，文案解析 fail F-002** | 59 路径/2 删除/新增全文/1555 保护和索引行审计通过；README pair/CODE_INDEX 最小一致、本地链接/锚点/围栏及 JSON 解析/对称通过。扩展到 detailKey 后五键不能解析，不记总 pass |
| AC13 | pass（生命周期事实） | 精确批准、DEV handoff、实际新 fresh Verification 串行成立；本轮独立写 qa_failed 并返回实现失败，未修实现、未代授 Owner 终验；下一 gate 为 DEV 返工与再 fresh QA |

## 5. 实际交互、映射与差异审计

实际旧→新核对覆盖 spec §4.2 全部行：总览身份/计数/heartbeat/数据库与就绪进入工作台摘要/运行详情；逐 PLC 旧读取/写库、all 组合控制、collector/最新 DB 组在工作台；PLC 只读配置和选择进入 plc-config，原合同摘要/类型/问题/一次读取/分页进入 points-groups；原 policy/path/version/latestMode/rawHotRetentionDays/选点与校验进入 reporting-storage；授权门禁完整保留工作台附属区；偏好保持宿主；上报日志如实未接入。已识别的内容丢失就是 F-002；首次未加载真实性失败就是 F-001，不额外宣称全矩阵无回归。

| 本轮亲自完成的路径 | 观察 / 调用断言 |
| --- | --- |
| 初始 mixed、配置中心、PLC-B 选择、点位跳转 | 初始仅一个 get_snapshot 和一个被截断 health；选择/跳页不增加调用；一次读取只发 `read_plc_samples_once_for_plc({plcKey:'PLC-B'})` |
| 样本第2页→storage→中英/明暗→points | PLC-B、fixture_point_5 起始、分页及现有读取结果保留且结果重译；调用轨迹完全不变 |
| 修改 sizes | 暗色 listbox 位于 `#daa-feedback`，theme=dark；实际选择 10/page 后样本为 10 行，current page=1，原 attrs/events 转发有效；受保护 TableShell 原字节未变 |
| 四逐台动作 | start_read 仅 PLC-B；stop_read/pause_persistence/enable_persistence 仅 PLC-A。非 reject 控制后仍仅原 get_snapshot+health，未新增 connect/upload/跨目标动作 |
| 控制回执 | blocked=warning/accepted=false+gate；partial=warning；accepted=true/status=failed 仍 error；reject=failed/error、affected为空；按钮忙态最终释放 |
| 全体操作 | start/stop 各自 Cancel 均不发命令；各确认只发一次 `start_plc_collection({})` / `stop_plc_collection({})`，不附 plcKey。停止弹窗实际保留“External headless collector processes are not affected.”说明 |
| 操作中重复与切页 | delayed stop 双击后立即切 plc-config，期间只有一条 stop；返回后只多原 snapshot/health，busy 释放，最后结果保留 |
| 一次读异常与选择重置 | succeeded / read-fail / not-attempted / IPC reject 分别为 success/error/warning/error，读 busy 结束。A 读取第2页后改选 B，分页回1、反馈清空、旧 A 样本不显示，选择不发 I/O |
| 无桥、空 PLC/合同缺失、read/write 关闭 | 无桥 fresh 页面无 IPC、明确 fallback，原 all/read 动作禁用；空 PLC 和缺合同可见；关闭 gate 后读/启写禁用且原因可聚焦，未尝试绕过门禁 |
| 键盘与侧栏 | Right 进子项、Enter/Space 选择、Left 回父并折叠，关闭子项 tabindex=-1；当前子叶及父组强调正确；隐藏/恢复维持 active 并展开父组，无 invoke/fetch |
| 弹层 | 暗色确认 dialog 位于显式 `.aw-ui[data-aw-theme=dark]`；实际 ElMessage、表格长 endpoint tooltip 与 sizes 均落 `#daa-feedback` 同主题作用域，颜色来自公共 token；不改 html/body 规避 |
| 独立 dist | QA 自身构建 4 页实际可达；服务记录仅 `/`、自身 JS/CSS 和 `/favicon.ico`（404），无 CU 服务/源码 HTTP 请求；health 是 head guard 截断调用 |

本轮主要 source 轨迹最终为 31 次夹具 invoke（16 snapshot、5 一次读、10 控制）和 15 次被截断 health 调用；有限命令和每个参数已断言，均非真实设备/DB/API 操作。37 项观测保存于 `qa/interactions.json`，关键条件检查为 `qa/interaction-assertions.json`。宽/窄截图已亲自查看；一次展开的仓外 fixture trace `<pre>` 将整个页面撑宽至 665，折叠 helper 后产品宽度恢复 390，该 helper 干扰未计为产品溢出或产品通过证据。

修改前库存 1614 项；进入 QA 时相对恢复基线恰 57 项差异：47 DEV（46 实施/说明加 tasks）及 10 个主协调 DAA 索引；本 checklist 创建后为 58。1555 个 allowlist 外库存项原字节保持。10 索引逐一排除 DAA-001 行后其余全文相同，CODE_INDEX 排除唯一 DAA 行后全文相同；未把整仓其他 dirty 归为本任务。

合法删除只有 `src/app/gates/manifest.ts`、`src/styles/theme.css`；新增三源码和 tasks 全文已纳入 before/after/patch。受保护 runtime facade、locale loader、ConsoleTableShell、Rust/Tauri/Cargo、package/lock、已接受设计、CU/Backend/SMA/CA/tools 和其他任务的库存指纹保持。真实 ignored env/profile 未读取或修改，不能把这份 source 库存称为真实运行数据审计。

DAA 两层 README pair、本地 bundle 链接与锚点/围栏已检查。批准 spec §2 对旧 `src/styles/theme.css` 的链接属于写前源码事实，目标按同一 spec 的 D allowlist 删除；独立审计显式记录为一项历史已删除源链接，未修改 PM 冻结 spec，也未把它当活跃 README 链接通过。没有发现其他活跃本地失效链接。

## 6. 限制、资源与下一 gate

产品失败：F-001、F-002，均未解决。环境 blocker：无；本轮不是 `qa_blocked`。R09 的可选 native UI smoke **deferred**：当前浏览器伪桥不能证明原生 WebView 挂载前全面截断健康请求/IPC，真实 snapshot 可能触 DB，而运行时是保护面；因此没有启动 Tauri。该具体延期按已批准 R09 不阻塞浏览器 UI 定义的交付，不能用它解释或豁免两项实现失败。

未验证且不授权：B/C、新长连接/SQLite/上传 API、真实 PLC/数据库/业务 API、headless 采集/长稳、后台托管/原生生命周期、跨平台/打包签名分发、生产切换/部署、Git refs/推送。源码和浏览器证据不等于上述运行证据。

本轮 own 临时资源已停止：source session 74874 / PID 4062 / 25196，built session 22503 / PID 7231 / 25197；均 Ctrl-C exit130，lsof 无监听。CUA 自建3个标签关闭，IAB inventory为空，viewport override已 reset；未停止用户/他人服务，未清偏好/profile。`qa/` 的隔离脚本、dist、截图/DOM、失败轨迹、审计与结果全部保留，DEV/root 原始证据也未删除，供返工和下一 fresh QA 追溯。无新分支/worktree/commit，未联系其他用户会话；通知窗口继续由 root 统一管理。

下一步通过唯一 coordinator `/root` 将 F-001/F-002 返回实际 Development，在已批准 r1 allowlist 内修复并记录真实返工、重算精确实现和 tasks handoff；随后实际启动新的 `verification` / `fork_turns=none`。本轮失败历史和证据必须保留，不能用覆盖 checklist 的方式抹去。若返工实质改变范围/风险/路径/AC，应按 workflow 返回 PM 新 Revision。

## 7. Human Owner final acceptance

**pending。** 本轮为 `qa_failed`，尚未进入可请 Human Owner 最终验收的 QA 通过状态。本文件没有代授验收、风险接受、发布、部署或外部动作权限。
<!-- QA1_VERBATIM_END -->
