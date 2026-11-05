Task ID: SMA-004
Revision: r1
Status: qa_passed
QA Verdict: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Verification QA2 -> Human Owner final acceptance pending；精确 r1 返工候选 9d514bc4c71ae3ebb0b634118c86c6f409835f5d8d933b3fab5bccc51fc93676 通过独立验证；QA1 失败历史保留，F-QA1-001/002/003 已在下文 QA2 关闭
Workflow Mode: STD
Execution Mode: agent_team_same_session

# SMA-004 r1 独立验证 QA1

本记录由实际命名 Verification `/root/sma004_verification_1` 在 fresh context 创建，未继承 Development 对话推理。仅验证并写本 checklist；不修改 spec/tasks、实现、测试、配置或协调索引，不代 Human Owner 验收。本 profile 是 `contract_only`，不宣称平台 ACL、强制路由或由 TOML 推断实际运行模型/effort。

## 验证基准与独立证据

- 正式交付工作树：`/Users/jason/Desktop/DreamCode/aiis-ics-arch`；HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，无本任务新 commit。并行 dirty 不属于本任务，不 reset/revert/clean。
- 精确批准 spec SHA256 `0090a318d66027257f913376edbadeadba176eb1a08ba492bc845aad31387927`；Development handoff tasks SHA256 `39bc69ef683edc563bace7dcdd25131c8b529aa507279f5a9d1aca7f25fc2724`。Human Owner 批准本地配置、纯预览和暂时关闭正常投递，完成后独立验证。
- 2026-11-04 18:29:12（Asia/Shanghai）独立从 tasks 完整表解析 53 项 `[仓库相对路径,beforeSHA|null,afterSHA|null]`，排序、UTF-8 compact JSON 重算 digest **`ca47b7a9b167d6cf3d656c565fda4ee369fcc6c771974c445c5b48c503de747c`**；当前 after、DEV before 文件及 entry-manifest 均匹配。
- SMA-003 的 31 项原 after 全部匹配 004 实际 before；原三元组 digest **`ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf`**。没有用 004 改后树冒充 003。003 checklist 仍 owner_accepted / qa_passed，SHA `39d34539b4629fdb0fa1597879b97a113569d95d810acbad2a7bc96b4b0e2f86`。父 001 r2 仍 draft，SHA `34e60423105d3056620e08aadc42ad1248429e14dab4dfd77920acf6c827f264`，不转移其批准或验收。
- 对 root 实际进入快照与 DEV 进入时字节核对 **283 项保护面，0 漂移**；001/004 的已授权 PM 批准登记以 DEV before 为准，不能归为 Development 修改。CODE_INDEX 相对 before 仅 SMA 行和新增本任务入口，未覆盖其它并行条目。
- QA 自有临时根 `/private/tmp/sma-004-r1-qa1-20261104/`；独立 entry-audit、status、命令日志、显式 disabled.env、可丢弃 SQLite profile、测试文件及同 SHA incognito app 均归本任务。任何产品启动使用绝对 SMA_ENV_FILE / SMA_PROFILE_DIR、空 Backend、HTTP=false；仅旧兼容测试使用自有 loopback fixture。未安装辅助依赖，未访问默认 profile、真实数据库/设备或业务服务。

## 独立命令检查点

命令在正式 SMA 根执行。`P` 表示 `pnpm --config.verify-deps-before-run=false --config.update-notifier=false`，仅复用锁定依赖；没有改项目配置。Rust 环境为 `SMA_ENV_FILE=/private/tmp/sma-004-r1-qa1-20261104/disabled.env SMA_PROFILE_DIR=/private/tmp/sma-004-r1-qa1-20261104/rust-profile SMA_BACKEND_BASE_URL= SMA_HTTP_ENABLED=false`。

| 实际命令 | 结果 | 证据层 |
| --- | --- | --- |
| `P check` | 0，vue-tsc 通过 | 本轮独立正式源码 |
| `P test` | 0，10 passed / 0 failed | Node 内存 IPC/文件/偏好 fixture，不冒充 SQLite/native |
| `P build` | 0，1684 modules；保留 PURE 注释及 >500kB chunk warning | 本轮独立正式 dist |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 0 | 本轮独立正式源码 |
| 上述隔离环境 `cargo test --manifest-path src-tauri/Cargo.toml --locked` | 0；14 本地配置 + 11 continuous + 3 manual/pure + 3 startup = **31 唯一命名测试** | 真 SQLite/CAS/回滚/busy/故障/跨 OS 子进程、受控 loopback；嵌套 child 输出不重复计数 |

本轮四个 pnpm/fmt 日志和 cargo-test.log 在 QA tmp 保留。DEV self-check 已消费，但不替代这些独立执行结果。

## 原生工具历史与实际覆盖检查点

最终 DEV incognito app 复制至 QA 自有路径，复制前后 binary SHA 均 **`fdd5644f7c5b69fe564dfca493a1616ff88a1e543f3351c2815bb2900a9feb52`**。只消费临时 `incognito:true` overlay，正式 identity/window/capabilities 未改。incognito 不证明 native 跨 OS 进程 UI 偏好持久化；Rust SQLite 使用显式 profile，可以独立跨进程重开。

1. 首次 `cua.getState()` 显式 timeout_ms=20000，20.0234s 返回 docs/inventory，无明确 locked 错误；不据此推断 Mac 已解锁或 app 可操作。
2. 显式 env/profile 启动实际 PID **6578**，完整路径匹配 QA 自有 app；10:30:33Z 日志 HTTP=false、Backend=false、SQLite revision0、startup=false。首次 getApp 显式30000ms，实际 **125.0961s 后返回完整连接页 AX**；显式时限未生效。AX 非0、截图0、UI操作0。主协调基于未收到回报发起有界中断；返回后收到 turn_aborted，新 turn 如实报告已返回，不能写成 AX=0 或用户取消。
3. 按该时点协调指令，下一 CUA 仅 completion_summary 并成功，10:34:01Z 精确核 PID6578/path 后 SIGTERM；postPs 为空，15192/14192 无监听。退出后没有读旧 AX/getApp，native-cleanup.json 保留。
4. 主协调据已真实返回的新事实安排一次受控新启动。同 SHA、同隔离 profile、显式 env 启动 **PID12097**，10:35:37Z 日志仍 HTTP=false、Backend=false、revision0。新 getApp **0.1924s** 返回完整 AX，无 pending；后续使用有效句柄实际验证，未盲目重复 bootstrap。

截至本检查点的实际 native 事实：

