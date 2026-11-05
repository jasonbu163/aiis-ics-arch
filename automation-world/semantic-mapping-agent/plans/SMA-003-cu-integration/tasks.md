Task ID: SMA-003
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> fresh-context Verification; SMA-003 r1 candidate ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf; native UI blocked by locked Mac / CUA getApp, no QA verdict
Workflow Mode: STD
Execution Mode: agent_team_same_session

# SMA-003 r1 Development

正式交付工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`；当前 HEAD `8030dbb3401ac6d1cf8bea46c81cfeff9e8e073b`，不提交或推送。已核对 approved spec SHA256 `47a5c51bdf27352edaddc6fdf30611925ea8a578d942dc1d968b3d0ef27bdc42`。Owner批准及依赖gate按spec §7；SMA-002 checklist为owner_accepted / qa_passed，SHA `c631ec1781502a0236d7d9cbbbf41eecb2d341d65c64385b18f329ffe5412f16`。从其tasks重算60项候选digest `af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2`，逐项当前after/删除状态全部一致。

## 基线、范围与实施顺序

已读根AGENTS及README/PLAN pair、canonical workflow、development.toml、AW/SMA最近README/PLAN、完整SMA-001总spec、002完整bundle、003 approved spec；消费CU owning文档、公共入口与CU-008接受证据。使用frontend-ui（DESIGN/FRAMEWORK）、i18n-workflow、desktop-tauri、aiis/project-governance和code-document-indexer。SMA/其它工程已有大量并行dirty，不reset/clean。触达前快照、原文件及status保存于本任务独占 `/private/tmp/sma-003-r1-dev/`，最终精确增量在handoff固定。

1. R1/R2：SMA自有依赖及public alias/dedupe，CU布局、五类职责稳定ID二级导航、sma.*主题/语言偏好；保持labels及业务组件挂载 → check/build、公共闭包与无业务调用验证。
2. R2/R4：Card/Action/Status组合、主题token与Teleport作用域、Element Plus locale；复用tableWidths/time覆盖全部触达普通表 → 双语明暗、表单弹层、列宽/上海时间回归及桌面/390×720观察。
3. R3/AC07–08：保持源snapshot/Backend地址/lease审计、preview/JSON-XLSX/运行与偏好原合同 → 既有Node/Rust回归、gate=false含旧autostart=true、隔离native smoke。
4. 精确文件及before/after digest、正式dist/native对应关系、命令/退出码/限制、资源与Developer handoff → root启动fresh Verification。

只写spec allowlist内展示文件和本tasks；root拥有所有PLAN/catalog/AW状态索引。Rust/Cargo/Tauri配置身份/capabilities/图标、前端业务API/store/文件合同及其它应用只读。CU公共profile/cardPadding18保持，不借CU node_modules。真实HTTP/DB/PLC、真实.env/profile/历史、Docker/部署/Git发布均无授权。

## 验证与资源保护

仅专用loopback Rust fixture可命令级打开HTTP；普通UI/native使用本任务绝对env/profile、空Backend、HTTP=false。`SMA_PROFILE_DIR`不隔离WKWebView，原生交互前须使用本机支持的唯一dataStoreIdentifier临时config overlay并确认进程/env；不改正式Tauri配置，不在默认WebKit store写偏好。浏览器/native证据分别记录。

旧 `/private/tmp/sma-002-r1-dev/` 与 `/private/tmp/sma-002-r1-qa-20261104/`仅供只读基线/原始证据消费，不启动旧.app、不删改；由root在003验收后确认无证据/后续依赖再回收。003独立构建和标识产物。新任务tmp、独立store及忽略构建产物会在handoff列实际用途/保留触发条件；自检不是QA verdict或Owner接受。

## 2026-11-04 13:29（Asia/Shanghai）执行检查点

产品源码已稳定；后续仅完成证据/文档，不扩展范围。SMA自身Element Plus2.14.2/icons2.3.2经现有store离线安装，frozen安装0；check0；Node7/7（原6+UI偏好隔离/fallback/无HTTP）；Rust17/17（11 continuous+3 manual/pure+3 startup/gate/time）及fmt0；最终incognito和原正式配置debug.app构建均0。正式构建前端与incognito最终dist的字节一致性将在最终handoff核对。

浏览器使用Chrome自建tab和任务独占 `http://127.0.0.1:25192`，不是独立OS浏览器profile。IAB不可用；无storage快照注入/恢复。临时实际App IPC夹具保持HTTP=false，另直接组件夹具只提供props、无Backend服务。5组件页×中英明暗20正常态、3表单×4组合12次弹层、390×720七页×5状态×4组合140次可见/布局检查已实际执行；最终矩阵均有标题且无页面横溢。初次direct fixture把Teleport宿主放末尾导致目标未存在，已只改临时夹具并重跑完整矩阵，未将失败矩阵算通过；产品宿主同时前置以确定装配顺序。已修正语言更新表头移除拖拽手柄、映射弹层grid撑宽、窄窗固定操作列覆盖数据和批量file input露出系统语言，均仅展示/helper范围。

