Task ID: ARCH-PLC-001
Revision: r8
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification
Handoff: Human Owner 决定是否按 r8 已列范围与风险最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch

# r8 独立文档复核 · 2026-11-18

**结论为 `qa_passed`，覆盖 r8 文档标准 C01–C05。** 本轮从 fresh context 读取[批准规格](spec.md)、[Development 交接](tasks.md)及其引用的七个任务 bundle。产品功能与原 r7 A06/A08 继续按下列历史证据及缺口判断。

| 标准 | 结果与独立核对依据 |
| --- | --- |
| C01 | 通过。逐一核对下表历史 checklist、批准 spec 及交接。旧时点失败和阻塞均有记录。父 r7 完整附录的字节摘要与 r8 声明一致。 |
| C02 | 通过。Owner 的界面报告、协调者的本机观察、Development 摘要与独立 QA 可分别追溯。私有会话的脱敏汇总与交接一致，具体覆盖见下文。 |
| C03 | 通过。交接明确标出原 A06/A08 及四个实施任务遗留风险，没有以其他轮次或层级补齐缺证。 |
| C04 | 通过。父 spec 与 tasks 的 SHA 均匹配精确 handoff。已有产品候选叠加变化，历史 QA 与当前组合树按时点分别记载。父任务文档复核无 blocker。 |
| C05 | 通过。五项精确范围批准见父 spec §5 及四个子任务各自 spec。各子任务由各自 Verification 交 Owner，两个 r5 可以各自终验。 |

| Task、Revision 与历史证据 | 独立核对的历史结论及衔接 |
| --- | --- |
| [DS-003 r5](../../device-simulator/plans/DS-003-plc-json-export/checklist.md)、[DAA-017 r5](../../data-acquisition-agent/plans/DAA-017-plc-json-import/checklist.md) | 两项各自 QA1 failed、QA2 曾 blocked，受控互通返修后各为 qa_passed；各待 Owner 终验。 |
| [DS-004 r2](../../device-simulator/plans/DS-004-bilingual-point-display-names/checklist.md) → [r3](../../device-simulator/plans/DS-004-bilingual-point-display-names/spec.md) | QA1–3 有失败，r2 QA4 总体 blocked。r3 单独批准文档收尾。 |
| [DAA-018 r3](../../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/checklist.md) → [r4](../../data-acquisition-agent/plans/DAA-018-bilingual-point-display-names/spec.md) | QA1 failed，QA2 定向复核后总体 blocked。r4 单独批准文档收尾。 |
| [DS-005 r2](../../device-simulator/plans/DS-005-plc-json-bidirectional/checklist.md) → [r3](../../device-simulator/plans/DS-005-plc-json-bidirectional/spec.md) | 保留 QA1 索引失败、后续手册失败和定向复验，旧候选总体 blocked。r3 单独批准文档收尾。 |
| [DAA-019 r2](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/checklist.md) → [r3](../../data-acquisition-agent/plans/DAA-019-plc-json-bidirectional/spec.md) | QA1、QA3、QA5 分别有失败，QA6 通过限定手册复验，旧候选总体 blocked。r3 单独批准文档收尾。 |
| [ARCH-PLC-002 r1](../ARCH-PLC-002-plc-json-export-feedback/checklist.md) | QA1 failed、QA2 passed，Owner 已明确验收导出命名与反馈。其历史指纹比较记录 DS 30 项中 12 项、DAA 36 项中 11 项变化，旧候选 QA 不覆盖后续组合树。 |

## 证据层级与仍未知的事实

- Owner 报告 DS、DAA 中英文切换和 DAA→DS→DAA 原生往返，DAA 拒绝当前同源，将历史文件导入为新本机实例后自动选中并显示 4 点。历史独立 QA 分别记录文件投影、普通 DB/UDT 和合成服务等限定比对。该轮原生 IPC 返回未截获。旧轮 context、样本其他列及 sample_delivery 缺逐行前值；后轮 37 表核对只适用于自身比较窗口。原 A06 仍缺证。
- 协调者 11 月 18 日观察本机 DAA v2 seq 91–103 共 13 条，sampleId 匹配，回执 status 为 committed，outcome 为 created 或 duplicate，正文与回执哈希有效。请求端未见显示名字段或对应双语文本；本机 MySQL history 所核点集未见显示类字段，来源、正文 SHA 及指定点的名称、类型、值、质量匹配。服务端检查限于所列字段和值。latest 为 3 点 good、最新 seq 103，来源绑定匹配，同期 DS 日志无 WARN/ERROR，最后 3 条于 14:39 获回执后目标待发 0，另有 44 条历史 local-only。
- 本 Verification 只读取 spec §2 私有定位中存留的工具结果。脱敏汇总显示样本 13、回执及哈希有效、请求无显示字段、history 找到/匹配/无显示字段均为 13、latest 点数 3、目标待发 0；双语对应文本命中分别为 0。绑定、日志、回执时点等按协调者观察引用。Development 的只读自检记在 tasks。历史工件已清理，只能审阅持久摘要。原 A08 的全路径、未设值和组合候选回归仍缺证，旧 test-only v1、fake transport 与该轮实际 v2 各按原记录理解。
- DS-004 原生编辑、顶栏、列宽跨重启/复位、普通入口与正常关闭重开未完整证明，通用 F3 无保存交错以及未知回执/异常时序保留。DAA-018 旧普通 native 遇新字段的拒绝、无误采、无空库误建及完整原生交互仍缺证；此前隔离事件影响未知。真实 PLC、Windows/VM、长稳和部署均未验证。

## 环境、命令与交接

正式交付树 main，`git rev-parse HEAD` 为 `f7c5608c0e433612b15821a578a7ef3e4f155cdb`。根契约适用，AW 范围内无单独 AGENTS.md。按 aiis、project-governance 复核根与 AW 文档、workflow、精确 bundle 及历史候选记录。分支内存在并行变化，各子任务结论按自身追加记录读取。

- `shasum -a 256` 核对父 spec 为 `38085d5f0dd5d9db444008b9e04963371ddff3995cbb050641281ce6517931e5`，tasks 为 `eb4914c2acdcddc3b8ad36f0b218b583bb7eb489f13721032e18e1085c4a2013`。Python 3 hashlib 重算 r7 附录为 `8c1e3f11da7b2784c95df2008d095a1ca1c34d0ad3ac78e90ec2ada426497b59`。均 exit 0。
- `git diff --numstat` 对父目录显示 tracked spec 增 249 行、删 0 行；交接 tasks 为新增文件。Python 3 全文读取父子 bundle，并核对 tasks 的 26 个相对文件链接，exit 0。`git diff --check` 对父目录 exit 0；新增本清单另用 Python 检查链接和尾随空白。
- 本轮只创建本清单，无临时资源。未运行产品测试、构建或 GUI，未访问应用 profile、数据库、网络、设备或重新上报。提交 Human Owner 对父 r8 的文档结论及所列风险单独终验。
