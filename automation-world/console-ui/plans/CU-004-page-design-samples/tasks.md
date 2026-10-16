Task ID: CU-004
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: CU-004 r1 implemented in current working tree at HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30; fresh-context Verification to review approved spec, this DEV record and incremental.diff
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-004 r1 Development

2026-10-16（Asia/Shanghai），依据 [批准规格](spec.md) 和 Human Owner 精确 r1 批准实施。读取根 AGENTS / README / PLAN pair、canonical workflow、development profile、AW/CU 最近 README/PLAN、消费者教程、当前 bundle（写前只有 spec）、既有 CU-001/002/003 记录及相关实现。未发现更近 AGENTS。按表面使用 frontend-ui、i18n-workflow、desktop-tauri、code-document-indexer，仅新增样例源码头注释，CODE_INDEX 不在授权范围。

计划：
1. 保存14路径清单及13个既有文件副本，再实现私有页面和最小公共样式；以增量 diff 核对 allowlist。
2. 增补独立消费者的 Element Plus 组合和双语教程；检查 locale 对称/文档链接。
3. 一轮 CU build / tauri dev 原生 ready 及同次浏览器聚焦观察，CU停止后 consumer build / preview；记录真实结果后交 fresh-context Verification。

受保护起点：当前工作树 HEAD `1a5aa2d2fe7089b5671218865238cfaa240f9a30`，CU-001/002/003 已验收未提交内容保留。无全仓快照、worktree 或 commit。恢复与证据目录：`/private/tmp/cu-004-r1-wzefyd_8`；manifest.txt 精确枚举14个实现/说明路径，before/保存13个既有文件；新增PageSamples及本tasks起点不存在。

本记录只属于 Development，不给 QA verdict 或最终验收；profile 为 contract_only，不宣称平台 ACL 或强制路由。CU-005及其他Agent不在本轮实现范围。

## 实际实施与边界

| 需求 | 实施 |
| --- | --- |
| R1 | Workbench 增加显式“页面样例”导航及 PageSamples 私有组件；保留三个原入口。直接组合 Element Plus Table、Form、Input、Select、Dialog，三条固定脱敏记录。表单有名称必填/非空白及2–24字符校验、类别选择、提交和重置；提交更新首行内存数据。弹窗独立 draft，取消不写入，确认校验后更新所选行，含设计样例标题/说明。 |
| R2 | 列表四个手动 radio 状态：正常表格、明确加载提示及 aria-busy、ElEmpty 解释、失败说明与本地重试。重试恢复正常并反馈，无网络/定时器。反馈通过受控 locale key 显示。 |
| R3 | theme.css 仅补充所需 Element Plus token 映射，既有 --agent-* 色板值保留。components.css 追加 aw-data-table、aw-sample-form、aw-form-actions、aw-page-state 及 dialog/select 样式；私有双列/单列布局留在 workbench.css。body Teleport 内有显式 .aw-ui/data-aw-theme 容器，ElDialog append-to-body=false；所有 ElSelect teleported=false，宿主主题持续传入，无 html/body 全局主题写入。八组件/API、公共出口及44px顶栏规则保留。 |
| R4 | consumer 用自身 Element Plus / ElConfigProvider locale、内存状态及翻译自行组合最小 table/form/dialog，通过既有 @aw-ui / @aw-ui-styles 消费公共层，不导入私有工作台。四README补充同义的组合、样式顺序、语义类、弹层主题和宿主责任合同；原源码可达/依赖单实例/自身dist合同保留。 |

样例内容刷新后不保留；仅既有 CU 宿主 cu.theme/cu.locale 偏好机制沿用。无 API/IPC/数据库/PLC/文件或业务持久化。未实现 CU-005 的样式编辑、草稿保存或 JSON 生成 CSS。

精确 Development 修改文件（相对 CU，14个实现/说明 + 本 tasks）：

```text
src/workbench/Workbench.vue
src/workbench/PageSamples.vue
src/workbench/workbench.css
src/locales/en-US/workbench.json
src/locales/zh-CN/workbench.json
src/ui/styles/theme.css
src/ui/styles/components.css
examples/source-consumer/src/App.vue
examples/source-consumer/src/locales/en-US.json
examples/source-consumer/src/locales/zh-CN.json
README.md
README.zh-CN.md
examples/source-consumer/README.md
examples/source-consumer/README.zh-CN.md
plans/CU-004-page-design-samples/tasks.md
```

