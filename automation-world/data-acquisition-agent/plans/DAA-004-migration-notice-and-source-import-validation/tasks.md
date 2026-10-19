Task ID: DAA-004
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: DAA-004 r1 implementation and incremental DEV self-check recorded; Owner native observation reconciled with explicit initial PLC enabled-draft deviation and external-change supplements; sole coordinator /root must start new fresh-context actual Verification, no QA or Owner verdict
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# DAA-004 r1 Development

实际 Development `/root/daa004_development`，sole active lifecycle coordinator `/root`。Human Owner 批准草案 SHA `5ee40a1b1e18ef3955c30073d6a91e3b620ddbf3523090d2b485351d6d9ca67a`，当前批准记录版 spec SHA `c84c93612e828578f0a4a3beaa406642b7fe7401624f1af71276a470cc1d5a8e`。精确 STD r1，无 commit/push；HEAD `f85bea8bbf36b491968c3dc9a839518a1ed434a8`。actual development TOML gpt-6.1-sol/high 仅配置证据，contract_only。

1. 完整当前 before 与批准核对 → 封闭16路径、旧bundle/全部Rust/owner保护审计。
2. README pair 和既有折叠详情内迁入历史 → 定向实际SFC状态/双语/guard检查。
3. 独立expected先行、受控DB21/UDT3叶 → 声明/期望对读、唯一ignore例外。
4. 必要构建和一次普通native真实文件选择/缺UDT取消/配对保存重载 → 同库ID/ETag/SHA/receipt及空active/样本对账，完整diff交接。

before=`/private/tmp/daa-004-r1-hppdbt2h/baseline.json` 与 `before/`，保护既有dirty/untracked，不用HEAD替代。证据只写该根 `dev/`；根通知窗口由coordinator管理，本角色不发送。阶段C、Backend/SMA/DS、真实env/profile/YAML/SQLite/PLC/API、旧B矩阵及依赖/锁/发布保持排除。最新效力及正式交接见§7；§4–§6保留当时checkpoint与等待事实。

## 2. 已实施的有限增量

- `diagnostics/index.vue` 撤下迁入组件和导入；`ConfigRevisionBar.vue` 复用原默认关闭的唯一原生 `details`，其中承接 `YamlMigrationNotice` 的有界历史/重试 section。配置栏外只在 `statusPersistence=unknown` 或 `status=failed && retryAllowed===true` 提示，unknown 优先；入口只设置同一个 details 的 `open=true`，不请求保存、激活或重试。
- 迁入标题、状态、来源及诊断明确为“迁入时记录”，成功/空/已有/不可再重试的旧失败不冒充当前故障。`common.local.codes.failed` 仍为“失败 / Failed”；迁入专用失败独立。Rust `retryAllowed` 与 `busy || dirty || editing` 禁用保持。
- DAA README 双语列明仓内默认 PLC_1、DB1/example_group、旧窗口和3点及 raw/latest/every_sample 退役策略；说明 process/env 可覆盖，不能冒称实际 profile 清单。app README pair 和 CODE_INDEX 仅本次 DAA 局部说明同步。
- `expected.json` 先依据 R05 固定3叶表人工独立编写，`dev/expected-first.json` 在两源码尚不存在时封 SHA；再手写 UTF-8 minimal.db/udt 与 fixture README pair。显式 DB21、1个payload引用MinimalPayload、3叶BOOL/INT/REAL；默认disabled/groupId=null/address=null。`.gitignore` 只新增唯一 minimal.db 路径 negation；旧三 ignored DB 不放开。
- `useLocalAcquisitionConsole.ts`、facade、全部Rust/原测试/锁/schema/ledger/两YAML、旧bundle及全部其他公开路径保持；没有修改真实 env/profile/库或读取其内容，没有删除任何产品路径。

## 3. DEV self-check 命令与结果

D=`/private/tmp/daa-004-r1-hppdbt2h/dev`。辅助脚本仅在 D，未安装依赖；项目命令 cwd 为 DAA 根。`python3 D/run.py <name> <argv...>` 剥离继承 DAA_/SQLite/SQLCIPHER/LIBSQLITE3/VITE_/TAURI_/CARGO_/Rust 覆盖，仅设置 D 内绝对关闭 env/profile、`CARGO_TARGET_DIR=D/target`、`CARGO_NET_OFFLINE=true`。每条 argv/cwd/env/真实exit/时长及完整 raw 在同名 `.result.json/.stdout/.stderr`。Python 标准库仅作文件/hash/只读取证控制器，不冒称项目 Rust 链接 SQLite 来源。

