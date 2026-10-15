# ARCH-MULTI-001 三界发展蓝本与双语 ROADMAP

Task ID: ARCH-MULTI-001
Revision: r2
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准此前明示以 ARCH-MULTI-001 r2 承接的双语 ROADMAP 文档范围；交 Development 创建两份 ROADMAP 与 tasks.md，代码与运行实施另行立项

Task Namespace: aiis-ics-arch
Classification: root
Capability: 将 PW / AW / AIW 发展方向、近期双 Tauri Agent 形态与分阶段准入条件固定为双语长期 ROADMAP
Owner: AIIS ICS Architecture Core
Acceptance Chain Reference: 本 spec r2 -> Human Owner 精确范围批准 -> Development 文档交付与 tasks.md -> fresh-context Verification checklist.md -> Human Owner final acceptance；各路线实施任务另行批准
Workflow Mode: STD
Execution Mode: agent_team_same_session
Related Task: ARCH-BE-003, CA-CONFIG-001, ARCH-BE-002
Created: 2026-09-08
Updated: 2026-10-13

## 1. 本轮目标、依据与批准边界

本轮只交付根目录 `ROADMAP.md` / `ROADMAP.zh-CN.md`。蓝本整理已讨论的三界职责、近期两个完整 Tauri Agent、共享 UI、AW 表命名、CA/TSS 复用和阶段推进条件。文档完成不代表任何阶段代码、表结构、目录迁移、构建或现场链路已经实现。

Human Owner 于 2026-10-13 的原文：

> 可以，就按这个方案。先写好 ROADMAP.md 和 ROADMAP.zh-CN.md，把三界路线、近期两个完整 Tauri Agent、共享 UI、aw_ 表前缀和 CA/TSS 复用方案明确下来，分阶段推进，暂时不要改代码。

本会话此前已向 Human Owner 明示“现有 ARCH-MULTI-001 草案可以通过 r2 承接这次调整，保留旧路线的修订记录”；随后两个完整 Tauri Agent、共享 UI 与构建边界逐项澄清，本轮原文明确批准“按这个方案”交付指定两份 ROADMAP。r2 据此固定此前已展示且获批的文档范围，不加入代码、目录迁移、数据库或运行实施，也不声称 Human Owner 曾逐字给出 Task ID / Revision。`owner_approved` 仅表示本轮双语文档范围已批准；文档独立 QA 与 Human Owner 最终验收仍待发生。

r2 将未来路线从 r1 的“按 v1/v2 默认值切换多种可互换后端”更新为“三界按职责演进”。r1 全文保存在本文件历史附录中，其日期、状态、当时方向和未实施事实均保持原样；不得将历史方向表述改写为已经实现。r1 的版本默认值、数据库兼容矩阵、Ant Design Vue 迁移和旧目录建议不再作为本轮未来路线的执行要求；若仍有实际需求，另立精确任务。

## 2. 当前基线与文档职责

当前仓库保留 `backend/` FastAPI/SQLAlchemy/Alembic、`frontend-js/` Vue JavaScript 前端和 `control-agent/` Rust/Tauri 采集应用。CA 既有链路采集并解码 PLC，直接写后端 raw/latest 快照，再由后端 Projection 框架解析输入、调用业务 Handler。此说明是当前源码职责，不宣称真实 PLC 链路正在运行或任一客户 Handler 已包含在公开模板。

DTB 的 `twin-state-studio/`（TSS）是来源工程，已有事实读取、目标 API 参数绑定与值规则、映射执行、租约和回执功能，但未迁入本仓库成为 SMA。拟议 `automation-world/` 目录、两个新 Agent、共享 UI 和 `aw_*` 表均属于目标形态；本轮不创建它们。

| 文档 | 权威职责 |
| --- | --- |
| `README.*` | 当前项目身份、现有源码结构与运行入口；本轮不修改，不把目标结构画成当前结构 |
| `ROADMAP.*` | 长期职责蓝本、当前到目标的演进阶段、阶段准入与完成条件 |
| `PLAN.*` | 当前任务状态、验证摘要、下一 gate 与任务入口 |
| `plans/<task>/spec.md` | 某个文档或实施任务的精确范围、验收、风险和批准历史 |
| `tasks.md` / `checklist.md` | 实际实施自检 / 独立验证事实；只在对应角色 gate 后创建 |

