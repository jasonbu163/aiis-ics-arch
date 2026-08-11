Task ID: ARCH-MIG-001
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner final acceptance recorded; ARCH-MIG-001 r1 closed, with ARCH-DOCKER-001 remaining a separate gate

Task Namespace: aiis-ics-arch  
Execution Mode: agent_team_same_session  
Verification Context: fresh-context Verification, independent of Development reasoning  
Verification Date: 2026-08-10  
Verification Root: `/Users/jason/Desktop/DreamCode/aiis-ics-arch`  
Role Separation: independent QA / Verification; only this checklist was written  

## 1. 验证依据与边界

本轮从 fresh context 重新读取了目标仓根 `AGENTS.md`、`README.md`、`README.zh-CN.md`、
`PLAN.md`、`PLAN.zh-CN.md`，backend `README.md` / `README.zh-CN.md`、`PLAN.md` /
`PLAN.zh-CN.md`，根 `plans/README.md` / `plans/README.zh-CN.md`，
`ARCH-001 r2` 三文件，`ARCH-MIG-001 r1` 的 `spec.md` 与 `tasks.md`，以及当前
Alembic migration、Core Model、`alembic/env.py`、parity test 和 `CODE_INDEX.md`。

本轮按 `project-governance`、`backend-arch`（含 `references/DATABASE_AND_MIGRATIONS.md`）和
`code-document-indexer` 的验证规则执行。Verification 只创建本文件；没有修改 `spec.md`、
`tasks.md`、migration、Model、测试、README/PLAN、`CODE_INDEX.md`、配置、锁文件或外部仓库。
没有执行真实 DB/Alembic online、Docker lifecycle、Git/GitHub、release/tag、PLC/Control Agent
或生产动作。

## 2. 环境与前置条件

| 项目 | 事实 |
| --- | --- |
| 主机 | macOS arm64；`uv 0.7.8`；目标仓无 `.git`、`.github`、项目 `.venv`、Docker Compose 或 `LICENSE`。 |
| 项目运行时 | `backend/pyproject.toml` 要求 Python `>=3.11`；缓存的 CPython 3.11.12 可用。 |
| 标准依赖 | 目标仓没有已安装的 pytest 运行环境；离线缓存也没有所需 pytest/Alembic wheel，网络 DNS 受限。真实错误见 §3。 |
| 隔离 harness | 使用缓存的 CPython 3.11.12 与只读缓存的 SQLAlchemy/Alembic 依赖；仅 stub FastAPI/settings 与 API package startup，实际加载 Core Model、migration 和 Alembic operation。stub 不连接数据库。 |
| 临时输出 | Python bytecode、uv cache、offline SQL 和日志路径均指向 `/private/tmp/archmig-*`；未在目标仓保留 `.venv`、`__pycache__` 或数据库文件。 |

## 3. 命令、证据与结果

