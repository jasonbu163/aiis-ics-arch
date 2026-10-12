Task ID: ARCH-FE-004
Revision: r3
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: ARCH-FE-004 r3 配置与双语文档增量完成、静态自检通过；交新的 fresh-context Verification，r1/r2 历史保留，Human Owner 最终验收待定
Workflow Mode: STD
Execution Mode: agent_team_same_session
Updated: 2026-10-10

> 以下至“r2 实施与交接”前为 r1 Development 原始历史正文，含 QA-001 返工；其旧交接指向不代表 r2 状态。r1 的 QA 已经文档复验通过，最终验收未发生。

# Development 实施与交接

## 批准与工作树

Human Owner 于 2026-10-10 在当前会话回复“批准”，PM 已在 [spec.md](spec.md) 记录
`owner_approved`。本记录精确对应 ARCH-FE-004 r1，Development 未修改 spec 或 checklist。
基线 HEAD：`cb4cb06b2a5d5024c55b7ca427082770940f5959`；实现保留在当前工作树，未创建提交、分支或
worktree。PM 的 spec 批准记录与协调者的六个计划/索引文件分别由对应角色拥有，不计入本实现增量。

已阅读根 AGENTS、README/PLAN pair、frontend-js README/PLAN pair、canonical workflow、完整 spec
与相关实现；此 bundle 开始时只有 spec，没有 tasks/checklist。使用 frontend-ui（含 FRAMEWORK）、
i18n-workflow、docker-project-ops、docker-expert、code-document-indexer；浏览器辅助参考 playwright。
未引入辅助依赖到项目环境，未修改 skills。

## 实际修改

| 文件 | 实施事实 |
| --- | --- |
| `frontend-js/src/config/systemName.js`（新增） | 最小 `withSystemNames`，两语言独立 trim，有效值覆盖对应 `common.systemTitle`；缺失/空白保留 assembled locale 默认。浅拷贝避免改写 Registry 消息对象。使用 i18n message function 保留 `@ { } \| < >` 字面量。 |
| `frontend-js/src/locales/index.js` | createI18n 一次接入覆盖，原 locale、fallbackLocale 与 Registry 规则保留。 |
| `frontend-js/src/App.vue` | watchEffect 从全局 `t('common.systemTitle')` 同步 document.title，首次及语言变化生效。 |
| `frontend-js/src/pages/login/index.vue` | 两处 `login.subtitle` 改为 `common.systemTitle`，现有三处名称统一。 |
| `frontend-js/src/locales/zh-CN/login.json` / `en-US/login.json` | 对称删除无消费者 subtitle。 |
| `frontend-js/.env.example` / `.env.docker.dev.example` | 新增两中性默认变量和英文说明，其余值未改。 |
| `frontend-js/Dockerfile` | 构建阶段新增两 ARG 与对应 ENV；不改变镜像、步骤、runtime。 |
| `frontend-js/README.md` / `README.zh-CN.md` | 配置、独立回退、单入口、公开构建值、dev 重启、生产重构建与既有交付合同。 |
| `frontend-js/tests/module-registry/system-name.test.mjs`（新增） | 使用真实 Vue I18n 检查逐语言不同默认、两项缺失/空/空白/单项有效、trim/内部空格/普通字符、语言切换与其他消息不变。 |
| `CODE_INDEX.md` | 仅新增 helper、合同测试和 App 标题职责条目。 |

未改 `index.html`、两语言 common.json、BrandLogo、MainLayout、样式、认证/权限/API、实际 env、
依赖/锁文件、品牌资产或仓库 dist。登录后系统名称未新增 UI 区域。

## DEV self-check

环境：Node `v22.19.0`，pnpm `11.11.0`，仓库现有 Vite `5.4.21` 与已安装依赖；Chrome headless。
以下均为 Development 自检，不是独立 QA verdict。

