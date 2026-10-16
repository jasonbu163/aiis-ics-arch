Task ID: CU-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-005 r1 implemented in current working tree; exact 19-path incremental.diff and DEV evidence ready for fresh-context Verification
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-005 r1 Development

2026-10-16（Asia/Shanghai）。依据 [批准规格](spec.md) 实施。读取根 AGENTS/README/PLAN pair、canonical workflow/development TOML、AW/CU 最近 README/PLAN pair、当前完整 bundle（开始仅 spec）、CU-004 完整已验收 bundle、消费者教程及相关实现；未找到更近 AGENTS。应用 frontend-ui/i18n-workflow/desktop-tauri/code-document-indexer，固定现有体系，根 CODE_INDEX 禁写。

计划：
1. 保存精确19路径起点，完成单一JSON源/纯校验映射/生成命令及有限编辑器 → 检查增量allowlist与默认值。
2. 更新双语文案和四README → 检查键/链接与消费责任。
3. 一轮必要CLI流程、CU build/原生启动/浏览器聚焦、停止CU后consumer build/preview → 记录真实结果并交fresh-context Verification，不做全量回归或CU-004追加测试。

写前保护：HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30`；19路径清单及已有文件必要副本在 `/private/tmp/cu-005-r1-xmo6kal3` 的 manifest.txt、before/。未创建worktree/commit或安装依赖；CU001–004及其他既有修改保留，不按HEAD全量归因。当前写入仅spec的19实现/说明路径及本tasks，spec/checklist与主协调索引禁写。

本记录是Development事实面，profile为contract_only，不授QA verdict、Human Owner验收或平台ACL/强制路由。

## 实际实施

- 参数入口保留既有label/tone/compact样例，另组合私有DesignProfileEditor；Workbench保留方案内存状态与最近有效预览，不自动读取草稿。明暗各9字段、共享5字段，范围/默认/派生规则符合r1。无效编辑保留最近有效预览并显示对称双语反馈，保存/导出禁用。
- 公共design-profile.json唯一拥有可编辑默认值。无副作用design-profile.js负责精确字段/版本/类型/范围校验、规范JSON、token/CSS生成；配.d.ts供现有TypeScript使用。浏览器/Node调用同实现，无依赖新增。theme.css移走方案拥有值，仅保留固定token与EP映射；styles/index.css固定主题→生成方案→组件顺序。components.css真实消费card padding/compact padding/action gap/table density及既有radius变量。
- 根AgentLayout透传style及PageSamples body Teleport显式aw-ui容器绑定同一previewVariables，宿主theme切换同步；ElSelect保持teleported=false。无html/body主题注入、任意CSS/script/path、自定义字段或新增公共组件API。
- 草稿仅cu.design-profile.draft.v1。显式保存/恢复/重置，保存前完整校验，缺失/损坏/不支持草稿回公共默认，storage失败如实反馈。只导出可复制规范JSON文本，不写原生文件/IPC。样例业务数据未纳入方案/草稿，cu.theme/cu.locale沿用。
- CLI固定锚定自身CU JSON/CSS，无任意输出参数；裸命令/help先返回帮助无文件读写。导入先完成全部校验/生成才安全替换单个目标，明确无两文件原子性。check只读，stale/缺CSS失败带generate恢复说明；build前置只读check。
- 四README说明字段/单位/默认责任、预览/草稿/公共源、导出→显式导入→generate/check、有效备份与IO恢复、消费者/未来宿主重构建责任。consumer源码、八组件、公共index/types及其他Agent未写入。
- 主协调截图审阅提出具体hover疑点：EP primary hover原取未映射light-3蓝色。核对已安装Element Plus mixins/_button.scss后，仅在allowlisted theme.css增加light-3/light-5映射，分别用现有accent与surface做70%/50% color-mix；无新方案字段、默认色或依赖。定向观察常态和hover，之后必要重构建，未重启原生或重跑矩阵。

精确实现/说明文件（相对CU，19个；另本tasks）：

```text
src/workbench/DesignProfileEditor.vue
src/workbench/Workbench.vue
src/workbench/PageSamples.vue
src/workbench/workbench.css
src/locales/en-US/workbench.json
src/locales/zh-CN/workbench.json
src/ui/styles/design-profile.json
src/ui/styles/design-profile.generated.css
src/ui/design-profile.js
src/ui/design-profile.d.ts
src/ui/styles/theme.css
src/ui/styles/components.css
src/ui/styles/index.css
scripts/design-profile.mjs
package.json
README.md
README.zh-CN.md
examples/source-consumer/README.md
examples/source-consumer/README.zh-CN.md
```

## DEV self-check：命令、退出码与事实

环境Darwin 24.6.0 arm64；Node v22.19.0、pnpm11.11.0，复用已有Vue3.5.38/ElementPlus2.14.2/TypeScript5.9.3及现有锁文件。未主动安装依赖；本机pnpm wrapper有“Already up to date”输出，package依赖区与写前逐值一致。shell启动时常有/opt/homebrew shellenv调用ps被沙箱拒绝提示，未视作项目编译失败。

以下命令产物在 `/private/tmp/cu-005-r1-xmo6kal3/`，除注明外cwd=CU；consumer命令cwd=examples/source-consumer。

| 命令/动作 | 实际结果 |
| --- | --- |
| `node .../cli-check.mjs > cli-check.log 2>&1`（最小临时验证程序，cwd为/private/tmp） | 退出0。直接调用实际CLI：bare/help各0且JSON/CSS内容与mtime不变；单个有效临时JSON显式导入0，accent小写、padding30、密度4真实生成；一个未知css字段非法JSON导入1且两目标内容/mtime不变；人工stale后check1且不写；generate连续两次0，字节一致；仅在目标仍与本检查最近输出一致时导入写前默认备份，JSON/CSS逐字节恢复，check0。纯helper最小内联断言覆盖非法版本/颜色/非整数/范围/密度/缺字段/额外path及规则复用，不建泛型测试框架。 |
| 初始 `pnpm build > cu-build.log 2>&1` | 退出0，check+vue-tsc+Vite，1628 modules，2.29s。该次在CLI流程前，因此CLI默认恢复后补取最终构建证据，未把先前构建冒充恢复后的构建。 |
| 恢复后 `pnpm build`（cu-build-before-hover-fix.log） | 退出0，1628 modules，2.19s；随后具体hover映射修复使该输出成为保留历史。 |
| hover修复后最终 `pnpm build > cu-build-final.log 2>&1` | 退出0，只读check、类型、Vite全部成功；第三方PURE与chunk>500kB提示保留。仅这两个顺序/具体变更原因触发补构建，没有类型失败或全量回归。 |
| 首次沙箱 `pnpm tauri dev`（tauri-dev-sandbox-failure.log） | 退出1，beforeDevCommand监听0.0.0.0:15193被EPERM阻止，尚无原生启动；历史保留。 |
| 已授权本机环境 `pnpm tauri dev > tauri-dev.log 2>&1` | 原生启动一次成功；Vite15193 ready，cargo dev0.46s，process/window/event_loop ready如下。浏览器流程结束只SIGTERM本任务PID87117(native)、87012(Vite)、86795(pnpm)，wrapper退出143（主动停止，不冒称自然0）。未做原生GUI交互或native打包。 |
| 同次服务 `http://localhost:15193/`，受控CUA IAB真实UI | 完成下述一轮聚焦观察。初始createBrowserTab遇连接未就绪及子agent visibility不支持，使用已选browser.tabs.new/goto后台标签成功。没有native cua.getApp、evaluate写状态、生产测试开关或存储后门。 |
| `node .../handler-check.mjs > handler-check.log 2>&1` | 最终退出0。从当前DesignProfileEditor.vue逐字提取script setup，现有TypeScript仅去类型/导入，VM复用真实Vue computed/ref/reactive/watch/nextTick、真实公共normalizeProfile/profileJSON和默认JSON；harness仅接线setup宏props/emits/i18n与替换localStorage。实际restore/save/reset handler的坏JSON、不支持版本、读/写/删失败分支返回默认/反馈，所有调用key均精确草稿key。该证据是隔离执行，**不是浏览器坏草稿操作**；遵循PM在spec§4新增的AC2证据组合解释，未改变验收结果或范围。最初使用最小Vue外壳的预检同样0，随后按主协调要求改为真实Vue primitives，以最终脚本/输出作为证据。 |
| consumer初始 `pnpm build`（consumer-build-before-cu-stop.log） | 退出0，但误在停止CU前运行，不作为AC6的停止后构建事实。停止CU后立即补取符合顺序的构建，保留该历史。 |
| CU停止后consumer `pnpm build`（consumer-build-before-hover-fix.log）及 `pnpm preview > consumer-preview.log 2>&1` | 构建退出0，1619 modules，2.51s；preview strict127.0.0.1:14194，自身dist独立运行，一轮table/form/dialog及宿主主题/语言观察如下。CU HTTP000、consumer HTTP200。该次preview停止wrapper143。 |
| hover修复后consumer最终 `pnpm build > consumer-build.log 2>&1` / `pnpm preview > consumer-preview-final.log 2>&1` | 构建退出0；CU已停止，最新自身dist独立HTTP200、CU HTTP000。只确认最终构建服务，不重复消费者交互矩阵；停止本任务监听PID91801，wrapper0。 |
| 具体hover疑点追加 `pnpm dev > hover-dev.log 2>&1` | 只启动CU Vite，未重启native。单点真实UI改dark accent=#CC5500并观察ExportJSON：常态rgb(204,85,0)，hover=true时背景/边框color(srgb 0.588235 0.273333 0.0517647)，确为现有accent/surface混合，已无默认蓝。只关闭本任务hover tab，SIGTERM90765/90718，wrapper0；该轮未保存草稿或改变偏好。 |
| `python3 .../static-check.py > static-check.log 2>&1` | 退出0，19路径均对受保护起点有精确增量，797行incremental.diff；111个CU叶子locale键对称，literal keys解析，四README34相对链接有效；package依赖不变，固定/生成token归属不交叉，默认JSON/CSS与备份逐字节一致，consumer无私有workbench/draft/storage引用，44px规则保留。 |
| `node scripts/design-profile.mjs --check`；`git diff --check -- automation-world/console-ui` | 均退出0。新增/未跟踪实现另由19路径逐文件增量审阅，不按HEAD全量归因。 |
| 最终 `lsof -nP -iTCP:15193 -iTCP:14194 -sTCP:LISTEN` | 退出1、无输出，两个本任务端口无监听。只停止确认属于本任务的进程，保留发现的其他任务pnpm进程78963。 |

