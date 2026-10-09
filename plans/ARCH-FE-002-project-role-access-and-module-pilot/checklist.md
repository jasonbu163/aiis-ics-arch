Task ID: ARCH-FE-002
Revision: r4
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 于 2026-10-09 明确授权接受 ARCH-FE-002 r4，Verification 代录最终决定；历史 QA 原文保留，本轮三模式访问与四 env 格式检查通过；协调者可机械同步本任务索引，其他任务及真实 API/部署等独立 gate 不变

# r2/r3 Verification 历史（完整保留）

Task ID: ARCH-FE-002
Revision: r3
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: fresh-context Verification 独立通过精确 r3 文档与配置注释范围；r2 完整 QA 历史保留，交 Human Owner 最终验收；真实宿主机未知授权阻塞和真实 API 未验证继续保留

# r2 Verification 历史（完整保留）

Task ID: ARCH-FE-002
Revision: r2
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: fresh-context Verification 通过精确 r2 源码/配置迁移/隔离运行范围；交 Human Owner 最终验收，真实宿主机未知授权阻塞与业务 API 未验证继续保留

# 验证依据与范围

- 2026-10-08，独立 Verification，contract_only profile；在 Development 最末 `Final handoff confirmation` 后读取当前 main 未提交工作树，未继承 Development 对话推理。
- 完整读取根 AGENTS、根 README/PLAN pairs、frontend README/PLAN pairs、app README pairs，以及完整 spec r2 / tasks。使用 project-governance、frontend-ui、i18n-workflow、code-document-indexer 验证合同；只写本 checklist，不改实现、测试、spec、tasks 或配置。
- 对照 Development changed files 与 Git diff；共享 router、MainLayout、locale loader、user store、auth 正式源码无本任务改动；无 backend/其他六模块/Compose/Nginx/依赖锁文件改动。本任务 r2 已批准，001 final acceptance 保持独立。

# AC 检查结果

| 标准 | 结果 | 独立证据 |
| --- | --- | --- |
| AC-001 模板、共用配置及原授权保留 | 通过，含既定限制 | 两公开模板和 Dockerfile 均为两新 key、安全空数组；宿主机 dev/build 共用 .env，Docker dev env_file 沿用 .env.docker.dev，未新增 production env。双语说明覆盖 Vite 优先级、重启 dev、重建 dist、Nginx 重绑既有语义。忽略文件中的两活动数组与保留的旧注释 JSON 成员和顺序相等：宿主机 20/14，Docker 0/0；无活动旧 key，两文件仍 ignored。 |
| AC-002 严格数组与 subset | 通过 | 独立复跑测试覆盖 missing、malformed、non-array、非字符串、非法格式、重复、unknown、disabled、admin-only、活动旧 key 与 operator 独有 grant；公开合法配置通过，空数组不给非 admin 页面，未知角色 fail closed。源码统一 helper 拒绝而非扩权。 |
| AC-003 route/menu/default 一致 | 通过 | Node 三角色及未知角色矩阵使用同 Registry/access 原语；浏览器独立检查 admin 三组、supervisor 两组、operator 一组。默认入口均为已授权 dashboard；disabled demo 无注册 route/menu，admin 与 operator 直达 demo 均返回 dashboard。 |
| AC-004 pilot 审核、双语、浏览器 | 通过限定范围 | dashboard/plan route name/path/pageId 与 HEAD 既有 identity 一致，组 order 10/20，system 80；模块自有 title 与 assembled messages 通过。25 个模块文件及依赖/API facade 审查未发现客户地址或密钥；搜索唯一 secret pattern 命中为 CSS el-mask-color 误报。隔离 build 和浏览器菜单/直达通过，真实业务 API 未验证。 |
| AC-005 checks 与证据边界 | 通过 | 独立 checker/test/build、mode/local/process 负例、12 本地文档 target、diff check 均通过。真实 .env development/production access 和 build 仍以 unknown pageId 拒绝，符合 r2 保留并报告规则；不将 fixture 通过称为实际配置可启动。 |

# 独立执行记录

