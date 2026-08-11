# AIIS ICS 多仓库项目管理与交付方案

Status: `ARCH-001 r2` is `qa_blocked`; ARCH-MIG-001 migration truth, the Human Owner license decision and final re-verification remain before publication  
Target repository: `aiis-ics-arch`  
Hosting: GitHub public repository

## 1. 目标

AIIS ICS 使用三个职责独立的仓库管理架构平台、实际项目和可复用模块：

1. 架构仓维护通用平台源码、Control Agent、通用工具、模板和版本基线。
2. 项目仓保存可独立启动、构建、测试和交付的完整项目源码。
3. 模块仓保存从真实项目中提炼、经过复用验证的可选业务模块。

总体原则是：

> 架构仓提供稳定基线，模块仓提供可选能力，项目仓拥有最终交付事实。

项目运行时不通过软链接、网络下载或动态 Git checkout 依赖其他仓库。每个项目必须能在只取得
项目仓源码和明确记录的外部 artifact 后独立交付。

## 2. 三个仓库

| 类型 | 仓库名 | 托管位置 | 可见性 | 主要职责 |
| --- | --- | --- | --- | --- |
| 架构仓 | `aiis-ics-arch` | GitHub | 公开 | 平台核心、Control Agent、通用工具、模板、版本与架构规范 |
| 项目仓 | `aiis-ics-l2-<项目号>` | Gitee | 私有 | 客户项目、业务模块、PLC 配置、migration、部署和交付 |
| 模块仓 | `aiis-ics-modules` | Gitee | 私有 | 可复用的前后端业务模块和接入说明 |

实际项目仓统一使用：

```text
aiis-ics-l2-<project-id>
```

旧 `vibe-l2-front-end` 仓暂时作为私有迁移来源和历史审计仓保留，不再继续承载新功能。待三仓
稳定后，将其设为只读归档；不得为了整理新仓而删除旧仓中的历史证据。

## 3. 依赖方向

```text
aiis-ics-arch
    │
    │ 稳定源码基线
    ▼
项目仓  ◀──────── aiis-ics-modules
    │                可选模块源码
    │
    └── 项目能力成熟后，经过脱敏、复核和第二项目验证，再向 modules/arch 提炼
```

边界如下：

- 项目只从架构仓的固定 release/tag/commit 获取源码基线，不跟随架构仓 `main` 自动变化。
- 项目按需从模块仓复制模块，模块仓不是项目运行时依赖。
- 架构仓不得通过 `frontend-custom`、`backend-custom` 或其他软链接反向引用项目仓。
- 模块仓不得依赖某个客户项目的真实数据库、PLC 点位、客户文案或部署环境。
- 跨仓库复制、提炼和升级都必须建立独立任务，不能继承另一个仓库的 approval 或 QA verdict。

## 4. 架构仓 `aiis-ics-arch`

### 4.1 职责

架构仓负责维护所有项目共同需要的能力：

- backend 平台框架；
- 当前 `frontend-js` 平台框架；
- 后续经批准的 TypeScript `frontend`；
- Control Agent 源码、构建和通用配置机制；
- 通用 PLC、映射、审计工具框架；
- 账号、认证、权限和系统管理基线；
- 前后端模块规范和默认关闭的 Demo 模块；
- Docker、初始化、升级和发布模板；
- contracts、design system、release scripts；
- 架构说明、版本记录和 3MD 任务记录。

初始仓库只建立已经存在并准备维护的目录，不预先创建大量未来空目录。目标结构可以逐步收敛为：

```text
aiis-ics-arch/
├── AGENTS.md
├── README.md
├── README.zh-CN.md
├── PLAN.md
├── PLAN.zh-CN.md
├── CHANGELOG.md
├── CHANGELOG.zh-CN.md
├── mutil-project-pm.md
├── backend/
├── frontend-js/
├── control-agent/
├── tools/
├── contracts/
├── design-system/
├── release/
└── plans/
```

