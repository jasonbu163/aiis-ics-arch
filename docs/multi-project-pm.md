# AIIS ICS 多仓库项目管理与交付方案

Status: 架构迁移基线与长期 dev 环境采用均已获 Human Owner 接受；GitHub `main` 已首次推送，ARCH-REL-001 r3 已批准并处于 Development release preparation，Git/GitHub 写入仍等待 Human Owner 手工执行
Target repository: `aiis-ics-arch`
Hosting: GitHub public repository
Canonical path: `docs/multi-project-pm.md`
Lifecycle owner: 根目录 [PLAN](../PLAN.zh-CN.md)

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

| 类型   | 仓库名                   | 托管位置 | 可见性 | 主要职责                                                |
| ------ | ------------------------ | -------- | ------ | ------------------------------------------------------- |
| 架构仓 | `aiis-ics-arch`        | GitHub   | 公开   | 平台核心、Control Agent、通用工具、模板、版本与架构规范 |
| 项目仓 | `aiis-ics-l2-<项目号>` | Gitee    | 私有   | 客户项目、业务模块、PLC 配置、migration、部署和交付     |
| 模块仓 | `aiis-ics-modules`     | Gitee    | 私有   | 可复用的前后端业务模块和接入说明                        |

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
- Docker、初始化、升级和源码定版合同；
- 根目录 `contracts/` Core 合同中心与 design system；
- `docs/` 下的跨仓库/流程类长期说明、根目录版本记录和 `plans/` 任务记录。

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
├── backend/
├── frontend-js/
├── control-agent/
├── tools/
├── contracts/
├── docs/
│   ├── README.md
│   ├── README.zh-CN.md
│   └── multi-project-pm.md
└── plans/
```

`main` 继续作为后续 Core 开发线。大版本维护线使用字面分支 `release/1.x.x`，未来使用
`release/2.x.x`、`release/3.x.x` 等，并只能在独立获批的对应大版本发布任务中 fast-forward。精确源码
版本只由不可变的 annotated tag 固定，例如 `v1.0.0`、`v1.2.1`、`v2.1.2`。架构仓不建立实体
`release/` 目录，也不以 `release/v1/backend`、`release/v1/frontend` 等路径重复复制整套源代码。

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
├── docker-compose.prod.yml
├── docker-compose.database-only.yml
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

## 11. contracts、design-system、源码定版和 runtime

- 根目录 `contracts/` 是当前 Core 跨运行时公开合同中心，不迁入 `docs/`；其后续变化必须由独立获批任务管理。
- `design-system/vibe-l2-next/` 不能以旧名称直接进入公开仓；先重命名并清理项目视觉事实。
- 源码定版使用 `main`、大版本维护分支与不可变 annotated tag，不迁移或创建实体 `release/` 目录；项目
  消费应锁定精确 tag 或 commit，不直接依赖可移动的维护分支。
- 发布脚本、manifest 模板、校验工具如未来确有复用需求，应由独立任务确定归属；生成产物始终不提交。
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

### 12.6 复制通用合同

```bash
rsync -a \
  --exclude '.git/' \
  --exclude '.env*' \
  --exclude '.DS_Store' \
  "$AIIS_LEGACY_SOURCE/contracts/" "$AIIS_ARCH_TARGET/contracts/"
```

早期迁移方案曾考虑复制旧仓的 `release/` 工具表面；当前源码定版合同已经收敛为 Git branch/tag，
因此不再复制旧仓 `release/`，也不在架构仓创建同名实体目录。

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

## 14. GitHub 当前事实与 1.0.0 手工定版顺序

GitHub public 仓库与首次 `main` 推送已经完成。ARCH-REL-001 r3 只准备 source-only 1.0.0 的受控文档、
碰撞检查、Development 证据和 Human Owner 手工发布交接；它不表示目标 branch/tag 已经发布。

当前发布的精确预检事实、12 路径暂存清单、可复制命令、动态 OID 与命令输出只记录在
[ARCH-REL-001 r3 tasks](../plans/ARCH-REL-001-source-release-1.0.0/tasks.md)。本长期文档不复制这些
易变化的命令或证据，避免形成第二个发布事实面。

长期顺序保持为：Human Owner 在碰撞和 allowlist gate 通过后形成唯一 release-preparation commit 并先
推送 `main`，再从该同一精确 OID 创建并推送 `release/1.x.x` 与 annotated `v1.0.0`；Development
记录 Human Owner 返回的原始输出后才能进入 `developer_handoff`，随后由 fresh-context Verification
独立核对 refs 与 annotated tag。`release/1.x.x` 只作为可 fast-forward 的 1.x 维护线，精确 tag 不移动、
不删除、不 force-update、不重建。最终接受后的治理 receipt 只追加到 `main`，本任务不推进维护分支。

1.0.0 只固定源码，不创建 GitHub Release 页面、不上传 asset、不生成 build artifact，也不执行部署。

## 15. 发布形式

backend、frontend-js、tools 和 modules 以源码版本作为正式基线：

- 不提交 `.venv`、`node_modules`、`dist` 和本地 build；
- 不在仓库内建立 `release/v1/backend` 源码副本；
- 目标系统根据 lock 重新安装和构建；
- 构建成功后记录系统、版本、commit 和验证结果。

Control Agent 是特殊交付物：源码只在架构仓维护，项目消费针对目标系统构建并评审的 artifact。CA
二进制可以作为 GitHub Release asset 或离线交付包发布，但必须记录 arch tag、commit、目标系统和
SHA-256；二进制不替代源码 release。该能力属于未来独立批准的 artifact 任务，ARCH-REL-001 r3 的
source-only 1.0.0 不创建 GitHub Release 页面或 asset。

## 16. 新项目创建和升级

新项目流程：

1. 从架构仓选择精确的 annotated tag 或 commit；只有经过独立批准的维护工作才使用对应的
   `release/1.x.x` 等大版本维护线；
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

截至 2026-08-21，以下迁移步骤已经完成：

1. 首个 `aiis-ics-l2-<project-id>` 已完成独立项目迁移、验证和 Gitee 私有仓推送；
2. `aiis-ics-arch` 已完成去项目化、Core migration 重建、Docker smoke/dev 验证和公开基线验收；
3. GitHub public `main` 已首次推送到 `https://github.com/jasonbu163/aiis-ics-arch.git`；
4. ARCH-DEV-001 r4 已获 Human Owner 接受；
5. ARCH-REL-001 r3 已获批准并进入 Development release preparation；当前动态 OID、branch/tag
   碰撞结果和工作树证据只归属该任务的 `tasks.md`，本长期文档不固化副本；
