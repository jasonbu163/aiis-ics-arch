# AIIS ICS Architecture 项目契约

本文件是本仓库的中文 canonical 长期工程契约。通用方法来自已安装的 AIIS skills；稳定运行事实归根目录 README 与 PLAN；使用 3MD 的一次性任务范围、证据和验收只写入对应的 `plans/<task>/` 三文件；DIRECT 的当前会话记录按开发 workflow 执行。

## 1. 开始前必读

非琐碎工作开始前，依次阅读本文件、`README.md` / `README.zh-CN.md`、`PLAN.md` / `PLAN.zh-CN.md`，再阅读最近触达目录的 README 与 PLAN。STD 写入任务及 BACKFILL 回填现有任务时还必须完整阅读所属 `spec.md`、`tasks.md`，以及交接后由 Verification 创建的 `checklist.md`。

根目录只放跨仓库架构入口，不承载项目客户业务。公共模块可以包含可复用领域 Model / Schema / Service / CRUD 与业务 API；`backend/app/energy/` 的能源单价及已批准公共业务切片属于已批准公共能力。客户专属规则、页面、真实数据与资源仍归消费项目。稳定的模块规则写在对应模块 README；持续工作的阶段状态写在 PLAN；具体范围和证据写在任务 bundle。

## 2. 仓库边界

- `backend/` 是 FastAPI、SQLAlchemy、Alembic 和 Core Service 的源码。
- `frontend-js/` 是保留 JavaScript 语言形态的 Vue 3 + Vite Core 前端模板。
- `automation-world/` 统一管理现场采集和语义映射；`automation-world/control-agent/` 是迁移后冻结的 Rust/Tauri 兼容运行时，DAA/SMA 为独立工程，均不依赖 backend 进程内轮询 PLC。
- `tools/` 是不默认导入 backend、数据库或 `.env` 的项目级独立工具。
- `contracts/` 是根目录 Core 跨运行时公开合同中心；源码版本由 Git refs 固定，不建立实体 `release/` 源码目录。
- `docs/` 保存跨仓库与流程类长期文档，由根目录 PLAN 统一管理，只建立双语 README 索引而不建立独立 PLAN。
- 项目客户模块、真实 PLC/数据库地址、输入工件、构建产物、日志和密钥不进入公开架构仓。

前后端模块采用 `app/<module>/.../manifest` 约定。后端 manifest 是模块向 Registry opt-in 的唯一入口；前端 route/locale 自动发现属于基础设施，菜单自动组装另行立项，不在本契约中默认宣称已实现。

`main` 是持续 Core 开发线；大版本维护线使用字面分支 `release/1.x.x`、未来的 `release/2.x.x`、
`release/3.x.x` 等，并只能在独立获批的对应大版本发布任务中 fast-forward。精确源码版本只由不可变的
annotated tag（例如 `v1.0.0`、`v1.2.1`、`v2.1.2`）固定；已发布 tag 不得移动、force-update、删除或
重建。源码不复制到实体 `release/` 目录，构建产物、GitHub Release 页面和部署状态也不属于源码定版
事实。创建或发布这些 Git refs 必须由独立获批任务明确授权，并由 Human Owner 手工执行。

## 3. 运行与安全边界

- 后端使用 `uv` 和仓库锁文件；前端使用 `pnpm`；Rust 使用 Cargo。
- 本仓使用Tauri的AW agent与工具，面向使用者的普通开发启动统一使用`pnpm tauri dev`。应用运行所需Cargo features由该应用Tauri配置统一传递，不要求使用者改换启动别名或手填驱动feature；专用测试、编译与打包命令在相应任务文档另行说明。
- FastAPI 请求线程不得轮询 PLC；现场采集、重连和设备事实归常驻 `control-agent`。
- 未经独立批准不得恢复 Celery、Redis、Beat、Flower、Python Worker 或旧工业命令合同。
- 数据库表结构变化必须通过显式 Alembic / schema-maintenance 任务；模块 Registry 不自动建表。
- 示例环境文件只能使用占位符、默认关闭选项和通用权限；真实 `.env` 永不提交。
- 工具默认从自身 `inputs/` 读取、向自身 `outputs/` 写入；跨工具传递必须人工确认并显式指定路径。

## 4. 写入任务治理

写入型任务先遵循 [Development Lifecycle Workflow](.codex/workflows/development-lifecycle-workflow.md)：默认 STD，实际选择 `pm` / `development` / `verification` TOML 角色，Verification 使用 fresh context（工具支持时 `fork_turns="none"`）；明确 DIRECT 不用 3MD，明确 BACKFILL 先实施后真实回填，默认仅影响当前任务。只读讨论不启动团队或创建空 bundle；角色失败不静默降级，session routing/registry 不作为开发依赖。详细流程、旧工具兼容、通知和资源收尾归该 canonical workflow。

STD 遵循 `spec.md -> Human Owner 批准 -> tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance`。STD 的 Revision、范围、allowlist、验收或风险发生实质变化时，停止写入并回到 PM 新 Revision。

STD 中 `tasks.md` 是 Development 的事实面；`checklist.md` 只能由独立 Verification 创建或更新。BACKFILL 的实际记录者和验证独立性按 canonical workflow 如实注明。QA 通过不等于 Human Owner 最终验收，也不授权发布、部署、数据库写入、真实设备操作或 Git/GitHub 推送。

## 5. 文档与代码质量