- 连接保存 revision **1**；本地 OpenAPI JSON 经 OS 选文件，preview 期间只读 SQLite 仍 catalog0/revision1；显式 apply 后 revision **2**，勾选保存材料 revision **3**；从已保存材料派生目标 revision **4**；UI 创建值规则 revision **5**、未知 sourceKey+factName 映射 revision **6**。
- Rust 已保存映射预览实际返回 mappingKey=qa-mapping、revision6、三项 fact_missing、request=null、deliveryAvailable=false、sourceReferences unverified；没有用模板0作为事实值。真实截图和 AX 均已返回。
- 三资源目标导入 OS 选文件 preview 显示创建1/更新0/不变7/错误0，期间尚未 apply；显式 apply 后 revision **7**。原生明→暗、中文→英文切换没有改变 revision。
- 用 QA **只读 SQLite 快照生成、明确标注的恢复 fixture** 补测恢复（产品完整导出失败见 F-QA1-001，不能用此 fixture 冒充产品导出成功）。英文暗色 native 预览列出删除 `targetApis:qa-imported`，确认框未勾时 apply disabled；显式勾选和 apply 后 revision **8**，整包内容恢复且仍英文/暗色/HTTP off。随后目标名称编辑 revision **9**，值规则编辑 revision **10**、删除 revision **11**。

## 已确认实现失败（不静默修复）

### F-QA1-001：完整配置 native 导出 MIME 不匹配

影响 AC02 / AC06 / AC12、R5.4。原生 revision6 点击“导出完整配置 JSON”，立即出现 **`本地配置操作失败 COLLECTION_FACT_FILE_EXPORT_INVALID`**，未打开 Save As、未产生备份文件。`TwinJsonContractPanel.vue::exportBackup` 构造 `mimeType: "application/json"`；现有 `src-tauri/src/services/file_export.rs::validate_export` 对 .json 精确要求 **`application/json;charset=utf-8`**。三资源原 helper 使用后者，完整备份新增调用未遵循现有合同。Rust export 字符串通过不能替代实际 native 保存链。复现中配置仍 revision6，无半写。需 Development 修复后新的 fresh QA 复核实际 Save As、文件字节及恢复。

### F-QA1-002：单资源导入预览未展示受影响资源 key

影响 AC05、R5.2。native 导入只含 `qa-imported` 的合法 targetApis JSON，预览只显示“预计新增1 / 预计更新0 / 保持不变7 / 错误项0”和 apply；**没有显示 qa-imported 或任何 create/update/unchanged 的资源 key**，完整 AX 与截图均确认。`MappingBatchOperationsDialog.vue` 只渲染三个数组的 length；只有 errors 渲染 item.key。该公共弹层用于目标/规则/映射三资源，Owner 无法从预览核对具体更新对象。整包恢复另有 key 列表，不抵消此失败。需 Development 显示实际变更 key 后复验新增/更新/不变及错误情形。

### F-QA1-003：新增裸文件控件未随中文应用国际化

影响 AC11、R8 和根用户可见文案合同。中文 native 明色实际截图中，新“预览恢复 JSON”及 OpenAPI 文件选择使用裸 `<input type="file">`，按钮/空状态仍显示 **Choose File / no file selected**；切换英文才与其匹配。新增控件没有通过现有本地化按钮/隐藏文件入口提供应用 locale 文案。003 的原批量文件入口已隐藏 native 文案，本任务新增两处未沿用。OS 文件对话框自身语言不计此项；失败仅指应用页面上的可见文件控件。需 Development 将该有限控件接入对称 i18n 后实际切换复验。

## 18:44 工作检查点（历史，后续结论见下）

本段是首次写入时的工作检查点，当时**尚非最终 verdict**。后续继续核对必要 native 配置维护、业务 SQLite 跨 OS 进程重开、普通启动及剩余 AC，结果见下。已证实实现失败不能归为工具 blocker 或写 qa_passed。Human Owner final acceptance **pending**；未来新 Backend/DAA/GET→POST、真实业务持久化、采用迁移、设备、部署或 Git 发布均未因此完成或获授权。

QA 不回收目录。DEV 原始证据及 QA 自有 tmp 因当前验证、失败复现和后续返工仍保留；主协调在最终接收并确认无运行/证据/后续依赖后盘点。当时 PID12097 仍为自有 native 验证进程，之后已按精确 path 收尾，退出后不再访问旧 AX/getApp，详见下文。

## 验证环境、读取与源码审计

完整消费根 AGENTS/README/PLAN 双语、最近 AW/SMA README/PLAN、SMA src/app README 双语、canonical workflow、verification.toml、004 spec/tasks、003 完整 bundle、001 父规格关系及实际 before/current 实现/diff。最近作用域没有额外 AGENTS。CU 公共输入与既有接受证据只作依赖及连续性依据，不把旧验收写成本轮重新操作。

使用 `project-governance`、`aiis`、`rust-runtime`、`desktop-tauri`、`frontend-ui`（FRAMEWORK 主题控制链/分层与既有 CU 视觉规范）、`i18n-workflow`、`code-document-indexer`，仅用于验证。实读 macOS **15.7.7 arm64**、Node **v22.19.0**、pnpm **11.11.0**、Cargo/rustc **1.89.0**；普通入口实际 Vite **6.4.3**。不安装测试辅助依赖，不加载不适用的 Backend/PLC/Worker skill 或执行其外部动作。

源码独立审查结果：

- 配置链为组件/store → localConfiguration IPC facade → 薄 commands → 单服务 Mutex → domain 全图校验 → ConfigStore；无 TSS CRUD/import/audit fallback。旧连接 localStorage 不再读取，环境 URL 不写入配置。事实/OpenAPI 仅显式操作且先门禁；本轮 Node fixture 把任何 fetch 当失败。
- schema v1 为唯一 configuration singleton；BEGIN IMMEDIATE、150ms busy_timeout、事务内 CAS/全图校验、完整 document 更新和不变不增 revision。真实 pretty UTF-8 信封使用 `to_vec_pretty(backup(document))` 校验；每类最终集合和完整信封都在每次变更校验，不能靠重复小保存绕过。明确 profile 相对路径在 logging 初始化之前拒绝。未新增业务历史/lease/outbox 或跨进程排他机制。
- 预览 token 绑定 intent Value、实际 observed revision 与候选图；apply 在事务中重校验。前端保存时不先获取新 revision 掩盖陈旧编辑；已保存 mapping preview 仅 id/revision，不传未保存 bindings。Node 旧草稿冲突回归与 Rust 内容/revision 冲突均通过。
- legacy HTTP service 的 before/current 差异只有三个入口改名 `legacy_*`、doc hidden 与新增正常入口拒绝 wrapper；原 HTTP/lease/failed/ambiguous/stop 算法没有修改。源码内 legacy 名仅出现其三个定义，正常 App 的 invoke registration 不注册 legacy 入口。旧测试仅改为显式 fixture 入口，原 17 项回归通过，不将可直接测 legacy service 宣称为产品开放执行。
- 锁文件只新增 rusqlite0.32.1 及其固定依赖闭包，共10个 package/version；无旧 package/version 删除或升级，无前端依赖变化。新关键 Rust/TS 文件有中文说明，CODE_INDEX 仅本任务 SMA 增量。文件分层与 allowlist 一致；F1 是新调用与既有保存合同不匹配，未为 QA 擅自改 Rust 保存服务。
- **18:52:54** 最终只读审计：53 项候选/approved spec/tasks/001/003 checklist SHA 均无漂移，283 项保护面0漂移；SMA 除声明候选、角色文档及协调索引外额外源变更0。12 份相关 Markdown 的 **186** 个本地链接有效，`git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md` 退出0。后续本 checklist 追加再进行最终链接/空白检查。