`release/` 只保存发布脚本、manifest 模板、校验工具和说明，不复制保存：

```text
release/v1/backend
release/v1/frontend
```

历史源码版本由 Git release 分支和 tag 保存，不在同一仓库中重复复制整套源代码。

### 4.2 公开仓禁止内容

`aiis-ics-arch` 将公开到 GitHub，首次提交前必须排除：

- 客户名称、项目编号和客户品牌；
- 真实数据库地址、用户名、密码、token、证书和私钥；
- 项目专用 PLC IP、点位表、设备编号和生产线身份；
- 项目业务数据、测试数据、Excel 输入输出和 SQL dump；
- 真实 `.env`、日志、数据库文件和现场截图；
- `.venv`、`node_modules`、`target`、`dist`、`build`、cache 等生成物；
- 项目专用业务模块和项目历史 3MD；
- 未完成脱敏的 `Vibe L2`、项目路径和旧仓库身份。

公开仓的 `LICENSE` 必须由 Human Owner 明确选择；未决定开源许可证前不得推送公开仓库。

## 5. 项目仓

项目仓不是只保存差异代码的薄壳，而是完整、独立、可交付的源码仓库。

```text
aiis-ics-l2-<project-id>/
├── AGENTS.md
├── README.md
├── README.zh-CN.md
├── PLAN.md
├── PLAN.zh-CN.md
├── CHANGELOG.md
├── CHANGELOG.zh-CN.md
├── ARCH_BASELINE.md
├── backend/
│   └── app/
│       ├── system/
│       ├── user/
│       ├── equipment/
│       ├── maintenance/
│       ├── quality/
│       └── ...
├── frontend-js/
│   └── src/app/
│       ├── system/
│       ├── equipment/
│       ├── maintenance/
│       ├── quality/
│       └── ...
├── tools/
├── docker-compose.yml
├── docker-compose.dev.yml
└── plans/
```

不再拆出 `backend-module/` 或 `frontend-module/`。项目模块直接放入现有标准位置：

```text
backend/app/<module>/
frontend-js/src/app/<module>/
```

项目仓负责项目业务模块、项目权限组合、项目 Alembic migration、seed、PLC 点位、快照策略、
映射输入、S7 模拟配置、Docker、部署和现场验收事实。

### 5.1 模块注册和数据库边界

后端普通模块通过 `backend/app/<module>/manifest.py` 声明名称、启用状态、路由、模型包和权限。

- `enabled=True`：模块 API 注册并进入 OpenAPI。
- `enabled=False`：模块 API 不注册。
- 模块关闭不等于删除表。
- models 被发现不等于数据库表自动创建。
- 新表、字段和索引仍必须通过 Alembic migration。
- 认证、权限、Control Agent 等高风险能力继续保留显式安全边界。

## 6. 模块仓 `aiis-ics-modules`

模块仓部署在 Gitee 私有仓库，不放在 GitHub，不与公开架构仓混合。

建议结构：

```text
aiis-ics-modules/
├── README.md
├── README.zh-CN.md
├── MODULES.md
├── backend/
│   ├── equipment/
│   ├── maintenance/
│   └── quality/
├── frontend-js/
│   ├── equipment/
│   ├── maintenance/
│   └── quality/
└── docs/
    ├── equipment.md
    ├── maintenance.md
    └── quality.md
```

每个模块说明至少记录：

- 模块用途和边界；
- backend 与 frontend-js 是否必须配套；
- 兼容的架构版本；
- 依赖的其他模块；
- 权限、API 和 pageId；
- 数据表和 migration 要求；
- 接入、初始化、验证和移除方式；
- 已知限制。

第一阶段不增加重复的 `project.yaml + module.lock.yaml` 体系。模块自身继续使用 `manifest.py`，
模块仓通过 `MODULES.md` 和模块说明管理跨仓关系。

