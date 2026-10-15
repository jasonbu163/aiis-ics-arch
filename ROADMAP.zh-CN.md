# AIIS ICS Architecture 发展路线

English version: [ROADMAP.md](ROADMAP.md)

## 1. 定位与当前基线

本路线描述 PW、AW、AIW 的目标职责，以及保留稳定基线、逐步到达目标的能力阶段。它是发展方向，不表示目标应用、数据表或部署已经存在。

当前源码仍为 `backend/`（FastAPI/SQLAlchemy/Alembic）、`frontend-js/`（Vue JavaScript）和 `automation-world/`（Rust/Tauri）。原 Control Agent（本次称 CAF 冻结参考）采集、解码 PLC 数据，直接写入后端拥有的 raw/latest 快照表，供后端 Projection 框架消费。公开模板不代表已包含客户业务 Handler，也不证明真实 PLC 链路正在运行。

`automation-world/control-agent/` 的既有文档记录迁移验证后冻结的旧 CA 兼容基线；新 CA 专指控制执行，CAF 的精确迁移路径由对应任务核对。本次不认证迁移。DAA 已从冻结 CA 继承独立工程，SMA 已从 `data-twin-backend`（DTB）Twin State Studio（TSS）过滤复制通用 HTTP 映射工程，原 TSS 保留。工程初始化和 no-I/O 原生启动由 [ARCH-AW-001](plans/ARCH-AW-001-agent-foundation/spec.md) 跟踪；独立 QA/最终验收以该 bundle 为准。`aw_*` 表、新 AW API、shared UI 与业务闭环仍是目标。

| 文档 | 职责 |
| --- | --- |
| [README.zh-CN.md](README.zh-CN.md) | 当前项目身份、源码结构与运行入口 |
| 本 ROADMAP pair | 长期职责、阶段、依赖与完成门槛 |
| [PLAN.zh-CN.md](PLAN.zh-CN.md) | 当前任务状态、证据摘要与下一 gate |
| [ARCH-MULTI-001 r2](plans/ARCH-MULTI-001-versioned-stack-roadmap/spec.md) | 本轮文档任务的批准范围；保留 r1 历史 |
| [AW 白皮书](docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md) / [详细原理](docs/AIIS_AW_Runtime_Design.md) | ARCH-AW-002 r2 修订的角色、近期 SQLite/API 与共享可视化流程设计；不代表实现 |
| 各实施任务 bundle | 精确获批范围、Development 证据与独立 Verification |

未来方向由 r1 的可互换后端/默认技术栈路线调整为按职责演进。旧版本默认值、数据库矩阵、目录建议及 Ant Design Vue 迁移不再作为本路线承诺；仍有实际需求时另立任务。

## 2. 三界职责

| 领域 | 拥有的职责 | 当前过渡与目标 |
| --- | --- | --- |
| PW | 业务模型、用户与权限、业务规则、事务、业务 API | 现有 FastAPI 业务继续属于 PW；未来目标为 C#/.NET/ASP.NET Core + FastEndpoints |
| AW — Automation World | 采集、现场事实、语义映射；后续按需归档与受控执行 | 使用 Rust，先复用 CAF/TSS 素材。近期本地 SQLite 保存配置，现有 FastAPI 暂承事实、持久意图与运行接口；AWB/Axum 延后 |
| AIW | 模型、分析、推理与建议 | Python/FastAPI；由 PW 业务规则和授权决定如何采用其输出 |

三界首先是职责边界，不强制三个仓库、立即独立部署或同时迁移语言。Python 业务代码不会因使用 Python 自动成为 AIW；AIW 也不直接取得现场动作权。

保留当前稳定基线，每项实施独立批准。现场控制、数据库更换、PW 迁移与 AWB 均另行推进；本方向不恢复 Celery、Redis 或退役工业命令合同。

## 3. 数据流与配置流

### 当前源码链路

```text
PLC -> 原 CA / CAF 采集/解码 -> 后端 raw/latest 快照数据库
    -> 后端 Projection 输入解析 -> 模块业务 Handler
    -> 业务状态/记录 -> 业务 API/UI
```

源码入口：[CAF 历史采集](automation-world/control-agent/src-tauri/src/services/plc_collection.rs)、[快照写入](automation-world/control-agent/src-tauri/src/infrastructure/database/repositories/mod.rs)、[Projection Runner](backend/projection/runner.py)。这是源码职责说明，不是现场验证。