| 区域 | 命令/检查 | 结果 |
| --- | --- | --- |
| Lock | `cd backend && UV_CACHE_DIR=/private/tmp/archmig-verify-uv-cache uv lock --check` | 通过；解析 81 packages。 |
| Compile | `cd backend && UV_CACHE_DIR=/private/tmp/archmig-verify-uv-cache PYTHONPYCACHEPREFIX=/private/tmp/archmig-verify-pycache uv run --no-project --python 3.13 python -m compileall -q app core database projection scripts tests main.py build.py` | 通过；仅静态编译。 |
| 标准 focused pytest | `cd backend && UV_CACHE_DIR=/private/tmp/archmig-verify-uv-cache uv run --no-sync python -m pytest -q tests/test_core_migration_baseline.py -p no:cacheprovider` | 未运行：uv 创建临时 `.venv` 后报告 `/backend/.venv/bin/python: No module named pytest`；Verification 已删除该临时目录。 |
| 依赖安装复核 | `uv run --no-project --offline --python <cached-3.11> --with pytest ...` 及 `--with alembic` | 未运行：离线 resolver 报 `pytest was not found in the cache` / `alembic was not found in the cache`；联网尝试报 DNS `Could not connect ... mirrors.aliyun.com ... nodename nor servname provided`。 |
| Migration parity | 隔离 CPython 3.11 harness 直接加载 `tests/test_core_migration_baseline.py`，执行 `test_core_baseline_executes_real_operations_and_matches_metadata`、`test_downgrade_drops_every_core_table_in_reverse_dependency_order`、`test_active_versions_are_one_core_revision_without_project_residue` | 三项均 PASS。实际 `upgrade()` operation 被 recorder 执行；未使用数据库连接。 |
| Core metadata | 同一隔离 harness 读取实际 `Base.metadata` | 14 张表：`users`、`token_blacklist`、`sys_dicts`、`sys_dict_items`、`projection_mapping_sets`、`projection_mapping_revisions`、`projection_mapping_bindings`、`projection_mapping_audit_events`、`projection_runtime_cursors`、`projection_runtime_audit_events`、`control_agent_gate_tokens`、`monitor_collector_states`、`plc_db_block_raw_snapshots`、`plc_db_block_latest_snapshots`；39 indexes。 |
| Operation counts | recorder 结果与 parity test | 14 `create_table`、1 cycle `create_foreign_key`、39 `create_index`；实际表集合与 `Base.metadata` 结构签名（列、类型/长度/精度/时区、nullable、PK、server default、FK、unique/check/index）一致。 |
| Alembic graph | `PYTHONPYCACHEPREFIX=/private/tmp/archmig-verify-pycache PYTHONPATH=<cached site-packages>:backend <cached-3.11>/bin/python3.11 -m alembic heads`；同环境 `history` | 通过；唯一 head：`d4e6f8a0b2c4 (head)`；唯一历史：`<base> -> d4e6f8a0b2c4 (head)`。 |
| Offline SQL | Alembic `upgrade head --sql`，占位 MySQL `mysql+aiomysql` URL，输出 `/private/tmp/archmig-verify-offline.sql` | 通过；326 行、15 个 `CREATE TABLE`（14 Core + `alembic_version`）、39 个 index definitions（含 2 个 unique index）、`d4e6f8a0b2c4` version insert；未建立连接。 |
| Downgrade | parity test 的 recorder operation 顺序 | 先删除 cycle FK，再按依赖反序删除 14 张表；metadata 最终为空。 |
| Active residue | `find backend/alembic/versions -maxdepth 1 -name '*.py'`、旧三文件精确路径检查、active source `rg` forbidden markers | 仅存在 `20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`；旧三文件均 ABSENT；active source 无 `applicants`、`equipment_`、`performance_`、`projects`、`quality_` 或旧 revision ID。 |
| env/import boundary | 读取 `backend/alembic/env.py`、`app/module_registry.py` 与 Core models；MySQL placeholder offline render | `target_metadata = Base.metadata`；model/manifest import 只暴露 metadata；offline render 无 SQLite/database file、seed/mock/DDL startup 或外部连接。online path 未执行。 |
| Docs/index | 交叉读取 backend/root 双语 README/PLAN、plans catalog、`CODE_INDEX.md`，并 `rg` migration facts | 双语文档均指向单一 `d4e6f8a0b2c4`、14 表、parity test；未把三条项目期历史描述为当前 Core baseline；`CODE_INDEX.md` 包含新 migration/parity 入口。 |
| External boundary | `find` 检查 `.git`、`.github`、Compose、`LICENSE`、DB/dump/SQLite artifacts；本轮命令审计 | 目标仓无上述发布/DB 产物；未执行真实 DB、Docker、Git/GitHub、release、PLC/CA。 |

## 4. Acceptance Audit（AC-001..AC-012）