未来路线图与当前工作树、既有任务状态必须区分。`ROADMAP.*` 不承载每个在途任务的动态状态，也不将路线认可替代实施批准。

## 3. 本轮写入 allowlist 与排除范围

### 3.1 角色写入边界

| 执行者 | 允许写入 | 限制 |
| --- | --- | --- |
| PM | `plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md` | 仅本 r2 规格及其真实批准历史；完整保留 r1 |
| Development | `ROADMAP.md`、`ROADMAP.zh-CN.md`，以及本任务 `tasks.md` | 只创建两份 ROADMAP 正文与本角色记录，不修改 README 或其他文档 |
| fresh-context Verification（developer_handoff 后） | 本任务 `checklist.md` | 验证 r2、文档与 diff，不修复正文、不授予最终验收 |
| 主协调者 | 根 `PLAN.md` / `PLAN.zh-CN.md`、`plans/README.md` / `plans/README.zh-CN.md` | 仅机械同步 ARCH-MULTI-001 行、真实存在的角色文件及其 gate，不改其他任务行 |

根 README pair 的路线入口改动不纳入本轮。各角色不得互写权威文档；上述是合同控制，不宣称平台 ACL 或强制路由。

### 3.2 本轮明确排除

- 不修改实现源码、测试、依赖、锁文件、Vite/Tauri/Cargo/Compose 配置、env、权限配置、迁移或数据库。
- 不创建或迁移 `automation-world/`、DAA、SMA、shared；不复制 DTB 代码或数据，不删除/重命名现有 `control-agent/`。
- 不实现业务接口、事实/配置 API、`aw_*` 表、SQLite、本地队列、独立服务、AWB、.NET PW 或 AIW。
- 不运行应用构建、Docker、数据库迁移、真实 PLC/现场操作，不创建/发布 Git refs 或执行 Git/GitHub 推送。
- 不修改 AGENTS、CODE_INDEX、根及模块 README、模块 PLAN、公开 contracts 或其他任务 bundle；现有能源价格等 dirty 文件不得覆盖、回退或计入本任务成果。
- 不批量纠正其他任务状态，不预先创建角色证据，不把未来阶段标为已完成。

## 4. 双语 ROADMAP 必须表达的需求

### R1：三界职责与技术路线

1. PW 负责业务模型、用户权限、业务规则、事务和业务 API。当前 FastAPI 继续承担现有 PW 业务，未来目标为 C#/.NET/ASP.NET Core + FastEndpoints；不得因现有代码使用 Python 就把业务职责自动归为 AIW。
2. AIW 以 Python/FastAPI 承担模型、分析、推理和建议；其输出需要由 PW 的业务规则与授权决定如何采用，不能直接取得现场动作权。
3. AW 以 Rust 承担采集、现场事实、语义映射及后续按需归档/受控执行。近期优先复用已有 CA 和 TSS；AWB/Axum 延后，当前 FastAPI 暂时提供 AW 的配置、最新事实和运行管理接口。
4. 三界首先是职责边界，不强制对应三个仓库、全部独立部署或立刻切换技术栈。保持当前稳定基线，每个实施阶段另有范围、验证和最终验收。
5. 后续真正的现场写入/控制、AWB、数据库更换、PW 技术栈迁移均为单独准入的未来工作；不恢复当前项目禁止的 Celery/Redis/旧工业命令合同。

### R2：近期两个完整 Tauri Agent 与命名

目标目录使用全称，讨论、日志角色标识使用 AW/AWC/DAA/SMA 缩写：

```text
automation-world/
├── data-acquisition-agent/    # DAA，CA 演进而来
├── semantic-mapping-agent/    # SMA，DTB TSS 演进而来
└── shared/
    └── console-ui/           # CA 风格的共用布局、主题与通用组件
```

两 Agent 均是完整的 Tauri 2 + Vue 3/TypeScript 工程，近期 Runtime 与 UI 同应用运行，各自拥有 `package.json`、前端锁文件、`index.html`、Vite/TS 配置、`src/`，以及 `src-tauri/` 下的 Cargo 清单与锁文件、`build.rs`、Tauri 配置、capabilities、icons 和 Rust `src/`。两者分别设置应用 identifier、开发端口和本地配置目录，可独立构建与交付。