| 实际 argv / evidence prefix | 结果与边界 |
| --- | --- |
| `pnpm build --config vite.validation.config.ts --outDir /private/tmp/daa-004-r1-hppdbt2h/dev/dist --emptyOutDir` / `frontend-build` | exit0，5.67s；实际vue-tsc+Vite，只有自有dist。原PURE和chunk-size警告保留。 |
| `node D/component-directed.cjs` / `component-directed` | exit0；实际两个SFC经现有Vue compiler编译，双语SSR覆盖成功/带诊断/空/仅策略/已有/validation/failed无retry/null，failed可retry，unknown优先，busy/dirty/editing禁用；Vue host renderer实际handler打开同一details且0保存/激活/重试。只是组件渲染，不冒充native。 |
| `node D/owner-rework-reviewed.cjs` / `owner-rework` | exit0；已审复制原13项owner定向反例：普通失败双语、保存非空/仍空、summary pending/失败先清旧动作、保存成功与摘要未加载分开、save失败保输入、精确双CAS和editing/dirty零retryIPC。确定性函数响应，无native桥或SQLite执行。 |
| `node D/owner-regression-reviewed.cjs` / `owner-regression` | exit0；原9项无桥零IPC/零timer、快照首次未加载/后来陈旧、编辑ETag与冲突/重试保护回归。 |
| `python3 D/audit.py` / `static-audit` | exit0；1652公开保护路径、3旧ignored DB字节、旧bundle/全部Rust/owner/YAML不变；16实现+tasks精确17自身变化，无删除/越界，HEAD不变。唯一ignore例外正反例、CODE_INDEX只DAA行、710 assembled双语键/176literal键/占位符及本地链接检查，先行expected与原声明对读。数字以最终audit.json为准。 |
| `python3 D/reuse-evidence.py` / `evidence-reuse-reviewed` | exit0；原golden/proof函数字节与冻结源匹配，完整旧raw/exit0/hash核用。current Rust及owner匹配对应DAA-003冻结版本；未新跑Cargo测试或旧B矩阵。 |
| `python3 D/patch-check.py` / `own-diff-check-final` | exit0；17份自己的before→after使用 `git diff --no-index --check`，只允许0/1且stdout/stderr均空，无新增空白错误；完整preview patch包含新文件全文。 |
| `pnpm tauri dev --help` / `tauri-help` | exit0；当前已安装CLI确认临时config merge用法，无产品行为执行。 |

原证据核用细节在 `D/reuse-evidence.json`：`offset_and_full_structure_golden` 采用 DAA-002 `local-runtime-closed-2.stdout`；`public_save_cannot_forge_source_proof_and_preview_ids_match_confirm` 采用 DAA-003 `directed-proof.stdout`。前者的DB/UDT定义及展开分支与冻结旧B源逐字相同，但 `tia_source.rs` 整文件曾在 DAA-003 移除 YAML 编辑导入/legacy分支，不能宣称整文件同旧B，有限diff留 `prior-tia-yaml-retirement.diff`；current全Rust与DAA-003冻结一致。两函数是旧fixture证明，不宣称新pair已由旧测试覆盖，也不替代本次普通文件选择。

真实非零全部保留：首次普通native sandbox回环49194 bind EPERM/exit1，同获批命令escalation获准后正常启动，未发生自动审批拒绝；`evidence-reuse` 初版错误拿DAA-003首轮owner hash比返工后owner而exit1，`evidence-reuse-final` 假设旧B整个tia_source不变而exit1，仅修自有审计以核最新owner及明确旧YAML退役diff，第三次exit0；`own-diff-check` 初版误认为no-index有diff也只能exit0而exit1，其stdout/stderr为空，改自有helper显式接受该命令0/1且无警告后通过。没有改产品掩盖失败。一次探索 `ls DAA003/dev/*derived*` 无匹配，未运行产品或写旧证据。

## 4. 普通原生 R06 当前阶段

唯一新运行资源 N=`D/native-r06`，新profile有 `.daa004-r1-owner`，env仅read=false及两个自有空YAML绝对路径；无mode/storage、local-validation/fixture/native驱动feature。`D/target` 由旧已关闭DAA003 target以 `cp -cR` 克隆为本任务自有缓存（exit0），没有写旧target；实际普通Tauri再次编译产品并在17.33s完成，机器码副本已封存 `N/frozen/aiis-data-acquisition-agent` 与 `N/binary.json`。源码seal固定199路径，本次启动后未改产品源。