实际App连接草稿 `sma003-draft.invalid` 未保存，主题/语言切换、切页、侧栏隐藏/恢复均保持，临时可见IPC trace的业务调用始终0。关闭当时全部2个任务tab后新开同origin：英文/暗色自动恢复，源事实列220→290px也恢复，草稿未跨关闭保存（符合原业务语义）。七个实际叶页在390窄窗逐一可达。其余7表已真实拖拽；截至本检查点，全部表的最后关闭重开/reset逐项覆盖尚待补齐，不宣称已全部完成。

### 原生工具阻塞与保护

未修改正式Tauri配置或Rust/Cargo。官方配置和本机Tauri2.11.3/tauri-utils2.9.3/Wry0.55.1支持macOS14+ `dataStoreIdentifier`；本机15.7.7。唯一UUID `7f4f76e6-13d1-4237-a33d-aeff8103c072` 的任务tmp overlay只给原完整window新增该16字节字段，但 `tauri::generate_context!` 报E0308：期望 `[u8;16]`，生成 `Vec<u8>`。本机tauri-utils `src/config.rs:3897` 使用 `opt_vec_lit(self.data_store_identifier, identity)`，3962插入该literal，字段2242为Option数组。原日志 `tauri-build-isolated.log` 保留；没有改宏或依赖源码绕过。

经主协调/PM核定按原r1分层验证，临时替代overlay只给原完整window增加 `incognito:true`，保持identity、1280×800及1024×720限制。其 `.app` 仅用于非持久原生smoke，不能证明原生跨进程偏好恢复。临时文件 `native-incognito-overlay.json` 不属于正式源码；测试binary SHA `a3c6d79ca9e0b3ad4a9b8ab145f903be49b8e4578290c7325e9b8734b9afe13c`。

05:06:55Z通过exec显式启动自有 `.app`，PID47936，精确路径 `/private/tmp/sma-003-r1-dev/incognito-final/AIIS Semantic Mapping Agent.app/Contents/MacOS/aiis-semantic-mapping-agent`。只读确认PID/该二进制和临时日志后才绑定CUA；日志gate=false、Backend=false、旧mapping autostart=true，均成功加载。随后唯一 `cua.getApp(完整.app路径)` 无返回，约1249.7秒后被主协调中断，tool明确返回 `aborted by user`。**实际native AX/页面/主题/弹层覆盖=0**，不能将进程启动或浏览器证据充当原生smoke通过。

中断返回后未再次getApp/AX或重激活native。已先完成CUA `completion_summary`（记录原生工具阻塞），才以exec检查PID47936 command精确匹配自有路径并SIGTERM，结果持久在 `native-cleanup.json`；不访问默认profile，不修改/删除旧002日志。正式无overlay构建最终已返回0；原生缺失覆盖作为工具blocker交fresh Verification，DEV不给QA verdict或Owner接受。


## 最终浏览器补齐、隔离与环境限制

主协调中断不是Human Owner取消。被中断的getApp调用未显式提供timeout_ms；工具schema虽声明默认30000ms，实际未在30秒内有界返回，不能把默认值当作已生效超时。一次受支持js_reset尝试返回aborted before dispatch；随后首条 `cua.getState()` 正常返回，并明确报告Native apps错误：**The Mac is locked and automatic unlock could not unlock it**。没有随后读取或重新激活native；后续仅Chrome extension DOM动作，主协调负责用户解锁沟通，Development不等待解锁重试。

剩余浏览器表恢复/reset现已全部补齐。所有值均来自真实拖拽，不注入localStorage，也不复制storage快照。关闭原2任务tab后同origin新开App和组件fixture；下表“恢复”值是重新挂载后实测，“重置”是点击各自恢复按钮后实测：