6. 旧 Vibe 仓保留为私有历史来源，不再承载 Architecture Core 新功能开发。

后续固定顺序为：

1. Development 完成 ARCH-REL-001 r3 的受控文档、碰撞检查、DEV self-check 与 Human Owner 手工交接；
2. Human Owner 只暂存显式批准路径，创建唯一 release commit 并 push `main`；
3. Human Owner 从该同一 OID 创建并 push `release/1.x.x` 与 annotated `v1.0.0`；
4. Development 记录 Human Owner 原始输出后进入 `developer_handoff`，fresh-context Verification 再独立
   核对 local/remote refs、annotated tag 与 peeled commit；
5. Human Owner 最终接受后，只向 `main` 追加 governance receipt，不移动 `v1.0.0` 或在本任务中推进
   `release/1.x.x`；
6. 在后续 `aiis-ics-arch/main` 执行独立的 `ARCH-FE-001` 前端模块自动组装；
7. 在后续 `aiis-ics-arch/main` 执行独立的 `CA-CONFIG-001` 打包配置管理；
8. 根据这两项能力的实际兼容性和验收结果决定下一 Core 版本，预计为 `1.1.0`；
9. 再启动 `aiis-ics-modules::MODULES-001`，从已固定的 Architecture 版本和真实项目提炼模块。

`ARCH-FE-001` 和 `CA-CONFIG-001` 不再从 Vibe L2 定版继续复制或拆分。Vibe 只提供历史参考；从
2026-08-11 起，这两项能力的唯一开发真相源是 `aiis-ics-arch/main`。

## 21. Architecture 长期 Docker dev 环境

本节记录本次迁移完成后的长期 Core 开发入口。它使用 `docker-compose.dev.yml`、MySQL `8.4.6`、
backend/frontend 源码 bind mount、一次性 migration 服务和 named volumes。该环境用于本地开发，
不等于 production readiness，也不替代后续 release gate。

### 21.1 本次 env 迁移事实

Human Owner 将旧 Vibe 环境中的 backend/frontend dev env 复制到 Architecture 仓后，
`ARCH-DEV-001 r2` 做了以下字段级收敛，未记录或输出 secret 值：

- 保留本地开发使用的 `JWT_SECRET_KEY`、`MYSQL_PASSWORD`、`MYSQL_ROOT_PASSWORD`；
- backend 身份改为 `AIIS ICS Architecture`，数据库改为 `aiis_ics_architecture`；
- Compose 内数据库地址固定为 `mysql:3306`；
- Projection、backend mock 和 admin/supervisor/operator bootstrap 默认关闭；
- backend API permission 与 frontend page access 均收敛为空对象；
- frontend 删除旧项目 brand logo/glow 变量；
- 两个真实 env 的 key set 与对应 example 一致，并由根 `.gitignore` 的 `.env.*` 规则忽略。

复用 secret 只适用于本地 dev。若同一值仍用于客户、现场、生产或其他共享环境，必须独立轮换，不能
因为 Git 忽略就把凭据复用当作长期安全方案。

### 21.2 首次启动准备

如果真实 dev env 尚不存在，先从 example 创建：

```bash
cd /Users/jason/Desktop/DreamCode/aiis-ics-arch
cp backend/.env.docker.dev.example backend/.env.docker.dev
cp frontend-js/.env.docker.dev.example frontend-js/.env.docker.dev
```

只在本地编辑 `backend/.env.docker.dev` 中的 JWT/MySQL secret。真实 env 不提交 Git，不把值写进
README、PLAN、3MD、日志或聊天。

可在当前终端定义临时快捷函数：

