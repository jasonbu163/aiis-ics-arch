Task ID: ARCH-QUALITY-001
Revision: r2
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: r2 已修复 QA1 F1，按文末精确摘要交第二次 fresh-context Verification；独立结论与最终验收待后续记录
Updated: 2026-11-23 Asia/Shanghai

# ARCH-QUALITY-001 r2 Development 实施与自检

## 正式树整合

Human Owner 批准 [r2](spec.md) 的精确 SHA-256 为 `452664c62b4ebf805a5ecfe1fa71c2d7fe6057c843ece8c250a94119eae52afd`。正式交付工作树位于本仓库，HEAD 仍为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。协调者在用户批准的窗口暂停正式目录原有的 `:8000` 开发进程。Development 在写入前以 `lsof -nP -iTCP:8000 -sTCP:LISTEN` 确认端口无监听，核对 r1 补丁摘要与 41 个原始正式文件的存在状态和 SHA-256，通过 `git apply --check` 后将相同补丁整合到正式树。未重启 `:8000`。后端验证直接执行正式源码的 FastAPI 装配和测试，前端从正式 `frontend-js` 构建到独立目录。

r2 另外更新七个文件的唯一当前 head 断言为 `f0a2b4c6d8e1`。只有清退测试的当前元数据预期增加两张质量表，历史集合、版本、父子关系和其他断言保留。七个测试文件共有八行修改，复查 Git diff 已确认用途。正式工作树 48 个源码/测试/合同路径的 SHA-256 均与预期逐一一致。其他并行改动保留。未迁移或连接真实数据库、部署或打开实际报告。

## r2 正式树 DEV self-check

后端验证以正式 `backend/.venv/bin/python` 启动临时目录中的 `r2/isolated_pytest.py`。启动器用 `.env.example` 合成设置，屏蔽真实运行 dotenv，默认拒绝的合成地址为 `127.0.0.1:1`。只有显式 `--quality-mysql` 路径使用独立 fixture 连接。以下命令省略了文末临时目录绝对前缀。

