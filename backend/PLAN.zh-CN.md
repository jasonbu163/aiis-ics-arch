# 后端计划

English version: [PLAN.md](PLAN.md)

## 当前基线

- [ARCH-BE-005 r3](../plans/ARCH-BE-005-backend-business-module-reintegration/spec.md)：`owner_accepted`；独立 A 及两轮隔离 MySQL 各五场景、专用资源清理完成，Human Owner 于 2026-10-16 最终验收；保留全部历史。

- [ARCH-BE-006 r1](../plans/ARCH-BE-006-mapping-business-api-expansion/spec.md)：`qa_passed`；A+B 独立验证通过，两轮专用 MySQL 及五页浏览器检查完成，资源与测试秘密已清理；155 项相关测试通过，四项历史冻结 profile 失败保留；Human Owner 最终验收 pending。

- [ARCH-BE-004 r2](../plans/ARCH-BE-004-energy-price-hourly-history/spec.md)：`owner_accepted`；记录时间小时覆盖、选日历史与新增弹窗已独立验证，F-001 已关闭；Human Owner 于 2026-10-13 完成人工试用并接受，真实数据迁移另行授权。

- [ARCH-BE-002 r3](../plans/ARCH-BE-002-energy-price-api/spec.md)：`owner_accepted`；在本仓库新增可复用 auxiliary 价格切片、三个 API 与后继迁移；独立 QA 通过，Human Owner 已于 2026-10-13 验收 r3，真实数据库/运行验证另行授权。
- [ARCH-BE-003 r3](../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md)：`qa_passed`; r3 A/B 独立通过：当前源码 483 通过/30 未选及编译通过，两轮 MySQL 各三场景全部通过；F-001/B-001 关闭，专用资源和测试口令已清理，待 Human Owner 最终验收.

- Core 模块：user、system、control_agent、schema_maintenance、monitor、aiis_demo。
- 普通模块通过 manifest opt-in；安全/运行时边界模块保持显式挂载。
- monitor Core 仅保留 collector/raw/latest 现场事实。
- `ARCH-MIG-001 r1` 已替换为仅含十四张 Core 表的单一 `d4e6f8a0b2c4` root；operation/metadata parity、
  downgrade 与 single-head 证据已通过 fresh-context Verification，并获得 Human Owner 最终验收。
- `ARCH-DOCKER-001 r1` 空 volume runtime 证明已获 Human Owner 接受。`ARCH-001 r3` Development 已恢复
  固定名称的热更新开发栈与 production-shaped 外部数据库 config/build 表面；下一步是 fresh-context r3 Verification。

详细工作记录归根目录架构任务三文件和单独获批的 backend 任务；本索引不承载项目业务 backlog。