本轮未手写 spec/checklist、PLAN/catalog、公共八组件源码/index/types、依赖/锁文件、main/App启动入口、Vite/Tauri/Rust/端口配置、CODE_INDEX、根/AW文档或其他Agent。工作树已有Tauri生成schema相对HEAD的description差异（CU-002 tasks已记录此现状），本轮不手改或恢复生成文件，不将HEAD全量差异归为CU-004。构建产物仍由现有ignore管理。

## DEV self-check：实际命令与结果

环境：macOS Darwin arm64，Node v22.19.0，pnpm 11.11.0；沿用已有依赖，无安装辅助依赖。以下默认cwd=CU，consumer行cwd=examples/source-consumer。证据目录 `/private/tmp/cu-004-r1-wzefyd_8/`。

| 命令/动作 | 实际结果 |
| --- | --- |
| 首次 `pnpm build > .../cu-build.log 2>&1` | 退出2；vue-tsc指出Element Plus DefaultRow不能直接传入私有typed row函数。已保留cu-build-first-type-error.log；将入口改为传row.key，函数按key在受控内存行中查找。 |
| 修正后的 `pnpm build > .../cu-build.log 2>&1` | 退出0；vue-tsc + Vite，1624 modules，2.17s。第三方PURE注释及大于500kB chunk提示保留，不扩大为依赖/拆包优化。 |
| `lsof -nP -iTCP:15193 -iTCP:14194 -sTCP:LISTEN` 启动前 | 无监听，退出1（预期）。 |
| `pnpm tauri dev > .../tauri-dev.log 2>&1`（本机授权执行环境） | 一次原生启动，Vite strict15193 ready，Cargo dev 0.36s；原生60602、Vite60505、pnpm60312。窗口/事件循环JSONL ready如下。观察后SIGTERM只停止这三本任务进程，wrapper退出143（主动停止）。 |
| 同次dev的 `http://localhost:15193/`，cua_repl IAB | 一轮聚焦交互，具体事实如下；浏览器交互与原生启动证据分开。子Agent visible=true不支持，改用visible=false创建后台tab成功，未调用native cua.getApp。 |
| consumer `pnpm build > .../consumer-build.log 2>&1` | 退出0；vue-tsc + Vite，1619 modules，2.40s，自身dist生成。 |
| CU停止后 consumer `pnpm preview > .../consumer-preview.log 2>&1` | strict127.0.0.1:14194；自身dist独立运行，IAB交互成功。最初沙箱curl显示HTTP000，随后在本机授权环境记录CU HTTP000 / consumer HTTP200；未将初次探测作为服务失败。 |
| `python3` 标准库定向静态检查（inline） | 退出0；14路径增量、CU81/consumer30个叶子翻译键各自对称、字面量t key可解析、四README相对链接有效；公共CSS无私有依赖，样例/consumer无API/IPC/storage，consumer不导入workbench，44px顶栏规则保留。输出在static-audit.log，未执行全仓hash。 |
| `git diff --check -- automation-world/console-ui` | 退出0，无输出。新增/未跟踪文件也通过before/逐文件生成incremental.diff审阅。 |
| `kill -TERM 61594`，等待preview session | 只停止本任务consumer preview；wrapper退出0。最终lsof无15193/14194监听，ps -p 60602,60505,60312,61594只返回表头、退出1（进程均结束）。两个本任务IAB tab已关闭；CU初始暗色/英语偏好已恢复。 |

### 原生启动事实（UTC）

```json
{"timestamp":"2026-10-16T01:41:57.341350Z","level":"INFO","fields":{"event":"cu_process_start","process":"aiis-aw-console-ui","result":"starting"}}
{"timestamp":"2026-10-16T01:41:57.587101Z","level":"INFO","fields":{"event":"cu_window_created","window":"main","title":"AIIS AW Console UI","result":"ready"}}
{"timestamp":"2026-10-16T01:41:57.608750Z","level":"INFO","fields":{"event":"cu_event_loop_ready","process":"aiis-aw-console-ui","result":"ready"}}
```