| 命令或方式 | 实际结果 |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python r2/isolated_pytest.py -q -rs` 后接规格 6.1 七个文件 | 66 passed、1 skipped，退出 0。跳过原因是固定到不可变 `f85bea8` 源码的历史 BE003/60 测试。 |
| 同一启动器 `-q` 后接质量专项、五个批准的既有门卫/观察测试、r2 七文件及 `test_business_integration_storage.py` | 173 passed、8 skipped，退出 0。保留在历史路径上的既有测试按原条件跳过。覆盖真实 SQLite 文件和新修订、历史质量读写与 SPC、并发部分更新、五处版本门卫及合同/示例。 |
| `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python r2/isolated_pytest.py --quality-mysql` | MySQL **8.4.6**，`127.0.0.1:13411`，空合成 schema `arch_quality_fixture_13411`。连接内核对实例 UUID、库和账号以及会话时区 `+08:00`。新修订从合成单一前驱升级后重复升级，验证保留前驱哨兵、无 FK、时间列精度与并发合成写入，1 passed，退出 0。验证范围是本次新修订，不重放整个历史迁移链。测试进程已结束；一次性实例由协调者持有并收尾。 |
| `pnpm check:modules` | 9 active modules、30 routes、9 groups，退出 0。 |
| `pnpm test:modules` | 110 passed、3 failed，退出 1。三项失败与 r1 正式基线的监控导航原排序断言一致。新质量组件专项三项通过。 |
| `pnpm build --outDir <temporary>/r2/dist --emptyOutDir` | 退出 0，Vite 非阻断的既有大 chunk 提示。前端使用 r1 记录的相同合成环境变量。 |
| `node <temporary>/r2/browser.cjs` | Chrome/Playwright 实际加载正式 Vite 产物，回环临时服务器，仅用合成权限与截获的 API。退出 0。英文浅色桌面通过链接文字和 URL、键盘打开新标签、详情、部分编辑、空态/失败态、实际拖动列宽、刷新保持、重置、历史导航及管理员菜单和冲突草稿复核。中文深色 430 px 在收起共享侧栏后验证两页及本地字段卡片的标题、筛选、表格左右内容边界。浏览器和临时端口已关闭。 |
| `git diff --check`、逐文件 SHA-256、OpenAPI 与链接 | 退出 0。正式树差异符合 41 个继承路径及 7 个 r2 路径，完整字节摘要见下。正式测试重新比较了 OpenAPI 与实例化路由并执行公开合成示例；18 个新文档相对链接在正式树可解析。 |

## 独立交接

交接精确 Revision **r2** 和上方正式工作树。正式变更清单 `ARCH-QUALITY-001-r2-official-manifest.json` SHA-256 为 `8e8885b1df840c97fe6dc00fc41489c0af94bac9f186dc9e0ff9c6820752c0d4`。清单位于 `/private/tmp/arch-quality-r1.eoaIV6/.quality-development/`。其中包括 48 个文件的前后字节 SHA、r2 规格摘要、r1 补丁摘要和正式基线。源码、合同、七个回归文件和任务记录均在正式树。待独立 Verification 复核正式树及用户入口，包括既有 Monitor 排序测试限制和独立 MySQL 夹具证据。

本次验证产物在上述目录的 `r2/`，含 `isolated_pytest.py`、日志、正式树 Vite 输出、浏览器脚本及四张合成界面截图。浏览器脚本 SHA-256 为 `2e74bf95229f63d08c659588d5501cb602bc0c6405cd968f33b726c51b17b7bb`。原 r1 候选、preimage 和补丁继续保留到独立验证可复现及协调者安全收尾。测试所用 MySQL 容器 `arch-quality-001-r2-dev-13411` 及其专用临时配置由协调者管理。正式 `:8000` 仍暂停。观察模块的既有 README 对私有 profile 的版本描述仍待独立范围维护。真实环境采用、网络隔离、部署和恢复正式开发服务仍按各自权限及准备条件处理。

---

# ARCH-QUALITY-001 r1 候选历史记录

## 授权和候选

Human Owner 已批准 [r1](spec.md)。实施前确认当时单一 Alembic head 为 `e9f3b5d7c021`，修订号 `f0a2b4c6d8e1` 未占用。批准后规格 SHA-256 为 `fdeda1a283a72e1db18938af424224528b9689a3ec81933cd3632355e59b895c`。

正式树存在并行改动，开发后端 `:8000` 还从正式 `backend/` 目录热重载。开发在 `/private/tmp/arch-quality-r1.eoaIV6` 中用当前正式树源码隔离实施，基线 HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。候选沿用现有锁定依赖；后端启动配置仅从仓库公共示例产生，并明确指向不可用的合成地址。浏览器和数据库验证使用合成数据。开发期间仅在正式任务 bundle 写入本记录，源码仍在候选，原运行进程继续使用原目录，未连接真实数据库、启动 Docker 或读取实际报告。

## 实施

- 后端新增独立 `quality_main` 和单行 `quality_field_config`，相同 `taskNo` 只经质量自身归一化并用唯一键约束。质量 API 只访问质量表。新旧质量路由按静态新路径优先注册。
- 管理员可保存带修订号的完整本地字段配置。结果按启用字段投影，完整保留停用值。配置与结果写入先锁配置行，同任务部分更新用该事务读取并合并。未知字段、目标冲突或类型错误不留部分写入。
- 质量列表沿用现有模块路径、页面权限、筛选组件和公共列宽偏好。历史检验可在原入口切换，旧控制页返回历史列表。新增管理员本地字段管理页、配置冲突核对、链接类型及可选显示文本。SPC 和计划、实绩业务文件保持现有实现。
- 共库修订只改批准的五处门卫。新增 revision 经相同的目标身份和注册表布局检查。迁移源码在线先验证前驱和明确的目标，并只创建质量表与初始化空配置。原质量历史记录沿用其时间口径。
- 同步双语合同与模块说明、精简 OpenAPI 切片、合成 API 请求和源码索引。

## DEV self-check

后端命令在候选 `backend/` 中以 `UV_CACHE_DIR=../.quality-development/uv-cache PYTHONDONTWRITEBYTECODE=1 MYSQL_HOST=127.0.0.1 MYSQL_PORT=1 BACKEND_MOCK_ENABLED=false` 运行。前端候选使用 `pnpm_config_verify_deps_before_run=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='["quality.list"]' VITE_OPERATOR_PAGE_ACCESS_JSON='["quality.list"]' VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false`。`uv run --no-sync` 与 pnpm 均使用现有锁定依赖。

| 命令或方式 | 实际结果 |
| --- | --- |
| `uv run --no-sync pytest -q tests/test_quality_results.py tests/test_quality_revision_guards.py tests_mysql/test_quality_results_mysql.py` | 8 passed，1 skipped，退出 0。 SQLite 合成前驱真实执行新 Alembic 修订并重复升级，验证旧表与历史数据、独立写入、并发不同字段、配置启停/权限、筛选、旧 CRUD/SPC 路径及发布 OpenAPI 和示例。MySQL 用例因无隔离目标按契约跳过。 |
| `uv run --no-sync pytest -q tests/test_generic_task_revision_guards.py tests/test_equipment_observation_domain.py tests/test_equipment_observation_r8.py tests/test_equipment_observation_r10.py tests/test_observation_write_sources.py` | 79 passed，退出 0。 |
| 上述既有测试及下列八个不在 r1 allowlist 内的测试文件共跑 | 152 passed，8 skipped，6 failed，7 setup errors，退出 1。执行到的回归失败均由硬编码全局 head 预期引起。 |
| `pnpm check:modules` | 退出 0，9 active modules、30 routes、9 groups。 |
| `node --test tests/module-registry/quality-results.test.mjs` | 3 passed，退出 0。实际编译 Vue setup，覆盖动态列、链接、零值、部分编辑、配置冲突草稿、双语键及历史入口。 |
| `pnpm test:modules` | 110 passed、3 failed，退出 1。失败集中在 monitor.energy 原期望排序。用正式基线执行 `node --test tests/module-registry/registry.test.mjs tests/module-registry/page-access.test.mjs` 得 19 passed、完全相同的 3 failed。这三个测试的质量期望增量与 Monitor 顺序独立。 |
| `pnpm build --outDir ../.quality-development/dist --emptyOutDir` | 退出 0，Vite 非阻断的既有大 chunk 提示。 |
| 新增文档路径、补丁与范围审计 | 18 个新增相对链接存在。41 个源码、测试或合同路径均在 r1 allowlist 内。候选补丁 `git diff --check HEAD`、候选反向 `git apply --check --reverse` 和正式树正向 `git apply --check` 均退出 0。 |

## 正式整合前的限制和仍需证据

- r1 允许改五个运行门卫。以下测试文件不在 r1 allowlist 内，为当前单一全局 head 断言或 fixture 更新范围，保留对各原始修订、下修订和退役表的既有合同断言。
  - `test_acquisition_consumption_contract.py`、`test_equipment_temperature_migration.py`、`test_generic_task_migration_r3.py`、`test_legacy_acquisition_retirement.py`、`test_mapping_migration.py`、`test_observation_receipt_separation.py`、`test_observation_retirement.py`（均在 `backend/tests/`）。
  - `test_legacy_acquisition_retirement.py` 同一用例还固定当前完整元数据表集，修订后需把 `quality_main` 和 `quality_field_config` 加到当前集合，保留历史迁移集合。
  - 一起运行的第八个文件 `test_business_integration_storage.py` 通过。该文件当前逐个验证既有版本。新旧直接目标门卫由质量专项覆盖。
  - `backend/app/equipment_observation/README.md` 和 `README.zh-CN.md` 的私有 profile 说明仍列原修订为唯一许可。两个文件均在 r1 allowlist 外。
- MySQL 8.4 原生迁移和并发尚待隔离执行。合成测试只在已明确提供的 loopback 端口 13411 / 13412、对应初始空 schema `arch_quality_fixture_<port>`、专用 `quality_fixture` 账号运行。需由获授权操作方提供 `QUALITY_FIXTURE_UUID`、`QUALITY_FIXTURE_PORT`、`QUALITY_FIXTURE_SCHEMA`、`QUALITY_FIXTURE_USER`、`QUALITY_FIXTURE_PASSWORD` 和 `QUALITY_FIXTURE_ACK=ARCH-QUALITY-001:<uuid>:<port>:<schema>`，以同一后端测试命令仅运行 `tests_mysql/test_quality_results_mysql.py`。用例在任何 DDL 前验证版本、UUID、schema、账号、时区和空目标。另建议按独立隔离环境核对完整历史迁移链。当前只运行了从合成前驱开始的 SQLite 新修订。真实环境的迁移和运行时切换保持独立授权。
- 普通沙箱拒绝临时 loopback 绑定。Vue 编译、setup 渲染逻辑和产物通过，浏览器实际明暗主题、窄屏对齐、键盘焦点和列宽拖拽待验证。
- 正式树仍由现有后端开发进程监视。由协调者处理安全窗口、校对正式树与候选及启动入口，然后启动 fresh-context Verification。此记录只陈述 Development 候选证据。

## 补丁和临时资源

- 当前正式工作树的精确 preimage 经逐文件核对。候选目录的 `.quality-development/ARCH-QUALITY-001-r1.patch` SHA-256 为 `2140ad206266968a7b352b8e8bdaf2eb3648e40ceca41ff5f0ac5ec000a5186c`。
- 同目录 `ARCH-QUALITY-001-r1-manifest.json` SHA-256 为 `b28f82c25b373ce807c09525b888a4c5498cb1e9357eff7e5734ab2d347b21ad`，列出 41 个精确路径及前后 SHA-256。补丁、manifest、合成测试日志、临时 patch 索引和 Vite 产物均由本任务所有，当前为整合比对保留。整合和独立验证所需证据持久化后，由协调者回收无需保留的临时资源。正式树和共享依赖不属于临时资源。

---

## r2 第一次独立验证返修及再次交接

[Verification](checklist.md) 首轮以 `qa_failed` 退回 F1（AC07）。日期形状的合法标识在列表和详情曾被当作时间截短。Development 在正式工作树只修改 `frontend-js/src/app/quality/views/results/QualityList.vue` 和 `frontend-js/tests/module-registry/quality-results.test.mjs`。固定列和详情传递字段键，只有 `createdAt`、`updatedAt` 做到秒的时间格式化。补充合法标识 `2026-11-23TASK-QUALITY-ALPHA`、`2026-11-23TARGET-QUALITY-ALPHA`、两种时间精度和空值的回归，以及列表和详情模板按键调用的检查。

- `node --test frontend-js/tests/module-registry/quality-results.test.mjs` 在修复后 4 passed、退出 0。新增回归在修复前失败。
- 正式 `frontend-js` 以本记录相同的合成环境执行 `pnpm check:modules` 和 `pnpm build --outDir <temporary>/r2/qa1-rework/dist --emptyOutDir`，退出 0。`pnpm test:modules` 为 111 passed、3 failed，退出 1，仍为原 Monitor 导航排序三项。
- `node <temporary>/r2/qa1-rework/browser.cjs` 退出 0。实际精确检查新构建列表和详情的两个完整标识、两个时间到秒，并重跑先前合成浏览器场景。隔离脚本 SHA-256 `14a39666a2e7ae394833b9325fde00e0660be0b19c756a431f60157f5d37007c`，附本轮 Chrome 日志和四张截图。浏览器和回环临时服务已关闭。
- `git diff --check` 退出 0。核对原交接的 48 项摘要，其中 46 项与首轮一致，两个前端文件有本轮变更。后端实现、迁移、r2 测试补充和规格摘要一致。正式 `:8000` 保持暂停。

再次交接精确 **r2** 的正式工作树。新 `ARCH-QUALITY-001-r2-qa1-rework-manifest.json` 位于 `/private/tmp/arch-quality-r1.eoaIV6/.quality-development/`，SHA-256 为 `79f6179dd819562df7372ed232cb63d42b46166c53fa5367935783893e8e31c6`。保留首轮清单及测试记录供追踪。独立 Verification 复核与资源收尾按原交接流程。