| 命令 / 检查 | 退出码 / 结果 |
| --- | --- |
| `pnpm --dir frontend-js check:modules` | 0；active dashboard/plan/system，5 records，3 groups |
| `pnpm --dir frontend-js test:modules` | 0；18 tests，18 pass，0 fail；含实际 Vite dev/build/custom mode 未知进程覆盖 exit1 断言 |
| `node frontend-js/scripts/check-page-access.mjs` | 0；仅 Usage，不读 env |
| `node frontend-js/scripts/check-module-manifests.mjs` | 0；仅 Usage，不读 env |
| `pnpm --dir frontend-js check:access --mode development` | 1；脱敏捕获确认 unknown pageId，未回显成员/地址 |
| `pnpm --dir frontend-js check:access --mode production` | 1；同上 |
| `pnpm --dir frontend-js check:access --mode docker.dev` | 0；supervisor/operator 0/0；不是 Docker 运行证据 |
| `pnpm --dir frontend-js build --outDir /private/tmp/arch-fe002-qa-real-blocked` | 1；真实配置 unknown pageId 拒绝；没有交付 build |
| QA 自建公开复制夹具中 `pnpm --config.verify-deps-before-run=false run build --outDir /private/tmp/arch-fe002-qa-dist` | 0；2192 modules transformed，built in 3.65s；仅临时夹具链接既有 node_modules，未安装依赖或改项目配置 |
| Python 脱敏原注释 / 活动数组比较，`git check-ignore` | 0；20/14 与 0/0 成员顺序相等、仍忽略 |
| package.json HEAD/current dependency sections 与 lock diff | 0；dependencies/devDependencies 一致，锁无差异，package 仅 scripts 增项 |
| 稳定双语 docs Markdown 本地 target 检查 | 0；12 targets 存在 |
| `git diff --check` | 0 |

QA 公开夹具 `/private/tmp/arch-fe002-qa-fixture` 排除全部真实 .env 与 dist；只写公开 mock 配置。独立构建日志 `/private/tmp/arch-fe002-qa-build.log`，构建 `/private/tmp/arch-fe002-qa-dist` 保留复核。既有大 chunk/outDir 提示不阻止源码构建，未将产物用作部署。

# 独立浏览器证据

CUA 后台新 tab，`http://127.0.0.1:5194/`，03:54–03:58 UTC；使用 Development 留存公开隔离 fixture，经协调者确认已停止使用后只在 `/private/tmp/arch-fe002-dev-fixture/src/api/mock/auth.js` 切 role 并通过登录 UI 更新会话，正式 auth 源码未变；未输入真实凭据。

| 角色 | 独立观察 |
| --- | --- |
| operator | root -> dashboard；仅 Dashboard/工作台组，中英文正常；direct `/plan/list` 与 `/aiis_demo/example` 返回 dashboard；近期计划无 View All 链接。 |
| supervisor | 工作台、计划管理依序，无 system；展开组后点击计划列表成功；英文 Plan List、Degreasing、中文计划列表/脱脂均显示；direct `/system/dict` 返回 dashboard；View All 入口可见。 |
| admin | root -> dashboard；Dashboard/Plan Management/System 依序，中英文对应；direct `/plan/list` 和 `/system/dict` 可达正确页面；direct demo 返回 dashboard。 |

- dashboard 与 plan 观察窗口的 error log 初始为空，雷达图修复后没有 radarLayout TypeError；指标、趋势、计划列表已呈现，未再白屏。
- admin 到 system/dict 后正确展示 Mapping Settings 壳；缺少后端 handler fixture 导致两个 HTTP 500 与加载错误提示。此项只证明 admin 路由权限，不证明 system 或业务 API 可用；没有启动/访问真实 backend。
- 常规计划 priority 与未知数值 fallback、materialStatus 双语呈现正常。未做业务写入、XLSX 或 linkage 操作。

# 限制、风险与下一 gate