本轮独立 build 的 dist 与冻结交付逐字节相同：

| dist 相对路径 | SHA256 |
| --- | --- |
| index.html | 9e2549edbdfedb52fdd71eb7155896fbe9e7e3650ae390c92b200e0f7fe6db52 |
| assets/index-BEVlKax_.js | 0f335ac92dcc03141e71b8218d4194c8925c68cc3c56afc1ae5d48638f7c19a9 |
| assets/index-DCMy5ngi.css | a60ed59b72d828dc85b101de278d0c60b3b5b058ca70e5e472baa99914c81da3 |

## 补齐的 native 生命周期、普通入口与资源结果

第二段 native 中，映射名称、间隔和 path 常量真实编辑为 `QA edited mapping` / 1500ms / `QA-A`，草稿预览显示 `/qa/QA-A`，其余未知事实继续缺值；保存后 revision **12**。已保存预览与草稿的标题/身份分开，原生不产生运行成功计数。运行页点击 Start 实际显示 `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE`、仍 Idle/0；随后通过 UI 显式保存 auto-start=true，独立 v1 偏好不改变业务 revision。

先 completion_summary，再精确退出 PID12097。一次 QA-only 收尾 helper 在 lsof 文本 UTF-8 解码时失败，**该失败发生在发信号之前**；改为仅该 PID 的 `lsof -a -p ... -i` 和容错解码后重新核 path、SIGTERM，18:47:19 postPs 为空、该 PID 网络列表为空。该瞬时检查不冒充全程抓包。

同 SHA / 同 native-profile、相同显式 disabled 环境启动新的 OS **PID30868**。18:47:52 只读 SQLite 比较：schemaVersion、revision **12**、完整 document 和 updatedAt 与退出前 snapshot **逐字段相等**；不是同进程重新加载，也不是 browser localStorage。新 getApp **0.1853s** 返回 AX，无 pending。UI 真实恢复连接127.0.0.1:9、目标 `QA edited target`、映射 `QA edited mapping` 及1常量/2事实绑定。incognito UI 回到中文/明色，符合非持久 WebKit 隔离，不把它计为 native 偏好持久化失败或成功。

旧 auto-start=true 实际从独立 v1 文件读取，并在18:47:48日志中由 `sma_execution_admission` 明确拒绝稳定错误码，未启动运行。native 点击删除仍被映射引用的目标，出现含 `qa-mapping` 的引用错误，revision 仍12；先删除 mapping 后 revision **13**，再显式确认删除目标后 revision **14**。因此新建/编辑/删除映射和目标、值规则的新建/编辑/删除均实际穿过 UI→Rust→SQLite，不以 Node fixture 代替。

实际观察中英×明暗四种组合的保留工作区与准入/错误文案，目标/规则/映射编辑弹层和 OS 文件选择均可操作；通过键盘 Right/Return 从组进入 Fact Table，HTTP=false 下输入qa-source读取只得到关闭态错误；日志明确 `SMA_EXTERNAL_IO_DISABLED`。表格局部横滚通过实际水平 scrollbar drag 到操作列，未改窗口限制。列宽/time/UI preference helper 和CU输入均未变，Node回归通过，003原八表drag/持久化/reset及完整140状态/12弹层证据保留为历史；本轮没有重新声称完成全部140状态或 native 跨进程 UI 偏好持久化。

18:50:56 当前段完成 CUA summary 后精确 SIGTERM PID30868，postPs 为空，退出后未读该句柄 AX/getApp。最终 native profile 保留 revision14 的可丢弃配置与 v1 auto=true fixture，用于失败复现；不回收目录。

普通启动独立执行的完整命令：

```text
SMA_ENV_FILE=/private/tmp/sma-004-r1-qa1-20261104/disabled.env
SMA_PROFILE_DIR=/private/tmp/sma-004-r1-qa1-20261104/dev-profile
SMA_BACKEND_BASE_URL= SMA_HTTP_ENABLED=false
npm_config_verify_deps_before_run=false npm_config_update_notifier=false
pnpm --config.verify-deps-before-run=false --config.update-notifier=false tauri dev
  --config /private/tmp/sma-004-r1-qa1-20261104/incognito-overlay.json --no-watch
```

上列为同一次命令的分行展示。正式普通入口未改；仅测试加受支持临时 incognito overlay，未启动正式默认 WK store。实际 BeforeDevCommand 为 pnpm run dev，Vite在**15192**启动，DevCommand `cargo run --no-default-features` 编译/链接成功（8.20s）；18:51:14–16日志确认 HTTP=false、Backend=false、配置revision0、startup=false及前端默认值加载。Ctrl-C有界退出，exec session返回 **0**，不是把主动停止算作运行失败；未将该无UI绑定的dev运行另记为 native UI操作证明。

另一 dev-profile 的 SQLite 实读 **revision0、空连接、六集合全部空**，未读到 native-profile 的配置。18:52:16最终ps/lsof退出0：6578/12097/30868旧native均已退出，本任务native/Vite无存活匹配，15192/14192无监听。没有任务 browser tab、JS dialog、viewport override、pending CUA 或常驻 fixture 服务；未操作用户浏览器既有页面/组。QA仅停止自有精确进程，不回收目录，不触及002事故原件、003旧profile或其它任务资源。

结构化应用日志共4/17/9行，提交revision1–14、引用拒绝和准入拒绝可追溯，没有记录完整配置、材料正文或事实值。第二段合并stdout/stderr另有一条macOS TSM CapsLockLED系统诊断，**不是JSON**；本轮保留，不能把合并终端文件写成每一行均为应用JSON。QA首个日志解析helper误设全文件JSON而失败，后分别解析应用JSON和该系统行；持久应用JSONL日志及事件语义未因此改写。