### 近期目标链路

```text
PLC -> DAA 采集/解码 -> FastAPI AW 事实 API / aw_* 最新事实
    -> SMA 绑定/校验/请求组装 -> PW 业务 API
    -> 业务 Service / 业务表 -> UI；后续 AIW 按授权消费

各 Agent UI -> 本机 Rust 配置服务 -> 自身 SQLite -> 校验/显式启用
第三方 -> 本系统 API 校验/持久化 -> CA 原子领取 -> 设备下发/确认
                                      CA -> 本系统执行回执
长期按需：中央配置发布 -> Agent 下载/校验/应用/状态回报
```

业务 API 接收设备/业务身份、测量值、时间和事件等语义数据。业务 Service 不解释 PLC DB 编号、offset、bit 或原始点名；来源信息可保留用于追踪。现场转换和请求组装归 SMA，订单流转、业务状态规则及事务留在 PW。

先冻结配置、事实、映射/回执合同和一个实际业务 API 试点，无需先实现已盘点的全部八个旧 Handler API。合同固定后，后端、DAA、SMA 可并行实施；闭环联调以真实可调用 API 为准。

## 4. 独立 Agent、CAF 与 CU

DAA/SMA 独立工程已由 ARCH-AW-001 记录；新 CA 是 Tauri 管理入口与独立 Rust 控制执行的目标角色。旧 CA 使用 CAF 冻结参考身份，不创造未确认的英文全称或新路径。当前仓库仍有旧 `control-agent/` 文档及 `console-ui/` 目录；目录存在不代表新 CA 或 CU 已交付。

| 角色 | 近期设计职责 |
| --- | --- |
| DAA | 固定 S7 采集链路、DB/UDT 导入与受限手动偏移推算、本地配置和事实 API；无业务流程画布 |
| SMA | AW 事实的语义加工、第三方/上层 API 投递；不写 PLC/业务库 |
| CA | 消费本系统持久且有效意图，映射/现场校验、设备写入/握手与回执；不直取任意外部 URL 写设备 |
| CAF | 原 CA 冻结参考、兼容来源；不是活动共享运行时 |
| CU / console-ui | 共享 UI 源码及可运行设计工作台；各 Agent 构建引用，运行无需工作台在线 |
| AWC | 长期控制台角色与管理形态，不能与 CU 源码组件混称 |

各角色拥有独立入口、配置/凭据、可写状态、队列与生命周期。同机部署不合并为一个常驻进程。窗口关闭、后台继续和显式退出由实施规格固定，Tauri 不自动提供 headless 托管。

## 5. 共享 UI、流程 Core 与独立交付

以 [CAF 控制台素材](automation-world/control-agent/src/layouts/AgentLayout.vue) 为视觉参考。CU 的 UI 编排用于页面/布局/参数呈现；SMA/CA 流程画布用于触发、取数、转换、判断与动作，两者发布语义分开。Rust Flow Core 是共享运行时能力，不归 CU，不让 CU 直连 PLC。

```text
CU 共享 UI 源码 + Agent 专有 UI -> 各自 dist -> 各自安装包
共享流程编辑器 + Rust Flow Core -> SMA / CA 各自宿主和节点
CU 工作台独立预览设计；安装后的 Agent 不依赖工作台在线。
```

推荐 Vue 画布加 Rust 解释版本化定义，不生成/编译每次流程。Vue Flow 是候选；Node-RED + Rust 设备服务是备选，不承诺任意 Node-RED JSON/Function 节点由 Rust 执行。SMA 装配时拒绝设备写节点；SMA 投递重试和 CA unknown 核实保持不同恢复策略。