| 表ID | 拖拽字段 | 拖前 → 调整/关闭重开恢复 → 重置（px） |
| --- | --- | --- |
| source-facts | name | 220 → 290 → 220 |
| api-materials | method | 100 → 155 → 100 |
| target-apis | apiKey | 220 → 275 → 220 |
| value-rules | state | 140 → 195 → 140 |
| mappings | state | 140 → 195 → 140 |
| mapping-bindings | parameter | 220 → 275 → 220 |
| target-parameters | location | 140 → 195 → 140 |
| target-materials | method | 110 → 165 → 110 |

翻页/筛选/刷新状态由现有source store与公共宽度独立状态及回归覆盖，配置fixture的normal/loading/empty/failed/closed往返和语言切换没有改变列宽；没有把默认宽度下的翻页称为“已调整值翻页实测”。最小宽度/失效字段由既有Node helper回归实测（name20→100、updatedAt坏值→190），没有在锁定Mac后伪造八表各自真实极限拖拽。普通字段最小100，源updatedAt最小160；特殊固定列不提供拖拽。全表横滚已在桌面/390窗口观察，窄窗操作列随表滚动，不遮住数据。

独立最终dist通过 `pnpm preview --port 24192` 在任务专属loopback origin实际打开：标题/五组菜单、CU壳、连接表单、默认HTTP关闭正常，无CU进程前置。公开源编译时可用与built产物运行独立分开说明；没有启动CU。该preview没有fixture IPC/fetch替换，未发业务请求。桌面明/暗、窄窗和弹层截图曾由CUA实际返回并目视检查；当前受支持API只返回图像bytes/展示，无额外截图文件写入路径，不为截图安装依赖或伪造绝对路径。

最后复位临时viewport，关闭所有自建任务tabs，再完成第二段CUA summary“完成浏览器恢复验证”。随后exec只按精确命令核对并停止fixture PID27993与preview PID70633；初次preview路径匹配因`.bin/../vite/bin/vite.js`差异主动未杀，确认完整实际命令后才SIGTERM。Native47936已不存在；15192/24192/25192均无监听（lsof无匹配返回1为正常无监听结果），没有pending CUA调用或测试服务。

## 表格/时间展示交接

所有表只使用 `src/console/tableWidths.ts`，基于已接受002 helper有限增加原生表directive；每表稳定字段如下，括号F为固定特殊列：

| 表ID | 字段ID，按显示顺序 | 恢复入口 |
| --- | --- | --- |
| source-facts | name, sourceKey, factKind, dataType, value, updatedAt, rowVersion | 表前筛选区 |
| api-materials | select(F), method, name, path, operationId, parameters, source, loadability, selected | 当前表上方 |
| target-apis | select(F), apiKey, name, method, path, origin, parameters, idempotency, enabled, actions(F) | 当前表上方 |
| target-parameters | location, name, jsonPath, dataType, required, actions(F) | 目标编辑弹层表上方 |
| target-materials | select(F), method, name, path, parameters, source, loadState | 加载材料弹层表上方 |
| value-rules | select(F), state, key, name, origin, dataType, values, enabled, actions(F) | 当前表上方 |
| mappings | state, key, name, targetApi, bindings, enabled, manualRun, actions(F) | 当前表上方 |
| mapping-bindings | parameter, mode, value, rule, validation | 映射编辑弹层表上方 |

偏好键统一 `sma.table-widths.v1.<tableId>`；主题/语言仅 `sma.theme`、`sma.locale`。不改业务配置版本、其它应用键或原sma.backend-connection.v1合同。时间展示触达点仅source updatedAt与runtime日志timestamp，继续既有 `time.ts` 显示Asia/Shanghai到秒，原值title保留毫秒。其它配置表未新增日历字段；不以刷新时刻生成“更新时间”，missing/无时区仍缺失，不改Rust时间合同或历史数据。

## 实际检查回执（DEV self-check，不是QA）

命令均在正式工作树SMA根；前缀 `pnpm --config.verify-deps-before-run=false --config.update-notifier=false` 为命令级复用锁定依赖，未改项目配置。隔离env/profile均在本任务tmp，Backend为空；只有Rust受控loopback命令级HTTP=true，gate子进程仍false。

