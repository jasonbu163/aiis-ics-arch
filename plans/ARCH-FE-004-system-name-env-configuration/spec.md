Task ID: ARCH-FE-004
Revision: r3
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已于 2026-10-10 明确批准 ARCH-FE-004 r3；交 Development 按冻结的 r3 allowlist 实施，保留 r1/r2 历史，developer_handoff 后交 fresh-context Verification

Task Namespace: aiis-ics-arch
Classification: root
Capability: 前端构建期双语系统名称与可选登录描述配置
Owner: frontend-js Core 模板
Related Task: ARCH-FE-002
Acceptance Chain Reference: ARCH-FE-004 PM spec -> Human Owner exact Revision approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance
Workflow Mode: STD
Execution Mode: agent_team_same_session
Created: 2026-10-09
Updated: 2026-10-10

# 系统名称与可选登录描述配置

## 1. 当前依据与 r3 增量

公司/组织标识沿用 Logo。r1 已实现双语系统名称、登录页三处同源文本及浏览器标题同步；
独立 Verification 首轮因 tasks 的 Handoff 元数据缺项记录 qa_failed，文档返工复验后为
qa_passed，Human Owner 最终验收尚未发生。完整实施与 QA 历史保留在现有 tasks.md、checklist.md。

r2 已实现独立双语 hero 小标题及空值隐藏，右侧登录框和浏览器标题继续使用系统名称；
[tasks.md](tasks.md) 保留 r1/r2 实施与 demo 注释补充，[checklist.md](checklist.md) 保留 r1
失败/复验及 r2 独立通过记录（25 项测试、四组隔离构建、40 个浏览器场景和后续注释静态复核）。
这些是既有 Revision 的历史证据，不是 r3 verdict；Human Owner 最终验收仍未发生。

Human Owner 现要求 example 直接给活动 demo 配置、英文说明与其一致，实际两个 env 也保留新增字段，
允许可选值为空，并补充双语 README。当前两 examples 已由用户改为唯一活动 demo 值；
`.env.example` 仍有去除 `#` 的过时说明。两实际 env 仅缺两 subtitle key，现有名称与其他值须保留。
r3 仅修订配置维护与文档范围：替代 r2 的 example 空默认及禁止真实 env 写入约束，R1/R2 功能合同不变。
本次 PM 仅写 spec；tasks/checklist 当前仍为 r2，待精确 r3 获批及对应角色接手后再推进。

## 2. 需求

### R1：系统名称沿用 r1

- `VITE_SYSTEM_NAME_ZH_CN` / `VITE_SYSTEM_NAME_EN_US` 分别控制 `zh-CN` / `en-US` 的
  `common.systemTitle`。trim 后为空或缺失时，使用对应语言原有默认 `AIIS ICS Architecture`；
  两语言独立，不借用另一语言的配置。
- 登录左侧大标题、右侧登录框 caption、所有现有 Logo alt 与浏览器标题继续消费
  `common.systemTitle`。不把描述拼入标题，不新增登录后名称区域或页面标题系统。
- 静态 HTML title 保留 `AIIS ICS Architecture`；应用初始化后按现有 localStorage locale
  或默认 zh-CN 同步 document.title，随语言切换、持久化语言刷新、登录/退出与导航保持有效。
  允许 JS 初始化前短暂显示静态默认；既有语言选择及 i18n fallback 规则不变。

### R2：可选双语登录描述

可选、公开构建期配置的源码与独立 Dockerfile 默认均为空；example 的活动 demo 值见 R3：

```dotenv
VITE_SYSTEM_SUBTITLE_ZH_CN=""
VITE_SYSTEM_SUBTITLE_EN_US=""
```

- 两项分别对应中文/英文，唯一显示位置为登录左侧 hero 大标题下的现有小标题。
- 值去除首尾空白，内部空格、标点和 `@ { } | < >` 等字符按普通文本保留；
  不解释为翻译表达式或 HTML，不自动翻译或改写。系统名称继续遵循同样的纯文本约束。
- 当前语言的配置缺失、空字符串或纯空白时，该语言的整行小标题隐藏，连同该行附带的间距。
  两语言独立；不回退到另一语言描述、系统名称、默认宣传语或 i18n key 字面量。
- 恢复独立 i18n 入口 `login.subtitle`，两语言 locale 默认均为 `""`。
  env 在现有全局 i18n 配置接入；组件只消费该 key 及其是否为空，不直接读取 env。
  空描述必须保持为空，不能被全局语言 fallback 补成另一语言内容。
- 仅调整该行文本及显示条件；保留现有登录结构、字号和其他间距，允许移除被隐藏行自身占位。
  不新增描述编辑界面，不改 Logo 文件、自然比例、对齐、光晕或认证壳布局。

### R3：配置与交付