| 命令/检查 | 结果 |
| --- | --- |
| `cd frontend-js && pnpm check:modules` | exit 0；活动 dashboard/plan/system，5 routes、3 groups。 |
| `cd frontend-js && pnpm test:modules` | exit 0；23/23 通过，含新增 2 个系统名称合同组。 |
| 隔离 fixture 下 `pnpm_config_verify_deps_before_run=false VITE_SYSTEM_NAME_ZH_CN='  工业  演示 @ {A} \| <B>  ' VITE_SYSTEM_NAME_EN_US='  Industrial  Demo @ {A} \| <B>  ' VITE_FRONTEND_MOCK_ENABLED=true pnpm build --outDir /private/tmp/arch-fe004-dev-j5muop15/dist` | exit 0；2196 modules，3.74 秒。仅既有大 chunk 警告与 outDir 位于项目外的提示；产物是公开 mock fixture，非交付 dist。 |
| `node /private/tmp/arch-fe004-dev-j5muop15/browser.cjs`（仅本地服务/Chrome所需 sandbox escalation） | exit 0；10 场景通过，pageerror/console error/外部或 API 请求均 0；脚本 finally 关闭 Chrome 和 HTTP 服务。 |
| Python 静态检查 | exit 0；两语言 login key 对称，无 login.subtitle 消费者，HTML 静态 title 保留，两实际 env SHA-256 与 fixture 建立时一致，README 本地链接有效，example/Dockerfile 两配置存在。 |
| Dockerfile 静态 diff 审查 | 仅两 ARG/ENV，默认与 examples 一致；Docker dev 既有 env_file 链路未改。未运行 Docker build/up/down。 |
| `git diff --check` | exit 0；实现增量全部在 §3 allowlist。 |

隔离 fixture 建立方式：在 `/private/tmp/arch-fe004-dev-j5muop15/frontend` 复制 frontend 的
`src/public/scripts/tests` 与 package/锁/workspace/index.html/vite.config.js；使用已跟踪 `.env.example`
作为该副本 `.env`，node_modules 仅软链接到现有项目依赖；未复制实际 env。上述两名称及 mock=true
由进程变量覆盖，原权限数组为公开 `[]`，API 默认仅同源且浏览器脚本拒绝任何 API/外部请求。

自检期间的非通过尝试如实记录：第一次误在 frontend cwd 使用带 frontend-js 前缀的写入路径，
创建测试与 README 修改均因路径不存在失败，没有产生额外文件；已在正确仓库根路径补正并重新跑
最终 23 项测试。fixture 第一次 pnpm build 触发 pnpm 11 deps-before-run 自动检查，网络 fetch 失败，
因 no-TTY 在移除 modules 前中止，exit 1；添加单次环境 `pnpm_config_verify_deps_before_run=false`
后使用既有依赖成功构建，不执行 install。首次本地 listen 在 sandbox 中 EPERM，精确 escalation 后
成功。浏览器脚本的标题断言最初未考虑原生空白规范化而 timeout；窄屏 Logo 检查最初未等
ResizeObserver，已等待布局稳定；鼠标点击退出菜单因既有 hover 关闭时序未出现确认框，最终采用
现有按钮的 focus + Enter 原生键盘交互完成退出。本任务未改这些产品行为。

## 浏览器 fixture 结果与限制

10 场景：首次无 locale 中文；登录页切英文；持久化英文刷新登录页；390×844 窄屏；
mock 登录成功进入 dashboard；持久化英文刷新认证页；认证壳切中文；导航 plan/list；
确认退出回登录页；退出后切英文。每个场景断言标题节点原文、浏览器标签标题、所有现有 Logo alt；
登录页额外断言三个名称位置一致、尖括号不产生 HTML 节点。Logo 自然比例、contain 与居中被测量，
日间无光晕/夜间 grid 光晕沿用源码；1280×800 日/夜与窄屏截图已目视检查，没有新增布局改动。

名称内连续两个空格保留在 i18n 返回、DOM textContent、Logo alt 和 title 节点 textContent；
Chrome 原生 `document.title` getter 按 HTML 语义折叠连续空白。最终脚本同时断言节点原文与
getter 的规范化结果。静态 HTML 初始化前仍显示默认名称，不承诺零闪烁。