| 命令 | 退出/结果 |
| --- | --- |
| `pnpm add element-plus@2.14.2 @element-plus/icons-vue@2.3.2 --offline`（上述命令级前缀，escalated自身store） | 0；21个锁定依赖项，未借CU node_modules |
| `CI=true pnpm install --frozen-lockfile --offline --config.update-notifier=false`（escalated自身store） | 0，锁文件一致 |
| pnpm前缀 `check` | 0；最终vue-tsc |
| pnpm前缀 `test` | 0；7 passed/0 failed，原6项+新增UI偏好隔离、round-trip、坏值/不可用fallback与无HTTP |
| pnpm前缀 `build` | 0；最后两次Tauri beforeBuildCommand也重跑同build，最终1683模块；注释PURE与>500kB chunk warning保留，未扩展拆包 |
| `cargo fmt --manifest-path src-tauri/Cargo.toml --check` | 0 |
| `SMA_ENV_FILE=…/disabled.env SMA_PROFILE_DIR=…/rust-profile SMA_BACKEND_BASE_URL= SMA_HTTP_ENABLED=true cargo test --manifest-path src-tauri/Cargo.toml --locked`（escalated，仅自身loopback） | 0；17个命名测试，原HTTP/lease/failed/ambiguous、pure五类型/四位置、v1/坏文件/gate保持 |
| pnpm前缀 `tauri build --debug --bundles app --config /private/tmp/sma-003-r1-dev/native-overlay.json` | 1；dataStoreIdentifier codegen E0308，未启动此构建 |
| 同命令换 `native-incognito-overlay.json` | 最终0；唯一改原window的incognito，专用非持久测试.app |
| pnpm前缀 `tauri build --debug --bundles app`（无overlay） | 最终0；正式配置debug.app，未启动以免写默认WebKit store |
| 普通 `pnpm tauri dev` | 本003未重跑；源码入口/端口保持。默认启动无法隔离WK store，专用incognito native UI又因锁屏/工具绑定阻塞；不借002历史普通dev证据当本轮完成 |
| `git diff --check -- automation-world/semantic-mapping-agent CODE_INDEX.md` | 最终0；中间空白提示已只清理本任务新增空白 |
| Python只读31文件allowlist/protected SHA/CU17公共文件/本地链接检查 | 0；16个已触达README相对链接有效，Rust/API/store/文件合同原字节保持 |

初始sandbox `pnpm add` 因store位置不同失败1，未改store配置；获准escalated后离线自身store成功。临时Vite在sandbox绑定25192 EPERM失败1，获准escalated loopback后启动；无automatic-review拒绝。Playwright CLI wrapper尝试无输出后主动Ctrl-C=130，未安装辅助依赖，实际UI只用CUA。CUA若干选择器因role差异/重复Connection组叶/弹层过渡超时，均按新状态重取并用受支持DOM动作修正；不算产品成功或native证据。


### 补充时间回归

`TZ=America/Los_Angeles pnpm --config.verify-deps-before-run=false --config.update-notifier=false exec node --test --test-name-pattern=Shanghai tests/cleanup.test.mjs` 返回0，1项通过。与默认上海宿主时区运行相同测试，都将 `2026-11-03T16:00:01.123Z` 显示为 `2026-11-04 00:00:01`，原毫秒字符串不改；缺失/无时区/单调值仍missing。

## 交付产物与资源

正式源码唯一交付在约定工作树；无新commit、worktree或临时源码交付副本。最后仅改模块README中“后续CU”的过时措辞为当前装配事实；前端/原生最后构建输入源码未再修改。正式无overlay debug.app位于 `src-tauri/target/debug/bundle/macos/AIIS Semantic Mapping Agent.app`（路径相对SMA），二进制SHA **`94e56c9bbfd0d1a11bc5227519f23c56a56eba1a16a22af1d09a356ced97ed5b`**；该原正式配置产物未启动。专用测试副本 `/private/tmp/sma-003-r1-dev/incognito-final/AIIS Semantic Mapping Agent.app` 的binary SHA见上，只有incognito编译context差异，不声称二进制完全相同。

两次最后构建的前端dist清单逐字节一致；以下为当前正式dist，运行不需CU进程：

| dist相对路径 | SHA256 |
| --- | --- |
| `assets/index-FOQxaQr3.css` | `d3d4c76a849bec323eba904ed9b560bfe7e0be158cbf9ee3683e784167be656d` |
| `assets/index-yphJwohS.js` | `de5c2b9eb5e414176403b4789ba059f99e3f1269a000d8e08ec731820c74b5c1` |
| `index.html` | `7e010b1cf613b4b244af5718adffe8d32ff03e23283a5aaeb6a414f78e2b5d86` |