- 宿主机 dev/build 继续共用 `frontend-js/.env`；Docker dev 沿用
  `frontend-js/.env.docker.dev`。Vite 文件/进程变量优先级不变，不新建配置分层。
- 两份已跟踪 example 保留用户已设的唯一活动配置，不再提供注释赋值或重复空赋值：

  ```dotenv
  VITE_SYSTEM_SUBTITLE_ZH_CN="Powered by AIIS ICS Architecture"
  VITE_SYSTEM_SUBTITLE_EN_US="Powered by AIIS ICS Architecture"
  ```

  对应字段上方的英文说明统一表达：这是可直接启用、两语言同文的登录 hero demo 署名；
  将对应值设为空即可隐藏该语言小标题。删除“remove #”等过时指引；其他活动值和注释保留。
- 两个实际 env 在已有系统名称配置之后，各补且仅补一个以下空配置块及必要英文用途说明：

  ```dotenv
  VITE_SYSTEM_SUBTITLE_ZH_CN=
  VITE_SYSTEM_SUBTITLE_EN_US=
  ```

  不替用户填入 demo、不改当前中英文系统名，不用 example 覆盖文件，不改其他值/注释/顺序。
  实际 env 继续 Git ignored，不能提交或把整文件及敏感值打印到证据中。
- 双语 README 配置说明须提供可直接复制的 example demo 与实际 env 空配置用法，明确替换同名项、
  避免重复 key；区分 example demo 默认展示与源码/独立 Dockerfile 空默认隐藏。
  在现有环境变量用途表补充名称、描述两组键并与下方配置专节一致，准确说明名称、描述和 Logo
  各自消费位置，以及逐语言 trim、名称默认回退、描述空值隐藏和 Logo 回退。
- 在双语 README 记录本前端公开配置的开发维护规则：以后新增字段时，同步维护对应 example
  与现有本地实际 env 的活动 key，并保留用户已有值；可选字段可留空且须说明空值语义，
  必填或有校验约束的字段仍需合法项目值或经批准的安全默认。该规则是开发变更时维护字段，
  不承诺运行时自动改写 env，不扩展本次 allowlist，也不追溯补既有可选 `VITE_OPEN_BROWSER`。
  改写旧“实际 env 不补项/缺少新变量”的维护叙述，保留程序运行时不自动写文件的事实。
- 说明生效时点：宿主机 dev 修改后重启 Vite；Docker dev 的 env_file 修改后须按既有流程
  重新创建相应容器以重新读取环境，单纯 restart 不重新加载容器环境；生产构建值修改后
  重新构建 dist 并按既有流程交付，单独修改 env 或重启 Nginx 不改变已有 bundle。
  本次只写配置/说明，不执行启动、重建、部署或 Docker 操作。

## 3. r3 精确未来实施 allowlist

仅在精确 r3 获批后由 Development 修改以下路径；本轮 PM 只更新本 spec。

| 路径 | 允许改动 |
| --- | --- |
| `frontend-js/.env.example`、`frontend-js/.env.docker.dev.example` | 仅同步 subtitle demo 用途/空值说明；保留用户已设的唯一活动 demo 值 |
| `frontend-js/.env`、`frontend-js/.env.docker.dev` | 仅本地补两唯一活动空 subtitle key 及必要英文说明，保持 Git ignored 与其他字节 |
| `frontend-js/README.md`、`frontend-js/README.zh-CN.md` | 同步 R3 配置、空值、维护规则与生效说明 |
| `plans/ARCH-FE-004-system-name-env-configuration/tasks.md` | 获批后记录 r3 实施、自检及 handoff，完整保留 r1/r2 历史 |

所有 Vue/helper/i18n、测试、Dockerfile/Compose、依赖/锁、CODE_INDEX 与 AGENTS 均不改。
主会话仅据角色事实机械同步根 PLAN pair、frontend-js PLAN pair 与 plans README pair 六索引；
Verification 在 r3 developer_handoff 后更新其 checklist，保留 r1/r2 历史。PM 不代写其他角色文档。
额外文件或实质合同变化须返回 PM 新 Revision。

## 4. r3 验收标准

| 编号 | 可验证结果 |
| --- | --- |
| AC1 | 两 examples 各有唯一活动中英文 subtitle key，值均为指定 Powered by 文本；英文说明相同且准确，无去 # 或重复空赋值指引 |
| AC2 | 两实际 env 各有唯一活动中英文空 subtitle key；剥除本次新增配置块后与 r3 开始前基线字节一致，现有名称和其他配置完整保留，Git ignored 状态不变 |
| AC3 | 四文件新增键集合对齐且没有重复 key；用现有 dotenv/Vite 解析或等价静态解析验证 examples 得到 demo 原文、实际 env 两值为空，只输出必要公开字段/集合或摘要 |
| AC4 | README pair 与英文注释、实际配置一致，完整说明 demo 与源码空默认差别、名称/描述/Logo 消费和空值语义、新增字段维护、已有值保全、无运行时自动同步、dev/Docker dev/生产生效时点 |
| AC5 | 本次 diff 仅在 r3 allowlist 和角色/机械索引面；源码、测试、Dockerfile/Compose、依赖及其他受保护文件摘要不变；文档本地链接与 diff 检查通过，r1/r2 历史及批准/失败/复验/QA 记录保留 |