### 同轮浏览器聚焦观察

- CU初始为英语/暗色。页面显示三行 Panel A/B/C，类别Standard/Compact及编辑入口。Loading显示明确手动加载提示；Empty显示恢复说明；Failed显示本地失败说明和Retry；Retry恢复正常三行并出现Local sample restored。
- 空名称提交显示Enter a sample name；输入X提交显示Use 2–24 characters；输入Preview Alpha提交后首行更新且出现Preview submitted in memory only。Reset后输入为空并出现Form reset locally（中文观察为“已在本地重置表单”）。
- 编辑首行草稿为Cancelled value后取消，列表仍为Preview Alpha，并显示取消反馈；再次编辑确认Edited Alpha后列表更新且显示内存反馈。关闭按钮可关弹窗，取消/确认均返回列表，不触发实际设备动作。
- 英语暗色弹窗与下拉：最近主题容器均dark，dialog背景rgb(24,34,44)、文本rgb(230,237,242)、边框rgb(51,68,82)；popup背景rgb(24,34,44)。切换中文/日间后表头、按钮、样例数据及反馈翻译生效；重新打开弹窗/下拉主题light，dialog/popup背景rgb(255,255,255)，dialog文字rgb(23,33,43)。documentElement data-aw-theme为空，未污染全局主题。
- consumer自身dist初始英语/亮色显示table/form；空提交出现Enter 2–24 characters，输入Consumer Alpha提交后列表更新。切换中文/暗色后控件和说明翻译，弹窗显示“编辑·设计样例”及只修改内存提示；dark容器dialog背景rgb(24,34,44)、文本rgb(230,237,242)，popup同背景，全局主题为空。确认Consumer Edited后其列表更新。此时CU已停止，不需在线CU。

截图（少量代表性证据，不是组合矩阵）：
- `cu-dark-dialog.jpg`：CU暗色英语弹窗与下拉。
- `cu-light-zh.jpg`：CU日间中文页面、表格/表单/内存反馈及44px顶栏。
- `consumer-dark-dialog.jpg`：consumer中文暗色弹窗与下拉。

## 增量、资源、限制与 developer_handoff

`manifest.txt` 精确14路径；`before/` 保存13个原文件；`baseline.txt`固定起点HEAD；`incremental.diff`（452行）逐文件对比受保护起点，新增PageSamples以/dev/null为起点。它不包含主协调的索引变化，也不把既有CU-001/002/003差异归为本任务。回退只能核对并发归属后处理此实际增量，当前未执行回退。

保留 `/private/tmp/cu-004-r1-wzefyd_8/` 的必要恢复副本、manifest、baseline、incremental.diff、两次CU build日志、tauri-dev/consumer-build/preview日志、static-audit.log、两份实际编辑脚本及三张截图，供独立QA和Human Owner审阅；关键结果已永久收录本tasks，临时目录不是唯一证据。无新增worktree/branch/commit/PR，临时指针已移除。CU/consumer已有node_modules/dist与CU target保留且忽略；只关闭本任务已确认归属的进程/tab。验收后资源由主协调盘点。

验证限于必要构建、当前macOS一次原生窗口创建/ready、同次浏览器聚焦观察及一次独立consumer引用；没有全量回归、其他Agent/CA/TSS、Cargo全套、额外native打包、跨平台、原生窗口交互、发布/部署/推送或真实数据库/PLC验证。保留现有依赖代际和chunk体量提示。编译期仍需公共源码可达及依赖单实例；构建后的consumer自身dist无需CU在线。未发现新增实现阻塞；实际QA verdict仍待fresh-context Verification。

**精确 developer_handoff：CU-004 r1 / 当前工作树（HEAD 1a5aa2d2fe7089b5671218865238cfaa240f9a30）**。Development实施与self-check如上；请主协调显式启动 `agent_type=verification, fork_turns=none`。验证输入为owner_approved spec、本tasks、14个实现/说明文件、before/及incremental.diff、真实日志与三张截图。Verification按AC1–AC6独立审阅，仅疑点/缺失才复跑，不因角色分离重测整套；仅写checklist。Human Owner最终验收在QA之后。本handoff不授予Git refs、发布部署或现场动作权限，不宣称平台ACL、强制路由或完整团队激活。
