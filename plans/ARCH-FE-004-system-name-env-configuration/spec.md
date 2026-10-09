Task ID: ARCH-FE-004
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 审阅并批准 ARCH-FE-004 r1 范围；批准前不启动 Development

Task Namespace: aiis-ics-arch
Classification: root
Capability: 前端构建期双语系统名称配置及显示一致性
Owner: frontend-js Core 模板
Related Task: ARCH-FE-002
Acceptance Chain Reference: ARCH-FE-004 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-09
Updated: 2026-10-09

# 前端系统名称 env 配置

## 1. 目标与当前依据

公司/组织标识沿用现有 Logo 能力；系统名称保留 `common.systemTitle` 作为唯一 i18n 显示入口，
增加构建期 env 覆盖，便于使用方项目配置中文和英文名称。

当前登录页主标题与 `BrandLogo.vue` 图片 alt 已使用 `common.systemTitle`；登录页另外两处
使用 `login.subtitle`，内容同为 `AIIS ICS Architecture`。两语言 `common.json` 的默认名称及
`index.html` 的静态 title 也均为该值。目前没有应用级 `document.title` 同步。
登录后的认证壳显示 Logo 和页面面包屑，本任务不增加新的系统名称控件。

本任务独立于 ARCH-FE-002 的已接受品牌/权限范围，不继承其批准或验收；003 仍预留给剩余模块迁移。
现有工作树包含其他任务改动，Development 与 Verification 必须针对本任务增量取证并保留既有改动。

## 2. 需求

### R1：双语配置与逐语言回退

增加两项可选、公开的前端构建期配置：

```dotenv
VITE_SYSTEM_NAME_ZH_CN="AIIS ICS Architecture"
VITE_SYSTEM_NAME_EN_US="AIIS ICS Architecture"
```

- `zh-CN` 对应 `VITE_SYSTEM_NAME_ZH_CN`，`en-US` 对应 `VITE_SYSTEM_NAME_EN_US`。
- 值去除首尾空白后使用；缺失、空字符串或纯空白时，回退到对应语言现有
  `common.systemTitle` 默认值，当前两者均为 `AIIS ICS Architecture`。
- 两语言独立解析。只配置一项时，另一项使用自身默认值，不借用已配置语言的名称。
- 名称作为普通文本显示，不解释为 HTML。保留输入名称内部空格与标点，不自动翻译或改写。
- env 覆盖进入全局 i18n 的 `common.systemTitle`。UI 和浏览器标题统一消费该入口，
  不在各组件直接读取 env，不维护第二份系统名称状态或重复回退字面量。
  Registry 的模块发现、权限与 locale 装配规则保持现有合同。

### R2：现有显示面统一

- 登录主标题及目前两处 `login.subtitle` 所在文本位置，均显示当前语言的
  `common.systemTitle`；保持现有结构、字号、间距和重复显示位置。
- 两语言 `login.subtitle` 在确认没有其他消费者后同步移除，避免继续保留第二个系统名称来源。
- 登录前后所有现有 `BrandLogo` 的 alt 自动使用同一当前语言名称。沿用组件现有绑定即可，
  不修改 Logo 文件选择、对齐、光晕、尺寸或认证壳布局。
- 登录、退出和页面导航不改变系统名称；不拼接页面面包屑或页面名称到系统标题。

### R3：浏览器标签页与语言

- JavaScript 初始化前，`index.html` 保留静态默认 title `AIIS ICS Architecture`。
  初始 HTML 不读取浏览器语言存储，也不新增服务端或运行时模板替换。
- 应用初始化时，沿用现有 i18n 的语言选择：读取现有 `localStorage` 的 `locale`，
  未设置时使用 `zh-CN`。应用挂载后立即将 `document.title` 同步为有效 i18n 语言的
  `common.systemTitle`；现有 i18n fallback 规则继续有效。