Development 与 fresh-context Verification 各记录增量静态检查的真实命令/结果。
本轮不改运行实现，既有 r2 功能矩阵仅作保留的历史依据，不重跑构建/浏览器或无关全仓 checker，
也不把 r2 qa_passed 改写成 r3 verdict。验证不启动 Docker，不打印整份真实 env、秘密值或无关配置值。

## 5. 风险、回退与排除项

- 长名称/描述可能占用现有区域；用合理长度验收，长度限制和响应式重设计另立范围。
- 缺失描述默认隐藏，已用 r1 的项目将移除重复名称行；这是 r2 明确行为变化。
- r3 example 复制后默认显示 demo 署名；这是示例选择，不改变源码及独立 Dockerfile 空默认。
  实际 env 只补空字段，保持当前隐藏行为。复制时须替换同名字段，避免重复赋值产生歧义。
- 真实 env 仍含其他本地配置；验证只保存必要摘要或严格受控的本地基线，不提交或泄露内容。
  若用户并发修改，重新核对基线并保留其修改，不能整文件覆盖。
- r3 回退仅撤销本轮说明及新增空字段，不撤销用户已设的 example demo、当前名称或其他工作树改动；
  回退不由本 spec 自动执行。描述仍可通过清空配置并按对应入口重启/重构建隐藏。

排除 Logo/favicon/主题改造、新增登录后名称或描述 UI、页面内配置编辑、认证/权限/模块迁移、
backend/CA/Tauri、自动 env 同步器/扫描器、追溯补齐其他既有可选项、实际 env 的其他写入、
Docker up/down/build/recreate/restart、真实数据库操作、生产 dist 构建、发布/部署与 Git push。

## 6. 角色、历史与下一 gate

PM 使用 project-governance、aiis 定义范围。Development/Verification 按触达面使用
frontend-ui、i18n-workflow，env 分层和生效说明使用 docker-project-ops + docker-expert；
仅做配置/文档增量，不以这些 skill 扩大到实现或 Docker 操作。执行链仍为精确范围批准 -> Development ->
fresh-context Verification -> Human Owner 最终验收，QA 或范围批准不授权发布/部署。

| 日期 | Revision | 事实 |
| --- | --- | --- |
| 2026-10-09 | r1 | Owner 认可双语系统名称 env 方案并授权起草。 |
| 2026-10-10 | r1 | Owner 明确“批准”精确 r1；三处登录文本同用系统名已实施，QA-001 元数据返工后独立 qa_passed；最终验收未发生，tasks/checklist 与失败/复验历史保留。 |
| 2026-10-10 | r2 | Owner 认可大标题=系统名、小标题=可选独立双语描述及新增 env，授权修订 spec；本 r2 替代 r1 hero 小标题同源要求，以 draft 提交，尚未获精确 r2 开发批准、实施或 QA。 |
| 2026-10-10 | r2 | Owner 对已冻结的本 ARCH-FE-004 r2 明确回复“批准”；状态记录为 owner_approved，Revision、合同与 allowlist 不变。下一 gate 为 Development，r2 实施、独立 QA 与最终验收尚未发生。 |
| 2026-10-10 | r2 | 后续 Development 已实施，独立 Verification 记录 25 项测试、四组隔离构建、40 场景通过；demo 注释补充另经独立静态复核通过。完整事实见 tasks/checklist；Human Owner 最终验收仍待定。r2 当时要求 example 空默认及不写真实 env，两条约束由 r3 提议替代，不能倒写为旧批准范围。 |
| 2026-10-10 | r3 | Owner 要求 example 活动 demo 与准确英文说明、两实际 env 补空 subtitle 字段、后续新增配置保留实际字段，并补充相关双语 README。本 r3 据此冻结为 draft；尚未取得精确 r3 范围批准，未实施或验证 r3。 |
| 2026-10-10 | r3 | Human Owner 对已冻结并呈交的 ARCH-FE-004 r3 明确回复“批准”，由主协调转交 PM 记录；状态改为 owner_approved，Revision、合同、allowlist 和验收标准保持原样。r3 实施、独立 QA 与最终验收尚未发生。 |

下一 gate：Development 按已批准的 ARCH-FE-004 r3 及 §3 allowlist 实施，
交 fresh-context Verification 独立验证 r3，最后再交 Human Owner 最终验收。