### 原生启动日志（UTC，真实事件）

```json
{"timestamp":"2026-10-16T02:22:50.736378Z","level":"INFO","fields":{"event":"cu_process_start","process":"aiis-aw-console-ui","result":"starting"}}
{"timestamp":"2026-10-16T02:22:50.947454Z","level":"INFO","fields":{"event":"cu_window_created","window":"main","title":"AIIS AW Console UI","result":"ready"}}
{"timestamp":"2026-10-16T02:22:50.966220Z","level":"INFO","fields":{"event":"cu_event_loop_ready","process":"aiis-aw-console-ui","result":"ready"}}
```

### 真实浏览器观察与恢复（区别于原生启动及VM）

- 起始CU暗色/英语。先按“恢复草稿”确认不存在既有草稿，反馈“No draft found. Public default applied.”，记录缺失起点后才写测试草稿；受控evaluate无localStorage能力，未尝试绕过或把DOM读值冒称存储备份。
- Dark Accent编辑#CC5500，shared padding30/gap20/cardRadius26/controlRadius18/table compact。ElInputNumber需Enter提交，DOM根style确认值真实更新；卡片实际padding30px、动作gap20px、cell padding4px、弹窗radius22px。无效bad及#fff显示英语/中文字段错误，保存与导出disabled，根仍保留最近有效预览。
- 点击Save draft出现诚实“Draft saved...”反馈；ExportJSON显示readonly可选复制文本，小写#cc5500及正确5个共享值，完整导出存于exported-profile.json。刷新后根先用公共默认accent#22d3ee/padding24/table8，**未自动恢复**；按Restore draft才回#cc5500/30/table4并显示恢复成功。
- 切PageSamples后根与body Teleport容器的style逐值相同，均dark；dialog/popup背景rgb(24,34,44)，文字rgb(230,237,242)，无全局data-aw-theme。另一套Light Surface改#FFF8EF后宿主仍dark，只有显式主题切换才light。切中文后界面/错误翻译正确；light dialog及popup实测背景均rgb(255,248,239)，两个作用域共享同一预览变量，dark palette仍保存#cc5500。
- 重置反馈已恢复公共默认/仅删除草稿，随后Restore反馈缺失，确认恢复缺草稿起点；宿主theme/locale没有被重置动作改变。最后通过原控件恢复暗色/英语，根默认值恢复，三个顶栏控件实测均44px。公共JSON/CSS未因浏览器草稿操作改变，与CLI有效默认备份字节相同。
- Consumer在CU停止后使用自身dist：light卡片padding24px、table cell8px，既有表格/表单存在；切中文/暗色并打开编辑dialog/dropdown，显式scope=dark，二者背景均rgb(24,34,44)，global theme为空。consumer源码无编辑器/草稿读取，运行不需在线CU。
- 异常隔离执行单独证明真实handler的坏JSON/不支持版本回公共默认+badDraft，读失败回默认+storageFailed，写失败不宣称成功，删失败恢复默认且不宣称删除；真实浏览器中不植入坏草稿，不将VM记成浏览器观察。