- **真实宿主机配置仍不可启动/构建**：保留旧授权含未迁入页面，unknown pageId exit1 是 r2 明确要求的兼容边界。需 003 迁入或 Owner 明确调整授权；本次没有清理或扩权。
- **其他 env 设置的历史保留证据有限**：未保存迁移前整份真实 env 或 checksum。独立复核迁移器仅替换旧 key 原行、注释保留原 JSON、插入新数组；成员/顺序可独立核对，其余设置保留依赖迁移器行为与 Development 执行记录，不能声称独立逐字比对迁移前全文件。未复制或回显敏感值。
- **真实业务 API 未验证**：dashboard GET facade、plan CRUD/XLSX/linkage 继续存在，但 Core backend 不在 r2 提供这些接口。前端 mock 编译/导航通过不等于业务数据或服务合同通过。
- 前端 role/page gate 不替代 backend API 权限，disabled 不承诺源码未被 bundler 扫描。
- 文档索引收尾已独立复核：协调者在获批索引范围将 frontend PLAN pairs 的旧“business modules/pageIds absent”表述改为 002 已接入 dashboard/plan 及 dashboard.home/plan.list，其余模块归后续 003；文字张力已修复。根 PLAN、frontend PLAN、plans README 三组共六文件均以 qa_passed 索引精确 r2，并明确 Owner final acceptance pending；三文件链接存在，双语语义一致。未扩大源码或验证范围。
- 未执行 Docker up/down/build、数据库迁移/写入、设备操作、生产部署、Git add/commit/push/tag。QA 不授予最终验收或发布授权。

# Verdict 与交接

**qa_passed**：ARCH-FE-002 精确 r2 的 AC-001～AC-005 在上述源码、迁移核对、公开隔离构建与浏览器范围内通过；无须 Development 返工的阻塞缺陷。真实配置限制及真实 API 未验证保留，不计为已完成运行交付。

Human Owner final acceptance: pending。由 Human Owner 判断是否接受 r2 交付与已列限制；本 checklist 不把 qa_passed 改写为 owner_accepted。协调者可更新本任务索引并处理已经明确不再需要的运行会话，复核证据文件与目录继续保留。

# r3 fresh-context Verification（2026-10-08）

## 依据与范围

- 当前精确对象：ARCH-FE-002 `owner_approved` r3 与 Development `developer_handoff` r3，共享 main 未提交工作树。独立读取根 AGENTS、README/PLAN pairs、docs README pairs、frontend README/PLAN pairs、app README pairs、完整 spec/tasks/checklist；按 verification contract_only profile 与 project-governance 执行，只写本 checklist。
- 当前元数据对应 r3；上文完整保留 r2 QA、命令、浏览器观察与限制，未将历史 verdict 自动继承。本轮对新增文档/注释单独复核，不重复运行 r2 build/browser/功能检查。
- 独立检查脚本 `/private/tmp/arch-fe002-r3-qa.py` 只在内存读取真实 env，输出计数与相等结果，不保存或回显私有值。Development 临时检查脚本仅用于理解证据格式，不作为本轮 QA 命令。

## r3 AC 与独立证据

| 标准 | 结果 | 独立证据 |
| --- | --- | --- |
| AC-r3-001 活动配置与忽略边界 | 通过 | 独立逐行解析四 env，规范化 active SHA256 及逐 key SHA256 与 before 基线、after 记录均相等；key 数 13/8/8/8，无重复 key、活动旧 key 或新增 OPEN_BROWSER。两真实文件 `git check-ignore` exit0。活动角色成员和顺序保持 host 20/14、Docker 0/0。 |
| AC-r3-002 历史移入双语 README | 通过 | 两真实 env 不再含 ARCH-FE-002 历史说明或旧 key 注释。两 README 的两个历史 JSON 对象分别等值；host 对象与未变的活动数组完全相等（含顺序），Docker `{}` 与空数组语义相同。历史对象严格只有 supervisor/operator 的 pageId 数组和空对象，没有地址、密钥或其他 env 配置。两文档明确不活动读取、不直接恢复尚未迁入授权。 |
| AC-r3-003 英文说明、用途与文档质量 | 通过 | 四 env 注释为 ASCII 英文，每项有用途注释，同 key 文字一致。双语 README 对现有 13 key 与可选 OPEN_BROWSER 覆盖完整；独立源码读取核对 API_CONFIG/base/timeout、Vite proxy/port/open、mockMode、login hints 与角色 helper。Core src 无 VITE_BRAND 消费者，文档明确 five brand keys unused，旧 hight-light 仅历史意图，未宣称当前兼容。6 本地链接及 anchor、代码块闭合与 diff check 通过。 |
| AC-r3-004 限定变更与历史/验收边界 | 通过限定范围 | 当前 96 个 frontend src/工具链基线文件重新计算 SHA256 与 before 相同，包含 package.json、pnpm-lock.yaml、vite.config.js、Dockerfile；权限 helper/Registry/模块源码行为没有 r3 改动。Git 总 diff 含 r2 已批准实现，不误判为本轮新增越权；本轮文档/comment 变化对齐精确 allowlist 与 r3 handoff。r2 完整开发/QA 历史保留，当前 r3 verdict 独立记录；未新增生产 env 或配置来源。 |

