Task ID: CU-006
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-006 r1 seven-path implementation and bounded DEV evidence ready for fresh-context Verification
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-006 r1 Development

Human Owner 精确批准 r1；只写 spec 授权的七个实现/说明文件及本 tasks。CU-005 仍为 qa_passed、Human Owner final acceptance pending，不修改历史状态。实际命名 Development；profile 为 contract_only，不声称平台 ACL 或强制路由。

## 短计划与保护起点

1. 读取根契约、README/PLAN pair、canonical workflow、Development TOML、最近 AW/CU README/PLAN、完整 CU-006 spec、CU-005 bundle 与相关实现；核对现有主题/校验/Element Plus 能力。
2. 保护七路径起点，实施当前 palette 可视编辑、同屏真实样例、就近/常驻有效性反馈及双语说明。
3. 最终 CU build 一次、当前主机 tauri dev 一次、一轮代表性浏览器编辑/草稿/弹层/滚动/窄窗观察；恢复本轮偏好和草稿，形成精确增量，交 fresh-context Verification。

工作树 HEAD：`1a5aa2d2fe7089b5671218865238cfaa240f9a30`。七路径清单和 before 副本：`/private/tmp/cu-006-r1-is03c7qe`。只固定 public UI、PageSamples、CLI/package/lock/Vite/main/App/Tauri 和 consumer 源码摘要供禁止面只读核对，不做全仓摘要。不创建 worktree/commit，不以 HEAD 全量 diff 归因或恢复。

Skills：frontend-ui（FRAMEWORK 主题与 EP 组合、既有设计优先）、i18n-workflow、desktop-tauri（既有启动路径）、code-document-indexer（现有源码中文说明，仅授权路径）。不新增文件结构或改 CODE_INDEX。

## 实施事实

- 七个授权路径均有本轮增量。Workbench 参数页为左侧有限编辑、右侧常驻状态和真实样例；右栏直接组合原 PageSamples 与公共卡片/动作，不复制或修改 PageSamples。既有 title/tone/compact 控件移到可展开次级区域，保留原事件；其他入口保持。
- 编辑器仅显示当前 theme 的九颜色字段，模式 selector 与顶栏共用 setTheme 和原 cu.theme；两 palette 保留。swatch 读取父级最近有效 profile，picker/HEX 写同一方案字段；无 alpha，仅既有六位规范校验。未复制默认或 token 映射。合法 picker active-change / HEX 即时更新，无需保存。
- 沿用 normalizeProfile 与 last-valid profile。字段旁显示六位 HEX 错误；右侧状态固定显示对应模式/字段、未应用和 last-valid，保存/导出禁用。共享数字/密度及原 save/restore/reset/export handlers/key/反馈保留。
- 拾色器 append-to 独立 body Teleport 的 #cu-color-overlays（现有 Element Plus 2.14.2 声明及实现确认支持 appendTo）；它与根和 PageSamples 原 Teleport 接收同一 theme / previewVariables。不写 html/body 主题，无 IPC/原生文件能力。
- 局部 CSS 只处理参数布局、颜色行、该 popup 表面。桌面 sticky top104px、max-height calc(100vh - 122px)，右内容区滚动；<=1180px 堆叠并解除 sticky/高度/overflow。公共 44px 工具、八组件 API、固定玻璃/卡片背景/阴影不变。用途说明明确 surface 是 EP 控件/表格基础面/弹层，固定装饰不冒称跟随。
- README pair 与对称 locale 解释当前模式、即时预览、用途及本地草稿非公共发布边界。

## 已执行 DEV self-check（历史执行顺序保留）

cwd=CU，复用已安装依赖，无安装请求或辅助依赖变更。pnpm wrapper 自有“Already up to date”输出保留；package/lock 在保护摘要中不变。shellenv 的 /bin/ps 沙箱提示未当作项目错误，也未重复 ps 或申请绕过。