DAA 管采集、PLC 解码、事实上传、配置应用与采集诊断；SMA 管事实绑定、目标 API、请求组装、映射调度及结果诊断。AWC 近期指两应用共同使用的控制台形态与交互规范，不新增第三个独立 AWC 应用。页面和运行状态留在各 Agent，不设计完整 AWC SDK。

Runtime 仍按 Rust Domain/Service/Infrastructure/Tauri adapter 分层；采集/映射生命周期不依赖 Vue 组件挂载。窗口关闭、后台运行和显式退出行为在实施规格中确定；未来提取无界面 Runtime 或集中 AWC 仍需适配入口、通信和进程管理，不宣称 Tauri 会自动完成拆分。

### R3：共享 UI 与构建/交付边界

1. 以当前 CA 的视觉壳、导航、主题与控件风格为准。共享范围限实际相同的布局、主题和通用组件；DAA/SMA 专有页面、状态、API 业务逻辑和 Runtime 不放入 shared。
2. 共享源码经 Vite 正常引用，各自构建进本应用 `dist`；Tauri 继续打包各自前端产物。安装后的 UI 无需外部 shared 目录。
3. 重新构建依赖本地 shared 源码；单独复制一个 Agent 目录而遗漏 shared 并不是自包含源码交付。应保留两个完整工程与明确依赖关系，不能把“完整 Tauri 工程”误写为“无任何共享源码依赖”。
4. 实施任务需要解决 Vite/TypeScript 解析、Vue/Element Plus 依赖一致性、各自 `frontendDist` 和开发端口；分别验证前端构建、Tauri 打包和安装启动。当前文档不能宣称这些构建已通过。

### R4：CA/TSS 复用与公开仓适配

1. CA -> DAA：保留成熟的 PLC 读取、解码、采集循环、诊断和日志；演进重点是通过后端 API 获取发布配置、通过事实 API 写入采集结果。
2. TSS -> SMA：复用纯 Rust 映射 Domain、Runtime 调度、事实/目标接口/参数绑定和值规则、编辑及诊断功能；保留功能逻辑，按 CA 视觉壳统一 UI。TSS 现有 Tauri 生命周期、网络与后端依赖需明确适配。
3. DTB 的通用后端事实、配置、执行租约与回执 API 也属于可复用来源；仅复制桌面目录不构成完整可运行 SMA。后端代码需要按本仓库 MySQL、模块 Registry/manifest、认证权限、响应和显式 Alembic 迁移适配。
4. DTB 的 MSSQL/ROWVERSION 等数据库专有机制不能直接套入 MySQL；既有来源迁移文件不能作为本仓库现成迁移。公开基线只接纳可复用能力与脱敏示例，保留来源追踪和适用许可；客户页面、真实配置、业务数据、资源及 legacy 直连写业务表路径不随复制进入新 AW 边界。
5. 当前 CA 直接数据库快照链路和后端 Projection 在新路径切换前作为明确的兼容/回退路径；新 DAA 不继续依赖直接写业务数据库，SMA 通过业务 API 写入。

### R5：配置、事实、业务数据归属与 `aw_` 前缀

1. 近期由现有 FastAPI 与后端数据库集中保存 AW 配置和最新事实，面向 DAA/SMA 提供 API；未来 AWB 可承接这组能力。表名前缀统一为 `aw_`，示例可包含 `aw_collection_configs`、`aw_collection_facts`、`aw_target_apis`、`aw_mapping_configs`、映射 Runtime 与 Agent 状态表，但示例不等于本轮最终 schema。
2. 只有 AW 拥有的配置、事实、映射及运行表使用该前缀。订单、设备业务状态、采样业务记录等业务表保留各业务 Owner；“被映射引用”不是表改归 AW 的理由。前缀是归属标记，不等于数据库隔离、权限隔离或已经完成 AW 拆分。
3. 采集配置同时覆盖 `plc_points.yaml` 中的连接、DB-block、类型、offset/bit 等定义，以及 `plc_snapshot_policy.yaml` 的 raw/latest 保存策略，不能只迁后一份。配置需要校验、版本发布、Agent 下载/应用及实际应用版本回报，细节留给实施合同。
4. 最新事实参考 `(sourceKey, factName)` 身份，同时明确来源/Agent 标识、稳定采样 ID 或序列、采集时间、接收时间、quality、点位合同版本和映射版本的责任。字段精确命名、批量原子性、鉴权、幂等与版本机制在 API/schema 任务中锁定。
5. latest 服务于当前状态，不能证明期间所有变化都被消费；需要逐条处理的事件、追加记录与历史归档分别设计。坏质量、缺失、过期和乱序数据必须有策略，避免将最后一个值长期当有效输入。
6. 本机完整 SQLite 事实引擎不是近期强制前置；持久缓冲/outbox、离线补传和配置快照按现场可靠性要求在后续精确阶段纳入。配置回滚不得删除运行记录、待发送记录或消费游标。

