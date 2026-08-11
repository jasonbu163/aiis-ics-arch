# ARCH-MIG-001 Core-only Migration Baseline — PM Spec

Task ID: ARCH-MIG-001  
Revision: r1  
Status: owner_approved  
Owner Role: PM  
Allowed Writers: PM, Human Owner  
Handoff: Human Owner approved r1 on 2026-08-10; handoff to Development for the exact scope and allowlist

Task Namespace: aiis-ics-arch  
Classification: independent_fix  
Capability: Core-only Alembic root baseline extraction and static schema parity  
Owner: AIIS ICS Architecture Backend schema and migration truth  
Depends On: ARCH-001 r2 developer_handoff Core model baseline  
Blocked By: none for Development; Docker runtime proof remains deferred to ARCH-DOCKER-001  
Acceptance Chain Reference: ARCH-MIG-001 r1 PM spec -> Human Owner exact approval -> Development tasks.md -> developer_handoff -> fresh-context Verification checklist.md -> Human Owner final acceptance  
Execution Mode: agent_team_same_session  
Created: 2026-08-10  
Updated: 2026-08-10

Revision History:

- `r1`：根据 ARCH-001 r2 fresh-context Verification 的 AC-006 阻塞建立独立 migration truth 纠偏任务；固定 14 张 Core 表、单 root/head、新空库边界、精确 Development allowlist、静态验证和后续 Docker gate。
- `r1 approval`：Human Owner 于 2026-08-10 明确批准并要求执行 ARCH-MIG-001 r1，将三条项目期 migration 替换为一条包含 14 张 Core 表的干净 root baseline；该批准只授权本 spec 的精确范围和 allowlist。

## 1. PM 结论

`ARCH-MIG-001` 只在尚未发布的 `aiis-ics-arch` 目标仓中，把复制来的项目期 Alembic 历史替换为一条
干净、可审计、面向新空库的 Core root baseline。它不迁移任何既有项目数据库，也不修改私有项目仓
保留的历史 migration。

当前 `backend/alembic/versions/` 有一条三 revision 链：

- `a9d7e5c3b1f0`：root baseline，静态清单包含 67 张表；
- `b68d7e5c3b1f`：依赖 `performance_main`；
- `c17d9e8f4a21`：继续新增 `performance_*` lineage 结构。

Revision 图本身连通且只有一个 head，但它仍包含 applicants、equipment、performance、project、quality
等消费项目表，不能作为公开 Core 的数据库真相。ARCH-001 明确禁止在其范围内静默重写历史，因此由
本独立任务关闭 AC-006。

本仓当前没有 Git 历史、公开 release 或已部署数据库兼容义务。基于这一事实，最小正确方案是单独替换
目标仓的复制历史，而不是在旧的 67 表 root 上追加“删除项目表”的 migration。后者会把项目历史继续
固化进公开 Core，也会为新空库制造无意义的 create-then-drop 链路。

## 2. 当前 Core schema 真相

本 r1 以当前 SQLAlchemy Model 和 Alembic `target_metadata` 为权威输入。Development 不得借本任务新增、
删除、重命名或重设计 Model。当前 Core 表集合固定为以下 14 张：

1. `users`
2. `token_blacklist`
3. `sys_dicts`
4. `sys_dict_items`
5. `projection_mapping_sets`
6. `projection_mapping_revisions`
7. `projection_mapping_bindings`
8. `projection_mapping_audit_events`
9. `projection_runtime_cursors`
10. `projection_runtime_audit_events`
11. `control_agent_gate_tokens`
12. `monitor_collector_states`
13. `plc_db_block_raw_snapshots`
14. `plc_db_block_latest_snapshots`

`alembic_version` 是 Alembic 自身的版本表，不计入上述 14 张业务/Core Model 表。`aiis_demo` 默认关闭且
无 Model 表；`schema_maintenance` 没有独立 Model 表。manifest/metadata discovery 不自动执行 DDL。

## 3. 成功目标

完成后必须同时满足：