| AC | Verdict | 独立证据与说明 |
| --- | --- | --- |
| AC-001 | 通过 | `spec.md`、`tasks.md` 与本 checklist 的 Task ID/Revision 均为 `ARCH-MIG-001` / `r1`；spec 为 `owner_approved`、tasks 为 `developer_handoff`；Verification 在交接后首次创建本文件，无提前 QA 文件。 |
| AC-002 | 通过（范围证据） | `tasks.md` 列出三份旧 migration 删除、固定 baseline/test 与事实文档 allowlist；本轮只写本 checklist，未触达来源仓、私有项目仓或 modules。无 Git 历史可供反向核验，Development handoff 的只读声明保留为边界证据。 |
| AC-003 | 通过 | active versions 只有固定文件；source metadata 为 `revision = "d4e6f8a0b2c4"`、`down_revision = None`；heads/history 均为唯一 root/head。 |
| AC-004 | 通过 | 实际 recorder operation 创建且仅创建 spec 固定的 14 张 Core 表；metadata 表集合与 operation 表集合相同；无业务数据写入。 |
| AC-005 | 通过 | 独立执行 migration 实际 `create_table`/`create_foreign_key`/`create_index` 后，逐表比较当前 `Base.metadata` 的列/类型、nullable、PK、FK、unique/check/index 与 server defaults；39 index 与 14 表均一致，不是仅比较第二份手写 schema。 |
| AC-006 | 通过 | 独立 recorder 验证 downgrade 先清除 cycle FK，随后按反依赖顺序删除全部 14 表；无旧项目表操作或数据/外部副作用。 |
| AC-007 | 通过（no-DB） | `env.py` 使用当前 `Base.metadata`，显式 Core Model import 与 registry model import 无 `create_all`/seed/mock/connection；MySQL placeholder offline render 成功，未建立数据库连接。online migration 未运行。 |
| AC-008 | 通过 | active versions 目录无旧三 revision 文件；active baseline source 无 applicants/equipment/performance/project/quality 表名或旧 revision 依赖；forbidden residue test PASS。 |
| AC-009 | 通过（AC-009 允许的环境 limitation） | `uv lock --check`、compileall、独立 migration parity、downgrade、heads/history、offline SQL 均通过。标准项目 `pytest`/完整 `-m no_db` 未重现，真实原因是目标 `.venv` 缺 pytest、离线 cache 缺包、网络 DNS 失败；这些错误已记录，且核心 parity/单 head 不被豁免，因此按 spec 的“不可运行项给出真实阻塞证据”归类为 limitation，不构成实现失败。 |
| AC-010 | 通过 | backend/root 双语 README/PLAN、plans catalog 与 `CODE_INDEX.md` 均记录单一 Core root、14 表和 parity test；未将项目期 migration 图当作当前 baseline。 |
| AC-011 | 通过 | `tasks.md` 记录 Development 精确删除/创建、命令、结果和限制；本文件由 developer_handoff 后 fresh-context 独立创建并给出正式 verdict。 |
| AC-012 | 通过 | 未运行真实 DB/Alembic online、Docker lifecycle、Git/GitHub、release、PLC/CA 或生产动作；empty-volume runtime 明确保留给 `ARCH-DOCKER-001`。 |

## 5. Acceptance Audit 总结

| Area | Current acceptance state | Next handling |
| --- | --- | --- |
| Core migration source truth | Human Owner accepted for r1 static/no-DB scope | Preserve as the public Core migration baseline; runtime proof remains separate. |
| Operation/metadata parity | Accepted | Preserve the fixed 14-table set; any schema redesign requires a new PM Revision. |
| Revision graph and downgrade | Accepted | Keep one `d4e6f8a0b2c4` root/head; do not restore project history in this public Core. |
| Standard project pytest/no-DB environment | Not independently rerun | Re-run in an environment with the locked Python/dependencies if Human Owner requires; this is an AC-009 environment limitation, not an observed implementation failure. |
| Empty-volume runtime / healthcheck | Deferred gate | Create and approve `ARCH-DOCKER-001`; no Docker action is authorized by this task. |
| PLAN/catalog aggregate row | Pending index synchronization | This Verification surface is restricted to `checklist.md`; PM/Human Owner may update `PLAN.*` and `plans/README.*` after reviewing this verdict. |