### R6：数据流、业务 API 与执行安全条件

当前链路和目标链路都须在 ROADMAP 中清楚标注。近期目标为：

```text
PLC -> DAA 采集/解码 -> FastAPI AW 事实 API / aw_* 最新事实
    -> SMA 事实绑定/校验/组包 -> PW 业务 API -> 业务 Service / 业务表
AWC（分别内嵌于 DAA/SMA）-> FastAPI AW 配置与运行管理 -> 各 Agent
```

业务 API 接收设备/业务身份、测量值、时间、事件等语义数据，业务 Service 不依赖 PLC DB 编号、offset、bit 或原始点名；来源信息可保留用于追踪。现场转换和参数组装归 SMA，订单/业务状态流转及业务事务留在 PW。

先冻结配置、事实、映射/回执合同和一个实际业务 API 试点；无需先实现被盘点的全部八个 Handler API。冻结合同后，后端与两个 Agent 的实现可并行，但闭环验证以真实可调用接口为准。ARCH-BE-003 当前草案需要按目标项目、采样身份、幂等与权限独立修订；CA-CONFIG-001 按新的 API 配置来源独立重审。本轮不修改它们。ARCH-BE-002 能源价格是独立公共能力，不是采样试点的前置依赖。

TSS 当前每周期重新读取绑定事实，相同值仍周期发送；结果不确定或失败时不自动重放。该行为不等于可靠离线投递。追加型业务接口必须定义稳定幂等键、事务内业务写入与回执、成功确认及重试/人工恢复边界；租约不得误称为跨 Mapping 的业务目标冲突仲裁。

新旧链路先比较结果，再按来源/目标切换。同一业务目标必须只有一个有效写入方；停用对应旧 Projection 后才启用 SMA 生产写入，并明确游标/采样身份、回退和重复消费边界。此处是未来实施准入条件，不是本轮现场切换授权。

### R7：能力阶段、依赖与完成条件

阶段是能力里程碑，不等于版本号、发布日期、已批准实施任务或完成承诺。ROADMAP 至少给出下列顺序与每阶段可检查结果：

| 阶段 | 范围 | 准入与完成条件 |
| --- | --- | --- |
| S0 文档基线 | 本轮三界蓝本、当前/目标区分、复用与命名边界 | 双语内容、路径与链接一致；独立文档 QA；Human Owner 最终验收 |
| S1 接口合同与单业务试点 | 采集配置、事实读写、映射/回执及一个 PW 业务 API | 明确目标项目/业务 Owner、样本身份、quality/time/version、权限和幂等；接口与迁移在独立实施任务验证 |
| S2 双 Tauri Agent 与最小闭环 | CA→DAA、TSS→SMA、CA 风格 shared UI；后端暂承 AW | 冻结 S1 合同后可并行开发；两应用分别构建/打包/启动；脱敏夹具完成 PLC/采集输入→事实→映射→业务 API 链路；切换前单一写入方与回退明确 |
| S3 现场可靠性与交付 | 配置应用/回退、质量与陈旧判断、资源/容量、持久缓冲和恢复、安装运行维护 | 按现场需求明确有界存储、断线/重启、重复/乱序、失败恢复与日志；真实 PLC、长期运行与现场部署单独获批并留证，不以短时 smoke 代替 |
| S4 按需三界承接 | AWB/Axum、独立 Rust Runtime 与统一 AWC、PW .NET/FastEndpoints、AIW Python/FastAPI | 基于项目需要分别立项；稳定合同与唯一数据/业务写入责任；逐模块等价/差异验证、迁移与回退；不是前期交付必需条件 |