15191启动前由既有node PID8497监听，未操作该窗口。只对本任务 `N/tauri.port.json` 的beforeDevCommand端口及devUrl设49194，产品tauri配置不改。实际 argv=`pnpm tauri dev --config /private/tmp/daa-004-r1-hppdbt2h/dev/native-r06/tauri.port.json`，cwd=DAA，环境及wrapper/pnpm PID在 `launch-escalated-process.json`；原sandbox失败完整保留。普通native PID71897持自有profile锁，启动为stopped，未连接或采集。

首开 `N/first-open.json`：0 PLC/DB/组/点/编辑来源，ETag=`018ed7e5-7e71-4f34-8717-0f344b5699b2`，唯一私有receipt ID=`0b91c0fe-1fa7-45d2-bed2-6228a9560637` / SHA=`4dd59ab487c1c22a7c3a86d16113cd4386c3518e4a2cb17694b192d223ca4b74`，`skipped_empty`。active=null，runtime来源/解释/激活/轮/样本/投递/引用均空。

CUA一次enabled inventory没有DAA，只有旧未运行CA，未getApp、未打开真实profile或注入假bridge。CUA文档要求UI交互使用其API；未用osascript/系统AX绕过。`N/cua-inventory-limit.json` 记录限制，由sole coordinator接续一次Owner实际文件选择/预览/取消/确认/重载/正常退出。当前该必要观察**尚待取得**，不能据首开、SSR或旧测试宣称AC06成立。

`D/native-watch.py` 已启动，每0.5s只读新同库，只有配置ETag/source原行或clean_exit变化才留完整阶段快照到 N/observed-*.json 和 watch.jsonl；并非每个UI点击都能从库看见，无变化的预览/取消阶段须由实际Owner观察及未变owner静态/raw共同说明。此处待取得真实操作后追加最终事实、同库对账和退出资源结果；不会伪造逐步状态或重跑旧整套B矩阵。


## 5. 2026-10-19 checkpoint 与接续

**当前仍是 `implementation_in_progress / waiting for native observation`，不是 developer_handoff。** 产品16路径写入已停止，必要增量self-check已完成；AC06必须的普通文件选择/缺UDT诊断/取消/完整pair确认保存/重载尚未取得，故不授予任何QA或Owner状态。sole coordinator已向Owner发出一次操作接续；后续不重问r1批准、不重开窗口或追加旧矩阵。收到实际观察后，只对账该同库阶段记录、补真实结果并正式交接新的fresh-context Verification。

| R ↔ AC | checkpoint真实事实 |
| --- | --- |
| R01 / AC01 | 精确批准前后SHA、当前before/17自身路径、1652保护路径/3旧ignored DB保持；角色串行，旧DAA002/003终验不变。 |
| R02 / AC02 | README pair具体默认3点/策略/角色、当前实例区别及迁入历史新位置；原YAML原字节保护、26本地链接已核。 |
| R03 / AC03 | 三组件局部调整；实际SFC/双语/同一默认关闭details/精确提示条件与无写handler定向结果通过。 |
| R04 / AC04 | 全Rust/owner/facade/receipt机制/既有配置与历史保护；13+9原owner函数反例及组件guards、旧raw有限核用。只对新tmp实例取证。 |
| R05 / AC05 | 先行独立expected、受控pair手写3叶/DB21、唯一ignore例外及旧DB保护已核；新pair实际导入结果待AC06。 |
| R06 / AC06 | 新普通native已启动、首开空来源receipt/业务表空已取证；**真实选择/预览/取消/确认/重载待Owner操作，尚未满足**。 |
| R07 / AC07 | 必要build/双语键/176literal/26链接/组件/guard完成，两个旧函数hash/raw有限核用；未运行Cargo测试或旧B矩阵，不称旧测试覆盖新pair。 |
| R08 / AC08 | 稳定文档和局部索引已同步；checkpoint完整增量patch/hash manifest及资源说明；正式handoff/新fresh QA/Owner终验均待真实后续gate。 |

