# DS计划

[English](PLAN.md) · [任务目录](plans/README.zh-CN.md)

本工程 PLAN 管理 DS 后续产品任务；根目录和 AW 只保留总体摘要及入口。根 ARCH-AW-005 历史原件保持原位；Human Owner已于2026-10-27（Asia/Shanghai）最终验收DS-001 r1及ARCH-AW-005 r5。

| 任务 | 状态 | 范围与下一步 |
| --- | --- | --- |
| [DS-001 r1：策略表格、批量编辑与界面整改](plans/DS-001-policy-table-and-usability/spec.md) | `owner_accepted` | Human Owner于2026-10-27接受DS当前版本，见[验收及收尾](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)。策略/批量编辑、输入/易用性、纯文字手册及另批DIRECT整改已交付；[DEV记录](plans/DS-001-policy-table-and-usability/tasks.md)保留原时点，独立QA未执行（DS-001例外）。本轮只收尾，未追加功能或整套QA。 |
| [ARCH-AW-005 r5：历史产品基线](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md) | `owner_accepted` | Human Owner于2026-10-27最终接受r5，见[验收及资源保留](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)。原QA4的qa_passed按精确候选保留，全部旧失败及G0退役证据保留；后续DS-001人工验收及DIRECT修正不倒记为旧QA4证据。 |
| [aiis-ics-arch::DAA-007 r2：关联联调启动配置](../data-acquisition-agent/plans/DAA-007-ds-joint-validation-and-time-contract/spec.md) | `implementation_in_progress` | 列明DS源码.env/profile增量已实施并完成必要自检，归DAA-007 r2冻结候选；既有DS验收保持，Owner联调及fresh核验待发生，不新建DS bundle。 |

DAA–DS读取至SQLite联调另批，阶段C暂不开展；本任务人工验收例外不改变后续联调核验要求。