此结果只证明公开 fixture 中 UI/路由/语言/标题行为；mock 登录/退出不是后端真实认证链路证明。
未接真实 backend、数据库、PLC、CA，未做 Docker runtime、生产部署或发布。合理长度之外的名称
仍可能占用现有区域，未引入长度策略或布局调整。

## 资源与精确 Developer handoff

本任务资源为 `/private/tmp/arch-fe004-dev-j5muop15/`：

- `frontend/`：上述隔离源码与公开 `.env`，以及只指向现有依赖的 node_modules 软链接。
- `dist/`：复杂双语名称、mock=true 的隔离生产构建。
- `browser.cjs`：可重复执行的本地静态服务与 Chrome 脚本，随机绑定 127.0.0.1 端口，拒绝 API/外部请求。
- `browser-result.json`：10 场景标题/locale/Logo测量、无错误结果。
- `login-zh-light.png`、`login-en-dark.png`、`login-mobile.png`、`shell-en-dark.png`：浏览器截图。
- `baseline-env-hashes.json`：仅实际 env 路径和摘要，不含配置内容。

另有本任务创建的 `/private/tmp/arch-fe004-dev-path` 路径指针。没有分支/worktree/Docker资源。
所有由脚本启动的临时静态服务与浏览器均已随 finally 关闭；保留副本与证据供 Verification 重现，
Human Owner 验收后由协调者确认无依赖再按 canonical workflow 收尾。

交接目标：fresh-context Verification，精确 ARCH-FE-004 r1 与上述 HEAD 的当前工作树。
请独立审阅 spec/tasks、13 个实现文件的增量和新文件，复跑模块检查/测试、隔离构建与必要浏览器场景，
核对真实 env/锁/资产/布局无改动；仅 Verification 创建 checklist.md 并给 verdict。
协调者机械同步六个索引；Development 不授予 QA、Human Owner final acceptance 或外部发布权限。

## QA-001 返工与重新交接（2026-10-10）

已完整阅读 [checklist.md](checklist.md) 第一轮 `qa_failed`：功能 AC1–AC7 独立检查通过，
唯一失败 QA-001 为本文件缺少必需的顶部 `Handoff:` 元数据。本轮只新增该非空字段与本返工记录，
保留第一轮 Development self-check、handoff 和 Verification 失败历史；未修改实现、spec、
checklist 或索引。13 个实现文件在本次文档修正前后的 SHA-256 均一致。

`git diff --check` exit 0；顶部 `Handoff:` 精确前缀计数为 1，值非空。未重复功能测试，
依据第一轮独立功能证据与本次无实现变化边界。没有新临时资源或运行进程。
重新交接状态为 `developer_handoff`，精确 Revision 仍为 ARCH-FE-004 r1、基线 HEAD 不变；
请新的 fresh-context Verification 仅独立复核 QA-001 文档增量及相关证据，之后才进入
Human Owner 最终验收 gate。本返工不提供 QA verdict。


# r2 实施与交接（2026-10-10）

Human Owner 已明确批准 ARCH-FE-004 r2，PM 的 [spec.md](spec.md) 为 owner_approved。
本轮仅实现 §3 allowlist，保留上述 r1 正文与独立 checklist 历史。HEAD 仍为
`cb4cb06b2a5d5024c55b7ca427082770940f5959`，无提交/分支/worktree。

## r2 实际增量

- `src/config/systemName.js` / `src/locales/index.js`：沿用 helper 和全局入口，独立解析两描述；
  即使空也提供该语言的 message function，返回空字符串而非触发 fallback，保留所有普通字符。
  系统名称的逐语言默认与纯文本行为保留。
- `src/pages/login/index.vue`：hero 小标题改为 computed `login.subtitle`，`v-if` 在空值时移除整行；
  无描述时仅将大标题原先配给描述的 16px 下边距设为 0。其余结构/字号/间距不改；右 caption 继续系统名。
- 中英文 `login.json`：对称恢复 subtitle 空默认。
- `tests/module-registry/system-name.test.mjs`：新增两合同组，覆盖缺失/空/空白/单语言配置、
  不借用其他语言或系统名、独立 trim/内部连续空格和特殊字符，保留 r1 名称测试。