1. `backend/alembic/versions/` 只有一条新的 Core baseline revision；
2. 新 revision 的 `down_revision = None`，同时是唯一 root 和唯一 head；
3. `upgrade()` 创建第 2 节的 14 张表及其当前列、主键、外键、唯一约束、检查约束和索引；
4. `downgrade()` 按依赖反序完整删除这 14 张表，不残留项目表操作；
5. migration、当前 `Base.metadata` 和 Alembic `target_metadata` 具有机械可复核的一致性；
6. active migration 中不再出现项目期表、旧项目 Task ID 或旧三 revision 的依赖链；
7. no-DB/static 验证通过，且没有连接或修改任何真实数据库；
8. 后续 `ARCH-DOCKER-001` 可在独立空 volume 上执行 runtime `upgrade head`，但该 runtime 证明不在本任务冒充完成。

## 4. 实施决策

### 4.1 目标历史形态

Development 必须删除目标仓中的三份复制历史，并创建以下唯一 revision：

```text
backend/alembic/versions/20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py
```

固定 revision metadata：

```python
revision = "d4e6f8a0b2c4"
down_revision = None
```

不允许保留旧链再追加清理 revision，不允许创建多个 root/head，不允许用空 migration、跳过导入、
`create_all()` 或运行时补表来伪造通过。

### 4.2 结构一致性

新 baseline 必须显式、可读地表达 14 张表的完整结构。Development 应增加一项可重复的静态测试，
机械核对 migration 实际声明的表/列/约束/索引与当前 Core metadata；测试不得只比较一份手写常量而
不检查实际 `op.create_table` / `op.create_index` 等操作。

若发现当前 Model 本身需要重设计、跨方言语义需要新产品决定，或 migration 无法在不修改 Model 的
情况下准确表达，立即停止并返回 PM 新 Revision；不得在 r1 内顺手改 Model/API/Schema。

### 4.3 兼容与数据库边界

- 新 baseline 只服务从本公开 Core 新建的空数据库。
- 既有私有项目继续保留自己的 migration 图和数据库升级路径；本任务不向它们反向同步。
- 本任务不提供从 67 表项目库“降级”为 14 表 Core 库的路径，也不删除任何真实数据库表。
- 本任务不新增 PostgreSQL/MSSQL/MySQL 能力，不改变当前 database settings、driver 或主库选择。
- 本任务不执行 seed、管理员 bootstrap、业务数据迁移、Alembic stamp/current/upgrade/downgrade 在线动作。
- Docker 空库 runtime smoke、healthcheck 和 volume lifecycle 归后续 `ARCH-DOCKER-001`。

## 5. 精确范围与 Development write allowlist

Human Owner 批准 r1 后，Development 只允许创建、修改或删除以下路径：

### Migration 实现

- 删除 `backend/alembic/versions/20260721_1600_a9d7e5c3b1f0_create_current_schema_baseline.py`
- 删除 `backend/alembic/versions/20260723_1800_b68d7e5c3b1f_add_performance_duration_fields.py`
- 删除 `backend/alembic/versions/20260725_1200_c17d9e8f4a21_add_performance_transform_lineage.py`
- 创建 `backend/alembic/versions/20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`
- `backend/alembic/env.py`（仅当 Core metadata 导入/可重复验证确有必要时做最小修改）
- 创建 `backend/tests/test_core_migration_baseline.py`

### 事实文档与索引

- `backend/README.md`
- `backend/README.zh-CN.md`
- `backend/PLAN.md`
- `backend/PLAN.zh-CN.md`
- `CODE_INDEX.md`
- `PLAN.md`
- `PLAN.zh-CN.md`
- `plans/README.md`
- `plans/README.zh-CN.md`

### 3MD 角色文件

- Development：`plans/ARCH-MIG-001-core-migration-baseline/tasks.md`
- QA / Verification：`plans/ARCH-MIG-001-core-migration-baseline/checklist.md`

PM 已创建的本 `spec.md` 只由 PM/Human Owner 维护。Development 不得修改本 spec 或预先创建
`checklist.md`。如果实现需要触达 Model、Schema、Service、API、settings、lock、Compose、来源仓或
allowlist 外文件，必须停止并提交 PM 新 Revision。