- 用户切换中文/英文时，同步更新可见名称、Logo alt 和 `document.title`。
  持久化英文后刷新登录页或认证页，应恢复英文名称；首次初始化、登录成功、退出后均适用。
- 允许 JS 初始化前短暂出现静态默认标题，不承诺零闪烁，也不新增页面标题系统。

### R4：配置与交付说明

- 宿主机 dev/build 继续共用 Git 忽略的 `frontend-js/.env`；Docker dev 继续使用
  `frontend-js/.env.docker.dev`。现有 Vite 文件及进程变量优先级保持不变，不新增 env 分层。
- 只在两份已跟踪 example 中补入上述中性默认值与英文用途说明。双语前端 README
  说明变量、逐语言回退、统一消费入口、公开构建值与生效时点。
- 实际 `.env` / `.env.docker.dev` 不在本 r1 写入范围内：不自动补项、不复制 example 覆盖，
  其他活动值保持不变。已有文件没有新变量时，由 R1 回退保持当前名称；使用方可自行添加项目名称。
- 独立 `frontend-js/Dockerfile` 未复制实际 env，以两项新增 ARG/ENV 将名称传入构建阶段，
  中性默认与 example 一致。仅补两变量，不改变镜像、依赖、构建步骤和 Nginx runtime。
  Docker dev 已通过 `env_file` 提供进程变量，无需改 Dockerfile.dev 或 Compose。
- 修改配置后，dev 需要重启；生产需要重新构建 `dist` 并按既有流程交付。
  修改 env 或单独重启 Nginx 不会改变现有静态产物。生产仍使用宿主机预构建 dist，
  不引入运行时配置接口、配置文件注入或后台编辑界面。

## 3. 精确未来实施 allowlist

以下是批准 r1 后 Development 可修改的路径及用途；本次 PM 只写本 `spec.md`。

| 路径 | 允许改动 |
| --- | --- |
| `frontend-js/src/locales/index.js` | 将两语言名称配置接入全局 `common.systemTitle`，保留现有语言与 Registry 合同 |
| `frontend-js/src/config/systemName.js`（按需新增） | 最小名称解析 helper，便于验证 trim、独立默认与纯文本规则；不建立通用品牌框架 |
| `frontend-js/src/pages/login/index.vue` | 仅统一两处重复系统名称的 i18n key |
| `frontend-js/src/locales/zh-CN/login.json`、`frontend-js/src/locales/en-US/login.json` | 仅对称移除不再消费的 `subtitle` |
| `frontend-js/src/App.vue` | 应用级首次及语言变化时的 `document.title` 同步 |
| `frontend-js/.env.example`、`frontend-js/.env.docker.dev.example` | 仅新增两名称变量与英文说明 |
| `frontend-js/Dockerfile` | 仅新增两名称变量的构建 ARG/ENV |
| `frontend-js/README.md`、`frontend-js/README.zh-CN.md` | 同步稳定配置合同与生效说明 |
| `frontend-js/tests/module-registry/system-name.test.mjs`（按需新增） | 名称解析、逐语言回退及 i18n 接入的有意义合同测试，复用现有 Node test 入口 |
| `CODE_INDEX.md` | 仅在新增 helper/测试或职责描述实际变化时维护对应条目 |
| `plans/ARCH-FE-004-system-name-env-configuration/tasks.md` | Development 在获批后创建实施记录与 self-check、handoff |

`index.html`、两语言 `common.json`、`BrandLogo.vue`、`MainLayout.vue` 是回归读取面，
无需为保留现有默认/绑定而修改。若实现确实需要额外路径、依赖、测试入口或实质变更验收合同，
应先返回 PM 新 Revision，不静默扩大 allowlist。

主会话按本 spec 机械同步根 PLAN pair、frontend-js PLAN pair 与 plans README pair；
这些索引只反映真实状态，不替代角色文档。Verification 仅在 `developer_handoff` 后创建本任务
`checklist.md`，记录 fresh-context 验证与 verdict。