## AC01–AC12 最终判定

| AC | QA1 结果 | 独立证据与界限 |
| --- | --- | --- |
| AC01 | 通过 | 003已接受候选与004 before连续、精确批准、53项和283保护面均核准；本地权威全链源码与Node零隐式fetch、native离线维护，无TSS配置/审计fallback或退役入口恢复。native未做全程网络抓包，不把瞬时lsof替代loopback捕获。 |
| AC02 | **失败 F-QA1-001** | native离线连接、OpenAPI预览/apply/选择、目标/规则/mapping CRUD和真OS重开revision12/全文相等、另一空profile已验证；完整JSON的native文件导出失败，不能给予整体通过。 |
| AC03 | 通过（纯预览层） | Rust五类型/四位置/fact-constant/类型/必填/规则既有回归；native保存行纯预览id/revision6、request=null与unverified明确，草稿常量预览分开；无claim/运行成功/目标请求。无真实事实来源或真实投递声明。 |
| AC04 | 通过 | native未知sourceKey+factName保存、重开一致与缺值；Rust最小metadata证据/无value/类型冲突、legacy正规化与冲突、factId错误合同拒绝通过。模板0未冒充事实。 |
| AC05 | **失败 F-QA1-002** | 三资源JSON/XLSX往返、旧九列POST、宏/公式/类型/引用/重复key/载荷边界、内容和observed revision绑定回归通过；native合法target import零写预览/显式apply通过，但未显示任何受影响key。 |
| AC06 | **失败 F-QA1-001** | Rust完整export→新隔离库restore、确认false/未知版本/引用/事务原子性及不倒退通过；native用明确QA只读快照fixture验证删除范围、确认与rev7→8，保持UI/HTTP；不能替代App完整导出及真实备份文件往返，后者失败。 |
| AC07 | 通过（隔离存储） | 14项真实SQLite回归覆盖同服务双线程CAS一胜、150msbusy、trigger事务中止、0444、损坏/未知schema/不可用/相对路径拒绝及最终全集/pretty信封上限；nativeprofile与devprofile隔离。未宣称OS跨进程排他。 |
| AC08 | 通过（源码/存储+native引用） | Rust材料/目标/规则引用拒绝、类型改变与disabled保引用、各非终态写入拒绝、终态后可提交；native引用目标拒绝含mapping key，解除引用后删除成功。没有自动停启。 |
| AC09 | 通过（分层准入） | 原生UI Start实际IPC拒绝、旧auto=true重开日志拒绝；Rust直接manual command的false/true子进程loopback零accept、正常service manual/start/resume拒绝、薄command注册及准入顺序源码核准；UI Test因local rowVersion=null禁用、说明可见。未另从native DevTools直发全部IPC，未将按钮disabled当核心证明。HTTPfalse事实/OpenAPI零fetch回归通过。 |
| AC10 | 通过（局部兼容） | 原17命名HTTP/lease/audit/failed/ambiguous/stop/五类型四位置/startup v1回归独立通过；old算法仅fixture入口更名；v1字节/惰性段及空profilefalse、旧localStorage/env不自动采用。正常App无legacy fallback。 |
| AC11 | **失败 F-QA1-003** | CU公共入口、身份/端口、七叶/键盘、四种中英明暗组合、弹层/横滚和真实上海到秒已核对；未变helper/003历史持久性证据与本轮Node回归分层保留。新增裸file input在中文页面暴露英文系统文案，未满足应用i18n。 |
| AC12 | **失败 F-QA1-001/002/003** | check/10Node/build/fmt/31Rust、普通dev编译启动/收尾、同SHA native实际CRUD/真OS重开、diff/allowlist/候选/链接均有真实证据；三项实现failure未关闭，不能以构建成功授整体通过。 |

## 最终 verdict、限制与返工 handoff

**QA Verdict: qa_failed。** 三项实现failure已由native AX/截图/实际错误与源码确认，当前不是 `qa_blocked`，也不能因为首次工具慢/被中断而将实现问题归为环境。首次getApp125.0961s时限失效和早先DEV原生0证据保留为真实历史；后续本轮0.1924s/0.1853s有效句柄已补足必要native配置维护与SQLite业务跨OS重开证据，无待解除的原生工具blocker。

返回 Development 的精确范围为本r1内 F-QA1-001/002/003：

1. 修复新增完整备份与既有native保存MIME合同，实际打开Save As并导出可再恢复的UTF-8完整备份；不得只测Rust字符串。
2. 单资源预览显示实际create/update/unchanged/error资源key，让用户在apply前可核对对象；保持内容/revision token和无半写约束。
3. 两处新增文件入口使用项目现有本地化按钮/隐藏file pattern及对称locale，中文/英文跟随应用；不以更改OS语言作为修复。

不得由QA修实现；返工完成必须记录新candidate/before-after、DEV self-check和handoff，再启动新的 fresh-context Verification QA2。可对精确不变面复核沿用本轮证据，改动面、native导出文件/恢复和变更key/文件控件须实际重验。本轮不会把原失败改写为通过或让Development修改checklist。若修复必须超出spec allowlist，先由PM处理精确范围，不由QA授新权限。

**Human Owner final acceptance: pending。** 本结果供Human Owner审阅、由协调者返Development；不授予阶段③、父SMA-001或总体SMA最终接受。真实/default profile采用、旧Backend停写、数据库迁移/清理、GET→POST执行、DAA上传/全链、真实目标业务保存、可靠恢复/容量、设备、部署、发布和Git动作仍不在本次授权范围。

## 证据与资源交接

关键结果与候选摘要已永久写在本checklist及DEV完整53项表，不仅依赖tmp。必要QA原始证据的SHA如下；图像由受支持CUA实际返回并目视检查，工具未提供本地截图文件路径，本记录不虚构截图附件。

