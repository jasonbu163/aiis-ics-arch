Task ID: ARCH-AW-002
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Handoff: Exact r2 documentation working tree to fresh-context Verification; Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# 白皮书修订与详细原理设计交付记录

## 1. 批准依据与保护边界

消费完整 `spec.md` r2（owner_approved），依据其第 1 节真实 Human Owner 文档授权执行。已读根 AGENTS、README/PLAN pair、canonical workflow、docs README pair、AW/DAA/SMA/CU 最近 README/PLAN、既有白皮书、ROADMAP pair 和 r1 设计素材。任务开始时仅 spec 存在，tasks/checklist 均未预建。使用 `aiis` 与 `project-governance`；本轮不加载未来实现面技能代替功能实施。

基准 HEAD：`363b297bffe65e020108f5504766b4fb1ec3b381`。当前为既有多任务 dirty working tree，包含后端/前端改动、旧 control-agent 删除和新 automation-world 等；没有 reset、checkout、回退或整理这些内容。白皮书和 ROADMAP 原本为未跟踪文档，基于任务开始时现有内容原位修改，保留有效来源与其他工作流事实；不将整库 dirty 算为本任务产物。

## 2. 实际顺序与文件

| 顺序 | 文件 / 实施 | 对应要求 |
| --- | --- | --- |
| 1 | 原位修订 `docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md`，保持入口；增加 2026-10-15/r2 修订关系；更正 CAF/新 CA、CU、DAA S7/SQLite/API、共享流程与近期/长期边界 | R1–R8 |
| 2 | 创建 `docs/AIIS_AW_Runtime_Design.md`，复用 r1 素材并补 CU 模块/构建/运行视图、配置启用恢复、节点合同及故障表 | R2–R9 |
| 3 | 同步 `ROADMAP.md` / `ROADMAP.zh-CN.md` 的角色、§3 配置流、§4–5 共享与独立运行、§7 权威和阶段/关联项 | R8–R9 |
| 4 | 同步 `docs/README.md` / `docs/README.zh-CN.md` 两文入口与用途 | R9 |
| 5 | 本 `tasks.md` 记录 DEV 自检并交接；根 PLAN/catalog 由主协调按本 handoff 机械同步 | §5 |

Development 写入仅以上 7 个 Markdown 文件；未修改 spec/checklist、AGENTS、源码、配置、依赖/锁文件、contracts、迁移或其他任务 bundle。没有创建新 workspace、Agent 工程或可执行合同。白皮书先落盘，再创建详细设计，最后同步索引/路线。

白皮书不是仅追加声明：实际替换 §1.3、§2.2、§4–5、§13、§15.1–15.2 等现行结论，并给中央配置/AWB/HA/Redis/PG 相关章节标明长期适用范围；历史 commit、U1–U6、D3、R0–R6、T1–T11 来源及旧稿去向保留，新增 U7 指向 r2。

## 3. DEV self-check

所有命令从仓库根执行。以下属于开发自检，不是独立 QA verdict。