checkpoint附件归 `D/checkpoint/`：`development.patch` 为基于本任务before的精确全量增量（包含5个新fixture及本tasks全文），`development-manifest.json`记录17路径before/after/hash，`source/`冻结17文件，`evidence-manifest.json`封已关闭命令/raw/脚本与静态附件。运行日志/实时SQLite/watcher.jsonl仍会变化，另列live资源，不伪封为immutable；checkpoint留其只读时间截面。批准spec及旧bundle不在Development增量patch中，另核精确hash。

资源归属：全部由本任务新建的dev/target（克隆缓存）、dev/dist、closed.env/两空YAML（closed-profile未创建）、native-r06新env/profile/SQLite/frozen机器码/端口override/原raw、只读快照和watcher、checkpoint及自有辅助脚本须保留供本次原生操作与fresh QA。无分支/worktree/ref/推送/邮件；旧DAA002 live76及用户15191不触达。最近只读lsof确认本次Vite PID71760监听127.0.0.1:49194，native PID71897持本任务profile锁；wrapper71406/pnpm71421在启动记录中，exec session89632保持运行；watcher exec session84888保持运行，0.5s有界，已留observed-000。不是宣称已正常退出。

接续标识：新窗口标题`AIIS Data Acquisition Agent`，只应是无PLC列表的本次新profile；源对绝对目录 `/Users/jason/Desktop/DreamCode/aiis-ics-arch/automation-world/data-acquisition-agent/src-tauri/tests/fixtures/source-import-minimal/`；profile=`D/native-r06/profile`。取证 `python3 D/native-snapshot.py <唯一label>` 仅mode=ro。watcher正常停止控制文件是 `D/native-r06/stop-watcher`，应在取得操作终态后由本任务执行者/唯一coordinator创建；不删profile锁或操作未知PID。Owner正常CmdQ后先核本条运行链退出/clean_exit及新源/ID/ETag/receipt稳定性，之后再盘点自有端口/进程。停止产品写入后，无须重新构建或重启来恢复当前检查点。

已知限制：受控手写样例不证明实际TIA导出兼容、UDT地址/DB长度或现场行为；无native截图/桥抓包/WebKit全网络观测，native操作需Owner真实relay配合本同库记录。无变化阶段无法单从库识别每次点击；不会把poll无变化伪记成已观察取消。原SQLite耐久性/版本限制保持，阶段C/Backend/SMA/DS/真实PLC/API/生产库/部署发布等全部排除。coordinator管理通知窗口与最终资源收尾。

## 6. 2026-10-19 原窗口误关闭后的运行接续（最新）

Human Owner 真实请求由sole coordinator传递：“我有真实的db和udt，本质上这两个文件其实是文本来的，是吧。你重新启动一下这个可以用来做验证的daa窗口，我刚刚误关闭了。然后告诉我应该如何验证？”这是同r1的运行恢复授权，不是AC06操作确认或范围扩展。没有提供真实文件路径，本轮仍保留获批受控pair，不读取真实来源或改变parser。

新接续证据 S=`D/resume-window-1792379112`，不覆盖原checkpoint/观察/raw。先核原 `launch-escalated-exit.json` 为exit0、03:01:59UTC `runtime_stopped/clean`，49194无listener、本profile锁无人持有；原watcher84888仍活，已记录observed-001。只读before与首开所有config表完全相同：0PLC/DB/组/点/编辑来源、原ETag与receipt字节保持，runtime clean_exit=1、业务表空。误关闭未观察到任何配置提交，不把它作为本次导入验证。

为遵守不重复构建/测试，使用此前普通 `pnpm tauri dev` 实际构建并冻结的同一机器码：`N/frozen/aiis-data-acquisition-agent`，SHA=`3ffc6ed4efedbd59d3aae7c657de88dda7ae5c92168a78e1d672b825b4a42805`；同时在DAA cwd启动既有 `pnpm dev --port 49194`。**这次直接启动已构建普通binary＋普通Vite，不重新运行tauri CLI/Cargo或文件watcher；不能写成又执行了完整pnpm tauri dev链。** 原普通构建与无fixture/driver来源证据保持。环境仍只指向同一 `N/native.env` / `N/profile`，read=false、两原空YAML，剥离继承业务覆盖，没有新profile、清库、删锁或重写receipt。仅为已明确授权的自有GUI/listener使用正常escalation，获准，无自动审批拒绝。