| QA自有tmp文件 | SHA256 |
| --- | --- |
| entry-audit.json | 25e9c752c5cb2537b3458314eaba6ffbcaf891fe75a0177147d19cbaf0599692 |
| pnpm-check.log | aacdfedc485449151e8f0cedfb8264a7d15047256a7b3c3a4a9e848e28e7b178 |
| pnpm-test.log | e890b5d9a7608605ddcce754f6aac2ec1c2e5266c4ffc9aa2887646bdf805bf4 |
| pnpm-build.log | fc95d3123ca2da055d9c7bb9572af511e9b41236134a9d577277c325122f26c8 |
| cargo-fmt.log | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| cargo-test.log | 21f83714f68e393e2b3cd3ce1dffc1755e33207b6e01da42a15788aaa780bbd9 |
| native-stdout.log | 92c27a341cc49d4c6227c1c2c96679c2fd9233ab7e5a6f3c546a99ea705b66e2 |
| native-stdout-2.log | 81cad2b1aec58cd8c36179508130105d5cf355c14e5758ed1124d147ea5cc805 |
| native-stdout-3.log | f2f1f9d721bc83abb8167ceaa30771836039e44e984aa1231a452be1572f8c7a |
| log-audit.json | ec114e667673b0fecd7597469b97b2d5610acce609f9d61ccde1e127796a4be9 |
| native-cleanup.json | 71441bb856fc5295c8d06b25bbb84daadda403fb6de7f32f8ee4393de33108bd |
| native-cleanup-2.json | baecc064683d9a7ca24d9aa202c2aed26562457627557288b9ff7608e91009f5 |
| native-before-reopen.json | 7dbe9e045ba832b1d9953bdab6e8fdc2268f40042d4b18fcc8c459791b52a7ed |
| native-reopen-3.json | 2f6e5afabdbdd320338180f3edad9b58d6b7a60e9eb72108dde13ef529d634d4 |
| native-cleanup-3.json | 6f5650585c0ce56e5c124ba5acbc32af239579d82fd0802c9a9e7c98a327f5b3 |
| native-final-snapshot.json | 78bacea7f9102c8da5ce3c1c390cac13f43ed221b276174550843d7b4a7b27ee |
| tauri-dev.log | 8f115f9c17fa5b9960a6a2621402622fa897ac4600e407cb10bc571fe4556170 |
| process-final.json | 6508a9a2e9de1c33df32c811d221e483349aa406af657aefabbcf50a3d04b46f |
| final-audit.json | 40ae0eadd9ea40fcca7e5271381fa6cb40dad582ce66099ce557bd219ca3bfc6 |
| qa-openapi.json | cef083b2c4a9bcb1c2c50822649813caf795edbadeaafdbe05f590c8d4721969 |
| qa-target-import.json | 69d6bee2a064e8cec2d1a9a456acc11640f97214064250ff25811eeee5dd3b7e |
| qa-restore-fixture.json | 5a154ea0687cd747c16e9b45012aa6245ba32e39ff37cec0a7f16ef9d308a6fb |
| qa-evidence-manifest.json | c5ea48b754f8d859e952967729404a8261cb6a7b5daac95ad11b8c49aee85f5c |

`/private/tmp/sma-004-r1-qa1-20261104/`及DEV `/private/tmp/sma-004-r1-dev-20261104/`保留供返工与QA2复核，包括同SHA app、原始日志、env、隔离profile/文件夹具与before/candidate。无新分支/worktree/替代交付源码。QA未执行目录清理；root在返工复核、必要证据已安全归档且无运行或后续依赖后再盘点可回收项。项目node_modules/dist/target/gen属忽略的构建资源，未清理或提交。没有通知/邮件动作。

18:57:34最终handoff审计退出0：53项候选、283项保护面及四份权威文档均无漂移；本checklist状态/QA Verdict一致为qa_failed、无尾随空白，范围git diff --check仍0。完整证据manifest包含24份实际QA日志/快照/夹具SHA；本轮唯一项目写入为本checklist，协调索引由root同步。以上三项失败保持未关闭，等待Development返工与新的fresh QA2。

<a id="qa2-r1"></a>

## QA2：r1 有限返工的独立验证（2026-11-04）

本段由新的实际命名 Verification `/root/sma004_verification_2` 在 fresh context 执行；未继承 Development 对话推理。此前 QA1 的原始 `Status: qa_failed`、三个失败及工具历史作为历史完整保留，上方当前元数据只反映本段最新结论。QA2 仅修改本 checklist；没有修实现、测试、spec/tasks、配置、索引或其它并行工作。profile 仍为 `contract_only`，没有由角色 TOML 推断运行 model/effort、平台 ACL 或强制路由。

### 精确基准、完整 diff 与复用依据

- 正式交付工作树仍为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`；没有新 commit、分支、worktree 或替代交付源码。其它 Backend/DAA/DS/FF dirty 未归为本任务，也未 reset/revert/clean。
- 实读根 AGENTS/README/PLAN、最近 AW/SMA README/PLAN、SMA src/app README、canonical workflow 和 verification.toml，完整 004 spec/tasks/QA1 checklist、003 接受事实及原 31 项表，独立读取当前配置/存储/准入/文件/UI 实现与两轮 diff。最近作用域没有额外 AGENTS。使用 aiis、project-governance、frontend-ui（FRAMEWORK 主题控制链）、i18n-workflow、desktop-tauri、rust-runtime 和 code-document-indexer，仅验证。
- approved spec SHA **`0090a318d66027257f913376edbadeadba176eb1a08ba492bc845aad31387927`**；当前 Development rework1 handoff tasks SHA **`43648f8747c5a4f992a0b50f27a2e305c4004e06959d839c972cc522570db750`**；进入 QA2 前本 checklist SHA **`214f711c2e735d10ff2b248038b17aeb067b5873911edb92e2d9076797dc0433`**。
- 从 tasks 原 53 项表和后附 6 项 delta 独立重建：保留原 before，仅替换六个 after，按仓库相对路径排序 `[path,before|null,after|null]`，UTF-8 compact JSON 重算整体 digest **`9d514bc4c71ae3ebb0b634118c86c6f409835f5d8d933b3fab5bccc51fc93676`**。不是六项 delta 的 digest。原 before、QA1 归档 source、当前 after 和完整 manifest 全匹配；原 ca47 digest 也重新核准。
- 对原 `candidate.patch` 的 **53 文件 / 143 hunk**，从 004 实际 before 逐 hunk 重建到 root 保存的 QA1 失败 source；对 `qa1-delta.patch` 的 **6 文件 / 13 hunk**，从该 QA1 source 重建到当前正式树。两轮重建结果逐字节相等，patch SHA 分别为 `5edb7931013ed2c1d667f28dd8fde22f86d59588e5b872f3ba453dfa3ceee600`、`5fb7ffcae8966627634ea969ea1cfa9907c897a55edd49be8abe65db138fdce6`。不是仅拿当前改后树反推 QA1。
- SMA-003 原 31 项 after 全部连续到 004 实际 before，原 digest 仍 `ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf`；003 checklist 仍 owner_accepted / qa_passed，SHA `39d34539b4629fdb0fa1597879b97a113569d95d810acbad2a7bc96b4b0e2f86`。父 001 r2 仍 draft，SHA `34e60423105d3056620e08aadc42ad1248429e14dab4dfd77920acf6c827f264`，没有继承其批准或最终接受。
- **283 项保护面无漂移**，包括 CU、正式身份/端口/普通入口、UI preference/列宽/time helper 等。六文件返工未改 Rust、SQLite/IPC/token、锁、旧 HTTP 算法、原 native `file_export.rs` 或 CU。原 53 项中的其余 47 项完全一致。锁相对 004 before 仅增加原批准的 10 个 package/version，无原 package/version 删除或升级。
- 已逐份重算 QA1 evidence manifest 的 **24 份原始日志/回执/夹具 SHA**，全部一致；实读 cargo-test、普通 tauri-dev、native/reopen/cleanup 和快照证据。因此明确复用 QA1 独立通过的 fmt、**31 唯一 Rust 命名测试**、普通 `pnpm tauri dev`、原生 CRUD/revision12 真 OS 重开及未变准入/引用/存储故障证据。本轮没有把这些复用写成重跑，也没有只用 DEV self-check 作 QA。

### QA2 独立命令、环境与产物

实读 macOS **15.7.7 arm64**、Node **v22.19.0**、pnpm **11.11.0**、Cargo/rustc **1.89.0**，版本查询均退出 0。正式 SMA 自身锁定依赖保持；没有安装辅助依赖或改工具链。临时根为 `/private/tmp/sma-004-r1-qa2-20261104-1915/`。下表 `P` 为 `pnpm --config.verify-deps-before-run=false --config.update-notifier=false`；普通前端命令同时固定该根的绝对 `SMA_ENV_FILE=…/disabled.env`、任务 profile、空 `SMA_BACKEND_BASE_URL`、`SMA_HTTP_ENABLED=false`。项目实际 `.env` 不存在；未读取真实/默认配置。

| 实际命令 / 检查 | QA2 结果 |
| --- | --- |
| 正式 SMA 根 `P check` | **0**，vue-tsc 通过 |
| 正式 SMA 根 `P test` | **0，12 passed / 0 failed**；含正式 SFC 导出/选择/恢复预览 handler，以及三资源 × 双语的正式批量 dialog slot 内容渲染 |
| 正式 SMA 根 `P build` | **0**，1684 modules；既有 PURE 注释和 >500kB chunk warning 保留 |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md` | **0**，最终追加后再核对 |
| Python 候选、before/QA1/当前、两轮全 patch、003 连续性、283 保护面和 authority 审计 | **0**；当前 53 项 / digest 匹配、未解释漂移 0 |
| 22 份相关 Markdown 的本地路径链接及 common locale 对称检查 | **0**；追加前 314 条本地路径链接有效，common 61 键对称；最终追加后结果见末尾 |
| Rust fmt / cargo test --locked / 普通 tauri dev | SHA 核准后复用 QA1 的独立 **0 / 31 项 / 0** 证据；本轮六文件返工没有改变这些表面，不重复运行 |