截图均为真实JPEG、1280×720：cu-editor-export.jpg（早期导出，保留已定位hover问题历史）、cu-dark-preview-dialog.jpg、cu-light-zh-preview-dialog.jpg、consumer-dark-dialog.jpg；最后cu-primary-hover.jpg为该疑点修复后的真实截图。关键流程/值已永久写入本tasks，原日志/截图不是唯一事实源。

## 增量、资源、限制和精确 handoff

写前19路径中13个已有文件已复制before/、6个新增以/dev/null为起点。incremental.diff只含本任务19实现/说明路径，不含本tasks、PM spec解释、主协调机械索引或CU001–004既有未提交内容；final-sha256.txt只固定这19文件。未手写spec/checklist、历史bundles、八组件/index/types、consumer源码/locale/package/config、锁文件、Vite/Tauri/Rust/capabilities/端口、根CODE_INDEX或其他Agent实现。未创建worktree/branch/commit/PR，HEAD如下；没有以HEAD做整目录恢复。

保留 `/private/tmp/cu-005-r1-xmo6kal3/` 的before/、manifest/HEAD/incremental.diff/final-sha256.txt、公共默认有效备份、valid/invalid/exportedJSON、CLI/handler/static脚本与日志、全部构建/启动历史和5张截图，供fresh-context QA及Human Owner审阅，验收后由主协调按归属盘点。一次性implement/editor/docs.py也属本任务，可在验收后回收；临时指针/private/tmp/cu-005-current-path在handoff时删除。已有node_modules/dist/target保留且按现有ignore处理。