## 7. 能力归属判断

### 7.1 放入架构仓

- 所有项目都需要；
- 属于认证、权限、模块注册、系统管理或 Projection 控制面基础能力；
- 属于统一构建、运行、升级或安全合同；
- 属于 Control Agent、通用工具或基础设计系统；
- 缺失后项目不能按标准结构运行。

### 7.2 放入模块仓

- 可能被至少两个项目使用；
- 不是所有项目都必须安装；
- 已移除客户名称、项目号、真实配置和专有数据；
- 有明确依赖、migration、权限、接入和验证说明；
- 已在真实项目完成验证。

### 7.3 保留在项目仓

- 客户特有业务流程；
- 项目专用表结构和初始化数据；
- 现场 PLC 点位、设备编号和生产线配置；
- 客户品牌、文案和权限组合；
- 项目部署、网络、账号和环境事实；
- 尚未证明可复用的实验功能。

## 8. 当前代码的架构提取分类

以下清单用于从一个已完成身份迁移的 `aiis-ics-l2-<project-id>` 提取架构基线，不授权立即删除
源项目内容。

### 8.1 明确保留为 backend 核心

```text
backend/app/user/
backend/app/system/
backend/app/control_agent/
backend/app/schema_maintenance/
backend/app/module_registry.py
backend/app/router.py
```

同时保留 backend 的 `core/`、`common/`、`config/`、`database/`、`projection/`、主程序、构建脚本、
锁文件和与上述核心能力对应的 tests。

### 8.2 明确不进入架构仓的 backend 项目模块

```text
backend/app/auxiliary/
backend/app/dashboard/
backend/app/energy/
backend/app/equipment/
backend/app/hr/
backend/app/maintenance/
backend/app/performance/
backend/app/plan/
backend/app/project/
backend/app/quality/
backend/app/reports/
```

这些模块继续留在项目仓。以后证明可复用后，再逐个提炼到 `aiis-ics-modules`。

### 8.3 `backend/app/monitor` 是混合模块

`monitor` 不能在复制阶段直接整目录删除：当前 `system` Projection mapping 仍引用其中的
`PlcDbBlockRawSnapshot`，而同一模块又包含项目专用的 HMI、温度、能耗和过程曲线。

正式拆分任务应当：

1. 将 raw/latest snapshot、collector state 等平台事实模型移动到明确的核心事实层；
2. 保留通用 collector/runtime 状态 API；
3. 将 HMI、温度、能耗、过程曲线等项目能力留在项目仓或提炼为可选模块；
4. 修复 `system` 对 `app.monitor` 的反向依赖；
5. 通过 migration graph、OpenAPI 和 focused tests 后，才决定是否删除核心仓中的旧 `monitor` 目录。

### 8.4 明确保留为 frontend-js 核心

```text
frontend-js/src/app/system/
frontend-js/src/router/
frontend-js/src/api/
frontend-js/src/components/
frontend-js/src/config/
frontend-js/src/layouts/
frontend-js/src/locales/
frontend-js/src/store/user.js
frontend-js/src/styles/
frontend-js/src/utils/
```

还应保留登录、认证、请求封装、主题、模块 manifest 发现和通用布局能力。

### 8.5 明确不进入架构仓的 frontend-js 项目模块

```text
frontend-js/src/app/auxiliary/
frontend-js/src/app/dashboard/
frontend-js/src/app/equipment/
frontend-js/src/app/maintenance/
frontend-js/src/app/monitor/
frontend-js/src/app/performance/
frontend-js/src/app/plan/
frontend-js/src/app/quality/
```

当前 `monitor` 前端包含项目专用实时 HMI、温度和能耗页面，不直接作为核心监控页面复制。后续可以
在架构仓新建只展示 collector/runtime 通用状态的轻量页面。

### 8.6 删除模块目录后必须同步清理的共享表面