S4 中 PW、AW、AIW 的独立能力可按需求分别推进，不要求一次性全迁；新组件的精确框架/驱动/版本、数据库支持组合、目录/部署形式和工期在对应任务中验证与批准。

### R8：双语与可追溯性

1. 英文 `ROADMAP.md` 与中文 `ROADMAP.zh-CN.md` 互链，章节、职责、技术栈、目录树、阶段与限制语义一致；英文是主文档，中文是配套版本。
2. 使用仓库相对链接连接根 README/PLAN、本 owning spec 及确有必要的既有任务，不链接尚未创建的目标目录或角色文件。未来目录仅展示为目标树/文本。
3. CA 来源可相对链接当前仓库文件；TSS 来源用项目名与来源相对路径说明，不在公开 ROADMAP 中写用户本机绝对路径或依赖不可移植的相邻 checkout 链接。保留其为外部来源、尚待复制适配的事实。
4. ROADMAP 不重复完整 3MD、权限清单或技术细节，不制造另一套执行真相源。阶段只规定目标、依赖、验收门槛与延后边界。

### R9：ROADMAP 章节骨架与批准对应关系

两份文档使用对应章节，允许为可读性微调标题，但不得删减下列内容或增加实施范围：

1. 定位、当前基线与演进原则。
2. PW / AW / AIW 的目标职责与技术栈。
3. 当前 PLC 链路、近期事实到业务 API 链路与配置流。
4. 两个完整 Tauri Agent、AWC 共同形态及全称目录结构。
5. shared UI 的边界、构建输入与独立交付。
6. CA/TSS 复用、数据库与公开仓适配。
7. 配置、事实、业务数据归属与 `aw_` 命名。
8. S0–S4 阶段目标、依赖、完成条件及迁移/回退。
9. 延后能力、待实施合同与既有任务衔接。

| Human Owner 已展示并同意的内容 | 本 r2 固定内容 | 本轮交付 |
| --- | --- | --- |
| 三界路线与当前稳定版本小步推进 | R1、R6、R7 | 职责蓝本和阶段条件 |
| 两个完整 Tauri Agent、Runtime/UI 同应用及全称目录 | R2 | 目标结构与生命周期边界 |
| shared 前端 UI、分别 build、安装后无需 shared | R3 | 构建与安装边界说明 |
| 以 CA 风格为准，CA→DAA、TSS→SMA | R4 | 复用清单、来源及适配限制 |
| 配置/事实先存后端，表名以 AW 开头 | R5 | `aw_` 归属规则及数据职责 |
| 先写双语 ROADMAP，暂时不改代码 | R8、§3 | 只创建两份文档，未来实现另行批准 |

## 5. 本轮文档验收标准

| 编号 | 验收条件 | 对应要求 |
| --- | --- | --- |
| AC1 | 双语 ROADMAP 存在且互链，章节/表格/阶段语义对称；两份根 README 均保持接手时内容 | R8 |
| AC2 | PW 当前 FastAPI 业务过渡、未来 .NET/FastEndpoints，AIW Python/FastAPI，AW Rust 与 AWB 延后的职责准确 | R1 |
| AC3 | 两个完整 Tauri 工程、Runtime+UI 同应用、正式全称路径、AWC 共同形态及后期拆分边界清楚 | R2 |
| AC4 | shared 只含通用 UI；各自 dist/打包；构建依赖 shared、安装后不依赖外部 shared；专有状态独立 | R3 |
| AC5 | CA/TSS 与通用后端的复用范围、当前/未来区分、MySQL/Registry/权限适配、来源与客户/legacy 排除完整 | R4 |
| AC6 | `aw_` 仅标记 AW Owner；两份 YAML 均覆盖；配置版本、事实质量/身份/时间、latest 与 events 区别清楚 | R5 |
| AC7 | 业务 API 语义、单试点与合同先行、TSS 实际发送/失败行为、幂等回执、单写入方切换与回退条件清楚 | R6 |
| AC8 | S0–S4 每阶段有目标、依赖与可验证完成条件；无日期/版本绑定或未来实施已获批/已完成的暗示 | R7 |
| AC9 | r1 原文完整保留、用户原话与此前明示 r2 的批准对应关系如实记录；无本轮范围之外写入 | §1、§3 |
| AC10 | 文档相对链接和配对入口有效；仅同步本任务索引行；dirty 工作树其他内容保留；开发自检与独立 QA 分开记录 | R8、§3 |