`/private/tmp/sma-003-r1-dev/`为本任务独占，保留before快照、初始status、candidate/diff、原始测试/构建日志、17项CU只读输入SHA、最小UI fixture及其Vite缓存、env、native-profile旧autostart夹具/日志、两个临时overlay、incognito测试.app、产物对照及精确收尾回执；QA仍需复现，暂保留。UUID custom store未成功编译/启动，未创建可用持久测试store；incognito为非持久store，进程已退出。项目自己的node_modules/dist/target/gen均为忽略的构建依赖或产物，不提交。

所有临时tab/服务已结束；不保留常驻mock或后台fixture。Chrome任务origin的本机sma.*测试偏好只来自UI操作，八表已各自reset；theme/locale为该任务origin局部，不修改15192/14192或其它应用origin。003最终接受后由root确认无QA/后续/证据依赖再回收任务tmp及可安全清理的自有构建产物；旧002两个tmp仍由root按其既有验收/证据依赖盘点，不启动旧.app、不删除默认日志原件。原始日志不是唯一证据，必要事实与源码SHAs均永久记录于此。

## AC交接与限制

| AC | DEV证据与边界 |
| --- | --- |
| AC01 | 精确003 spec批准SHA及002 60项候选/接受gate核对；只在已接受清理基线上增加31项展示增量，未恢复退役入口 |
| AC02 | 八个CU公共组件与两入口实际消费，SMA自有Element Plus/icons、alias/dedupe、受限fs、基础CSS顺序；17项公共源保持；自身dist preview正常。正式身份/端口/Cargo/Tauri合同未改 |
| AC03 | 五组七叶、当前页/隐藏恢复/稳定labels及Connection草稿实际观察，主题/语言操作trace业务调用0；既有CU-008公共键盘合同只读消费，本轮未完整重跑全部方向键/单次select计数矩阵，不把CU既有QA当SMA独立QA |
| AC04 | 实际browser页面/状态/12表单主题组合、390×720、横滚/弹层滚动与截图目视；原生UI实测0，受锁屏/getApp阻塞，未验证原生下拉/主题/键盘完整矩阵 |
| AC05 | 八表实际拖拽、独占origin关闭重开恢复与各自reset；最小值/坏字段helper回归；精确已实测与未逐表真实极限/已调整值分页的范围见上。原生incognito跨进程持久化未实测，不用浏览器冒充native persistence |
| AC06 | 统一既有上海helper、两宿主TZ、原值精度/missing，源表/runtime显示；不改时间合同/迁移 |
| AC07 | 原JSON/XLSX/pure preview、五类型/四位置、单次/持续/lease/失败ambiguous/stop、v1旧段与false gate17 Rust+既有Node回归保持；native仅启动日志gate false/autostart true，无UI运行操作证据；无真实Backend/DB/PLC |
| AC08 | frozen/check/7Node/build/fmt/17Rust、正式/隔离两构建、diff/allowlist/相对链接0；原生工具blocker如实交QA。未宣称QA通过/Owner接受、部署/发布或总体闭环 |

## Developer handoff

精确 **SMA-003 r1**，approved spec SHA `47a5c51bdf27352edaddc6fdf30611925ea8a578d942dc1d968b3d0ef27bdc42`；正式工作树与HEAD见开头，无新commit。源/稳定文档/测试31项变更清单的紧凑JSON三元组digest为 **`ae9b3c4900e6e3f326a61e700f1736d67338247716e609a559a90a598a1d8bcf`**。编码规则：为下表SMA相对路径添加 `automation-world/semantic-mapping-agent/` 前缀，以工作树相对路径排序；每项 `[path,beforeSha|null,afterSha|null]`，UTF-8，`separators=(',',':')`；“—”转null。before为003实际触达前已接受002工作树，包含已有dirty；不是HEAD。下表排除角色文档、root协调PLAN/catalog/AW README索引及共享CODE_INDEX。

根CODE_INDEX仅在既有SMA说明行后追加uiPreferences与cu-integration.test两条SMA增量，保留DAA/DS/Backend等并行dirty。root拥有SMA/AW PLAN/catalog与AW README索引机械同步，本Development不写这些状态索引。未改spec/checklist/skills/角色/workflow/CU/其它应用；Rust、Cargo、Tauri identity/capabilities/图标、业务API/store/文件合同均与003初始字节一致。

最终source候选在此冻结。下一gate由主协调启动新命名fresh-context Verification（fork_turns=none），独立核对该候选/公开CU输入及实际证据并创建checklist；Mac实际解锁后再以安全临时隔离方案补齐native必要证据。当前handoff为Development self-check与已知工具限制，不是QA verdict、Owner最终接受或任务整体完成。