不能只删除 `src/app/<module>`。架构提取任务还要检查和清理：

- `frontend-js/src/layouts/MainLayout.vue` 中的业务菜单和 pageId；
- `frontend-js/src/config/permissions.js` 中的项目页面权限；
- `frontend-js/src/locales/**` 中的业务导航和 breadcrumb；
- `frontend-js/src/store/energyPrice.js` 等业务 store；
- frontend mocks、fixtures、业务样式选择器和业务测试；
- backend 项目 seed、项目 scripts 和业务测试；
- backend 业务模块之间的交叉 import；
- README、PLAN、BUILD、INITIALIZATION、Compose 和源码头中的项目身份。

### 8.7 Alembic 不允许手工批量删除

项目业务 migration 和核心 migration 当前可能位于同一 revision graph。不得根据模块目录名直接删除
Alembic revision。必须由独立任务识别平台表、业务表、依赖关系和 heads，形成可从空数据库建立的
核心 migration graph，并验证不会修改实际项目数据库。

### 8.8 Demo 模块

不要直接把现有 `dashboard` 当作架构 Demo。架构仓后续创建脱敏、默认 `enabled=False`、不创建业务表、
不访问真实数据库/PLC 的 `aiis_demo`，只展示标准模块结构、API 注册、前端页面和 mock 示例。

## 9. tools 提取边界

架构仓保留工具源码、测试、README、pyproject 和 lock，删除项目输入输出：

- 不复制 `tools/.venv` 和 `__pycache__`；
- 不复制项目 Excel、生成 YAML、mapping JSON 和 simulation profile；
- `inputs/`、`outputs/` 只保留空目录或脱敏 sample；
- PLC 点位、快照策略和 S7 模拟配置继续由项目仓拥有；
- 架构仓提供生成器和 schema，不提供某个项目的实际生成结果。

## 10. Control Agent 提取边界

Control Agent 源码从旧 `vibe-l2-front-end/control-agent` 迁入架构仓，但不得复制：

```text
control-agent/.env
control-agent/node_modules/
control-agent/dist/
control-agent/logs/
control-agent/src-tauri/target/
control-agent/src-tauri/logs/
control-agent/config/ 中的项目 YAML
```

迁移后需要独立任务完成：

- `vibe-l2-control-agent` crate、binary、bundle identifier 和产品标题去 Vibe 化；
- 构建后的可写配置根目录；
- `plc_points.yaml` 与 `plc_snapshot_policy.yaml` 成组导入、校验、激活和回滚；
- 数据库连接设置页；
- PostgreSQL adapter；
- MSSQL driver 技术选型与独立可行性 gate；
- CA artifact 版本和 SHA-256 记录。

项目仓不保存 CA 源码，只消费由架构仓固定版本构建并评审的 artifact。项目 YAML 和数据库目标仍由
项目仓拥有，不能编译进通用 CA 二进制。

## 11. contracts、design-system、release 和 runtime

- `contracts/` 可以迁移，但必须先清除 Vibe/项目身份并确认适合作为公开合同。
- `design-system/vibe-l2-next/` 不能以旧名称直接进入公开仓；先重命名并清理项目视觉事实。
- `release/scripts/`、`release/templates/` 和通用 docs 可以迁移。
- `release/out/` 是生成产物，不复制、不提交。
- `runtime/` 当前探索内容不作为首批架构基线；确认有真实源码和长期 Owner 后另立任务迁入。
- `desktop-tauri/` 不是每个项目必需，首批不复制；需要时在架构仓另立可选能力任务。

## 12. 手动复制教程

本节命令只复制到本地 `aiis-ics-arch`，不执行删除、不初始化 Git、不上传 GitHub。复制后必须先完成
脱敏、模块拆分、测试和 public audit。

### 12.1 设置明确路径

