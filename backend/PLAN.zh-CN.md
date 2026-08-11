# 后端计划

English version: [PLAN.md](PLAN.md)

## 当前基线

- Core 模块：user、system、control_agent、schema_maintenance、monitor、aiis_demo。
- 普通模块通过 manifest opt-in；安全/运行时边界模块保持显式挂载。
- monitor Core 仅保留 collector/raw/latest 现场事实。
- `ARCH-MIG-001 r1` 已替换为仅含十四张 Core 表的单一 `d4e6f8a0b2c4` root；operation/metadata parity、
  downgrade 与 single-head 证据已通过 fresh-context Verification，并获得 Human Owner 最终验收。
- `ARCH-DOCKER-001 r1` 空 volume runtime 证明已获 Human Owner 接受。`ARCH-001 r3` Development 已恢复
  固定名称的热更新开发栈与 production-shaped 外部数据库 config/build 表面；下一步是 fresh-context r3 Verification。

详细工作记录归根目录架构任务三文件和单独获批的 backend 任务；本索引不承载项目业务 backlog。