Node 新用例的 vendor dialog 外壳为 headless stub，生产 slot/handler 实际执行；它不证明 native Save As。三资源 JSON/XLSX、公式/宏、旧九列 POST、陈旧编辑/preview revision 和内容约束等原回归也在本轮 12 项中通过。真实文件保存/恢复的证据在下节，未用内存 IPC 或 browser localStorage 冒充 SQLite。

本轮独立 build 的 HTML/CSS/JS 与返工 artifact 逐字节相同：`index.html` SHA `cfb35623e09311517fbc0231d0588b2d2c8f4c96fafcf7d336b89f67e7ce6eb3`；`assets/index-BMgQ2-2s.css` SHA `86e118a47de8f3e265a2a28f2fdecb0e32ac70b76845b1b1dc657a1a89f27272`；`assets/index-zObT9eb3.js` SHA `015e84b4b100200a63d314548cbf5269b1bd00f9b1bfe5107cd91351faf5ddb0`。复制到 QA2 自有路径的 incognito app binary SHA **`79b7f666cc70b51a9cf7126f86919158a8026557a565aa8138f623b1865cb95f`**，复制前后相等；未用旧 fdd564 产物代表本候选。

QA-only 辅助历史如实保留：初次 003 摘要脚本把 SMA 相对路径当成仓库相对路径，断言失败后修正路径；首次最终审计在系统 Python 缺少 tomllib 时退出 1，改为只读解析锁文件的 package/version；随后 patch scanner 未识别 `/dev/null` 新文件 header 而退出 1，补齐 scanner 后完整 53/6 文件逐 hunk 校验成功。以上只修 QA 辅助检查，没有改产品或测试。两个最初 pnpm wrapper 的 login shell 先报告 Homebrew `ps: Operation not permitted`，pnpm 本体均退出 0；后续使用 login=false。必要的精确 app/PID 检查 escalation 获准，没有 automatic-review 拒绝。

### F-QA1-001 关闭：真实 Save As 文件与隔离恢复

先明确夹具来源：source profile 是 QA2 新建的可丢弃 schema v1 库，使用 QA1 已关闭的合成 UI revision6 快照 `native-saved-rev6.json`（SHA `5487d74f7786fb1e1774702350b09279b91ee7c06fb86edbe620b5d47b4ae714`），另为目标/规则/映射各增加一条 stable 项；仅用于原生交互的受控配置。它不是本轮产品导出，也不冒充新空 profile 采用证据。source 中 catalog/material 各 1、目标/规则/映射各 2、sourceMetadata 为空数组。target 是另一独立 QA2 profile，以唯一 `targetApis:qa2-target-only` sentinel 和 revision20 作显式替换/删除测试；该初值同样是 QA 夹具，不是产品历史。没有写 QA1 profile。

19:17:41 显式 env/profile 启动 source **PID62568**，ps 完整路径为 QA2 自有 app，启动日志 HTTP=false / Backend=false / revision6；确认进程后才绑定 UI。`getState` 5.5320s 返回 docs/inventory；cold getApp 显式180000ms、实际 **70.4047s** 返回完整 AX，无 pending。一次首动作前工具要求刷新 app state，先读新 AX 再继续，没有据未执行动作推断结果。旧 115.4s/QA1 125.0961s 历史不作为当前 blocker。

新 app 中文明色点击“导出完整配置 JSON”实际打开 OS **Save As**，选择 QA2 `exports/` 并保存 **`qa2-native-backup.json`**。先 completion_summary，再独立读取真实文件：**10980 bytes**，有效 UTF-8，无 BOM，SHA **`a1370184932e06c5523e3ab985709dd68c33d28b0d092221757c61ca46dbeb8f`**；精确 envelope 为 `format=aiis.sma.configuration` / `schemaVersion=1` / `document`，document 的七字段与源 SQLite **全文相等**。仅含配置，排除 gate、UI/startup 偏好、运行记录及真实事实值；bodyTemplate 的模板值没有被当作事实值。source 完整快照/revision6/updatedAt 保持不变。没有用 QA1 手工恢复 fixture 或 Rust export 字符串替代本文件。