## 实际命令与结果

| 命令 / 检查 | 退出码 / 结果 |
| --- | --- |
| `python3 /private/tmp/arch-fe002-r3-qa.py` | 0；4 active/逐 key hash 相等，96 基线文件未变；同 key 注释一致，历史对象及成员顺序一致，13+1 key 完整，6 本地 target/anchor 和 fences 通过 |
| `rg` 读取 src/vite/scripts 中配置消费者 | 0；API base/timeout、mock、demo hints、Vite dev proxy/port/open 与 README 对齐；VITE_BRAND 当前无消费者 |
| `git diff -- frontend-js/.env.example frontend-js/.env.docker.dev.example frontend-js/README.md frontend-js/README.zh-CN.md` | 0；人工审阅公开差异；r2 配置迁移与 r3 注释/配置表/历史节区分，未搬入真实私有地址 |
| `git check-ignore frontend-js/.env frontend-js/.env.docker.dev` | 0；两文件继续 ignored |
| `git diff --check` | 0 |

规范化 checksum 的修改前证据来自 Development 留存的 `/private/tmp/arch-fe002-r3-before.json`，与 after 字节语义等值；QA 独立重算当前文件和逐 key digest，而非仅相信 Development 的 pass 文本。修改前整份真实 env 未复制；这些证据证明活动 key/value 和列入基线的文件未变，不声称恢复被移走注释的逐字全文。

## Verdict 与下一 gate

**qa_passed**：精确 r3 AC-r3-001～004 在 documentation/config-comment-only 范围内通过，没有需 Development 返工的阻塞缺陷。

- 当前宿主机授权仍包含未迁入 pageId，unknown-page 阻断保持；本轮没有重新运行 dev/build，不据文档通过宣称真实配置可运行。
- 真实业务 API、部署、Docker 操作、数据库、设备、Git 发布及 ARCH-FE-001 final acceptance 均未验证或授权。r2 功能 QA 证据保留为历史，不扩大本轮结论。
- Human Owner final acceptance: pending。协调者可按本 verdict 机械同步任务索引；最终接受 r3 与已列边界须由 Human Owner 记录。

# r4 fresh-context Verification（2026-10-09）

## 精确对象、角色与环境

- 独立 Verification 从 fresh context 读取 ARCH-FE-002 `owner_approved` r4、Development 最末 `developer_handoff` r4 及完整历史 bundle，没有继承 Development 对话推理；旧 r2/r3 verdict 没有自动成为本轮结论。
- 依顺序完整读取根 AGENTS、根 README/PLAN pairs、frontend README/PLAN pairs、app README pairs、spec/tasks/checklist；另读取最近 styles README pair、Verification TOML、canonical workflow、实现、Git diff、冻结来源和可用 DEV 输出。
- 使用 project-governance、frontend-ui、i18n-workflow、code-document-indexer 验证相应表面；浏览器按 frontend-testing-debugging 执行。当前工具无 Browser plugin / CUA / browser automation，使用项目外已安装 Playwright 和本机 Chrome；未安装依赖。
- 目标为共享 `main` 未提交工作树，HEAD `ac316ebabb65c1799a6b8f2e4fbd4096b5afc9ec`；Node `v22.19.0`、pnpm `11.11.0`、Vite `5.4.21`、Chrome `154.0.8037.98`。profile 仅 `contract_only`，不宣称平台 ACL 或强制路由。TOML 的 model/effort 是配置证据，本 checklist 不将其写成独立测得的运行值。
- 本轮只修改本 checklist；临时独立脚本、报告、构建与截图写 `/private/tmp`。保留共享工作树中 prior r2/r3 和其他任务变更，不 reset，不修实现、测试、spec、tasks 或配置。