## 4. 验收标准

| 编号 | 可验证结果 |
| --- | --- |
| AC1 | 双语 env 各有非空不同名称时，trim 后分别进入 `common.systemTitle`，切换语言显示对应名称；内部空格和普通标点保持原值 |
| AC2 | 分别覆盖两项缺失、空值、纯空白、仅一项有效的情况；每种语言独立回退到自身现有默认，没有空标题或借用另一语言配置 |
| AC3 | 登录页三处现有名称与所有现有 Logo alt 均来自 `common.systemTitle`；`login.subtitle` 无残留消费者，双语 locale key 对称 |
| AC4 | 静态 HTML 默认 title 保留；应用挂载后、中文/英文切换、持久化语言刷新、登录前后及退出后的 `document.title` 均满足 R3，不被路由覆盖 |
| AC5 | 两 examples、Dockerfile 构建传值与双语 README 一致；实际 env 没有被本任务改写，其他权限/API/mock/品牌值不因本任务变化 |
| AC6 | Logo 自然比例/对齐/光晕及认证壳结构无回归；名称使用现有文本区域，不新增登录后系统名称 UI |
| AC7 | 现有模块检查与测试、隔离输出构建通过；变更文件链接与 diff 检查通过；没有修改依赖/锁文件、客户资产、真实 env 或产物 |

Development 记录实际命令、结果和环境限制，至少覆盖 `pnpm check:modules`、`pnpm test:modules`
及输出到 `/private/tmp` 的生产构建。名称边界用公开 fixture 验证，不为简单 UI 文本创建
镜像实现的测试；登录页和认证壳的语言/标签页行为用隔离浏览器 fixture 检查，fixture 不接真实
backend、不写真实数据库，也不算真实认证链路证明。必要的静态 Dockerfile 传值审查不等于镜像运行。

## 5. 风险、回退与排除项

- 过长名称可能占用现有文本区域；本任务保留当前布局，使用合理长度中性名称验收。
  若需调整响应式布局或新增名称长度策略，应另行澄清范围。
- 配置未重启 dev 或未重建 dist 会继续显示旧值；README 必须明确交付时点。
- 静态默认标题在 JS 初始化前可见，属于 R3 明示限制。
- 回退优先通过删除/留空两配置并重新构建恢复既有默认；源码回退只针对本任务增量，
  不回退 ARCH-FE-002 或其他工作树改动。

排除运行时品牌管理、favicon/Logo/布局改造、新增登录后名称区域、登录认证/权限变更、
模块迁移、backend/CA/Tauri 配置、真实 env 修改、Docker up/down/build、真实数据库操作、
发布/部署与 Git/GitHub push。后三类外部动作按根契约另需具体授权。

## 6. 角色 handoff 与批准历史

PM 依据 `project-governance` 和 `aiis` 沉淀范围。Development 与 Verification 按实际触达面
加载 `frontend-ui`、`i18n-workflow`；Dockerfile 构建传值加载 `docker-project-ops` 与
`docker-expert`；涉及文件头/代码索引时加载 `code-document-indexer`。PM 不替这些角色实施或验证。

| 日期 | Revision | 事实与下一 gate |
| --- | --- | --- |
| 2026-10-09 | r1 | Human Owner 确认公司/组织标识使用 Logo，认可双语系统名称 env 方案并授权“可以落 spec”；该授权是起草授权。当前精确 r1 为 draft，等待 Human Owner 范围批准；Development、独立 Verification 和最终验收尚未发生。 |

无待决设计问题。下一步是 Human Owner 批准 `ARCH-FE-004 r1`；批准后由 Development 创建
`tasks.md` 并实施，完成 `developer_handoff` 后由 fresh-context Verification 创建 `checklist.md`。
QA 通过后再交 Human Owner 最终验收。批准、QA 和验收均不自动授权发布或部署。
