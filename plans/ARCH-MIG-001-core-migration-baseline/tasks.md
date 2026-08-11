# ARCH-MIG-001 Development 任务记录

Task ID: ARCH-MIG-001  
Revision: r1  
Status: developer_handoff  
Owner Role: Development  
Allowed Writers: Development  
Task Namespace: aiis-ics-arch  
Execution Mode: agent_team_same_session  
Approved: Human Owner 于 2026-08-10 批准 `aiis-ics-arch::ARCH-MIG-001 r1`，按 spec 精确范围和 allowlist 开始 Development。  
Handoff: Development completed; waiting for fresh-context Verification

## 1. 目标与边界

本轮只在 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 目标仓完成 ARCH-MIG-001 r1：以当前 Core SQLAlchemy metadata 为真相，删除复制进目标仓的三条项目期 Alembic 历史，创建固定文件名和 revision 的单一 Core root baseline，并以 no-DB 静态证据交接。

本轮未修改 Model、Schema、Service、API、settings、lock、Compose 或 `backend/alembic/env.py`，未触碰来源仓、私有项目仓或 modules 仓。未连接或修改任何真实数据库，未执行 Alembic online、Docker lifecycle、Git/GitHub、release、PLC 或 Control Agent 动作。既有私有项目继续保留自己的 migration 图；Docker 空 volume runtime proof 仍归 ARCH-DOCKER-001。

## 2. 精确执行清单

- [x] 读取 ARCH-MIG-001 r1、ARCH-001 r2 三文件、backend/root 双语 README/PLAN 和相关治理/后端/索引技能。
- [x] 记录并删除目标仓的三份复制历史：
  `20260721_1600_a9d7e5c3b1f0_create_current_schema_baseline.py`、
  `20260723_1800_b68d7e5c3b1f_add_performance_duration_fields.py`、
  `20260725_1200_c17d9e8f4a21_add_performance_transform_lineage.py`。
- [x] 创建 `20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`，固定 `revision = "d4e6f8a0b2c4"` 与 `down_revision = None`。
- [x] 创建 `backend/tests/test_core_migration_baseline.py`，执行 migration 的实际记录 operation，并与导入后的 `Base.metadata` 做机械 parity 比较。
- [x] 同步 backend/root 双语 README/PLAN、plans README pair 和 `CODE_INDEX.md` 的 migration 事实；未预先创建 QA `checklist.md`。
- [x] 按 spec 验证并记录真实命令、退出码、替代 harness 和环境限制。
- [x] 将本文件交接为 `developer_handoff`，由 fresh-context Verification 创建并填写 `checklist.md`。

## 3. 实施记录

### 2026-08-10 — Development completion

- Active versions 目录现在只包含 `20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`。该 migration 为新空库的显式 Alembic baseline，按依赖顺序使用实际 `op.create_table`、`op.create_foreign_key` 和 `op.create_index`，未使用 `create_all()`、动态补表或空 migration。
- Baseline 实际创建以下 14 张 Core 表：`users`、`token_blacklist`、`sys_dicts`、`sys_dict_items`、`projection_mapping_sets`、`projection_mapping_revisions`、`projection_mapping_bindings`、`projection_mapping_audit_events`、`projection_runtime_cursors`、`projection_runtime_audit_events`、`control_agent_gate_tokens`、`monitor_collector_states`、`plc_db_block_raw_snapshots`、`plc_db_block_latest_snapshots`。cycle FK `fk_projection_mapping_set_active_revision` 在两张 mapping 表创建后显式补上；共显式声明 39 个 index。
- `downgrade()` 先删除 cycle FK，再按反依赖顺序删除全部 14 张表；没有项目表、seed、数据迁移或外部副作用。
- `backend/tests/test_core_migration_baseline.py` 的 `MigrationRecorder` 替代 Alembic op surface，执行 migration `upgrade()` 的实际操作，建立记录 metadata，并比较每张实际记录表与导入完成后的 `Base.metadata` 的列、类型/长度/精度/时区、nullable、PK、FK、unique/check、index、server default。测试另行验证 14 表集合、39 indexes、downgrade 反序和 active version 禁止残留。
- 未修改 `backend/alembic/env.py`：现有 target metadata 导入已足够，未发现需要扩大的导入或 runtime 行为。
- 双语事实文档已同步为单一 Core root baseline；未修改 `spec.md`、任何 Model/API/settings/lock/Compose 文件或来源仓。

## 4. 验证证据

### 4.1 核心静态 parity/no-DB