| 命令 / 方法 | 实际结果 |
| --- | --- |
| pnpm build > /private/tmp/cu-006-r1-is03c7qe/build.log 2>&1 | exit0；design:profile --check一致，vue-tsc成功，Vite5.4.21 1628 modules / 2.25s，index-CUy0kFaJ.css与index-De2sxpnb.js。第三方PURE/chunk提示保留，不扩大优化范围。 |
| 初次 pnpm tauri dev（沙箱） | exit1；Vite listen EPERM 0.0.0.0:15193，未启动 native；原失败日志 tauri-dev.log保留。 |
| 经具体动作 require_escalated 授权 pnpm tauri dev | session7602，Vite15193 ready，既有cargo run缓存0.42s；2026-10-16T05:43:11.356852Z cu_process_start、05:43:11.555891Z cu_window_created(main / AIIS AW Console UI / ready)、05:43:11.572372Z cu_event_loop_ready。tauri-dev-authorized.log保留。未把浏览器交互记成native GUI证据。 |
| Python只读 locale/源码literal key/README相对链接/精确增量/保护摘要复核 | exit0；128叶子键对称，literal key均存在，README链接有效，38个固定禁止面源码摘要不变，七路径incremental.diff生成于保护目录。 |
| CUA后台入口与独立 origin尝试 | 初次127.0.0.1在服务未就绪时连接拒绝，生成本任务error tab1；明确visible:false重开返回subagent不支持visibility。按documented tabs.new后台入口生成tab3后，127.0.0.2 Page.navigate超时、DOM读取CDP focus超时。无存储/状态写入、无原生getApp；已交主协调以同次15193服务继续有限UI观察，避免重复争抢工具。 |

本任务未重跑consumer/CLI/草稿异常/Cargo全套/字段主题矩阵，不动其他Agent、DB、PLC、native包装、Git refs、发布部署。状态继续in_progress，UI事实、偏好/草稿恢复及最终资源会在handoff前补齐。

## Handoff 前具体问题及定向修复历史

主协调在同次15193服务的真实UI执行：进入参数页→恢复草稿提示不存在（未覆盖未知草稿）→强调色HEX改 #c2410c，根/色块/表格active即时改变→点击拾色器后popup未出现。控制台ElColorPicker/Tooltip/Popper报TypeError emitsOptions及Teleport patchBlockChildren。定位为append-to目标#cu-color-overlays位于编辑器模板末尾，首次渲染picker时目标尚不存在。最小修复只将原同源Teleport容器提前到模板首部，先挂载目标，再渲染含picker的Card；未扩范围或改公共层。原首次build成功日志仍保留，但修复后需必要最终build；native同次服务保留，无重复启动。

追加根因证据：主协调保存 ui-initial-error.json，Vue警告明确 Failed to locate Teleport target #cu-color-overlays; target must exist before component mounted；初始参数页每个picker均出现。初始原偏好light/zh-CN，Restore明确missing且未保存草稿；#c2410c只是内存，因此修复后可安全reload。此失败历史保留，不冒称首次picker流程通过。

挂载顺序修复后的必要最终 `pnpm build > /private/tmp/cu-006-r1-is03c7qe/build-final.log 2>&1` exit0：只读方案check一致、vue-tsc通过、Vite1628 modules / 2.41s，index-CUy0kFaJ.css / index-B2oRNEMl.js。先前build.log仅为修复前历史。未重复native启动或扩大回归。

第二个具体UI疑点：主协调代表性编辑流程已观察通过，但桌面右滚动区grid将首个样例面板压到2px（computed gridTemplateRows=2px 819px、scrollTop0），首卡内容不可见。最小修复仅在私有 .design-profile-preview-content 增加 grid-auto-rows:max-content 和 align-content:start，让样例保持内容高度，超出通过既有区内overflow滚动。未改公共Card或PageSamples。之后只需确认首卡恢复及必要最终build，不重走UI全套。