## 6. 明确不做

- 不修改任何来源仓、私有项目仓或 modules 仓；
- 不连接、创建、删除、迁移、stamp 或 seed 真实数据库；
- 不运行 Docker `build/up/down`，不创建或删除 Docker volume；
- 不修改 Model、API、Service、Pydantic Schema、模块 Registry 或 schema-maintenance 行为；
- 不接入项目业务模块或恢复 applicants/equipment/performance/project/quality 等表；
- 不新增数据库 provider/driver 或宣称 MySQL/PostgreSQL/MSSQL 运行兼容已验证；
- 不执行 Git/GitHub、branch、tag、release、CI 或许可证动作；
- 不实现 `ARCH-FE-001`、`CA-CONFIG-001` 或尚未创建 spec 的 `ARCH-DOCKER-001`；
- 不创建数据 dump、备份 SQL、真实 `.env`、凭据、客户数据或构建产物。

## 7. Development 顺序

1. 读取本 spec、ARCH-001 r2 三文件和 backend README/PLAN；记录开始时的 migration 文件与 revision 图。
2. 在 `tasks.md` 记录 Human Owner 对 r1 的精确批准、执行边界和原始三文件清单。
3. 删除三份目标仓复制历史，创建固定文件名/ID 的单 Core root baseline。
4. 增加实际 migration operation 与 Core metadata 的结构一致性测试和 forbidden project table 断言。
5. 仅在必要时最小修正 `alembic/env.py` 的 Core metadata 导入；不得扩大到 Model 改造。
6. 同步 backend 双语 README/PLAN、根 PLAN/catalog 和 `CODE_INDEX.md` 的 migration 事实。
7. 运行第 8 节验证，把真实结果、退出码、环境限制和未运行项写入 `tasks.md`。
8. 状态更新为 `developer_handoff`；由 fresh-context Verification 创建 `checklist.md`。

## 8. 验证矩阵

Development 与 fresh-context Verification 至少覆盖：

| 区域 | 最低验证 |
| --- | --- |
| 文件/图 | `backend/alembic/versions/` 只有固定的新 baseline；revision/down_revision 为单 root/head；旧三个 ID 不在 active versions 中 |
| Schema 集合 | migration 实际 operations 与导入完成后的 Core `Base.metadata` 都只包含第 2 节 14 张表 |
| 结构 | 每张表的列、PK/FK、unique/check/index 被机械核对；upgrade/downgrade 顺序静态可审计 |
| Alembic no-DB | 使用公开占位 env 运行 `uv run alembic heads`、`uv run alembic history` 和可行的 offline SQL render；禁止在线连接 |
| Backend | `uv lock --check`；compileall；`test_core_migration_baseline.py`；现有 `-m no_db` 回归 |
| Forbidden residue | active versions 中无 applicants、equipment、performance、project、quality、旧 Task ID/旧 revision 依赖 |
| 文档 | backend/root PLAN、双语文档、catalog 和 `CODE_INDEX.md` 与新事实一致 |
| 外部边界 | 没有 DB、Docker lifecycle、Git/GitHub、PLC/CA 或 release 动作 |

offline SQL render 如果因当前 Alembic async/dialect 环境限制不能完成，必须记录具体命令和错误；它不能被
写成通过。静态 operation/metadata parity、单 root/head 和 no-DB 回归仍是本任务不可豁免的核心门。

## 9. Acceptance Criteria