- 根 README/PLAN/CHANGELOG/INITIALIZATION 保持英文主文档与中文 pair；本契约中文为唯一执行语言版本。
- `docs/` 不替代 `contracts/` 或 `plans/`：公开合同继续归根目录 `contracts/`，任务范围、Development 证据与 Verification 结论继续归 `plans/`；运行与发布操作事实只归相应 README、INITIALIZATION 和当前任务 `tasks.md`。
- 用户可见文案必须进入 i18n，中文和英文键保持对称。
- 新增或修改的关键源码保持中文头部说明或现有文件风格；真实结构发生变化时同步维护 `CODE_INDEX.md`。
- 裸运行工具入口只显示帮助，不读取默认输入或产生副作用；验证产物优先写入 `/private/tmp`。
- 不运行全局 `/init`、`/document-init`，不把一次性任务内容复制回本契约。

## 6. 交付前检查

STD 交接或 BACKFILL 回填时先更新所属任务文档；三个模式均运行与范围匹配的静态检查、编译、单元测试和文档链接检查，记录真实命令、退出码、环境限制和未授权边界。发布版本、版本分支/tag、托管平台设置、Docker `up/down/build`、真实数据库迁移和现场 CA 操作均需另行批准。

- **源码交付一致性**：开发默认在约定的交付源码工作树中进行。使用临时副本或其他隔离工作树时，有效变更须在交付前整合至该工作树，并核对其与已验证候选的一致性及实际构建、启动入口；不得将应交付的变更仅留在临时副本中，或以临时副本的验证结果替代正式源码交付。
- **临时资源生命周期**：临时源码副本、测试环境及构建产物须明确任务归属与回收条件。整合及必要验证完成后，按 canonical workflow 的资源收尾规则及时回收无运行、后续任务或证据依赖的自有资源；确需保留的，记录路径、用途、保留原因及清理时点或触发条件。关键结论与必要证据须持久化，不得仅依赖临时路径；整合与回收不得覆盖真实配置、数据库和历史数据，或影响任务外资源。

## 7. 时间与时区

本节是新增开发与后续触达旧模块时的统一时间合同，不代表既有实现和历史数据已完成整改，也不触发任务范围外的批量改造或数据迁移。

- 第一版项目业务时区与存储时区统一为 `Asia/Shanghai`（东八区，UTC+08:00）。后端、Tauri、数据库、API、UI、报表和业务导出遵循同一口径，不随访问电脑、服务器或容器的系统时区自动变化。
- 业务事件、创建、更新等日历时间统一按上海本地时间保存。MySQL 使用 `DATETIME`，保留原有精度；SQLite 时间文本使用携带 `+08:00` 的 RFC 3339 格式。不得在同一字段混存 UTC 和上海时间。
- API 与普通业务 IPC 的时间戳明确携带 `+08:00`。UI 时间输入、显示、日期筛选、自然日和班次统计均按上海时区处理。外部其他时区的输入在接入边界转换一次，禁止重复加减八小时。
- UI 中的业务日历时间默认使用 24 小时制 `YYYY-MM-DD HH:mm:ss`，显示到秒；仅在诊断或明确业务需求下显示毫秒等更高精度。显示精度不改变底层存储、API/IPC 原始值和日志保留的时间精度；时区及字段含义通过页面统一说明或字段旁提示交代，避免在每个单元格重复堆叠。
- 时间字段必须对应明确的事实语义，区分事件发生、采集、保存、实际更新和界面刷新时间；“更新时间”不得用界面刷新或查询时刻冒充。缺少真实日历时间时显示缺失状态，不猜测日期，也不直接把单调计数当日历时间格式化。
- 调整旧模块时，核对时间输入、生成、数据库默认值、存储、查询、API 与 UI 全链路；发现不一致，纳入当前任务整改。历史数据先确认原有时区，再制定显式迁移步骤，禁止盲目整体加八小时；数据库结构及历史数据迁移仍遵循本契约的任务与批准边界。
- 时区通过项目统一配置或公共时间工具管理，不在各模块散落硬编码。新项目可在首次写入数据前选定其他业务及存储时区；已有数据的项目改变存储时区，必须单独评估和迁移。
- Unix 时间戳、单调时钟、耗时、纯日期及需保留原貌的协议数据按自身语义处理，不机械转换成东八区日历时间。

## 8. 表格列宽与本机偏好

本节适用于新增开发与后续触达旧模块时的业务数据表。现有表格按当前任务范围逐步整改，不因本规则生效而触发任务范围外的全量改造。

- 普通业务数据列默认支持通过拖拽表头列边界调整宽度，同时设置合理的最小列宽；表格总宽度超出容器时允许横向滚动，避免内容被强行挤压。
- 选择框、序号、操作等特殊功能列可根据交互需要固定宽度，作为默认可拖拽规则的例外。
- 用户调整后的列宽应在翻页、筛选、数据刷新及页面切换时保留，并在页面重新加载或应用重启后恢复。
- 列宽作为本机界面偏好保存，按应用、页面/表格及稳定字段标识隔离，不使用翻译后的字段标题作为存储键；不写入业务数据或业务配置版本，跨设备同步另立范围。
- 每张表提供“恢复默认列宽”入口，清除当前表的列宽偏好并恢复默认布局；列结构变化时，对失效的偏好回退到默认值。
- 拖拽、列宽记忆和恢复默认通过公共表格组件或公共列宽工具统一提供，页面不重复实现同一套机制。
