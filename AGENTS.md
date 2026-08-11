# AIIS ICS Architecture 项目契约

本文件是本仓库的中文 canonical 长期工程契约。通用方法来自已安装的 AIIS skills；稳定运行事实归根目录 README 与 PLAN；一次性任务的范围、证据和验收只写入对应的 `plans/<task>/` 三文件。

## 1. 开始前必读

非琐碎工作开始前，依次阅读本文件、`README.md` / `README.zh-CN.md`、`PLAN.md` / `PLAN.zh-CN.md`，再阅读最近触达目录的 README 与 PLAN。写入任务还必须完整阅读所属 `spec.md`、`tasks.md`，以及交接后由 Verification 创建的 `checklist.md`。

根目录只放跨仓库架构入口，不承载项目客户业务。稳定的模块规则写在对应模块 README；持续工作的阶段状态写在 PLAN；具体范围和证据写在任务 bundle。

## 2. 仓库边界

- `backend/` 是 FastAPI、SQLAlchemy、Alembic 和 Core Service 的源码。
- `frontend-js/` 是保留 JavaScript 语言形态的 Vue 3 + Vite Core 前端模板。
- `control-agent/` 是独立的 Rust/Tauri 现场事实采集运行时；它不依赖 backend 进程内轮询 PLC。
- `tools/` 是不默认导入 backend、数据库或 `.env` 的项目级独立工具。
- `contracts/` 保存跨运行时公开合同；`release/` 只保存经批准的源码版本材料。
- 项目客户模块、真实 PLC/数据库地址、输入工件、构建产物、日志和密钥不进入公开架构仓。

前后端模块采用 `app/<module>/.../manifest` 约定。后端 manifest 是模块向 Registry opt-in 的唯一入口；前端 route/locale 自动发现属于基础设施，菜单自动组装另行立项，不在本契约中默认宣称已实现。

## 3. 运行与安全边界

- 后端使用 `uv` 和仓库锁文件；前端使用 `pnpm`；Rust 使用 Cargo。
- FastAPI 请求线程不得轮询 PLC；现场采集、重连和设备事实归常驻 `control-agent`。
- 未经独立批准不得恢复 Celery、Redis、Beat、Flower、Python Worker 或旧工业命令合同。
- 数据库表结构变化必须通过显式 Alembic / schema-maintenance 任务；模块 Registry 不自动建表。
- 示例环境文件只能使用占位符、默认关闭选项和通用权限；真实 `.env` 永不提交。
- 工具默认从自身 `inputs/` 读取、向自身 `outputs/` 写入；跨工具传递必须人工确认并显式指定路径。

## 4. 写入任务治理

写入型任务遵循 `spec.md -> Human Owner 批准 -> tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance`。Revision、范围、allowlist、验收或风险发生实质变化时，停止写入并回到 PM 新 Revision。

`tasks.md` 是 Development 的事实面；`checklist.md` 只能由独立 Verification 创建或更新。QA 通过不等于 Human Owner 最终验收，也不授权发布、部署、数据库写入、真实设备操作或 Git/GitHub 推送。

## 5. 文档与代码质量

- 根 README/PLAN/CHANGELOG/INITIALIZATION 保持英文主文档与中文 pair；本契约中文为唯一执行语言版本。
- 用户可见文案必须进入 i18n，中文和英文键保持对称。
- 新增或修改的关键源码保持中文头部说明或现有文件风格；真实结构发生变化时同步维护 `CODE_INDEX.md`。
- 裸运行工具入口只显示帮助，不读取默认输入或产生副作用；验证产物优先写入 `/private/tmp`。
- 不运行全局 `/init`、`/document-init`，不把一次性任务内容复制回本契约。

## 6. 交付前检查

交接前先更新所属任务文档，再运行与范围匹配的静态检查、编译、单元测试和文档链接检查，记录真实命令、退出码、环境限制和未授权边界。发布版本、版本分支/tag、托管平台设置、Docker `up/down/build`、真实数据库迁移和现场 CA 操作均需另行批准。