```bash
AIIS_PROJECT_SOURCE=/absolute/path/to/private/aiis-ics-l2-project
AIIS_LEGACY_SOURCE=/absolute/path/to/private/legacy-repository
AIIS_ARCH_TARGET=/absolute/path/to/aiis-ics-arch

test -d "$AIIS_PROJECT_SOURCE/backend"
test -d "$AIIS_PROJECT_SOURCE/frontend-js"
test -d "$AIIS_LEGACY_SOURCE/control-agent"
test -d "$AIIS_ARCH_TARGET"
```

### 12.2 复制 backend 工作基线

复制完整 backend 作为本地工作基线，但排除环境、生成物和项目历史 plans。业务模块先保留在本地工作
副本中，随后由架构提取 Development 按第 8 节清理；在清理完成前不得提交到公开 Git 历史。

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  --exclude '.DS_Store' \
  --exclude 'build/' \
  --exclude 'dist/' \
  --exclude 'data/' \
  --exclude 'logs/' \
  --exclude 'plans/' \
  "$AIIS_PROJECT_SOURCE/backend/" "$AIIS_ARCH_TARGET/backend/"
```

### 12.3 复制 frontend-js 工作基线

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.pnpm-store/' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'coverage/' \
  --exclude 'playwright-report/' \
  --exclude 'test-results/' \
  --exclude '.DS_Store' \
  --exclude 'plans/' \
  "$AIIS_PROJECT_SOURCE/frontend-js/" "$AIIS_ARCH_TARGET/frontend-js/"
```

### 12.4 复制 tools 框架，不复制项目输入输出

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.ruff_cache/' \
  --exclude '.DS_Store' \
  --exclude 'inputs/' \
  --exclude 'outputs/' \
  --exclude 'plans/' \
  "$AIIS_PROJECT_SOURCE/tools/" "$AIIS_ARCH_TARGET/tools/"
```

### 12.5 从旧仓复制 Control Agent 源码

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.pnpm-store/' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude 'logs/' \
  --exclude 'config/' \
  --exclude 'plans/' \
  --exclude '.DS_Store' \
  --exclude 'src-tauri/target/' \
  --exclude 'src-tauri/logs/' \
  --exclude 'src-tauri/gen/' \
  "$AIIS_LEGACY_SOURCE/control-agent/" "$AIIS_ARCH_TARGET/control-agent/"
```

`control-agent/plans/` 不进入公开架构仓 staging。CA 历史证据继续保留在旧私有仓；历史任务不做
伪造性改写。需要公开的长期决策由后续任务重新整理为 public-safe 文档。

### 12.6 复制通用合同和 release 源文件

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.DS_Store' \
  "$AIIS_LEGACY_SOURCE/contracts/" "$AIIS_ARCH_TARGET/contracts/"

rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.DS_Store' \
  --exclude 'out/' \
  --exclude 'plans/' \
  "$AIIS_LEGACY_SOURCE/release/" "$AIIS_ARCH_TARGET/release/"
```

`design-system/` 暂不复制，先处理 `vibe-l2-next` 命名；`runtime/` 和 `desktop-tauri/` 也不进入首批复制。

### 12.7 不复制的根内容

不要把项目仓根 README、PLAN、AGENTS、CHANGELOG、Compose 和项目 plans 原样覆盖到架构仓。
架构仓应建立自己的中文 canonical `AGENTS.md`、双语 README/PLAN、CHANGELOG 和独立 3MD。

项目 Compose 可以作为后续模板提取的只读参考，但不能在尚未删除项目模块、数据库身份和 container
命名时直接进入公开架构仓。

## 13. 本地公开前检查

完成架构提取 Development 和验证后，先检查文件名，不读取或打印真实 secret 内容：

```bash
AIIS_ARCH_TARGET=/absolute/path/to/aiis-ics-arch
cd "$AIIS_ARCH_TARGET"