文档任务验证限 Markdown 结构、双语语义、相对链接、Task ID/Revision 与 diff/allowlist 审计；不要求运行应用测试、Tauri 构建或真实环境验证。未来阶段构建/运行条件应明确为后续验收，不可拿本轮文档检查代替。

## 6. 风险、兼容与回退

- 风险：将讨论建议误写成当前源码、支持矩阵或版本承诺。处理：分开“当前基线/近期目标/远期按需”，保留 r1 历史并标明未来路线已更新。
- 风险：共享 UI 的源码依赖被漏交付，或两应用被误认为单目录完全自包含。处理：明确构建输入与安装包边界，构建/依赖细节交独立实施验证。
- 风险：复制 TSS 时引入 MSSQL 专有行为、客户资源或旧直连业务写入。处理：仅复用通用能力，保留来源，适配本仓库接口与数据库合同。
- 风险：latest 轮询丢失期间事件、同值周期请求生成重复业务记录、旧 Projection 与 SMA 同时写。处理：在后续准入明确事件身份、幂等确认、影子比对、单一写入方与回退。
- 风险：本轮工作树已有能源价格实现、多个 dirty 文档及 BE003/BE004 草案。处理：以接手时快照和窄 diff 审计保护其他工作，不覆盖、不回退、不变更他人任务状态。
- 本轮回退仅是文档修改恢复，需保留 r1 历史、其他 dirty 内容及真实角色证据；不得据文档回退触发源码、数据库、现场或 Git ref 回退。

## 7. Skill 路由与角色交接

本 PM 使用 `aiis`（含 BLUEPRINT/CONTRACTS）与 `project-governance`（含文档职责/讨论沉淀参考），只写本 `spec.md`。

文档 Development/Verification 按范围使用 `aiis`、`project-governance`，核对当前源码和来源文档，不替后续任务实现技术工作。后续真正落地时在各自实施 spec 加载：后端 API/schema 用 `backend-arch`；Rust Agent 用 `rust-runtime`；桌面工程/打包用 `desktop-tauri`；Vue UI 用 `frontend-ui`；用户文案用 `i18n-workflow`；PLC 点表用 `plc-point-mapping`；源码结构索引用 `code-document-indexer`；必要血缘核对用 `interface-lineage-audit`。本轮不因提到未来技术而加载并执行这些实施 skill。

交接顺序：

1. PM 交付本 owner_approved r2 与精确 allowlist/验收，并如实保存已展示方案与用户本轮批准原文的对应关系。
2. Development 完整读取 bundle、创建 `tasks.md`，仅实施两份 ROADMAP 文档 allowlist；发现实质新增范围则返回 PM 新 Revision 与 Human Owner 批准。
3. Development 记录真实自检、变更列表和 `developer_handoff`；主协调者启动 fresh-context Verification。
4. Verification 只在 `checklist.md` 记录独立结果；Human Owner 最终验收仍独立保留。
5. 主协调者仅凭已存在的角色事实同步本任务索引，不能把 S1–S4 规划变成实施批准。

## 8. 决策与 Revision 历史

- 2026-09-08 r1：记录当时 v1/v2 多后端及数据库/UI 目标；仅有 PM 路线 spec，无 Development/Verification。
- 2026-10-13 r2：根据本会话三界、双完整 Tauri Agent、共享 CA 风格 UI、`aw_` 与 CA/TSS 复用讨论，以及用户明确文档请求，固定本轮仅文档规格。此前已向 Owner 明示通过 r2 承接，该文档方案经本轮原文明确批准，故记录 owner_approved；r1 全文附后，不伪称用户逐字给出编号，不倒填最终验收。后续实施必须独立立项。

## 附录：r1 原文（历史依据，完整保留）

以下 fenced 内容为接手时原始 r1 全文，逐字保留；其中历史元数据与写入范围均不作为 r2 的当前授权。