## r4 AC 与独立证据

| 标准 | 结果 | 独立证据 |
| --- | --- | --- |
| AC-r4-001 品牌解析正反例 | 通过 | 独立阅读 `brand.js`/薄纯 helper 与测试，并复跑 21 组 Node 合同矩阵，全部通过。包含已打包文件、缺失/未知文件、路径分隔符、穿越、URL、alignment 三值/invalid default、三段 glow 四值、大小写/空白和 `hight-light` alias。glob 仅本地已打包资产；fallback SVG 存在且无客户图片。 |
| AC-r4-002 构建与实际品牌渲染 | 通过限定范围 | 独立隔离 build 通过，fixture `src` 与当前全部源码逐文件相同。独立浏览器复验 5196/5197/5198 的登录及 mock admin 壳层，两主题、三对齐、三段 glow/none/alias、有效资源/非法路径/不存在文件回退全部通过。自然比例 2:1、contain 与 ResizeObserver 的 viewport 更新可观测；无白屏、Vite overlay 或运行 error。390×844 无横向溢出，Logo 可见。 |
| AC-r4-003 配置差异、历史和说明 | 通过 | QA 独立重算当前 key SHA256 与 r4 before/final 证据：host 13 key 中仅两授权数组不同，Docker 8 key 全同，五品牌/mock/API 等值保留。以当前 Registry 非 admin leaf 与 README 历史数组独立求交，原顺序得到 host sup3/op2，Docker0/0。两份 README 的历史 20/14 与 `{}` 原文 block SHA256 均与 before 相同，双语对象等值；四 env 同 key 英文说明一致，两 example 中性默认/空授权/mock与demo关闭。6 个本地 Markdown target/anchor、fences、Docker 五品牌 ARG/ENV 通过。 |
| AC-r4-004 实际配置及必要检查 | 通过 | 真实 `.env` 的 development/production access 检查各 exit0；有限 dev ready156ms 后主动停止，只验证启动，不访问真实页面/API。真实 `.env` 临时输出 build 与公开隔离 build 均 exit0、2195 modules；module checker、21组 tests、diff check 通过。deps/lock 无变动，没有安装依赖或迁六模块。 |
| AC-r4-005 allowlist、历史与独立 gate | 通过 | 96 文件 DEV pre-r4 基线中 94 不变，变化仅允许的 BrandLogo/Dockerfile；新增 source 仅品牌 config/helper/demo SVG。BrandLogo 与冻结组件仅 header 路径不同。Docker 与 HEAD 相比除历史 r2 两数组迁移外，只增加五品牌 ARG/ENV；CODE_INDEX 对真实新增结构有入口，header 路径准确。完整 r2/r3 QA 原文保留，r4 当前元数据和 verdict 独立形成；真实 API、部署、001 与 Human Owner 最终验收没有被冒称完成。 |

## 实际执行记录