find . -type d \( \
  -name '.venv' -o -name 'node_modules' -o -name 'target' -o \
  -name 'dist' -o -name 'build' -o -name '__pycache__' -o \
  -name '.pytest_cache' -o -name 'logs' -o -name 'data' \
\) -print

find . -type f \( \
  -name '.env*' -o -name '*.pem' -o -name '*.key' -o \
  -name '*.pfx' -o -name '*.p12' -o -name '*.sql' -o \
  -name '.DS_Store' \
\) -print
```

扫描项目身份和旧品牌残留：

```bash
rg -n --hidden \
  -g '!.git/**' \
  -g '!**/plans/archive/**' \
  'AIIS ICS L2 [0-9]|aiis-ics-l2-[0-9]|Vibe L2|vibe-l2|vibe_l2' .
```

扫描疑似连接串和 secret 标记；结果必须人工判断，示例和变量名不等于真实 secret：

```bash
rg -n --hidden \
  -g '!.git/**' \
  -g '!**/*.lock' \
  '(mysql|postgres|postgresql|mssql)://|password\s*=|token\s*=|secret\s*=|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY' .
```

至少运行：

```bash
cd backend
uv lock --check
uv run python -m compileall -q app core database projection scripts tests main.py build.py
uv run pytest -q

cd ../frontend-js
pnpm install --frozen-lockfile
CI=true pnpm build

cd ../tools
uv lock --check

cd ../control-agent
pnpm install --frozen-lockfile
pnpm build
cargo test --manifest-path src-tauri/Cargo.toml
```

具体 focused tests、数据库边界和 CA feature tests 由后续已批准 spec 固定。公开前验证不得连接生产数据库、
真实 PLC 或客户环境。

## 14. GitHub 手动初始化和推送教程

以下步骤只在代码清理、脱敏、测试、LICENSE 决策和 Human Owner final acceptance 全部完成后执行。

### 14.1 在 GitHub 创建空仓库

在 GitHub 创建：

```text
aiis-ics-arch
```

建议设置为 Public。创建时不要自动生成 README、LICENSE 或 `.gitignore`，避免与本地文件冲突。

### 14.2 初始化本地 Git

```bash
AIIS_ARCH_TARGET=/absolute/path/to/aiis-ics-arch
cd "$AIIS_ARCH_TARGET"