私有grid修复后的必要最终 `pnpm build > /private/tmp/cu-006-r1-is03c7qe/build-final-layout.log 2>&1` exit0：只读方案check一致、vue-tsc通过、Vite1628 modules / 2.37s，index-CScqeDGP.css / index-Dxj_fp_W.js。此前两份build保留各自历史，不代替最终输出。最终Python只读复核exit0：128 locale叶子键对称/literal key可解析/README链接有效/七路径无尾空白/38禁止源码摘要不变。

## 同次服务的代表性 UI 证据与恢复

UI操作者为主协调主线程，方法为documented CUA真实点击/输入/只读DOM与computed观察；Development读取其交付 ui-observations.json 与消息证据归档，不冒称Development自行独立GUI观察，更不作为QA verdict。原生启动证据来自本Development pnpm tauri dev的同次服务；没有原生WebView交互证明。脚本evaluate没有写状态/存储后门，没有生产测试开关。

- 起点原偏好为light / zh-CN，点击Restore明确missing、应用公共默认；此后仅创建本轮自有测试草稿，未覆盖未知用户草稿。
- HEX强调色#c2410c后root、色块及primary背景均为rgb(194,65,12)。picker实际展开在body的cu-color-overlays中，theme=light、accent=#c2410c、surface背景rgb(255,255,255)，矩形302×242，x195/y376，位于1280×720视口内，未被Card/滚动裁剪。picker改变后HEX/root/色块/picker/弹层/primary同为#c23d0c（rgb194,61,12），无需save/export/restart。
- 非法#gggggg保留root/色块/primary的#c23d0c，字段附近显示六位HEX反馈；右侧可见状态明确“日间 · 强调色：修改尚未应用。正在展示最近有效方案，已禁用保存与导出”。save/export enabled均false。修正后有效状态恢复。
- 显式夜间后编辑/预览theme=dark；夜间强调色#10b981，root/picker/样例dialog Teleport同值、primary rgb(16,185,129)，原样例弹窗可见并正常取消。返回日间仍为#c23d0c，两palette分别保留。已记录dialog overlay scope=dark和primary值；json中dialog background=rgba(0,0,0,0)、1280×720矩形对应overlay容器，**不是dialog面板背景实测**，不误称面板色值。
- 共享动作gap12→20px、卡片radius20→10px、表格cell vertical padding8→4px均computed可见；正常Save反馈local-only，改色后Restore恢复#c23d0c/gap20/radius10/compact。只做一轮正常草稿流程，未重测坏草稿/CLI异常套件。
- 桌面1280×720向下调参时right sticky y104；最终首卡287.59375px（修前2px），右content clientHeight512、scrollHeight1104，保持区内滚动；gridRows=287.594px 796.5px，首卡标题“样例面板”与动作可见。前期初始压缩截图仅留历史；最终cu6-live-preview.jpg对应修后。
- 一个1000×800窄窗观察：单列713px，controlsBottom585.609375 / previewTop603.609375，preview position=static、maxHeight=none、content overflow=visible。此观察发生在grid内容行修正之前，响应规则未改变；未重复尺寸矩阵。
- 最后通过UI Reset只删除本轮自有draft，再Restore明确missing；root/visible HEX恢复公共默认#0891b2，gap12/radius20/standard恢复，原light/zh-CN保留。主线程最终视口回1280×720，最后tab3关闭；其早先tab1/2失效且最终列表空，未冒称逐个手动关闭。

四张真实JPEG位于保护目录：cu6-initial.jpg（初期历史，不代替最终布局）、cu6-invalid.jpg、cu6-night-dialog.jpg、cu6-live-preview.jpg（最终布局）。关键值及恢复依据已永久写入本tasks，临时JSON/截图不是唯一事实源。主协调复查新tab控制台无error；存在既有PageSamples undefined类别翻译warning（workbench.pageSamples.undefined），PageSamples保护摘要未变；本任务如实保留，不范围外修复或扩大回归。取消dialog后立即check radio一次受动画时序影响未改变，fresh UI状态后正常，不当作新项目失败。已修复的真实picker挂载与grid压缩问题保留上述历史。