| ID | 验收条件 |
| --- | --- |
| AC-001 | `spec.md` metadata/Revision/Execution Mode/allowlist 完整；Human Owner 精确批准前不存在 `tasks.md` 或 `checklist.md`。 |
| AC-002 | Development 只写目标仓精确 allowlist；来源仓、私有项目仓和 modules 仓保持未写入。 |
| AC-003 | active versions 仅有 `20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py`，其 revision 为 `d4e6f8a0b2c4`、`down_revision=None`，Alembic 图恰好一个 root/head。 |
| AC-004 | baseline `upgrade()` 实际创建且仅创建第 2 节 14 张 Core 表；不创建项目表或业务数据。 |
| AC-005 | migration 实际 operations 与 Core metadata 的列、PK/FK、unique/check/index 具有可重复的机械一致性验证，不以手写常量或 ignore 掩盖差异。 |
| AC-006 | `downgrade()` 按依赖反序完整删除 14 张 Core 表，不引用旧项目表，不执行数据/外部副作用。 |
| AC-007 | `alembic/env.py` 的 target metadata 只汇入当前 Core Model；Model/manifest import 不执行 DDL、seed、mock、连接或 runtime 初始化。 |
| AC-008 | active versions 中不存在旧三个 revision 依赖或 applicants/equipment/performance/project/quality 等项目表残留。 |
| AC-009 | backend lock、compileall、迁移结构测试、Alembic heads/history 和现有 no-DB 回归通过，或对不可运行项给出真实阻塞证据；核心 parity/单 head 不得豁免。 |
| AC-010 | backend/root 双语文档、PLAN/catalog 和 `CODE_INDEX.md` 不再把项目期 migration 描述为当前 Core baseline。 |
| AC-011 | `tasks.md` 记录实际删除/创建、命令和 Development self-check；fresh-context `checklist.md` 独立验证并给出正式 verdict。 |
| AC-012 | 未运行真实 DB/Alembic online、Docker lifecycle、Git/GitHub、release、PLC/CA 或生产动作；Docker 空库证明明确保留给 `ARCH-DOCKER-001`。 |

## 10. 风险与回滚

| 风险 | 控制 |
| --- | --- |
| 把项目库升级路径误当 Core 路径 | 新 baseline 只服务公开 Core 新空库；私有项目历史不改、不反向同步。 |
| migration 漏表或约束漂移 | 固定 14 表集合，并机械比较实际 migration operations 与 metadata。 |
| 单 root 中的循环 FK/创建顺序错误 | 允许在同一 baseline 内使用稳定命名和延后约束；runtime 证明由后续空 volume Docker gate 完成。 |
| 删除后缺少本地 Git 回滚 | 删除前在 `tasks.md` 记录精确文件/ID；原始私有来源仓保持只读并保留历史。不得把私有源码备份复制进公开仓。 |
| 为兼容多方言扩大范围 | r1 不新增 provider/driver；发现方言设计问题即停止并回 PM。 |

如 Development 尚未完成 handoff，可在目标仓恢复原三 migration 文件并删除新 baseline/test，回到本
spec 的起始状态。任何恢复都只能发生在目标仓，且要记录在 `tasks.md`。Human Owner final acceptance 后
如需改变已接受 baseline，必须新建 migration Revision，不回写已接受历史。

## 11. Stop conditions

出现以下任一情况立即停止：

- 14 表集合与当前 Model 实际 metadata 不一致；
- 必须修改 Model/API/Schema/settings/lock/Compose 才能完成；
- 需要保留或恢复任一项目表；
- 需要连接真实 DB、执行在线 migration、启动 Docker 或处理业务数据；
- 需要新增第二个 revision/root/head，或改变固定 revision ID/文件名；
- 需要修改来源仓、私有项目仓、modules 仓或 Git 状态；
- material scope、risk、allowlist、compatibility 或 Acceptance Criteria 变化。

material change 必须回到 PM 形成 `r2` 并重新获得 Human Owner 精确批准。

## 12. 批准门与下一步

本 spec 当前为 `owner_approved`。Human Owner 于 2026-08-10 已明确批准并要求执行 r1；标准批准语句为：

```text
批准 aiis-ics-arch::ARCH-MIG-001 r1，按 spec 精确范围和 allowlist 开始 Development。
```

批准事实已成立，Development 现在可以创建 `tasks.md` 并按 allowlist 实施；仍不得运行数据库或 Docker。
后续按 Development -> fresh-context Verification -> Human Owner final acceptance 顺序执行。即使本任务
`owner_accepted`，也只关闭 Core migration source-truth gate；它不等于 ARCH-001 最终接受、Docker
runtime 通过、许可证已决定或 GitHub/release 已授权。