git init -b main
git status --short
git add -n .
```

`git add -n .` 只预演。确认没有 `.env`、日志、数据库、项目 Excel、PLC YAML、生成物和客户信息后：

```bash
git add .
git diff --cached --check
git diff --cached --stat
git status --short
```

人工检查暂存内容后提交：

```bash
git commit -m "chore: initialize AIIS ICS Architecture"
```

### 14.3 连接 GitHub 并推送 main

将 `<github-account>` 替换为实际 GitHub 账号或组织：

```bash
git remote add origin https://github.com/<github-account>/aiis-ics-arch.git
git remote -v
git ls-remote --heads origin
git push -u origin main
```

这一步只推送 GitHub，不添加 Gitee remote。`aiis-ics-modules` 后续才在 Gitee 建立私有仓库。

### 14.4 固定第一个版本

不要在未经验证的原始复制状态创建 `1.0.0`。当架构核心和 CA 基线通过完整验收后：

```bash
git switch main
git pull --ff-only
git branch release/1.0.0
git tag -a v1.0.0 -m "AIIS ICS Architecture 1.0.0"
git push origin release/1.0.0
git push origin v1.0.0
```

长期云端分支为：

```text
main
release/<version>
```

临时 feature/PR 分支合并后删除。已发布 tag 不移动；修复形成 `release/1.0.1` 和 `v1.0.1`，不覆盖
`1.0.0`。

## 15. 发布形式

backend、frontend-js、tools 和 modules 以源码版本作为正式基线：

- 不提交 `.venv`、`node_modules`、`dist` 和本地 build；
- 不在仓库内建立 `release/v1/backend` 源码副本；
- 目标系统根据 lock 重新安装和构建；
- 构建成功后记录系统、版本、commit 和验证结果。

Control Agent 是特殊交付物：源码只在架构仓维护，项目消费针对目标系统构建并评审的 artifact。CA
二进制可以作为 GitHub Release asset 或离线交付包发布，但必须记录 arch tag、commit、目标系统和
SHA-256；二进制不替代源码 release。

## 16. 新项目创建和升级

新项目流程：

1. 从架构仓选择稳定 `release/<version>` 或 tag；
2. 复制项目所需 backend、frontend-js、tools、Compose 和治理模板；
3. 不复制 Control Agent 源码；
4. 建立项目身份和独立 Task Namespace；
5. 在 `ARCH_BASELINE.md` 记录 arch URL、tag、commit、采用组件和日期；
6. 按需从模块仓复制模块；
7. 创建项目 Alembic migration、权限、PLC 和环境配置；
8. 完成 backend、frontend、Docker 和现场验证；
9. 推送 Gitee 私有项目仓。

项目升级不自动跟踪 arch `main`。每次升级建立项目自己的任务，比较目标 release、选择性导入变更、
保留项目模块和配置、检查 migration graph、完成测试和 Docker 验证，再更新 `ARCH_BASELINE.md` 和
CHANGELOG。

## 17. 模块提炼流程

模块先在项目仓完成真实开发，再考虑进入 Gitee 私有模块仓：

1. 确认不是单一客户专有；
2. 清除客户名称、项目号、账号、配置和数据；
3. 整理 backend/frontend-js 配套关系；
4. 提供权限、migration、seed、接入和测试说明；
5. 在模块仓建立独立 3MD；
6. 导入第二个测试项目验证；
7. Human Owner 接受后进入 `MODULES.md`。

不能把项目目录原样复制到模块仓并宣称为通用模块。

## 18. 3MD 与治理

三个仓库分别拥有自己的 `AGENTS.md`、README/PLAN、plans 和 Human Owner gate。跨仓任务使用完整身份：

```text
aiis-ics-arch::ARCH-001
aiis-ics-arch::CA-CONFIG-001
aiis-ics-modules::MODULE-001
aiis-ics-l2-<project-id>::UPGRADE-001
```

架构仓的验收不能自动替代项目仓或模块仓验收。公开 arch 的任务记录不得包含客户 secret；私有项目
和模块任务也不能被公开 arch 反向引用为运行依赖。

## 19. 已废弃方案

新版方案明确废弃：

- `frontend-custom` / `backend-custom` 反向软链接项目；
- 项目运行时软链接到 Core；
- `release/v1/backend` 形式复制历史源码；
- 只有 `backend-module` / `frontend-module` 的薄项目仓；
- 项目动态依赖模块仓；
- 仅因目录存在就无条件暴露后端 API；
- 把 models 自动发现当作数据库 migration；
- 把项目 YAML 编译进通用 CA；
- 把设置页、YAML 编辑、PostgreSQL 和 MSSQL 塞进一个 Development 任务。

## 20. 当前执行顺序

1. 首个 `aiis-ics-l2-<project-id>` 完成独立项目迁移、验证和 Gitee 私有仓推送。
2. 旧 Vibe 仓继续作为私有历史来源。
3. 在本地 `aiis-ics-arch` 落本方案和 ARCH-001 PM spec。
4. 手动复制工作基线，但不立即 GitHub push。
5. ARCH-001 Development 完成去项目化、脱敏、模块拆分和验证。
6. Human Owner final acceptance 后初始化 Git，并推送 GitHub public `main`。
7. 架构核心稳定后创建 `release/1.0.0` 和 `v1.0.0`。
8. 在架构仓依次规划 CA 配置、设置页、PostgreSQL 和 MSSQL gate。
9. 架构基线稳定后，再初始化 Gitee 私有 `aiis-ics-modules`。