## 精确增量、资源、限制与 developer_handoff

七个实现/说明路径（相对CU；另本tasks为Development事实文档）：

```text
src/workbench/Workbench.vue
src/workbench/DesignProfileEditor.vue
src/workbench/workbench.css
src/locales/en-US/workbench.json
src/locales/zh-CN/workbench.json
README.md
README.zh-CN.md
```

最终工作树 HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30`（handoff前git rev-parse exit0确认），无worktree/branch/commit/PR或Git/GitHub写入。保护目录 `/private/tmp/cu-006-r1-is03c7qe/` 保留 manifest.txt、七路径before/、最终299行incremental.diff、final-sha256.txt、audit.json、38文件protected-sha256.json、三次真实build历史、失败/成功tauri日志、UI初始错误/最终观察JSON及四张JPEG，供fresh-context QA与Human审阅；一次性implement.py保留同目录，验收后由主协调核对归属及证据依赖收尾。已有node_modules/dist/target按原ignore保留；不将既有CU001–005未提交内容归因于本轮。

- 最终incremental.diff SHA256：`36cd5f1b65844b34ad98acdd0787898059bc5123cd88cf0880f4be42c42d5163`。
- 有序七路径final-sha256.txt摘要：`9499b521d5bda3b47783665bf2e097e30465647b131447101758b8d453ad85f6`。
- 最终Python只读复核exit0，128双语叶子键/literal key/README链接/尾空白通过，38选定禁止面源码摘要不变；git diff --check -- automation-world/console-ui exit0。未做全仓hash；spec/checklist/四索引/历史bundle及其他Agent均未由Development写入。
- UI完成后仅对本任务session7602发送Ctrl-C，write_stdin返回exit0。lsof -nP -iTCP:15193 -sTCP:LISTEN exit1无输出；lsof -t CU/src-tauri/target/debug/aiis-aw-console-ui exit1无输出，未广杀或停止用户服务。两项只证明当前未观测到该监听/该native executable打开记录，不冒称全机进程审计。
- Development早前CUA创建的error tab1/blank tab2/超时tab3在主协调接手后没有再次调用CUA list/close；其归属与自动回收状态不能独立确认。主协调最后的自有tab已关闭且其列表空；不得把两种标签证据混同。未绕过data:error policy，不反复GUI轮询。

限制与已知风险：验证仅当前macOS一次native window/ready与同次服务有限浏览器流程；浏览器观察由主协调执行，本Development如实消费证据。未做native GUI/包装/跨平台、consumer、CU005 CLI/坏草稿VM、字段主题矩阵、Cargo全套、全量回归、其他Agent/DB/PLC/现场、发布部署。合法配色的可读性/对比度仍由Human审阅；固定装饰背景/玻璃/阴影没有改成可编辑面。既有PageSamples翻译warning不在本任务allowlist，未修复。临时证据依赖应保留到QA/Human审阅，截图只支持所示代表性状态。

**Developer handoff：CU-006 r1 / 当前工作树 / 上述HEAD与精确七路径增量。** DEV self-check已完成上述限定实施与证据记录，不授QA verdict、Human Owner final acceptance或平台ACL/强制路由。主协调下一步显式启动 `agent_type=verification, fork_turns=none`，输入为owner_approved精确spec、本tasks、七路径当前源码、before/与incremental.diff、最终build/native日志及真实UI JSON/四截图。fresh-context Verification按AC1–AC6独立审阅，仅疑点/缺失复查，不重复整套构建/启动/编辑矩阵；只写checklist。QA通过后仍需Human Owner最终验收；CU005状态保持原qa_passed/pending，不代接受。
