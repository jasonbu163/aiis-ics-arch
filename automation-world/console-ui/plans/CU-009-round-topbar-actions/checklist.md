Task ID: CU-009
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: AC01–AC04 独立验证通过，交 Human Owner 对精确候选最终验收。
Task Namespace: aiis-ics-arch
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-009 r1 独立验证

## 候选与环境

- 2026-11-12 至 2026-11-13（Asia/Shanghai）在 Development 交接后由 Verification 以 fresh context 独立验证。读取根 AGENTS、README/PLAN、角色合同与 canonical workflow，复核 AW/CU 与各宿主的适用规则、任务 bundle、源代码、diff 及可用 DEV 产物。使用 project-governance、frontend-ui、i18n-workflow 和 playwright。触达面只有根 AGENTS。角色按 contract_only 执行。 [批准范围](spec.md) · [Development 交接](tasks.md) · [Canonical workflow](../../../../.codex/workflows/development-lifecycle-workflow.md)
- 交付树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的 HEAD 为 `fd999224a8756feda314a33148304b4bf3461876`，交接列出的 12 个未提交实现及说明文件 SHA-256 全部匹配。按交接原顺序对 12 行摘要计算的 SHA-256 为 `c9c031f698ef1357a64552b2e4504ad057ce2e75b5e0a1bdd1d3ff6c6408f935`。spec SHA-256 为 `deef91ac2f8033619e9d8ca915f1ccae12c5b59dce4a446d6cbaf9e49c1f5770`，tasks SHA-256 为 `841d72bff3db603c7d7ea993ac3648e039e90ebecaaf5ba8b24d9301df097dc6`。同树并行变更按各自任务范围归属。
- macOS 15.7.7（24G720）、Darwin arm64、Node v22.19.0、pnpm 11.11.0，使用各工程现有依赖。浏览器为 Chrome 157.0.8103.78 的临时会话。静态产物与两处宿主忙态夹具仅由任务自有环回 HTTP 服务提供，页面请求限制在各自服务源内。

## 验收结果

| 编号 | 结论 | 独立结果 |
| --- | --- | --- |
| AC01 外观与文案 | PASS | 在 DAA、DS、CU 实际前端构建中测得主题、语言、刷新按钮均为 44 × 44 CSS px、圆角 999px。中文显示目标 `EN`，英文显示目标 `中`。两语刷新控件无正文，只有装饰 SVG。DAA、DS 及 CU 的空闲 SVG 均为 20 × 20 CSS px，与按钮中心的偏差为 (0, 0) px，SVG 图形边界中心偏差约 (0.0013, −0.0017) px，无空文字 span。对照 Owner 提供的旧截图，查看 QA 独立截图确认 DAA、DS 的刷新图标已居中。SMA 与独立消费者的圆形语言控件两语可切换，顶栏原动作集合保留。普通按钮在夹具中保留 40px 高、可见文字和单次点击反馈。 |
| AC02 操作与无障碍 | PASS | 五个前端通过 Tab 到达语言按钮，三处刷新同样可达。明暗主题均观察到 2px 焦点轮廓。语言按钮的鼠标、Enter 和 Space 各切换一次，键盘切换后保持可见焦点。两语 `title` 和可访问名称相符，刷新名为「刷新」/ `Refresh`，装饰图标带 `aria-hidden`。DAA、DS 语言短标签截图清晰，取计算前景及截图实际背景得到明色 5.71:1、暗色 7.21:1，刷新图标使用同一前景 token。刷新空闲时无旋转，忙态图标 20 × 20px、中心偏差 (0, 0) px，`rotating` 周期 2s。用真实 DAA/DS 顶栏源码、受控 props 与事件计数独立检查，鼠标/Enter/Space 令原 `refresh-runtime` 计数依次为 1/2/3，忙态的鼠标及按键尝试后仍为 3，恢复后为 4。另对公共组件单独施加 loading 或 disabled，均无触发。CU 英文界面中，鼠标/Enter/Space 令样例反馈计数按 1/2/3 更新，中文反馈键及计数参数由静态检查核对。CU、DAA、DS、SMA 重载后保持各自语言和主题，独立消费者使用原英文初值及会话内状态。 |
| AC03 窗口与集成 | PASS | DAA 检查了 1280 × 820 及 960 × 640 英文长副标题与侧栏展开、收起四种组合，另检查 1280 × 820 中文初始布局。标题和动作区无交叠，圆形按钮均在顶栏内，标题、动作区、顶栏、工作区的横向溢出测量均为 0。DS、CU、SMA、独立消费者在 960 × 640 检查展开、收起，另通过 CU 580 × 640 窄窗。核对 DAA、DS、SMA、独立消费者的 Vite alias 指向 CU 公共源码和样式入口，CU 工作台走同一公共组件出口。DAA、DS 仍绑定宿主 `refreshBusy` 并经原 `refresh-runtime` 到 `local.refresh()`。五工程各自独立 `pnpm build` 均退出 0。 |
| AC04 范围与说明 | PASS | 双语工作台 JSON 各 156 个叶键，52 个静态引用均可解析，新增样例文案均包含 `{count}`。四份消费说明准确写出目标语言、`round-icon`、`icon`、翻译 label 与 title fallback。四份说明和 spec/tasks 共 49 处本地文件链接可达。工作树和暂存区的 `git diff --check` 均退出 0。CU-009 的 DAA 代码改动仅顶栏启用 `round-icon`。DAA-010 r5 第 4 节另有 Rust、SQLite、上报及业务页面候选，第 6 节规定自有合成 profile 和独立 S7/HTTP/MySQL 运行目标。CU-009 环回浏览器观察只用于本任务 UI 验收。 [DAA-010 r5 规格](../../../data-acquisition-agent/plans/DAA-010-sample-facts-upload/spec.md) |