先 summary、核 path 并退出 source 后，19:24:59 同 SHA app 在 target profile 启动新 **PID68981**；ps/path/env/log 再核准，getApp **0.1392s** 返回 AX。target 旧 auto-start=true 来自明确复制的 QA1 合成 v1 文件，实际日志仍拒绝 `SMA_LOCAL_CONFIGURATION_EXECUTION_NOT_AVAILABLE`。在 UI 切成英文/暗色后，通过 **Tab 到 Preview JSON restore、Return** 打开 OS chooser，选上述产品真实导出的文件。页面显示文件名、七个创建 key、更新 catalog/connection，以及 **Will delete: targetApis:qa2-target-only**；确认框未选时 apply disabled。此时只读 SQLite 与 target 初始全文/revision20/updatedAt 相等，preview 零写入。

显式勾选确认后点击 apply，native 显示 **revision21 / 2026-11-04 19:26:45（上海到秒）**。独立只读 SQLite 核对：target 完整 document **等于真实备份及 source document**，sentinel 删除，revision20→21 不回退，updatedAt 保留原始毫秒和 +08:00；source 完整快照仍 revision6 且未改。独立 startup 文件 SHA 前后均为 `deb987799ff577d492a52dea6b1c28ea82cb62105e51c8c081adb820dede6aa0`；apply 后仍英文/暗色/HTTP off，未恢复 UI/gate/startup 或启动运行。

**F-QA1-001：closed by QA2。** Native 此夹具的 sourceMetadata 为 []；非空 metadata 的来源证据、无值和类型拒绝沿用未变 Rust 测试及序列化合同源码，不虚称本轮另做了非空 metadata 原生往返。损坏/未知版本/取消/事务故障仍复用精确未变的 QA1 存储证据。

### F-QA1-002 关闭：具体资源 key 可见，preview 仍零写

source native 目标批量导入选取 QA2 JSON，真实公共弹层显示 **新增1 / 更新1 / 不变9 / 错误0**，并逐项可见：新增 `targetApis:qa2-created-targetApis`、更新 `targetApis:api-material-2ef9fac57b29beca`、不变 `targetApis:qa2-stable-target` 及其它未变对象。完整 AX 和实际截图均确认，用户可以在 apply 前核对对象。

随后在同一弹层选择重复 key 文件，真实结果为 **0 / 0 / 0 / 1**，可见错误 key `configuration` 及 **`SMA_CONFIGURATION_DUPLICATE_KEY:qa2-created-targetApis`**，apply disabled。没有执行导入 apply；上述两次预览及 OpenAPI/主题语言操作后，SQLite schema/revision6/document/updatedAt 全部与 source 初始快照相等。

本轮 12 Node 中另实际渲染正式公共弹层 slot：**targetApis / mappingValueRules / mappings × 中英**，逐个核对 create/update/unchanged/error key；只有 vendor 弹层外壳为 headless stub。此处采用一个充分 native 目标场景与其余资源正式组件渲染分层，没有声称原生重复全部资源矩阵。Rust preview/apply token/intent/revision、CAS 与原子性源码/测试 SHA 未变，原 QA1 真实存储回归保持。**F-QA1-002：closed by QA2。**

### F-QA1-003 关闭：两文件入口的四组合、文件名和键盘

实际 native 中，两处新增入口均为本地化 ConsoleActionButton，页面不再暴露 Choose File/no file selected 的裸控件；hidden input 复用原 `.facts-file-input { display:none }`。中文显示“预览恢复 JSON”“导入本地 OpenAPI JSON（先预览）”“尚未选择文件”，英文对应 Preview JSON restore / Import local OpenAPI JSON / No file selected。**中英 × 明暗四组合**均有实际 AX/截图检查，文件名不随翻译改变，无重叠或页面横溢。

OpenAPI 按钮经 Shift-Tab 实际获得焦点，Return 打开 OS chooser，选择 `qa2-source-openapi.json` 后显示文件名和真实 catalog preview；由于受控输入改了 sourceLocator 文件名而原材料仍被引用，preview 明确拒绝 `SMA_CONFIGURATION_REFERENCE_MISSING:material-2ef9fac57b29beca`、apply disabled，原配置零写。这是来源身份/引用保护，没有把失败 preview 当作应用成功。恢复按钮的 Tab/Return、系统选择真实产品备份、文件名及 restore preview/apply 已在上节实测；恢复文件名在四个中英/明暗组合仍正确可见。OS chooser 自身语言没有被修改，也没有用系统语言变化冒充应用 i18n。common locale 61 键对称，正式组装/handler 回归通过。**F-QA1-003：closed by QA2。**

### AC01–AC12 当前判定

| AC | QA2 结果 | 当前证据与实际边界 |
| --- | --- | --- |
| AC01 | 通过 | 精确批准/003连续性、53项和283保护面再次核准；UI→IPC→Rust/SQLite/零隐式 fetch 回归重跑，未变配置/审计无 fallback 与退役闭包证据复用。native 没有全程抓包。 |
| AC02 | 通过 | QA1 原生离线连接/材料/目标/规则/mapping CRUD、真 OS 重开 revision12 全文相等及另一空 profile 证据经 SHA 核准；本轮补齐真实 native 完整 JSON 导出。QA2 seed profile 不冒充新空采用。 |
| AC03 | 通过（纯预览层） | 未变 Rust 五类型/四位置/fact-constant/必填/规则、native saved id/revision/request=null 与草稿分离证据保持，本轮 Node 回归重跑；没有目标投递或业务成功声明。 |
| AC04 | 通过 | QA1 未知 sourceKey+factName 的 native 保存/重开/缺值与 Rust metadata/legacy 冲突/错误身份合同证据保持；没有以模板0或 metadata 充事实值。 |
| AC05 | 通过 | 本轮12Node保留三资源 JSON/XLSX/旧九列/公式宏/类型/引用/载荷和内容/revision约束；native实际具体key/错误可见且完整快照零写，三资源×双语正式slot覆盖其余展示面。F2关闭。 |
| AC06 | 通过（分层配置合同） | 新 native Save As 的真实 UTF-8 文件→另一受控隔离profile实际restore preview/删除范围/显式确认/apply，全文相等且source不动；startup/UI/HTTP边界保持。未知版本/取消/中途失败复用未变存储证据；native metadata [] 的限制如上。F1关闭。 |
| AC07 | 通过（隔离存储） | 未变14项SQLite/CAS/两客户端/150msbusy/trigger中止/0444/损坏/未知schema/非法路径/全集与pretty信封上限的QA1独立证据核准；未新增或宣称OS跨进程排他。 |
| AC08 | 通过 | 未变引用/类型/disabled/runtime-busy统一检查与QA1 native解除引用后删除证据保持；本轮换sourceLocator的catalog预览也明确拒绝引用失效且零写，无自动停启。 |
| AC09 | 通过（分层准入） | 正常manual/start/resume/auto-start源准入、QA1直接command false/true loopback零accept及UI Start拒绝证据保持；本轮target旧auto=true新OS进程日志再次拒绝，HTTPoff未因恢复开启。无全程网络抓包或新增native全IPC注入声明。 |
| AC10 | 通过（局部兼容） | 原17项HTTP/lease/audit/failed/ambiguous/stop/五类型四位置/startup v1独立回归及其SHA核准；本轮startup恢复前后字节相等、正常执行仍关闭。不是新增GET→POST或真实业务回归。 |
| AC11 | 通过（本r1 UI范围） | 两文件入口/空态/文件名/键盘/系统chooser后preview及中英明暗新原生实测通过；CU/helper/身份/端口/普通入口不变，003已接受列宽/本机偏好分层证据保持。incognito不证明native跨OS进程UI偏好持久化。F3关闭。 |
| AC12 | 通过 | 新check/12Node/build、两轮diff/authority/文档审计和同SHA隔离native文件往返有独立证据；未变fmt/31Rust/普通dev/CRUD重开证据明确复用，进程/端口均收尾。F1/F2/F3均关闭。 |