### 31项实际文件与before/after SHA256

| SMA相对路径 | Before | After |
| --- | --- | --- |
| `README.md` | `c9c4647fba2327ebbcfbdc162d1c979f2d256e53660462edb996587e5d110f93` | `fe09d78178722b83f4ede32a3078c00311caec7b287a3fedc35dd745760376de` |
| `README.zh-CN.md` | `cb246fcd88db8a9a09c37323e89063bed11b72e70a948e458f347a4798fa022f` | `617abb12d28f209659aea5739b1055a2be5757a28b88d426395dd56e50456aca` |
| `package.json` | `7c444320226a4ec44fad28489f294fec7fab8d8015f413117ea157618b7fa916` | `691d8402948b3423820abf87aa06dda2075471ff859319bb5282a27f77ef99b6` |
| `pnpm-lock.yaml` | `a1e3e2399b521a105e76b1a5d2d825a3492bdffe9864eb3f63a7ee49342f6215` | `09ad5fb4c55b9036913db0407a95aab9ba12af51214c3be2872a72f3eca5d548` |
| `src/App.vue` | `ed6c777197397bc16e85cb8c0e2f0a2a375349bf9ab7d1b5d4e9f5afd782afea` | `6823b173f1c4416f8f69b4066f14415633162f718ca23fe132ec01344aaa83ce` |
| `src/app/README.md` | `24bcb95c74c67733c90fec3102748cda97627408a946932ef531122ce32a82fb` | `988ac21e50de620d78a230ca945b4327cc2c31bb0688c80e8c09d90130a1ebda` |
| `src/app/README.zh-CN.md` | `be71d89b1cf7ec2b75aeb8d2f880c9259dbadf9f881ab7793db5fad9a94665f3` | `6bfeb1ed5fba1d139d839f869b2f6fe07e8298bd61d244b57e7c28fb624cf18f` |
| `src/app/connection/components/BackendConnectionPanel.vue` | `a48d18f992ae966b12e5830926969598f4420e3e0855b1c3332a4c120b34aeda` | `a89f5cd2037f575dc265216f70a52ef21c1b1bc75acf77572c83a44107fa35ae` |
| `src/app/connection/components/OpenApiOperationCatalog.vue` | `87ea90f361b18977acb13879971ddc91f57befd53ccbfed2bf671d71d4a3d9af` | `392bd04195eba4afca15aa0374e5afebe94f2892e4fbea84abdfda1bf0a58495` |
| `src/app/connection/styles.css` | `3e754d1d7deefacd007fc48f1c6e8ec3a38451772e905c919057a9a19c9857ec` | `8a6505dc3ca9bc228a1866f7ddd97f620f6f1a9c3fbab250baa7dc3aa4dba256` |
| `src/app/styles/responsive.css` | `6ff3587993f06f5ba351a28e7eeaca12f3e66583c31d66bab676da94465a4373` | `733d45f6cd88004f8bb903fed8ef186f4ee424696528408a47dbf6ef0a4c2cf1` |
| `src/app/styles/shared.css` | `232698b2d1887d6b5bd1a9ccaedba264f99b17cd60f3265476616bdb530c5c15` | `d80f1d15929986920548e73be2dc4f60740e5131b27be7d9718333a733d2f9b2` |
| `src/app/styles/shell.css` | `64781d2fe77a33126a744024a680139b9fbe095c69447ec67de329a337cfb2e8` | `4066008455e06d73864e801c2119cf005c6ab8a63f90fbedddc73e31e2eb9da2` |
| `src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue` | `ff95c95b03ff1f0050bad7145e28d7daa8148187e52796a051355d6031838e22` | `4b489a2ca6b56a69bdf53184e192cf22f39c81346ceed8857dd719c6ef12be5d` |
| `src/app/twin-facts/components/ApiMaterialsPanel.vue` | `9caa18ac21e9d38ffd26f0c61e15b8df15b3e3a4723e1b123b2acda0279e3381` | `32dc31c90200263cf70a2c85eca439d57469eb9517752c4babbf830183f26cb1` |
| `src/app/twin-facts/components/FactsTablePanel.vue` | `7e2f12d844c16f436e2021b6d3a5fae31dec28288194eccc1cce6109c27880c8` | `d5aafa2adc59e5ed053329d6af34924650b6e3107c4233d64d2d6f42c8c26471` |
| `src/app/twin-facts/components/MappingBatchOperationsDialog.vue` | `f8ee46a9661bec6450d339d36f4932ec0eaa30098578c044a04bb9d4ae82a6a3` | `88b4368f3c7c049b19a78caa026de698ed10a1dbef5ab8df80f770de15046de0` |
| `src/app/twin-facts/components/MappingConfigurationsPanel.vue` | `58ccb66b391a0a21bf6c70f4f4eda8323932a2ffe9175188bf5954958a0d218a` | `850ef66efbd8416e021f9cddd3e29f409bc8fd044592967970d664c1420fbe04` |
| `src/app/twin-facts/components/MappingValueRulesPanel.vue` | `50d4c4db5d56ac323e6109cdbfa27cf415a5171285a36bf15c49dbea7be23568` | `9924274a1a9b2eebeb8a7c555cdab1c54a3f38f80cec185b9270692566da7776` |
| `src/app/twin-facts/components/TargetApiConfigurationPanel.vue` | `24be1a07d602fa0fecd8a47e076fe59783c081f24938779d29a7a2b02156b25b` | `2618c35d9c5dd7a0e71436ebded6b4170885c8d09f043961aeb157aff5ec818b` |
| `src/components/BackToTopButton.vue` | `6f4c87bf0c6f3e8e290ae437e8d032c0714cc97b25a316f00a47175a2bb15584` | `7ba829de66fc448ef15ab45bcdfb90ad1b90e872541e59214f806ed63318faee` |
| `src/components/PaginationBar.vue` | `a2335d9210b1331dbca234470fb5c7357f80bca0da762ae6a296b4ae991ed9bd` | `bbffd0d584432fbb644e75a59300b7b01db90dc0313bebbec17d92ca03d96028` |
| `src/console/tableWidths.ts` | `bf50df871aab635f6aa5f9795596ee0cfade7fd17c40e21a4cd7f596105bdfe8` | `1fd128f61cef9d62db54cedd52eb8e23a35f0cbc5be16906f31f8662f856e9dd` |
| `src/console/uiPreferences.ts` | `—` | `68b162d8fcd03f497dac2b4732d650611f983cc8e21905fb461456d7120a0fb6` |
| `src/locales/common/en-US.json` | `dd72599bdad188099044031514dc5d255da5d7755ad9636f9c5955309710424c` | `1bad19a38316f74c33bfd4e3102950a6c735f18eae8c4001cfbfb438a7a01422` |
| `src/locales/common/zh-CN.json` | `839b21ffbcc5cfec9d4d8deb682977cbfabb388e539be23babfb1e825806fa6b` | `90f15b3f8005c5df89deac944e2687270da48b548ee84e6be73e289f3719c999` |
| `src/main.ts` | `af2f0b676644fb91dbc7eda91fcf41c929045e9bd01f9b965c5ccd3a223be10e` | `1a2648bfb27ce54fed599ffbc29ce03a913ce9c7c633dfa5df30040b50c5d741` |
| `src/styles.css` | `fb85bfd1e90e07e485bb59466743c067ef4ca76235dad44821b658db6f36b91a` | `47717119da90e79d266f6ae833f193061adf6938fed03a214852b01684fb7d2f` |
| `tests/cu-integration.test.mjs` | `—` | `cb1261b9ed097c8b0dbd9197512dcfd6c18ae362a0e7889ca545ba3c558ef327` |
| `tsconfig.json` | `a7a5e9a7631fcf1d08e44c3fb5738722845dbfdb991511d66088ad7796bfa5af` | `1d66a86089d55a1e256b95a51bea94a7547b67cd024f16db03214a44a7311866` |
| `vite.config.ts` | `73fc8aab0e70b69c3c0809202e552ceb6341284daeaa0080c827f6348480a2c5` | `0fb3f2a340dcf7d9ca5bb879a70be2a10fbb96d3eb8028cd2e51c00797740345` |