```bash
dcdev() {
  docker compose \
    --project-name aiis-ics-arch-dev \
    --env-file backend/.env.docker.dev \
    -f docker-compose.dev.yml "$@"
}
```

该函数只在当前终端有效；新开终端后需要重新定义。

### 21.3 首次构建和启动

dev Compose 固定使用以下 Docker Desktop 容器显示名：

```text
aiis-ics-arch-dev-mysql
aiis-ics-arch-dev-migration
aiis-ics-arch-dev-backend
aiis-ics-arch-dev-frontend
```

`bootstrap` 是按需 `run --rm` 的临时维护容器，不固定名字。固定容器名意味着同一 Docker daemon
不能并行启动第二套同名 Architecture dev checkout，也不支持对这四个服务做 Compose scale。

```bash
dcdev config --quiet
dcdev build backend frontend
dcdev up -d mysql
dcdev up migration
dcdev up -d backend frontend
dcdev ps -a
```

预期状态：

- `mysql`、`backend`、`frontend` 为 healthy；
- `migration` 为 `exited (0)`，这是一次性迁移服务的正常终态；
- backend 使用 `http://127.0.0.1:8000`；
- frontend 使用 `http://127.0.0.1:5190`；
- MySQL 宿主机开发端口默认为 `3307`。

只修改 `container_name` 时镜像内容没有变化，不需要重新 build。已有 dev 栈应执行：

```bash
dcdev down --remove-orphans
dcdev up -d backend frontend
dcdev ps -a
```

不要加 `--volumes`；MySQL 数据、backend venv 和 frontend node_modules named volumes 会继续保留。

日志和 HTTP 验证：

```bash
dcdev logs -f backend frontend

curl -fsS http://127.0.0.1:8000/health
curl -I http://127.0.0.1:5190/
curl -i http://127.0.0.1:5190/api/v1/auth/me
```

`/api/v1/auth/me` 未登录时预期返回 `401 Not authenticated`，它可以证明 Vite `/api` proxy 已到达
backend。当前 backend health route 是 `/health`；不要用 `/api/v1/health` 的已知 404 判断 proxy 失败。

### 21.4 日常开发

以后启动 Docker Desktop，进入仓库并重新定义 `dcdev` 后运行：

```bash
dcdev up -d backend frontend
dcdev ps -a
```

- 修改 `backend/` Python 源码后，Uvicorn reload 自动生效；
- 修改 `frontend-js/` 源码后，Vite HMR 自动生效；
- 普通源码修改不需要 rebuild；
- 模块新增、删除、重命名或 manifest 拓扑变化仍应重启对应容器；
- 新增表、字段、约束或索引仍必须新增 Alembic migration，module registry 不自动建表。

后端依赖变化：

```bash
dcdev run --rm backend uv sync --frozen --extra dev
dcdev restart backend
```

前端依赖变化：

```bash
dcdev exec frontend pnpm install --frozen-lockfile
dcdev restart frontend
```

新增 migration 后：

```bash
dcdev run --rm migration
dcdev restart backend
```

只有 Dockerfile、Python/Node 版本、系统依赖、基础镜像或 ODBC driver 变化时才需要重建：

```bash
dcdev up -d --build --force-recreate backend frontend
```

### 21.5 可选本地管理员

Architecture public 默认不创建账号。如果需要登录进行本地 UI 开发：

1. 只在被忽略的 `backend/.env.docker.dev` 中设置强本地密码；
2. 临时把 `ADMIN_BOOTSTRAP_ENABLED` 改为 `True`；
3. 显式运行一次：

```bash
dcdev --profile bootstrap run --rm bootstrap
```

4. 完成后立即把 `ADMIN_BOOTSTRAP_ENABLED` 恢复为 `False`。

不要默认启用 supervisor/operator，也不要把项目权限矩阵复制回 Architecture Core。

### 21.6 停止、保留和清空

临时停止并保留全部容器和数据：

```bash
dcdev stop
```

删除容器和网络，但保留 MySQL、backend venv、frontend node_modules named volumes：

```bash
dcdev down --remove-orphans
```

彻底清空整个本地 dev 环境：

```bash
dcdev down --volumes --remove-orphans
```

最后一条会删除本地 MySQL 数据和依赖 volumes，只能在明确需要重置时使用。MySQL volume 建立后，
仅修改 env 密码不会自动修改数据库内部账号；应通过数据库修改密码，或明确删除 dev volume 后重建。

### 21.7 执行 1.0.0 手工定版前的人工 gate

ARCH-REL-001 r3 已获批准。Human Owner 真正提交前仍需确认 dev 运行状态可接受、没有真实 env 被 Git
跟踪、tracked worktree 只包含精确批准路径，并重新核对本地/远端目标 refs 不存在。当前精确检查命令、
预期输出和发布证据只使用 [ARCH-REL-001 r3 tasks](../plans/ARCH-REL-001-source-release-1.0.0/tasks.md)，
不从本长期文档复制执行。版本分支/tag 只由 Human Owner 手工产生；dev Compose 不产生任何 Git 状态，
本 r3 也不创建 GitHub Release 页面。