| 命令 / 检查 | 退出码 / 结果 |
| --- | --- |
| `pnpm --version` / `node --version` | 0；11.11.0 / v22.19.0 |
| `pnpm --dir frontend-js check:modules` | 0；active dashboard/plan/system，5 records、3 groups |
| `pnpm --dir frontend-js test:modules` | 0；21 tests、21 pass、0 fail，含3组品牌矩阵、严格权限负例、mode/local/process 覆盖与双语 literal key |
| `pnpm --dir frontend-js check:access --mode development` | 0；supervisor3/operator2 |
| `pnpm --dir frontend-js check:access --mode production` | 0；supervisor3/operator2 |
| `pnpm --dir frontend-js check:access --mode docker.dev` | 0；supervisor0/operator0；不是 Docker runtime 证据 |
| `pnpm --config.verify-deps-before-run=false --dir frontend-js build --outDir /private/tmp/arch-fe002-r4-qa-real-dist` | 0；2195 modules，3.38s；读取真实 `.env`，只向临时目录构建，没有部署 |
| fixture 目录：`pnpm --config.verify-deps-before-run=false run build --mode center --outDir /private/tmp/arch-fe002-r4-qa-isolated-dist` | 0；2195 modules，3.40s；公开 env、既有 node_modules，无安装 |
| frontend 目录：`pnpm --config.verify-deps-before-run=false dev --host 127.0.0.1 --port 5195 --strictPort` | Vite ready156ms；QA Ctrl-C 停止，pnpm 包装退出1。启动成功与主动停止分开记录，没有打开真实页面/登录/API |
| `python3 /private/tmp/arch-fe002-r4-qa-audit.py` | 0；独立 key/history/source/fixture/English comments/defaults/Docker/index/header/link audit，报告 `/private/tmp/arch-fe002-r4-qa-audit.json` |
| `diff -u` 当前/frozen BrandLogo | 1（预期有一处差异）；只有文件 header 路径；Python 再次断言替换路径后全文等值 |
| `diff -u` 当前/临时 fixture Vite config | 1（预期有一处环境差异）；最终只多 `cacheDir: path.resolve('/private/tmp/arch-fe002-r4-vite-cache', mode)` |
| `node /private/tmp/arch-fe002-r4-qa-browser.cjs` 最终独立执行 | 0；session32251，三个 mode 全完成；结果 `/private/tmp/arch-fe002-r4-qa-browser-result.json` |
| `git check-ignore frontend-js/.env frontend-js/.env.docker.dev` | 0；两真实文件仍 ignored |
| `git diff --check` | 0；包括本轮 checklist 收尾 |

一次性 `verify-deps-before-run=false` 仅阻止 pnpm 的依赖状态自动安装，不修改项目配置、依赖或锁。两 build 均保留既有 outDir 位于项目外与大 chunk 提示；isolated shell 的 Homebrew `/bin/ps: Operation not permitted` 提示没有阻止编译。这些构建不是部署工件。

## 浏览器矩阵、交互与视觉证据

目标流程：公开 fixture `/login` -> 昼夜/语言切换与 viewport resize -> mock admin 登录 -> `/dashboard/home` 的 sidebar BrandLogo -> 再切日间；全程阻止非指定 loopback 请求，未使用真实账号或后端。

| fixture | 五配置的可观测结果 |
| --- | --- |
| 5196 center | 已存在 demo SVG；accent/light/accent。登录 224px 容器中 fit160×80、offset32；sidebar fit144×72、offset25.5。 |
| 5197 left | `../outside.svg` 被拒绝，使用 demo；空白大写 `HIGHT-LIGHT` -> high-light，center none、right light。登录 offset0，sidebar offset0；夜间颜色分别强白、透明、白。 |
| 5198 right | `missing.svg` 回退 demo；none/none/none。登录 offset64，sidebar offset51；三个 pseudo-element 背景均透明，符合显式 none。 |
| 390×844 center | 容器192×68、fit136×68、offset28；Logo 可见、无横向溢出；恢复1280×800后回到原尺寸，ResizeObserver 正常更新。 |