### 当前 verdict、资源与 Human Owner handoff

**QA Verdict: qa_passed。F-QA1-001/002/003 均由 QA2 关闭，无新的实现 failure 或未解除 blocker。** 本结论仅覆盖精确 SMA-004 r1 本地配置与纯预览，以及明确批准的正常投递暂关；此前 QA1 的 qa_failed、各次工具失败和证据限制全部保留。**Human Owner final acceptance: pending**，由 Human Owner 决定阶段③最终接受；父 SMA-001 r2/总体 SMA、阶段④GET→POST、DAA/Backend全链、真实目标业务保存、可靠恢复/容量、真实/default profile采用/迁移、设备、部署/发布和Git动作均未因此获准或完成。

19:24:59 前 source PID62568 已核准精确 path 后 SIGTERM、postPs 空；19:27:48 target PID68981 同样核 path 后 SIGTERM、postPs 空。退出前该 PID 的 lsof 网络列表为空；**瞬时 lsof 不冒充全程抓包**。15192/14192 均无监听（各 lsof 返回1/空）；没有 QA2 browser tab、fixture监听服务、JS dialog、viewport override 或 pending CUA。每段原生结果后先 completion_summary 再切其它工具/退出；退出后没有再读旧 AX/getApp。未操作用户 Chrome 已有页面/组，未触及默认 WK store、真实 profile/日志/.env/DB/Backend/设备。两段应用 stdout 分别4/6行，均可解析JSON，记录有限启动/准入/配置恢复事件，没有完整配置/材料正文/事实值日志。

QA2 唯一临时根 `/private/tmp/sma-004-r1-qa2-20261104-1915/` 保留：同SHA incognito app、显式 disabled.env、两个可丢弃配置profile、QA-only seed与导入夹具、产品实际导出备份、命令日志和审计/收尾回执。没有回收目录、分支或他人资源。原DEV/rework1、root QA1失败归档与QA1证据根也保持；待Owner接受、必要证据安全归档且无运行/后续依赖，由主协调盘点回收。正式 node_modules/dist/target/gen 为忽略构建资源，未提交或清理。本轮无通知/邮件动作。关键结果、候选/文件SHA和限制已持久于本 checklist，不仅依赖tmp。

| QA2 自有证据（相对该根） | SHA256 |
| --- | --- |
| entry-audit.json | d3dc2f159cf589a0c2750e190550b2b457eec96b0131029aa919527ee97340b4 |
| pnpm-check.log | aacdfedc485449151e8f0cedfb8264a7d15047256a7b3c3a4a9e848e28e7b178 |
| pnpm-test.log | e3ffbb9a7d75d4383c5113d36a84e8631469e220693a80f1d897d4c09d1034eb |
| pnpm-build.log | 2f8ca4b165b0f86f0476f71987ef6feef1103b019d386be705b9f61a6ba26729 |
| final-source-audit.json | 50ab8740f6c03d8d65c30c19c0b261a5cd86f67fdf1815c11b8009434ce8ffc8 |
| native-export-audit.json | 43784395e9c98f0611b81c43915a899352a71db1d05f2fdfbd2c91ff8790cc6e |
| exports/qa2-native-backup.json | a1370184932e06c5523e3ab985709dd68c33d28b0d092221757c61ca46dbeb8f |
| source-before-preview.json | defa6877c54d656852cffcbc08ce889bb2b8405226fe880697e9e3afab940f9a |
| native-preview-audit.json | c1e923ccf517aed6e18b19b4432518e7dcf3b5f9c656146b9bef97b6a8e24cfd |
| native-restore-preview.json | 3826c70d349f648b9460b11e311d6ebcdccaa5916146d27fcfa7afad3a587f91 |
| native-restore-audit.json | 628aeecc4e9a13f98ffabae2d4a3c599b055c90bd671de9bd3b6cf28f9c3f1d8 |
| target-after-restore.json | 9203145564e2c53611c72d6f9aaaa8db87b74e54110693599997ee1e2c699ea7 |
| native-source-stdout.log | a5f8213453e215f8c902cf042764fddcc01826fa581cedb614c624306aebc2df |
| native-target-stdout.log | 71a171e6ade3cb558551b6c02208ed7d704370116468cc8403a365eaef06d90d |
| native-source-cleanup.json | 97e3ac8963264b19bc13fee22ea8509c4fc43edd791d58ccde691ab7db8528e5 |
| native-target-cleanup.json | dd93bbe2632bfa1e036f8c16b3e57720f2833848daf09e67c36193652ff4eef4 |

图像为本轮受支持 CUA 实际返回并目视核对；工具未提供本地图像路径，不虚构截图文件。原31Rust、普通dev和QA1原生CRUD/reopen原始日志SHA仍见完整QA1记录及已核准manifest。

最终 QA2 handoff 审计（2026-11-04T19:37:37.206707+08:00）退出0：53项候选/283项保护面/spec/tasks/001/003权威SHA均保持；原QA1正文除当前三项metadata更新外逐字保全，当前qa_passed与Owner final pending一致；22份Markdown的314条本地路径链接有效、无尾随空白。仅本checklist为QA2项目写入，索引由root机械同步。
