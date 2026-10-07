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