- 三个 context 均验证 title/URL、非空内容、无框架 overlay、图片加载和自然比例；登录与壳层日间 glow display 为 none、夜间为 grid。语言切换通过实际控件，Username/用户名互换，img alt 使用 i18n `common.systemTitle`。
- 最终每 context 的 pageerror/console error、API 请求与意外外部请求均为0。每 context 有两条既有 Element Plus `el-radio label act as value` deprecation warning，来自 dashboard 原有 radio，不属于品牌变更；无其他 warning 类别。r4 不修该范围外组件。
- QA 目视 center 夜间登录/sidebar/mobile、left 夜间登录及 right none sidebar，品牌/光晕符合对应模式，没有白屏或重叠。mock 图表数据与动画不构成真实业务数据证据。
- 最终截图：`/private/tmp/arch-fe002-r4-qa-center-light.png`、`center-dark.png`、`left-light.png`、`left-dark.png`、`right-light.png`、`right-dark.png`、`center-shell.png`、`left-shell.png`、`right-shell.png`（同 qa 前缀），以及 `/private/tmp/arch-fe002-r4-qa-mobile.png`。详细尺寸/颜色/日志保存在最终 JSON；关键结果也已在本 checklist 汇总，不依赖临时路径作为唯一事实。

## 失败尝试、环境恢复与证据限制

- 最初 sandbox Chrome launch 被 SIGABRT 终止并出现 kill EPERM，未跑浏览器检查；按工具合同用受限 `require_escalated` 命令后成功启动。一次提权复跑调用等待334.2秒后被中断，未返回 cell/session，不能记为浏览器 pass 或产品 failure。
- 第一版 QA 输入 `qa_public_fixture_admin` 超过现有 username max20，mock 登录停在表单校验，waitForURL 超时；QA 将临时脚本输入改为 `qa_fixture_admin` 后复跑，没有修改产品校验。
- 随后 session58142 的 center 全通过，left 登录品牌检查通过，但进入 dashboard 返回 `504 Outdated Optimize Dep`，产生动态 import/Router 错误；API 请求为0。失败保留于 `/private/tmp/arch-fe002-r4-qa-first-browser-failure.json` 和 `qa-login-failure.png`。协调者一度机械运行同一 QA 脚本，也复现相同504；该次结果没有作为最终通过证据。
- 三 mode Vite 使用链接的 node_modules 时复用 `.vite` 缓存。fixture 创建者只在其临时 Vite config 增加按 mode 隔离的 `/private/tmp` cacheDir，08:07:16 重启原三个服务；QA 独立 diff 确认只有该一行环境差异，产品 src/env 没改。此后 QA 自行执行最终 session32251 全矩阵 exit0，环境阻塞已解除，不静默修复实现。
- pre-r4 key/source/history baseline 来自 Development 保留的脱敏证据；QA 独立重算当前文件并逐项比对，没有独立生成修改前时间点的证据，也没有保存迁移前完整 env。证明范围为活动 key/value、历史 JSON 原文块及96个列明基线文件；不宣称所有历史注释全文逐字可恢复。

## Verdict、资源与下一 gate

**qa_passed**：精确 ARCH-FE-002 r4 AC-r4-001～005 在源码、配置核对、有限启动、临时构建和公开 mock 浏览器范围内独立通过；没有需 Development 返工的实现 blocker。环境504已按明确临时 cache 隔离解除，失败证据仍保留。

- 当前真实 host 两数组已可通过严格 checker/start/build；r2/r3 历史 unknown-grant 阻断仅为当时状态，不能当作 r4 当前限制。实际品牌文件在 Core 不存在时按已批准合同使用中性 fallback，没有迁入客户图片。
- 真实登录、backend/API 数据/权限、CRUD/XLSX/linkage、Docker、DB/设备、部署、Git 发布、ARCH-FE-001 final acceptance 均未验证或授权。前端可见性不替代后端授权；public mock 通过不证明现场业务可用。
- Human Owner final acceptance: pending。QA 只将 verdict 与边界 handoff 给 Human Owner；协调者可机械同步本任务索引，不能代为授予 owner_accepted。
- QA 浏览器脚本最终关闭自身 Chrome，真实有限 dev 已停止。协调者报告已 Ctrl-C 停止其三个公开 fixture session35883/79205/77531（均 exit130）；QA没有停止或修改 parent 服务。该停止状态注明为协调者资源事实，不冒称独立进程盘点。
- `/private/tmp` 的 r4 before/final/source baseline、QA audit/browser JSON、失败副本、截图和两临时 build 继续保留到 Human Owner 复核；旧 r2/r3 证据也保留。临时 cache/fixture 由创建者管理，QA不回收资源，验收后应先核对证据及运行依赖再处理。


