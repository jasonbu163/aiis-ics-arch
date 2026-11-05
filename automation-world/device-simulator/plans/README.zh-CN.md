# DS任务目录

[English](README.md) · [DS计划](../PLAN.zh-CN.md)

后续 DS 产品任务的唯一范围归本地 `plans/<任务>/spec.md`，进度归本工程 PLAN。ARCH-AW-005作为根目录历史关联保留，不搬动、复制或继承其审批和验收。

| 任务 | 状态 | 范围入口 | 后续记录 |
| --- | --- | --- | --- |
| DS-002 多协议设备模拟与设备读写调试设计 | `draft` | [r1 spec](DS-002-multi-protocol-simulation-and-device-debugging/spec.md) | 实际PM设计待Human Owner精确批准；后续实施阶段分别批准。tasks.md待精确实施范围获批后由Development创建，checklist.md待真实交接后由fresh-context Verification创建；当前两份文档均未创建。 |
| DS-001 策略表格、批量编辑与界面整改 | `owner_accepted` | [r1 spec](DS-001-policy-table-and-usability/spec.md) | Human Owner于2026-10-27最终接受当前版本，见[验收/收尾](DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)。[实施/自检记录](DS-001-policy-table-and-usability/tasks.md)及[纯文字手册](../USER_GUIDE.zh-CN.md)保留；独立QA/checklist未执行（本任务例外）。 |
| 关联aiis-ics-arch::DAA-007 r2启动增量 | `owner_accepted` | [DAA唯一spec](../../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | 关联DAA-007 r2及本次受控阶段B已于2026-10-30验收。DS启动配置增量按DAA记录接受，不倒记为DS旧QA/接受。历史限制保留，阶段C/自动启动/现场另项。 |

历史基线：[ARCH-AW-005 r5 spec](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) · [DEV记录](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) · [核验及2026-10-27 Owner最终接受](../../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)。历史技术QA与Owner接受分层保留；DAA–DS读取至SQLite联调另批，阶段C暂不开展。