03:05:49UTC真实重开日志为 `yaml_migration_skipped/skipped_empty` 与 `runtime_started/stopped`。`S/reopened.json` 所有config表与重开前逐值相同，原ETag=`018ed7e5-7e71-4f34-8717-0f344b5699b2`、receipt ID=`0b91c0fe-1fa7-45d2-bed2-6228a9560637` / SHA=`4dd59ab487c1c22a7c3a86d16113cd4386c3518e4a2cb17694b192d223ca4b74` 不变；active为空、runtime业务表仍空，metadata仅回到运行clean_exit=0并增加启动事件。

最新运行资源：S/reopen.py wrapper85343，Vite pnpm85346/node85376只监听49194，native85398只持本任务原profile锁，exec session68833；原native session89632已exit0。原只读watcher session84888复用，没有两个watcher同时写。S/reopen.py在本次native正常退出后只向它自己创建并持有的Vite进程组发SIGTERM并等待，不操作用户15191。PID/argv/cwd/环境/资源差异在S/process.json，首开before/reopened及ready均为只读控制器证据。

窗口已就绪：标题`AIIS Data Acquisition Agent`，PLC列表为空、无任何已有配置。sole coordinator负责给Owner一次清晰验证步骤；本角色不重复询问。AC06仍待实际文件选择、缺UDT诊断/取消、完整pair无issues后确认保存、重载的真实观察；本次仅恢复原窗口，不宣称导入通过或developer_handoff。此次记录后再次停止产品与文档写入，保留同窗口/同库/watcher供Owner完成本轮操作，收到真实观察后才只对账并进入正式handoff。

## 7. 最新正式 Developer handoff：Owner 原生观察与同库闭环

**最新效力：`developer_handoff`。** §4–§6 是当时真实checkpoint/等待/误关窗恢复历史，完整保留；本节在Owner本次完成实际操作后补充，取代其中“尚待操作”的当前效力。仅表示Development实现、自检和证据交接，**不是QA verdict或Human Owner最终验收**。sole coordinator `/root` 下一步须启动全新的fresh-context actual Verification；旧DAA-002/003最终验收仍独立pending。

### 7.1 实际观察、运行与数据库事实

Owner真实回复由coordinator本轮传递：“前面的5个步骤我都做好了，5步操作都没问题。”另说明第四步后尝试了辅助DB偏移并出现不支持。`C/owner-attestation-relay.json` 留原话、来源与观察边界，C=`D/closeout-1792380367`。Owner确认涵盖实际文件选择/取消、仅DB21缺UDT预览且未确认、完整pair无issues预览、确认框先取消再确认保存、重载和正常退出。缺UDT的具体file/line/path屏幕、每次取消和预览的对象ID未独立截图/抓包；不能把SQLite的无变化阶段冒充逐次点击记录。其证据是Owner实际操作确认，结合未变owner预览confirm=false/取消不调提交的控制流、原LocalEngine preview/confirm同ID证明及下面同库阶段快照；未调用被测parser反向产生expected，未再次运行原生矩阵。

`N/observed-000`至`006`与C/final-closed.json的配置对账：

| 阶段 | 真实持久状态 |
| --- | --- |
| 000首开 / 001误关窗 / 002同库重开 | 原ETag `018ed7e5-7e71-4f34-8717-0f344b5699b2`；0PLC/DB/组/点/编辑来源，唯一空来源receipt原样。 |
| 003，03:08:40.995UTC | 首次保存PLC `DAA004-Owned`、loopback；**enabled=true**，尚无DB/点/来源，ETag `036f14ae-f631-44de-9de6-01e911665b8d`。这是实际偏差，不改写成停用。 |
| 004，03:08:51.410UTC | 同PLC ID改为 **enabled=false**，仍无DB/点/来源，ETag `3f4fd0c3-508f-4629-bf78-626f4497c745`。导入前已停用；read=false、无active、业务账本空，全程无连接/采集。 |
| 005，03:14:23.468–471UTC | 唯一完整pair提交：1PLC、DB21、3点、2编辑源、0组，所有导入点与PLC停用，草稿issues=[]；ETag `c7db1116-2738-479c-8f13-4f6c65cab9a5`。 |
| 006正常退出 / final-closed | 与005所有config表逐值相等，ID/源原文/SHA/DB树/ETag保持；runtime clean_exit=1，只有有界生命周期/保存事件增加。 |

额外两次PLC保存的实际enabled true→false偏差完整保留给Verification按R06/AC06独立判断，coordinator明确无需重做本轮操作。未发生激活/连接/读取；不把它描述为新增产品回归或扩展实现。