<!-- BEGIN ARCH-MULTI-001 r1 ORIGINAL -->
```text
# ARCH-MULTI-001 v1/v2 技术栈与多后端路线

Task ID: ARCH-MULTI-001
Revision: r1
Status: draft
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: 路线决策已记录；后续实施需拆分精确范围并批准对应 Revision

Task Namespace: aiis-ics-arch
Classification: root
Capability: v1/v2 技术栈、可选后端和数据库支持路线
Owner: AIIS ICS Architecture Core
Acceptance Chain Reference: 本路线 spec -> 各实施任务精确 Revision 批准 -> Development -> fresh-context Verification -> Human Owner final acceptance -> 独立发布任务
Execution Mode: agent_team_same_session
Created: 2026-09-08
Updated: 2026-09-08

## 1. 决策来源与状态

Human Owner 于 2026-09-08 明确：部分服务器不方便部署 Docker，因此 .NET 后端必须在 v1 系列开发并发布，不推迟到 v2；v2 默认后端改为 Rust，默认数据库改为 PostgreSQL。
背景来自任务“方案-v2路线”（Codex task ID `01a07aa3-1702-71a3-a544-06bca676ab3c`）和本次路线确认。

本文件承接已明确的产品方向，不把方向确认等同于全部实现细节、QA 或发布授权。`draft` 表示实施范围尚待细化，不表示 .NET 所属版本仍未决定。当前 `v1.0.0` 保持不变；v1 指后续 1.x 系列。

## 2. 目标技术栈

| 层面 | v1 系列目标 | v2 系列目标 |
| --- | --- | --- |
| Web 前端 | Vue 3 + JavaScript + Element Plus + Vite | Vue 3 + TypeScript + Ant Design Vue + Vite |
| Web 配套 | Vue Router、Pinia、Axios、Vue I18n、ECharts；pnpm | 延续路由、状态、请求、国际化、图表能力；上述配套优先延续，具体兼容版本由实施任务锁定；pnpm |
| 默认后端 | Python + FastAPI | Rust Web 后端 |
| 可选后端 | C# + ASP.NET Core（.NET） | Python + FastAPI、C# + ASP.NET Core（.NET） |
| 数据库支持目标 | MSSQL / SQL Server、MySQL；本轮未指定变更默认数据库，暂沿用现有 MySQL 默认 | PostgreSQL 默认；MSSQL / SQL Server、MySQL 可选 |
| CA 控制台 | Vue 3 + TypeScript + Element Plus + Vite，保持现状 | Vue 3 + TypeScript + Ant Design Vue + Vite |
| CA 运行时 | 独立 Rust + Tauri 2，继续负责 PLC 采集和现场事实 | 延续 Rust/Tauri 的职责与进程边界；按目标数据库补适配 |
| 部署 | .NET 必须提供不依赖 Docker 的服务器交付路径；既有 Docker 路径保留 | 延续原生服务器交付与可选 Docker 路径，具体交付矩阵另定 |

“antd”在本 Vue 路线中明确指 Ant Design Vue。CA 已是 TypeScript，不需要在 v1 改为 JavaScript；v2 的 Element Plus -> Ant Design Vue 是实际 UI 迁移工作。所谓 CA 不调整是保留采集职责和运行时架构，不代表 UI、驱动和数据库 SQL 均无需修改。

## 3. 当前事实与缺口

2026-09-08 按当前 checkout 核对：

- `frontend-js/package.json` 声明 Vue 3、Element Plus、Vite、Router、Pinia、Axios、Vue I18n、ECharts，Web 主体为 JavaScript。
- `control-agent/package.json` 声明 Vue 3、Element Plus、TypeScript、vue-tsc、Vite、Tauri 2 API 和 Vue I18n。
- `backend/` 是现有 FastAPI/SQLAlchemy/Alembic 实现；尚无 `backend-dotnet/`、`backend-rust/` 实现。
- `backend/settings.py` 有 MSSQL/PostgreSQL URL 配置；当前 `backend/pyproject.toml` 未声明 MSSQL 的 aioodbc/pyodbc 驱动。配置入口不构成完整支持证明。
- CA 的 `src-tauri/Cargo.toml` 当前 SeaORM 启用 MySQL；MSSQL/PostgreSQL 全链路仍待适配与验证。
- MySQL 有既有隔离运行验证记录；不得据此宣称任一其他数据库或新后端已受支持。

## 4. 范围与要求

1. R1：在本 arch 仓库规划多实现；保留 `backend/` 为 FastAPI 路径，.NET 计划使用 `backend-dotnet/`，Rust 计划使用 `backend-rust/`。v2 默认变化不要求立即重命名现有目录。新 Web 路径在 v2 实施 spec 中确定。
2. R2：v1 交付 .NET 可选后端；不能仅交付健康接口脚手架。需逐项明确 Core 认证、系统、模块注册、CA 授权、schema-maintenance、monitor 与 Projection 的等价能力或经批准的差异。
3. R3：v1 将 MSSQL、MySQL 作为正式支持目标，覆盖两套后端、迁移、数据库 SQL、CA 快照写入和 Projection 读取。v2 将同样的验证扩展至三套后端与三种数据库；未验证的组合不得标记支持。
4. R4：.NET 原生交付必须覆盖配置、日志、进程服务托管、启动/停止/重启、健康检查、前端静态资源/API 接入、数据库驱动与显式初始化、升级和回退；运行不得依赖 Docker。目标服务器 OS/架构、框架依赖或自包含发布、托管方式在实施 spec 中确定。
5. R5：各后端保持模块语义和公开 API 行为一致，以合同测试检查响应、错误、认证、权限和数据语义；不要求文件逐一翻译。同一部署选择明确的后端实现，并保持唯一 Projection writer。
6. R6：第一阶段继续以现有 FastAPI 行为和 SQLAlchemy/Alembic 为参考及 schema 权威，禁止 EF/Rust 迁移工具自动成为第二写入权威。原生 .NET 交付是否容许 Python 迁移工具依赖必须在实施前明确；若要求完全不依赖 Python，需单独设计迁移交付方案。
7. R7：v2 引入默认 Rust Web 后端、Vue/TS/Ant Design Vue Web 与 CA UI、默认 PostgreSQL，同时继续支持 FastAPI/.NET 和 MSSQL/MySQL。精确框架、驱动和版本在各实施任务中验证并锁定。

## 5. 推进顺序与验收标准

1. v1：明确目标服务器和原生交付约束，建立 API/数据库/CA/Projection 一致性测试基线。
2. v1：实现 .NET Core 等价能力与原生交付；完成 FastAPI/.NET 对 MSSQL/MySQL 的目标支持矩阵，包括 CA 链路。
3. v1：在批准的隔离目标环境执行原生安装、初始化、登录、业务 API、快照/Projection、服务重启、升级与回退验证；经独立 QA 和 Human Owner 接受后，进入独立的 1.x 发布任务。
4. v2：分别立项 Rust 后端、Web TS/Ant Design Vue、CA UI 迁移和 PostgreSQL 全链路适配；完成兼容矩阵后才能切换默认值并进入独立 2.x 发布任务。

路线文档验收：技术栈表与用户决策一致；准确说明 CA 已使用 TS；分清目标支持与当前事实；明确 v1 .NET 原生交付、数据库全链路和后续实施 gate；根 PLAN 与双语任务目录可追溯到本文件。

## 6. 本次 PM 写入边界

仅创建本 `spec.md` 并同步根 `PLAN.md` / `PLAN.zh-CN.md`、`plans/README.md` / `plans/README.zh-CN.md` 的路线索引。不创建代码、依赖、构建目录或未来角色证据；不变更已有任务状态。
后续实施由独立任务明确 allowlist、需求映射、依赖和验收；本路线不是跨模块批量实现的直接执行单。

## 7. 风险、回退与待细化项

- 数据库驱动、方言、JSON/时间/事务行为以及 CA 写入兼容性可能扩大适配工作量；必须按实际组合验证。
- v1/v2 共存时不得破坏既有 1.x 消费项目；代码回退与 schema 回退分别设计，已发布 tag 不变。
- 原生服务器 OS/CPU、.NET 发布形式、迁移工具依赖、最低数据库版本、v2 前端目录以及具体版本号在实施任务中细化。
- 本任务不引入消息中间件，不调整真实服务器、数据库或 PLC，不创建或发布 Git refs。

## 8. 决策与 Revision 历史

- 2026-09-08 r1：根据 Human Owner 本轮明确决定，记录 .NET 属于 v1、Rust 默认后端及 PostgreSQL 默认属于 v2、两代前端和 CA UI 路线。PM 补充 CA 当前 TS 事实、数据库适配缺口和原生交付验收要求。尚未批准具体代码实施 Revision，尚无 Development/Verification 记录。
```
<!-- END ARCH-MULTI-001 r1 ORIGINAL -->