# Human Owner final acceptance（2026-10-09）

- **精确接受对象：ARCH-FE-002 r4；最终状态：owner_accepted。** 决定者为 Human Owner；本节由独立 Verification 按真实用户授权代录，不是 QA 自行授予最终验收。
- 授权依据：Human Owner 在前端 env 格式 DIRECT 调整后说明已自行同步 `.env.docker.dev`，并明确要求“其他没什么问题了，是不是可以 human-owner 接受了？是的话帮我接受”。协调者将接受对象限定为本任务 r4；本轮确认既有 r4 `qa_passed` 无未关闭实现 blocker，满足该指令的接受条件。
- 本次记录从 fresh context 独立读取根 AGENTS、README/PLAN pairs、canonical workflow、frontend README/PLAN pairs、完整三文件 bundle、相关配置读取实现与公开 env diff。使用 project-governance、frontend-ui、i18n-workflow；只写本 checklist，不修改 spec、tasks、实现、测试或配置。
- r2/r3/r4 的 Development 与 QA 历史原样保留。后续 DIRECT 是 env 分节、英文注释、逐项说明和排版调整；Human Owner 自行同步 Docker 配置的事实单独注明，不把这些后续变化追溯为旧 r4 QA 已覆盖的内容。

## 接受前当前配置检查

环境：共享 main 未提交工作树；macOS 15.7.7 arm64、Node v22.19.0、pnpm 11.11.0。未安装依赖；真实 env 仅在内存读取，输出只含 key 数、计数和布尔结果，没有回显私有值。

| 命令 / 检查 | 退出码 / 结果 |
| --- | --- |
| `pnpm --dir frontend-js check:access --mode development` | 0；supervisor 3 / operator 2 |
| `pnpm --dir frontend-js check:access --mode production` | 0；supervisor 3 / operator 2 |
| `pnpm --dir frontend-js check:access --mode docker.dev` | 0；supervisor 0 / operator 0；仅 Vite 有效配置校验，不是 Docker 运行证据 |
| 内联 `python3 -` 四 env 结构/格式审计 | 0；`.env`、`.env.docker.dev` 及两份 `.example` 当前均为 13 个唯一活动 key，key 顺序与六组分节一致；逐 key 用途注释相同且为英文，每项均有说明，boolean/JSON 引号语法正确，无活动旧 key；两公开 example 的权限数组仍为空 |
| `git check-ignore frontend-js/.env frontend-js/.env.docker.dev` | 0；两真实文件仍 ignored |
| `git diff --check` | 0 |

Docker dev 当前授权仍是 0/0，并未变为宿主机的 3/2；“保持一致”在本记录中不被扩大解释为所有场景配置值完全相等。用户同步后 Docker 文件当前有五项品牌 key，旧 r4 QA 记录的 Docker 8 key/无品牌 key 只代表当时状态。本轮未重跑 build、dev 启动、浏览器或真实 API；旧 r4 的这些验证保留各自原始时点与边界。本轮配置检查通过，没有新发现的接受 blocker。

## 接受边界与资源 handoff

- Human Owner 接受本任务 r4 的既有交付与已披露限制，并授权本节记录。ARCH-FE-001、ARCH-BE-001、后续 003 及其他任务不在此次接受范围；真实登录/业务 API/CRUD/XLSX/linkage、部署、数据库/设备、Docker 操作和 Git 发布继续为独立 gate。
- 按既有文档盘点，继续保留 `/private/tmp` 中 r2/r3/r4 脱敏 before/final/source 基线、QA audit/browser JSON、失败副本、截图与临时 build，作为审计复核依赖；已有 fixture/cache 由创建者管理。本轮未启动服务、未生成新临时证据文件、未删除资源，也未重新证明历史服务停止状态。
- 交接：Human Owner final acceptance 已按授权代录完成；协调者可据本 checklist 机械同步本任务六份索引。历史 `qa_passed` 仍为独立 QA verdict；`owner_accepted` 记录的是 Human Owner 的最终决定。