PLC ID=`1ae7d756-f2cb-471e-b98c-cc1a327d03ae`；DB ID=`207988f5-0f34-4f01-b99e-e531ba26feed`，name=MinimalImport、number=21、complete=true、flat=false；tree中唯一payload引用MinimalPayload，展开ready/count/temperature三叶。3点的sourcePath/type与先行expected完全一致，enabled=false/groupId=null/address=null，均绑定同PLC/DB。

| 编辑来源 | 稳定ID | 原文字节SHA-256 |
| --- | --- | --- |
| minimal.db，显式dbNumber=21 | `9492ca76-e061-4c48-bd35-8a2bb4c0520c` | `ce75a52c2a7806c406bcec3354d2e50ebd0188b7ee9c4f03c09a5250ad752d6b` |
| minimal.udt，dbNumber=null | `d30b6a39-ef2f-4e82-b175-21ca80508e22` | `1967d3e0b55550560a218cf8e969fd690da3e5ec18ae8f9609bf1c41cbd62a31` |

两来源在SQLite的原文逐字等于受控文件，DB.sourceId指向该DB来源；3点ID及全部引用在005/006/final保持。详细ID树与字段在 `C/native-reconciliation.json`，不预设UUID。DB length=65536是既有默认边界，不是实际DB长度证据。

私有receipt ID=`0b91c0fe-1fa7-45d2-bed2-6228a9560637`，SHA=`4dd59ab487c1c22a7c3a86d16113cd4386c3518e4a2cb17694b192d223ca4b74`，从首开到全部7阶段及最终整行/原文字节保持。active/previous=null，revisions/activation_intents空；runtime的plc_sources、configuration_contexts、activation_journal、collection_cycles、samples、sample_delivery、sample_references在每阶段均空。没有重写迁入历史、来源身份、采样/投递/ACK。

### 7.2 辅助偏移额外尝试的现有边界

Owner报告在第四步试“推算DB”失败。受控DB引用UDT，实际complete=true、flat=false；未改的 `plc_layout.rs::preview` 在 `!d.complete || !d.flat` 直接返回 `offset_inference_unsupported`，不进入地址推算/确认。此次没有独立IPC错误码抓包或持久错误日志，不能把源码推断的code写成捕获到的runtime错误；Owner观察与实际DB形态/现有guard一致。005至006/final配置、ETag、源/点ID/全null地址完全未变。此处只说明已有flat-only边界，不添加复杂布局支持、不改变parser/确认语义或要求额外步骤，不重跑测试。

### 7.3 命令、终态资源与保护审计

本次closeout只执行mode=ro的同库快照、读取已有raw、机械hash/diff/资源对账及停止自有watcher；没有新增构建、测试、GUI、源导入或设备操作。实际命令包括 `python3 C/snapshot.py final-closed` exit0、`python3 C/native-reconcile.py` exit0；完整输出报告、argv/cwd/限制在 `C/closeout-command-history.json` 与各JSON。`C/frozen-profile/{config,runtime}.sqlite` 是正常关闭后本任务同库的逐字副本，保留原profile不删库/锁。Python取证不冒称Rust链接SQLite版本证据。

Native于03:22:06.982UTC `runtime_stopped/clean`，session68833实际exit0；wrapper只结束自己创建的Vite组，exit=-15（资源收尾，不冒称Vite正常GUI退出）。49194和本profile锁的lsof均exit1且stdout/stderr空。按已有 `N/stop-watcher` 协议停止watcher84888，实际exit0、7次变化记录；没有重复watcher。无新listener/进程保留，所有本任务profile、冻结机器码、双库/raw/旧失败与checkpoint及resume证据继续保留给QA/Owner；其他用户15191/真实profile与旧live76未触碰。

Owner本轮另外自行放入 `DB_20260701.db` / `UDT_20260701.udt`，**不是Development的5个新fixture或16实现面**，没有采用为本次运行输入、修改、移动、删除或增设ignore例外。coordinator Supplement=`/private/tmp/daa-004-r1-hppdbt2h/owner-source-inputs.json` 单独固定来源。Development仅对照其精确字节hash，不解析/导入原文：DB 40649B / SHA=`691617444859a39364613f263e724b84a230d366fe5f7c1910003d82b23b3680`；UDT 709B / SHA=`939e3754acb1ec1d72e9dcf39b7212ab8506160fda8ea443a58ee5452aafa1f2`。DB继续被原一般规则ignored，UDT是Owner新增untracked；源码/版本发布可见性另归Owner/coordinator，不在本任务擅自纳入。