## 6. Blockers、限制与失败回路

### Blockers

本任务 r1 无实现 blocker，未发现需退回 Development 的 migration/parity/downgrade failure。
QA 给出的 `qa_passed` 仅表示本 spec 的 source/static/no-DB acceptance gates 已满足；Human Owner
最终验收已在 §8 单独记录。该验收仍不授权发布、部署、数据库写入、Docker、Git/GitHub、平台 ACL
或强制路由能力。

### Limitations

1. 目标仓锁定依赖不能在当前环境完整安装：`uv run --no-sync` 报缺少 pytest，offline resolver
   报 pytest/Alembic 不在 cache，联网尝试因 DNS 失败。标准全套 no-DB regression 因此未运行；真实
   错误未被写成通过。
2. 独立 parity/offline harness 使用缓存 CPython 3.11、只读依赖 site-packages、placeholder
   settings 与 API package stubs，隔离应用启动和数据库连接；它验证实际 migration operations 与
   Core metadata，不等价于完整项目安装或 online runtime。
3. offline SQL 采用 MySQL placeholder dialect；未验证任何真实数据库、多方言 online 行为，也未运行
   `upgrade`/`downgrade` against database。SQLite cycle-FK online/runtime 行为仍属于后续环境验证。
4. 目标仓没有 Git history，无法用 Git diff 反向证明外部来源仓的写入状态；本轮命令仅在 Verification
   Root 内执行，Development handoff 的来源只读声明仍是该边界的可用证据。
5. Verification 完成时根/backend PLAN 与 plans catalog 曾显示 `developer_handoff`；协调会话已在
   QA verdict 后同步为 `qa_passed`，并在本次 Human Owner 最终验收后进一步同步为 `owner_accepted`。

### Rework routing

若 Human Owner 要求锁定环境完整 no-DB 回归，按同一 r1 重新运行并追加 QA 证据；若发现表结构、
revision、allowlist、风险或验收范围发生实质变化，必须停止并回到 PM 新 Revision，不得在本文件
静默改范围。若后续出现实际 migration implementation failure，应以精确证据返回 Development。

## 7. QA Verdict 与 Handoff

**QA verdict: `qa_passed`**

ARCH-MIG-001 r1 的单一 Core root、固定 revision/down_revision、14 表实际 upgrade operations、
operation-to-`Base.metadata` parity、downgrade 逆序、env no-DB import boundary、项目表/旧 ID
残留清理、双语文档/index 事实和外部边界均已独立核验。AC-009 的标准 pytest/no-DB 全套只因
环境依赖缺失未重现；由于核心 parity 与单 root/head 已通过且 spec 明确允许对不可运行项提供真实
阻塞证据，本项记录为 limitation，不改判 `qa_blocked` 或 `qa_failed`。

Handoff：本 `qa_passed` 结果已由 Human Owner 最终验收，记录见 §8。`ARCH-DOCKER-001` 仍负责空
volume runtime proof；本任务接受不授权 GitHub、release/tag、Docker、真实数据库、PLC/CA 或生产动作。

## 8. Human Owner 最终验收

- 验收日期：2026-08-10。
- Human Owner 明确指示：`Human Owner 最终接受 aiis-ics-arch::ARCH-MIG-001 r1。`
- 最终状态：`owner_accepted`。
- 接受范围严格限于 r1 已验证的单一 Core root、固定 14 表、operation/metadata parity、downgrade、
  single-head 与 source/static/no-DB 边界；§6 的标准依赖环境限制继续保留为事实。
- 本次接受关闭 `ARCH-MIG-001 r1`，但不自动接受 `ARCH-001`，不启动 `ARCH-DOCKER-001`，也不授权
  Docker、真实数据库、许可证选择、Git/GitHub、release/tag、PLC/CA 或生产动作。