### CU公共输入SHA固定（17项均未修改）

以下相对CU的src/ui；实际运行闭包为index、8组件、types及4份CSS；其余公共profile源/声明同样只读固定，默认cardPadding18未变。

| 路径 | SHA256 |
| --- | --- |
| `components/AgentLayout.vue` | `177f6fe8e009c73fb08a629929ea5260dcffc6bb2210b8acde6ab70941ec85b9` |
| `components/AgentSidebar.vue` | `b53495b30e589aed06ba51b470c582fcc1d7984a590c9b0d811e9bb0de629533` |
| `components/AgentTopbar.vue` | `25b334b9c88b223d1bd069407f13a517db9cac04527b01bcc15f06c2903f9157` |
| `components/ConsoleActionButton.vue` | `7ec106be7d3e3789fcd93e966a5a25bfb1c58e528ca51f3556cf04daf46b7fdb` |
| `components/ConsoleCard.vue` | `54e2ce46d726e0eb424aacd5f28df3d5921e5f61a81b0c799ccfac4ddcabf3b4` |
| `components/LanguageSwitch.vue` | `e36844e9f693eb6527e76603e6b6d04e8f93f2c3ccabf9013f6b831a99f8c5a1` |
| `components/StatusCapsule.vue` | `62e605544f911759b6134482c9c251575fd24a9505d8dd1e336a8b62262439ed` |
| `components/ThemeToggle.vue` | `a7429753eee5abb9b8cc04b4a201f4230004c236176ff49bc8c378d73c95c1a2` |
| `design-profile.d.ts` | `b21ba90f57fa92e98c61bed14e3922eacb12c167c53c96049dccc95c69f828cf` |
| `design-profile.js` | `c36901caa5048df7f6a94fe26cabeec7ea9e527a98ca9c84ebd203d426f4f2c0` |
| `index.ts` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |
| `styles/components.css` | `734cd1402a71ffe1e3500c128d392c38bcdf8404bc1d008e8098b06268206fbb` |
| `styles/design-profile.generated.css` | `ac270f6c0658fe400d356497727bfae865472cdb307d6fb28234cda8c1fb70f2` |
| `styles/design-profile.json` | `9591913678f8fd22d6455456c63c8697df68d1210d926475ad4f6271c8d96bf3` |
| `styles/index.css` | `4d7113c32d88e12e85a598076eb608e395ef578e5417aeccbe351d4b0e6acdc5` |
| `styles/theme.css` | `1c631f285a29f98db9778644c4e95f7311ca1c9ea7bc65b1a62160769914a160` |
| `types.ts` | `b0ea3bd1e8d31e4cf26b2068fde4d8199dcf82e23d2112d29db34187b50ae18f` |