成功创建的CU/hover/consumer交互标签已关闭。首次连接未就绪产生的本任务错误标签id1无法通过受控get重新绑定（工具URL policy拒绝其data:error页），未绕过策略；本轮结束工具默认回收agent-created临时标签，若仍出现由主协调按归属关闭。该标签不承担证据、无运行服务。所有本任务监听已停；截图/日志/恢复依据保留。没有广杀进程。

限制：仅当前macOS一次原生window/ready、浏览器有限交互、异常handler隔离执行、限定CLI与编译/引用证据。未做原生GUI交互、全量/字段主题矩阵、Cargo全套、其他Agent/CA/TSS/DAA/SMA、跨平台、native打包、数据库/PLC/现场、发布部署或Git/GitHub写入。合法配色可能降低对比度，仍由Human审阅；IO只有单文件替换，不保证两文件事务，按README恢复/check。第三方PURE/chunk提示保留，不扩依赖或拆包范围。本DEV self-check不等同QA verdict或Human最终验收。

**精确 developer_handoff：CU-005 r1 / 当前工作树 / HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30`**。19实现文件有序SHA256清单摘要 `db1a9a64b6e3d95feb11ae04d7b9d87775cdecafb1a019d5f03d01aceb4b8535`；incremental.diff SHA256 `d4a9217bf809bded42c14c70f92fb4a1574350e7903c2ac68879b17969fc05bd`。请主协调显式启动 `agent_type=verification, fork_turns=none`，输入为当前owner_approved spec（含AC2证据解释）、本tasks、19路径当前实现、before/精确增量和原始日志/截图。Verification独立对应真实handler与VM补充证据，按AC1–AC7仅疑点/缺失复查，不重复整套构建/启动或追加矩阵；仅写checklist。下一gate为fresh-context QA，然后Human Owner最终验收；不授Git refs/发布/部署/真实配置或设备权限。