- 两 examples、Dockerfile：仅补两描述变量与空默认/英文说明及构建传值。
- README pair 和 CODE_INDEX：同步名称/描述不同消费位置、回退与显示规则、公开值和交付时点。

上述相对路径均在 frontend-js 下（CODE_INDEX 为根文件）。r2 实现共 12 个文件，另更新本 tasks；
没有新增实现文件或依赖。App、静态 HTML、common、Logo/壳、权限/API/mock/品牌值、真实 env 与锁保持。

## r2 DEV self-check 与浏览器

沿用 r1 已读取 skills 与工具链；Node v22.19.0、pnpm 11.11.0、Vite 5.4.21、现有依赖和 Chrome。
以下是 Development self-check，不是独立 QA。

| 检查 | 结果 |
| --- | --- |
| frontend-js 下 `pnpm_config_verify_deps_before_run=false pnpm check:modules` | exit 0；dashboard/plan/system，5 routes、3 groups。 |
| 同目录 `pnpm_config_verify_deps_before_run=false pnpm test:modules` | exit 0；25/25 通过，含 r1 及新增两描述合同组。 |
| `node /private/tmp/arch-fe004-r2-dev-w7sy36us/build.cjs` | exit 0；both/zh/en/none 四次独立生产构建均 exit 0，输出各自 dist；仅既有大 chunk 与项目外 outDir 提示。 |
| `node /private/tmp/arch-fe004-r2-dev-w7sy36us/browser-batch.cjs` | exit 0；四个 fixture 各 10 场景，共 40 通过；各 pageerror/console error/外部或 API 请求均 0。仅本地 listen/Chrome 申请精确 sandbox escalation。 |
| Python 对照 r2 baseline manifest | exit 0；24 项中只有批准的 12 个实现文件改变；其余 12 项包括 App、HTML、common、Logo/壳、依赖/锁、实际 env 与 checklist 摘要不变。 |
| Python locale/README 检查 | exit 0；两 subtitle 默认空、login key 对称、本地 README 文件链接有效。Dockerfile 静态增量仅两描述 ARG/ENV，空默认一致。 |
| `git diff --check` 与 tasks 必需元数据检查 | exit 0；Task ID/Revision/Status/Owner Role/Allowed Writers/Handoff/Workflow Mode/Execution Mode/Updated 各一条非空；当前 Revision r2。 |

fixture 使用公开 example 为自身 .env，不复制真实 env；node_modules 只软链接现有依赖。
`build.cjs` 按以下矩阵用进程变量覆盖：

| fixture | 中文描述 | 英文描述 |
| --- | --- | --- |
| both | 首尾带空格的 `描述  @ {A} \| <b>文本</b>` | 首尾带空格的 `Description  @ {A} \| <b>Text</b>` |
| zh | 首尾带空格的中文描述 | 纯空白 |
| en | 空字符串 | 首尾带空格的英文描述 |
| none | 不设进程变量，公开 example 空默认 | 不设进程变量，公开 example 空默认 |

名称仍使用 r1 复杂双语 fixture。四次构建均在隔离 frontend cwd 运行
`pnpm_config_verify_deps_before_run=false` 和 `VITE_FRONTEND_MOCK_ENABLED=true` 的
`pnpm build --outDir <对应dist目录>`；具体名称/描述及完整参数见保留的 build.cjs/fixtures.json。
缺失、两空、纯空白及单项有效的所有组合还由真实 Vue I18n 合同测试覆盖；无翻译 fallback 警告。

每个浏览器 fixture 都独立完成首次中文、切英文、英文登录页刷新、390px 窄屏、mock 登录成功、
英文认证页刷新、壳切中文、导航 plan/list、确认退出、退出后切英文。登录时额外断言当前语言
描述文本或 DOM 节点计数 0，标题下边距分别为 16px/0px，`<b>` 不生成 HTML 元素；始终回归
hero 大标题、右 caption、所有 Logo alt、title 节点及浏览器标题。Logo contain/自然比例/居中也保留。
四组截图各四张，已目视 both 非空、none 隐藏与 en-only 英文夜间截图；未见本次增量导致重叠。
无描述时原布局会按既有 flex 分布重新排列，这属于移除该行占位的既定行为。