构建/打包验证仍需各自的 Vite/TypeScript 解析、依赖一致性、frontendDist、独立端口与目标平台启动证据。共享源码是重建依赖，不是在线服务；本轮不证明这些能力完成。构建边界参考 [Tauri 工程结构](https://v2.tauri.app/start/project-structure/)。

## 6. CAF、TSS 与通用后端复用

| 来源 | 复用内容 | 必要适配 |
| --- | --- | --- |
| 冻结参考 [CAF](automation-world/control-agent/README.zh-CN.md) | PLC 读取、解码、采集循环、诊断与日志 | 配置显式导入本地 SQLite，事实经 API 上报；长期中央发布另行设计 |
| DTB `twin-state-studio/` | 纯 Rust 映射 Domain、调度器、事实/目标 API 绑定、值规则、编辑与诊断 | 适配生命周期、网络和后端依赖；保留功能逻辑，复用 CAF 视觉素材 |
| DTB 通用后端 | 事实/配置 API、执行租约与回执 | 适配本仓库 MySQL、Registry/manifest、认证权限、响应合同与显式 Alembic 迁移 |

DTB 外部来源路径为 `twin-state-studio/README.zh-CN.md`、`twin-state-studio/src-tauri/src/domain/mapping_runtime/mod.rs`、`twin-state-studio/src-tauri/src/services/mapping_runtime/mod.rs` 和 `backend/app/tss/`。它们固定 SMA 的来源归属；当前 SMA 仅保留适用桌面 HTTP/纯计算实现，并排除客户/SQL/legacy IPC、跨 DTB 帮助生成。SMA 可独立启动，其在线功能仍要求兼容 Backend 合同；本轮不迁入 DTB backend，也未建立新 AW API。

MSSQL 的 `ROWVERSION` 等专有机制需要 MySQL 兼容合同。DTB 旧迁移文件属于来源历史，不能作为本仓库现成迁移。保留来源归属与适用许可，仅接纳可复用公共能力与脱敏示例；客户页面、真实配置、数据/资源及 legacy 直接写业务表路径不进入新 AW 边界。

受控切换前保留CAF 历史数据库快照与后端 Projection 链路，作为明确的兼容/回退路径。目标链路中 DAA 使用事实 API、SMA 通过业务 API 写入结果；当前 DAA 暂保留旧快照实现且外部门禁关闭，新事实 API 接入尚待后续任务。

## 7. 配置、事实与 `aw_` 归属标记

近期 DAA 配置权威为本地 SQLite，SMA/CA 建议沿用且实例独立；FastAPI 提供事实、持久意图、领取与回执 API。中央配置发布和 AWB 延后。下列 `aw_` 名称仅说明后端 AW 归属，配置/映射表属于长期中央化候选，不要求近期与 SQLite 同时成为可编辑权威。

| 表名示例 | AW 职责 |
| --- | --- |
| `aw_collection_configs` | 版本化采集配置 |
| `aw_collection_facts` | 事实定义与最新值 |
| `aw_target_apis` | 目标 API 参数合同 |
| `aw_mapping_configs` | 事实/固定值绑定与映射配置 |
| `aw_mapping_runtime_states` | 映射运行状态、租约和回执 |
| `aw_agent_states` | Agent 状态与已应用配置版本 |

这些名称说明归属，不是最终 schema。订单、设备业务状态与业务采样记录保留各业务 Owner 和表名；被 Mapping 引用不代表改归 AW。前缀不等于数据库隔离、权限隔离或已经完成 AW 拆分。

采集配置同时覆盖 [plc_points.yaml](automation-world/control-agent/config/plc_points.yaml) 的连接、DB-block、类型、offset/bit，以及 [plc_snapshot_policy.yaml](backend/config/plc_snapshot_policy.yaml) 的 raw/latest 保存选择。旧配置须显式导入、预览和校验；通过本机 Rust 服务保存草稿，再明确启用完整版本。长期才增加中央发布/下载；SQLite 提交与内存切换分开，恢复协议待定。

事实可沿用 `(sourceKey, factName)` 身份。API/schema 任务需要明确来源/Agent 标识、稳定采样 ID 或序列、采集和接收时间、quality、点位合同版本与映射版本，以及批量原子性、鉴权、幂等和版本机制。

latest 表示当前状态，不能证明期间每次变化都已消费。事件、追加型业务记录和历史归档需要分别明确合同；缺失、坏质量、过期和乱序数据需要处理策略，避免来源停止后最后一个值长期被视为有效。

本地 SQLite 配置是近期方向；完整事实引擎不是前置。draft/active/previous 是候选编辑生命周期，与白皮书长期 current/previous 稳定双槽的精确关系待定。Agent 不持 Backend/Redis 存储凭据，后端换存储不得静默降低接收回执语义。按现场需求纳入有界持久缓冲/outbox、离线投递及配置快照；配置回滚必须保留运行记录、待发送记录和消费游标。

## 8. 能力阶段与切换门槛

S0–S4 是能力里程碑，不对应版本号、日期或实施授权。每项实施需要独立范围与验收证据。

| 阶段 | 目标 | 依赖 / 准入条件 | 可检查的完成条件 |
| --- | --- | --- | --- |
| S0 — 文档基线 | 本双语蓝本、当前/目标区分、复用与命名边界 | 文档范围已批准 | 双语内容、路径与链接检查；独立文档 Verification 和 Human Owner 最终验收 |
| S1 — 合同与单业务试点 | 采集配置、事实读写、映射/回执及一个 PW 业务 API | 确定目标项目与业务 Owner | 固定采样身份、quality/time/version、权限与幂等；接口和显式迁移在独立获批实施任务验证 |
| S2 前置 — Agent 工程初始化 | 原 CA（CAF）迁入/冻结、DAA继承、TSS过滤为SMA及配置/原生启动隔离 | 可先于 S1 API 实现；不改变 S1 合同 gate | ARCH-AW-001 r1 的工程证据/独立QA/最终验收见唯一bundle；不代表共享UI或业务闭环完成 |
| S2 — 本地配置与有限闭环 | CAF素材→DAA、TSS→SMA、本地SQLite、CU、事实API；新CA共享流程/模拟下发另立任务 | 冻结 S1 合同后可并行实施 | 各应用分别构建/运行；验证S7支持矩阵/导入推算、SQLite启用、事实→映射→API及CA模拟握手；共享Core权限/恢复验证后才能现场另批 |
| S3 — 现场可靠性与交付 | 配置应用/回退、质量/陈旧判断、资源/容量、持久缓冲/恢复与维护 | S2 链路和明确的现场可靠性需求 | 验证有界存储、断线/重启、重复/乱序、失败恢复与日志；真实 PLC、长期运行和部署证据另行授权 |
| S4 — 按需三界承接 | 中央配置发布、AWB/Axum、PG/Redis、HA/SA、独立 Rust Runtime/统一 AWC、PW .NET/FastEndpoints、AIW Python/FastAPI | 项目需求与稳定合同；分别立项 | 唯一数据/业务写入责任，逐模块等价或获批差异、迁移与回退验证；不是近期交付前置 |

TSS 当前每周期重新读取绑定事实，相同值也发送；失败或结果不确定的目标请求不自动重放。这不等于可靠离线投递。追加型 API 需要稳定幂等键、事务内业务写入与回执、成功确认，以及明确的重试/人工恢复边界。单个 Mapping 的租约不负责不同 Mapping 对同一业务目标的冲突仲裁。

先比较新旧结果，再按来源/目标切换。停用对应旧 Projection 后才能启用 SMA 生产写入，保证每个业务目标只有一个有效写入方；明确游标/采样身份、回退和重复消费边界。这些是未来切换门槛，不授权现在改变现场系统。短时 smoke 不替代长期或现场验证。

## 9. 延后决策与任务衔接

- [ARCH-BE-003](plans/ARCH-BE-003-mapping-service-api-pilot/spec.md) 需要针对目标项目、采样身份、幂等与权限独立修订；从一个业务 API 开始，不先补齐全部旧 Handler。
- [CA-CONFIG-001](plans/CA-CONFIG-001-packaged-configuration-management/spec.md) 按本地 SQLite 权威及长期中央发布的阶段独立重审；本路线不修改或批准其实施。
- [ARCH-BE-002](plans/ARCH-BE-002-energy-price-api/spec.md) 是独立公共能力，不是采样试点的前置依赖。
- AWB、无界面 Runtime 提取、统一 AWC、数据库更换和 PW 技术栈迁移按需延后。PW/AW/AIW 能力可分别推进，无需一次性全迁。
- 精确组件版本/驱动、数据库支持组合、部署形态、本目标以外的目录决策与工期归实施任务。自动 OpenAPI 导入、完整导入导出与模拟器按需要再确定范围。

本轮文档不创建 Agent 目录、代码、API、表结构或部署产物；后续阶段均为规划。构建、运行、现场证据及最终验收记录在所属任务 bundle 中，不从本路线推断。
