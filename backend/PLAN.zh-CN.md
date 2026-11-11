# 后端计划

English version: [PLAN.md](PLAN.md)

## 当前基线

- [ARCH-ACQ-003 r2](../plans/ARCH-ACQ-003-acquisition-data-optional-filters/spec.md)：`owner_accepted`。指定 dev 库已到 `4e6a8b0d2f14`，两张事实表的原记录对账一致。Human Owner 于 2026-11-11 验收 r2 提供方及指定 dev 范围。

- ARCH-ACQ-002 r2 已通过独立 QA。`3d5f7a9c1e23` 已清退指定 3307 dev 库的九张空表并保留两张 v2 表，待 Human Owner 最终验收。 [QA 记录](../plans/ARCH-ACQ-002-legacy-projection-retirement/checklist.md)
- ARCH-BE-012 r4 在 `2c4e6a8b0d12` 引入样本接口和两张 v2 表。独立源码复核和 dev 功能检查已通过，原隔离矩阵和最终验收待完成。 [QA 记录](../plans/ARCH-BE-012-simplified-plc-facts/checklist.md)

- [ARCH-BE-009 r1](../plans/ARCH-BE-009-backend-facts-integration/spec.md)：`owner_accepted`；Development 9项正式MySQL及42项扩展；fresh QA独立通过9项正式、47项具名扩展、181项聚焦和44项旧测试（9项未选）通过；A与全部失败史保留。2容器/2卷/2网及8专用库、27份临时口令/操作配置已清理且独立核验。Human Owner于2026-11-05验收获批源码及隔离A+B交付；真实采用、DAA/SMA联调及生产长期SLA仍为独立gate；现有库/真实历史未操作。

- [ARCH-BE-010 r2](../plans/ARCH-BE-010-anonymous-business-integration/spec.md)：`owner_accepted`；两轮真实MySQL/ASGI/时间/并发/断线、各161项受影响源码回归及事实清理后永久业务回执通过；A与全部失败史保留。2容器/2卷/2网及8专用库、27份临时口令/操作配置已清理且独立核验。Human Owner于2026-11-05验收获批源码及隔离A+B交付；真实采用、DAA/SMA联调及生产长期SLA仍为独立gate；现有库/真实历史未操作。

- [ARCH-BE-005 r3](../plans/ARCH-BE-005-backend-business-module-reintegration/spec.md)：`owner_accepted`；独立 A 及两轮隔离 MySQL 各五场景、专用资源清理完成，Human Owner 于 2026-10-16 最终验收；保留全部历史。

- [ARCH-BE-006 r1](../plans/ARCH-BE-006-mapping-business-api-expansion/spec.md)：`qa_passed`；A+B 独立验证通过，两轮专用 MySQL 及五页浏览器检查完成，资源与测试秘密已清理；155 项相关测试通过，四项历史冻结 profile 失败保留；Human Owner 最终验收 pending。

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md)：`owner_accepted`；记录时间小时覆盖、选日历史与新增弹窗已独立验证，F-001 已关闭；Human Owner 于 2026-10-13 完成人工试用并接受，真实数据迁移另行授权。

- [ARCH-BE-002 r3](../plans/ARCH-BE-002-energy-price-api/spec.md)：`owner_accepted`；在本仓库新增可复用 auxiliary 价格切片、三个 API 与后继迁移；独立 QA 通过，Human Owner 已于 2026-10-13 验收 r3，真实数据库/运行验证另行授权。
- [ARCH-BE-003 r3](../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md)：`qa_passed`; r3 A/B 独立通过：当前源码 483 通过/30 未选及编译通过，两轮 MySQL 各三场景全部通过；F-001/B-001 关闭，专用资源和测试口令已清理，待 Human Owner 最终验收.

- Core 模块：user、system、control_agent、schema_maintenance、monitor、aiis_demo。
- 普通模块通过 manifest opt-in；安全/运行时边界模块保持显式挂载。
- monitor Core 提供采集器状态。旧 raw/latest 快照表及对应 Core 查询已清退。
- `ARCH-MIG-001 r1` 已替换为仅含十四张 Core 表的单一 `d4e6f8a0b2c4` root；operation/metadata parity、
  downgrade 与 single-head 证据已通过 fresh-context Verification，并获得 Human Owner 最终验收。
- `ARCH-DOCKER-001 r1` 空 volume runtime 证明已获 Human Owner 接受。`ARCH-001 r3` Development 已恢复
  固定名称的热更新开发栈与 production-shaped 外部数据库 config/build 表面；fresh-context r3 Verification及Human Owner接受已在[ARCH-001](../plans/ARCH-001-public-architecture-baseline-extraction/checklist.md)完成；这份历史Core接受不代后续provider完成采用。

详细工作记录归根目录架构任务三文件和单独获批的 backend 任务；本索引不承载项目业务 backlog。

API-only `plc_facts` owner 写入 v2 样本，通过样本历史和逐点最新值两张表提供授权查询。历史迁移链包含 BE-009 `0a2c4e6f8b10` → BE-010 `1b3d5f7a9c20`。BE-010 拥有四张业务集成表及有限时间兼容。Human Owner 于 2026-11-05 验收 BE-009、BE-010 两项获批源码与隔离 A+B 交付。两项的实际目标采用及 DAA/SMA 联调仍单独处理。