| 检查与真实命令 | 结果 |
| --- | --- |
| `git status --short`、`git rev-parse HEAD` | 退出 0；读取 dirty 基线与上述 HEAD，保护并发修改 |
| `find docs plans automation-world -name 'AGENTS*.md' -print` | 退出 0，无额外作用域 AGENTS；根契约适用 |
| `python3 /private/tmp/ARCH-AW-002-dev-r2/revise-whitepaper.py` | 退出 0；先原位更新白皮书 |
| `python3 /private/tmp/ARCH-AW-002-dev-r2/create-design.py` | 退出 0；其后创建详细设计 |
| `python3 /private/tmp/ARCH-AW-002-dev-r2/revise-roadmaps.py` | 退出 0；同步 ROADMAP pair、docs README pair |
| `python3 /private/tmp/ARCH-AW-002-dev-r2/audit-docs.py` 首次 | 退出 1；ROADMAP 英文多一个 Tauri 工程结构参考链接，中文已补齐 |
| 同一 `audit-docs.py` 修复后 | 退出 0；6 文件、58 本地链接、40 表格块；路径/新增锚点无错误，围栏平衡，双语链接目标归一后相同 |
| `git diff --check -- docs/README.md docs/README.zh-CN.md ROADMAP.md ROADMAP.zh-CN.md docs/AIIS_AW_Whitepaper_Roadmap_v0.4.md docs/AIIS_AW_Runtime_Design.md` | 退出 0；该命令仅覆盖 Git 已跟踪差异，未跟踪正文另由本地内容检查覆盖 |
| 白皮书和 ROADMAP 的 `rg -n` 阶段关键词复读 及 ROADMAP 阶段关键词复读 | 术语/阶段逐项复核；给 §8.2、§10 再补长期多输出适用限定，避免直连 Redis 误读为近期要求 |
| Python `difflib.unified_diff` 比对开始前副本与当前文档 | 白皮书 +166/-251 行；每份 ROADMAP +43/-63；每份 docs README +3；详细设计新增 236 行。全为 allowlist Markdown |

文档内容复核覆盖：CAF 无伪造全称/迁移认证；CU 构建依赖与两种画布；DAA 完整 DB/UDT、非优化、手动预览/实点核对；SQLite 单一权威/草稿建议/运行记录分离；API 回执保障；SMA/CA 节点权限及差异恢复；CA 原子领取、握手、unknown、唯一写入、PLC 联锁；分阶段验证与开放问题。

本轮另外读取官方 Vue Flow、Node-RED embedding/first-node、Tauri IPC、Siemens block-access 页面核验详细设计中对应事实，页面均成功返回；链接已在段落就近保留。没有将候选库或版本写成批准依赖，没有重新核验全部历史 T1–T11 来源。

## 4. 限制与已知风险

这是纯文档交付：未运行工程构建/测试、原生启动、数据库/Redis/PLC、Docker、推送、发布或现场操作。文档静态检查不证明技术算法、后台托管、设备安全、真实 API 或恢复实现正确。

- CAF 英文全称和最终路径未确认；仓库现有 control-agent/CU 文档仍沿用旧描述，本次 allowlist 不授权修这些模块文档。两份新正文诚实标识现状与设计，未来 owning task 核对。
- SQLite draft/active/previous、SMA/CA 沿用本地库是建议，长期 current/previous 稳定双槽另有合同；精确 schema/保留/恢复仍待定。
- S7 支持矩阵、latest/samples、API、画布库、节点、凭据、握手/仲裁、headless/平台打包均是后续任务决策，非本次冻结选型。
- 现有 DAA 旧快照路径、SMA 旧 HTTP 合同及冻结来源未退役；未来切换必须限定唯一有效写入方和回退。

## 5. 精确 developer_handoff

交接目标：`aiis-ics-arch::ARCH-AW-002 r2`，**developer_handoff**，上述 HEAD 上的当前 dirty working tree，无新 commit。批准 spec SHA-256：`44a02d93fbcc0e07bfeebe6912c71ead403334dcaef7c7c170260fd292c24565`。Verification 应读取完整 r2、本文、7 个 Development 文档和主协调机械同步的根索引，只验证/记录、不静默修文；下一 gate 为 fresh-context Verification，随后 Human Owner final acceptance。

本任务临时资源：`/private/tmp/ARCH-AW-002-dev-r2/` 保存开始前副本、三份一次性编辑 helper 和文档 audit helper，暂保留供 diff 审阅；没有新分支、worktree 或后台进程。r1 素材 `/private/tmp/ARCH-AW-002-r1-design-source.md` 由上游提供，不冒认为本角色创建。持久内容、命令结果、限制已记录在仓库，临时路径不是唯一证据；最终验收后的安全清理由主协调办理。

`contract_only` 不代表平台 ACL、强制路由或自动设备授权。本角色没有给出 QA verdict 或 Human Owner 验收结论。