### 原始日志/回执SHA摘要

| 任务tmp相对路径 | SHA256 |
| --- | --- |
| `check.log` | `aacdfedc485449151e8f0cedfb8264a7d15047256a7b3c3a4a9e848e28e7b178` |
| `node-test.log` | `273fab3978b8d9485a74f14a28b607ff130aa51024222c3abca61c168995755e` |
| `fmt.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rust-test.log` | `e653e69c12ad46474702612f63b22ba3f3e2183517fc24f1e20394dcd07838e5` |
| `timezone-test.log` | `b42dbfea43d829b023b94187ea9faab21276f7f287b05f1dd56c0566c76c9b26` |
| `tauri-build-isolated.log` | `3192c9feccc8563326998bfc8996bc84ad65247e49d974e7518d82f645169ffd` |
| `tauri-build-incognito-final.log` | `54b4c90113b247cb06793cae2f11ab9e55addbe5a1875ca43f423685d09095ed` |
| `tauri-build-formal-final.log` | `eac7e4c92f091ec50dd7bf81a464d8b2a40bedb217775129152f3e5d03a0e5e4` |
| `native-stdout.log` | `26d0bf78b1a2b245cd5b9b5292f094e6e3dd9e78d291a000302995cba9fcfbd8` |
| `native-cleanup.json` | `0b27d1f37773fa662361f0c1c744b0781d7c029ee11295b7c156b6cc1c259a18` |
| `artifact-comparison.json` | `dcfef1942b162162a7ce73395c04b0839f59660617bf04455be2141939313e89` |
| `sma-003-source.patch` | `c62f97bd4554a0b948e945f6214f806b1f7bad64f64690f8c6971e523ce06963` |
| `cu-public-manifest.json` | `41e1f22aa68c8054f8dab56b90aae6d712b9199771dbee4d3a1e05a865b526ce` |

最终只读审计：从本tasks表重新解析31项，当前after SHA及紧凑JSON digest全部一致；31文件与tasks无尾随空白，git diff --check为0，尚无本任务checklist。112项受保护的Rust/业务API/store/文件工具/CU公共输入与003起点字节一致。最终环境实读macOS15.7.7、Nodev22.19.0、pnpm11.11.0、Cargo/rustc1.89.0。此后不再修改产品候选；Development不发送邮件，执行窗口/后续fresh QA和通知由主协调管理。