r1 标题 getter 空白规范化限制仍适用。所有浏览器/静态服务在每轮 finally 中关闭；没有本轮
失败尝试、依赖安装、Docker、真实 backend/DB/设备访问或生产 dist 改写。公开 mock 结果不证明
真实认证，Dockerfile 仍仅静态审查；长文本策略不在 r2。

## r2 资源与精确 handoff

协调者提供的 `/private/tmp/arch-fe004-r2-baseline-4u7nu2wn/` 保留 r2 开始前 14 个文件副本和
24 项 manifest（真实 env 仅摘要），用于区分 r2 增量与 r1/角色历史。Development 未改 baseline。
本轮新资源 `/private/tmp/arch-fe004-r2-dev-w7sy36us/` 包含隔离 frontend、四组 dist、
`build.cjs` / build 日志 / fixtures.json、`browser.cjs` / `browser-batch.cjs` / browser 日志、
四个 `*-browser-result.json` 及各四张截图；另有路径指针 `/private/tmp/arch-fe004-r2-dev-path`。
r1 与 QA 旧证据保持，不删除任何归属不明资源；无新分支/worktree/Docker 资源或存活服务。

交接为 ARCH-FE-004 r2 `developer_handoff`，当前工作树相对上述 r2 baseline 的 12 个实现文件
加本 tasks，原 HEAD 不变。请新的 fresh-context Verification 对照 approved r2、完整历史 bundle、
baseline 和当前源码，独立验证描述与系统名各自行为、空行间距及保全边界；仅 Verification 更新
checklist，协调者机械同步六索引。实现已冻结。Human Owner 最终验收及发布/部署均未发生。


## r2 demo 注释补充与交接（2026-10-10）

Human Owner 新授权在两份 env example 的描述字段上方提供可复制 demo，英文采用
`Powered by AIIS ICS Architecture`。本轮只在 `.env.example` / `.env.docker.dev.example`
加入相同的两条注释赋值和用法：去除 #，替换现有对应赋值，不追加重复 key。
活动两描述默认继续为空；未改源码、真实 env、依赖或其他活动配置，不改变已批准 r2 行为合同。

以 `/private/tmp/arch-fe004-demo-comments-baseline-mpx4_fg9/` 的原副本为基准：
Python 静态检查 exit 0，两文件 demo 注释逐字相同、删除新增注释后与基线字节相等、
全部活动赋值原样保留；用现有 Vite loadEnv（其 dotenv parser）去注释解析，两描述值均为示例文本。
`git diff --check` exit 0。本轮只改两 examples 和本 tasks（顶部 Handoff 与本追加段），
此前实施/QA 历史保持；未重复未变的功能测试、构建或浏览器，无新增服务或保留临时资源（解析用临时目录已在 finally 回收）。
精确交接仍为 ARCH-FE-004 r2 `developer_handoff`、原 HEAD 的当前工作树；
请新的 fresh-context Verification 对照上述 demo baseline 复核注释与活动项保全。


# r3 配置维护与文档交接（2026-10-10）

Human Owner 明确批准 ARCH-FE-004 r3；已读取完整最新 approved spec、tasks/checklist 历史、
根契约及 Development profile，并沿用当前会话已读的前端/i18n、Docker env 边界 skills。
本轮只触达配置与文档，不改运行实现。基线 HEAD 仍为
`cb4cb06b2a5d5024c55b7ca427082770940f5959`，无提交/分支/worktree。

## r3 实际文件与保全

- `frontend-js/.env.example` / `.env.docker.dev.example`：保留用户已设的唯一活动
  `Powered by AIIS ICS Architecture` 中英文 demo 值；统一两行英文用途/清空隐藏说明，
  删除 host 过时 remove # 指引。除这两处说明变动外与 r3 baseline 字节相同。
- Git ignored 的 `frontend-js/.env` / `.env.docker.dev`：只在现有英文系统名称行后插入
  一个英文说明及两项空 subtitle 活动配置块；没有替换文件、原名称或任何其他字节。
  剥除本次新增块后的 SHA-256 与 r3 开始前各自摘要一致。实际文件不提交、不打印或备份全文。