原始全树审计 `C/raw-global-scope.json` 如实 `passed=false`，outside为Owner新增UDT与并行 `plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md`；首个closure-audit因此真实exit1。baseline未重设，原outside/失败输出保留，DS正文未改/未作实施输入。coordinator核外部DS归属并提供独立Supplement；不得将未归属变化静默清除。16产品路径与原checkpoint全部匹配，owner/Rust/依赖/锁/YAML/旧bundle/三个ignored旧DB保持；DS文档漂移和Owner输入须在最终机械归属报告单列，不伪称整棵工作树从未变化。

归属核对已由coordinator完成：`/private/tmp/daa-004-r1-hppdbt2h/external-change-supplement.json`只覆盖上述两Owner输入及DSspec三精确路径。DSspec当前SHA=`fc0ab9a11b4145b994bc3586e014ef87b98148b87c3d2f6a53a65204f4d6379b`、131375B，来源为独立会话“主-DS 设备模拟器”获Owner授权的r1批准/P0只读核查及r2 PM草案，Development未向该会话发消息或操作其文件。最终`closure-audit-final` exit0仅表示明确归属后Development边界匹配：1651基线公开保护路径及3旧ignored DB未变，16产品字节未变；原raw全树报告仍passed=false、两outside和首helper exit1完整保留。三外部路径逐项hash/字节数与Supplement相等，不进入Development patch，不因此扩大任务allowlist。

### 7.4 R ↔ AC 最终Development证据映射与精确交接

| Spec | Development交接依据（不代替QA） |
| --- | --- |
| R01 / AC01 | 当前批准spec SHA、原before、17自身路径完整patch/新增全文/hash，旧bundle及保护面，外部Owner输入/DS漂移Supplement分权；没有改spec/checklist/协调索引。 |
| R02 / AC02 | README pair具体3点/策略及文件权威/当前实例区别，26链接；原YAML原字节保持。 |
| R03 / AC03 | 旧PLC主卡撤下，原默认关闭details承接历史；实际SFC双语渲染、精确提示条件/同一details无写handler检查。 |
| R04 / AC04 | receipt/所有Rust/owner保护，原13+9反例和新位置guards；首开到final receipt整行、active与业务表对账。 |
| R05 / AC05 | expected先行手工叶表、受控pair/唯一ignore例外；native最终3叶/2源/DB21/完整引用及默认状态吻合，不把默认长度当实证。 |
| R06 / AC06 | Owner五步实际确认＋同库7阶段/退出raw；最终ETag/ID/源SHA/receipt稳定、无业务账本。首PLC短时enabled偏差与无逐点击抓包限制如实保留，由fresh QA独立判断。 |
| R07 / AC07 | 必要构建/组件双语/guard/locale/链接通过，旧golden与proof按当前分支hash/raw有限核用；额外辅助偏移仅说明既有拒绝，无重复矩阵/构建/新测试。 |
| R08 / AC08 | README/app/i18n/局部索引与17路径最终diff/证据/资源一致；正式developer_handoff后停止全部写入，交新的fresh-context Verification，再由Owner决定终验。 |

交接对象是原dirty working tree，HEAD仍 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，无commit/push。最终 `D/final-handoff/development-manifest.json` 列17路径before/after；`development.patch` 是相对本任务原before的完整增量，5个新fixture及本tasks全文均在内；`source/`冻结17文件。`evidence-manifest.json`、commands、外部Supplement和`developer-handoff-receipt.json`固定完整命令/raw/hash、本次native闭环、真实偏差/限制及资源。旧checkpoint和两次窗口历史不覆盖；真正receipt SHA由handoff消息提供，避免自引用。

本次全部资源证据仍需保留，最终安全回收由sole coordinator在QA及Owner gate后按归属/依赖决定。受控手写pair不建立真实TIA导出、多DB编号映射、UDT地址/PLC长度或现场能力；新增真实来源不进入本次实施/验证结果。阶段C、Backend/SMA/DS实现、真实PLC/生产DB/API、上传ACK、依赖升级、发布/部署/推送继续排除。此交接不授予任何QA结论、Owner终验或现场权限。