## 命令与证据

下列构建分别从对应工程目录运行。所有输出写入独立临时目录。已查看 Development 的原始截图和 UI 日志，且用自己的构建、浏览器和夹具复验。

| 工程或检查 | 实际命令 | 结果 |
| --- | --- | --- |
| CU | `pnpm build --outDir /private/tmp/cu009-r1-qa-eRS3nt/cu` | 0，design profile check、vue-tsc、Vite。 |
| 独立消费者 | `pnpm build --outDir /private/tmp/cu009-r1-qa-eRS3nt/consumer` | 0，vue-tsc、Vite。 |
| DAA | `pnpm build --outDir /private/tmp/cu009-r1-qa-eRS3nt/daa` | 0，vue-tsc、Vite。 |
| DS | `pnpm build --outDir /private/tmp/cu009-r1-qa-eRS3nt/ds` | 0，vue-tsc、Vite。 |
| SMA | `pnpm build --outDir /private/tmp/cu009-r1-qa-eRS3nt/sma` | 0，vue-tsc、Vite。 |
| 交付产物核对 | 分别对五工程执行 `diff -qr /private/tmp/cu009-r1-dev-KQq5vD/final/<app> /private/tmp/cu009-r1-qa-eRS3nt/<app>` | 均为 0，两个角色独立构建的静态产物逐字节相同。 |
| 受控忙态夹具 | `automation-world/console-ui/node_modules/.bin/vite build /private/tmp/cu009-r1-qa-eRS3nt/fixture --outDir /private/tmp/cu009-r1-qa-eRS3nt/harness` | 0，引用交付树的公共入口与 DAA、DS 实际顶栏组件，夹具控制 busy/disabled 并计数。 |
| 浏览器 | `node /private/tmp/cu009-r1-qa-eRS3nt/verify-ui.cjs` | 最终退出 0，五前端和两个受控宿主共七组断言全过。默认 sandbox 的 Chrome 启动试探为 SIGABRT，使用获准的沙箱外命令及临时会话解决。首次可运行轮次按源码修正 QA 脚本中 SMA 的现有提示「切换为英文」、消费者英文初值和主题过渡取样时序，最终轮次通过。 |
| 明暗截图对比 | `python3 /private/tmp/cu009-r1-qa-eRS3nt/contrast.py` | 0。DAA、DS 的前景亮色 RGB (90, 104, 117) 对实际背景 (254, 255, 255)，暗色 RGB (164, 177, 189) 对实际背景 (26, 36, 44)。 |
| 源码与文档 | `python3 /private/tmp/cu009-r1-qa-eRS3nt/verify-static.py`、`git diff --check`、`git diff --cached --check` | 均为 0。核对精确 HEAD、摘要、双语键及本地文件链接。 |

Vite 报告第三方 PURE 注释位置与部分 chunk 大小提示，五次构建均成功。角色元数据可由 `Owner Role: Development` 和实际 `developer_handoff` 核对，`tasks.md` 缺 project-governance 模板的 `Allowed Writers` 字段。本记录保留该格式偏差，AC01–AC04 的实现和证据均可追溯。

## 限制、资源与交接

本次证据覆盖已批准的源码、构建、静态浏览器 UI 和受控宿主刷新事件。Tauri 原生 WebView、已安装桌面版本、实际 S7 采集、数据库及 HTTP 上报由各自运行与验收范围管理。预检发现现有 DAA、DS Vite 已占用 15191、15194，QA 的自有端口由系统分配，最终轮次为 58351–58356，浏览器及其环回服务已关闭，复查这些端口无监听。QA 仓库写入仅此文件。

QA 临时目录 `/private/tmp/cu009-r1-qa-eRS3nt` 约 6.1 MiB，包含独立五宿主构建、只含合成状态的夹具、脚本、日志和截图。DEV 临时目录 `/private/tmp/cu009-r1-dev-KQq5vD` 由 DEV handoff 列明。两处供 Owner 验收期间追溯，关键测量和结果已收入本记录，验收后交主协调按归属核对回收。

**QA verdict 为 `qa_passed`（AC01–AC04）。当前无实现返工项或验证阻塞。Human Owner 最终验收待定。**