- `frontend-js/README.md` / `README.zh-CN.md`：用途表补名称/描述两组键，说明各自消费位置与
  trim/回退/隐藏，以及 Logo 配置和回退的既有合同；给 example 活动 demo 和实际 env 空块，
  强调替换同名项、避免重复 key。新增字段须开发时同步维护对应 examples 与本地实际活动键并
  保留用户已有值，可选可空且说明语义，必填/受校验项合法；不承诺运行时自动写文件，不追溯
  补 VITE_OPEN_BROWSER。区分 host 重启 Vite、Docker dev env_file 需重建相应容器、生产重建
  dist 后按原流程交付；没有执行这些运行操作。README 历史角色配置节及其后原文完整保留。
- 本 `tasks.md`：顶部 Revision/Handoff 更新为 r3，追加本记录；此前 r1/r2 完整正文保留。

r3 实际增量共七个文件（其中两个 ignored 实际 env 不出现在普通 Git diff），其余源码/测试/
Dockerfile/Compose/依赖/锁/CODE_INDEX/AGENTS 及角色文件保持。spec 归 PM、checklist 归 QA，
六索引归协调者；Development 未修改这些文件。

## r3 DEV 静态自检

| 命令/检查 | 结果 |
| --- | --- |
| `python3 /private/tmp/arch-fe004-r3-dev-check.py` | exit 0；四文件各 17 个活动 key，集合一致且无重复；两 examples 的描述解析为公开 demo 原文，实际 env 两项解析为空。 |
| 同脚本原字节/ignore 检查 | exit 0；两实际 env 剥除唯一新增块后分别匹配 baseline SHA；git check-ignore --quiet 两项均 exit 0，git ls-files --error-unmatch 两项均非零，仍 ignored 且未跟踪。examples 除允许说明替换外与 baseline 相同。 |
| 同脚本受保护/历史/链接检查 | exit 0；118 项受保护摘要全部一致，checklist 与 baseline 相同；旧 tasks 完整正文保留，README 本地文件链接均存在。 |
| Python README 历史节比较 | exit 0；中英文历史角色配置节及后续原文与 r3 baseline 逐字相同。人工复核 pair 的配置/维护/交付条款与 R3 一致。 |
| `git diff --check` 与 tasks 必需元数据检查 | exit 0；九项元数据各一条非空，Revision r3、Status developer_handoff。 |

静态解析只读取活动键并按 dotenv 空值/双引号赋值语法解析两新增公开字段，没有输出真实 env
整体内容或其他值。输出仅公开 demo、空值状态、键数量及保全结果。本轮未安装依赖，
未重跑 r2 功能测试/生产构建/浏览器/无关全仓 checker；旧 25 tests/四构建/40 场景仅为历史证据，
不替代本 r3 独立 QA。未启动或操作 Docker/backend/DB/设备，未生成生产 dist、发布或推送。
本轮无失败检查或残留 blocker。

## r3 资源、限制与精确 handoff

协调者的 `/private/tmp/arch-fe004-r3-baseline-xtin_eoa/` 保存两公开 examples、README pair、
spec/tasks/checklist 原副本与 manifest；实际 env 只保存 SHA，没有秘密副本。
Development 未改 baseline。本轮唯一新临时资源为
`/private/tmp/arch-fe004-r3-dev-check.py`，可重复执行的只读静态审计脚本，不含真实 env 值；
保留供 QA 复验。没有服务、容器、分支/worktree 或其他运行资源；旧证据继续保留，
验收后由协调者确认依赖再收尾。

实现冻结并交 `developer_handoff`：精确 ARCH-FE-004 r3、原 HEAD 的当前工作树，
相对 r3 baseline 仅上述七文件增量。请新的 fresh-context Verification 对照 approved spec、
完整 bundle 和 baseline，独立核对 demo/空键唯一与解析、原字节保全、Git ignore、README pair、
受保护摘要和历史完整性；只有 QA 更新 checklist 并给 verdict。Human Owner 最终验收仍待定。