- `cd backend && UV_CACHE_DIR=/private/tmp/archmig-uv-cache uv lock --check`：exit 0，resolved 81 packages。
- `cd backend && UV_CACHE_DIR=/private/tmp/archmig-uv-cache uv lock`：exit 0；`backend/uv.lock` 内容和 mtime 未变化，未把 lock 变更纳入本轮。
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/archmig-compile-cache UV_CACHE_DIR=/private/tmp/archmig-uv-cache uv run --no-sync python -m compileall -q app core database projection scripts tests main.py build.py`：exit 0。
- 用缓存的 Python 3.11、SQLAlchemy/Alembic 依赖和仅用于隔离 settings/engine 的 no-DB stub 直接加载当前 Core model packages，运行新测试的三个函数：
  `test_core_baseline_executes_real_operations_and_matches_metadata`、
  `test_downgrade_drops_every_core_table_in_reverse_dependency_order`、
  `test_active_versions_are_one_core_revision_without_project_residue` 均 PASS。该 harness 记录并执行真实 migration operation；parity 不是第二份手写 schema 常量比较。未创建数据库或发起连接。
- `cd backend && uv run --no-project --python <cached-python-3.11> alembic heads`：exit 0，唯一 head 为 `d4e6f8a0b2c4 (head)`。
- 同环境 `uv run --no-project --python <cached-python-3.11> alembic history`：exit 0，仅显示 `<base> -> d4e6f8a0b2c4 (head)`。
- 使用同一缓存依赖、占位 `settings`/`jose` module 和 `alembic upgrade head --sql` 的离线渲染：exit 0，输出保存于 `/private/tmp/archmig-offline-uv.sql`；326 行、15 个 `CREATE TABLE`（14 个 Core 表加 Alembic `alembic_version`）、39 个 index 定义、最终版本插入 `d4e6f8a0b2c4`。该命令只生成 SQL，使用占位配置，没有数据库连接。

### 4.2 标准环境限制（真实记录）

- `cd backend && UV_CACHE_DIR=/private/tmp/archmig-uv-cache uv sync --locked --no-install-project --offline` 未完成：离线缓存缺少 lock 中的 `pandas==3.0.2`，命令以非零退出；本轮删除了该命令创建的临时 `.venv`。
- `cd backend && PYTHONPYCACHEPREFIX=/private/tmp/archmig-pycache UV_CACHE_DIR=/private/tmp/archmig-uv-cache uv run --no-sync python -m pytest -q -p no:cacheprovider -m no_db` 未完成：在无完整项目环境的 target venv 中 `pytest` 不存在（`No module named pytest`）。先前尝试的跨缓存全量 pytest 还受到不匹配的 cryptography/FastAPI/Pydantic 依赖阻塞；因此没有把标准 no-DB 回归写成通过，也没有伪造 QA verdict。
- 未执行 Alembic online、真实 DB、Docker、Git/GitHub、PLC/CA 或生产动作；offline SQL 和自定义 parity harness 不能替代后续空 volume runtime proof。

## 5. Development self-check

- [x] AC-001：本轮消费的 PM spec 为 Human Owner 已批准的 r1；未修改 spec，也未在批准前创建角色文件。
- [x] AC-002：写入限定在本 tasks.md 与 spec §5 allowlist；来源仓、私有项目仓和 modules 仓保持未写入。
- [x] AC-003：active versions 仅一份固定 baseline；`revision=d4e6f8a0b2c4`、`down_revision=None`；静态 heads/history 各为单一 root/head。
- [x] AC-004：实际 `upgrade()` operation 创建且仅创建 spec 规定的 14 张 Core 表；未写项目表或业务数据。
- [x] AC-005：测试执行并记录真实 `op.create_table`/`op.create_foreign_key`/`op.create_index`，对比当前 `Base.metadata` 的结构签名；未以手写常量或 ignore 掩盖差异。
- [x] AC-006：`downgrade()` 反依赖删除 14 张表并清除 cycle FK；自定义 recorder 测试 PASS。
- [x] AC-007：未改 env.py；Core metadata 导入未在本轮执行 DDL、seed 或 runtime 初始化。
- [x] AC-008：active migration source 和版本目录无旧 revision 依赖及 applicants/equipment/performance/project/quality 项目残留。
- [x] AC-009：lock/compileall/parity/heads/history/offline static checks 已通过；标准 `pytest -m no_db` 因离线依赖和空 venv 限制未完成，已保留具体阻塞证据，不作豁免或 QA 结论。
- [x] AC-010：backend/root 双语文档、PLAN/catalog 和 `CODE_INDEX.md` 已同步新 baseline 事实。
- [x] AC-011：本 `tasks.md` 记录精确删除/创建、命令、结果、限制和 Development self-check；fresh-context QA 文件未创建。
- [x] AC-012：本轮未运行真实 DB/Alembic online、Docker lifecycle、Git/GitHub、release、PLC/CA 或生产动作。

Development 自检不等于 fresh-context QA verdict，也不等于 Human Owner final acceptance。

## 6. 限制、风险与交接

- 当前锁定依赖在本环境无法离线完整安装，标准 pytest/no-DB 回归需在依赖可用的干净环境重新运行。
- offline SQL 使用占位 settings/jose 和缓存解释器完成静态渲染，仅证明 Alembic SQL 生成路径，不证明 MySQL/其他 provider 的 online 运行兼容性。
- 未执行真实空数据库 `upgrade head`、downgrade、healthcheck 或 Docker volume lifecycle；这些属于后续 ARCH-DOCKER-001。
- cycle FK 的具体方言运行行为、部署环境默认值和已有私有项目数据库兼容性未在本任务扩大验证；私有项目 migration 历史保持独立。
- fresh-context Verification 需要重新读取 spec、本 tasks.md 和全部实现，独立核对实际 migration operations 与 Core metadata，并创建唯一的 `checklist.md` 给出正式 QA verdict。Human Owner final acceptance、发布、部署和回滚仍未发生。

Development 已完成并交接为 `developer_handoff`。
