# 最小源码导入对

[English](README.md)

归 [DAA PLAN](../../../../PLAN.zh-CN.md) 管理，本结构性夹具用于 DAA-004 受控源码导入验证。`minimal.db` / `minimal.udt` 为手写 UTF-8 源码，不是实际 TIA 导出或现场输入。`expected.json` 依据获批叶表先于源码独立编写，是验证清单，不是运行时配置或 parser 生成结果。

在普通点位页的文件输入中同时选择 DB 及其 UDT，均绑定所选的停用 PLC，并显式填写 DB 编号 **21**。DB 声明 `MinimalImport`、标准访问，唯一字段 `payload` 引用 `MinimalPayload`。

| sourcePath | 类型 | 导入默认值 |
| --- | --- | --- |
| `payload.ready` | BOOL | 停用、未分组、无地址 |
| `payload.count` | INT | 停用、未分组、无地址 |
| `payload.temperature` | REAL | 停用、未分组、无地址 |

期望 2 个编辑来源、1 个 complete/non-flat DB 及完整引用展开树、3 点、0 组。source/DB/point ID 由服务产生，检查 PLC/DB/source 引用及重载稳定性，不预设 UUID。来源 SHA-256 应与所选文件原字节一致。不推算本 UDT 的 offset，也不把默认 length 当实证 DB 长度。

只选 DB 会诊断缺失 UDT；预览与取消不提交。本次验证只在完整配对且无 issues 后确认，再重载并对账同一自有 SQLite 库。既有确认语义可以保存带诊断候选，本夹具不新增阻断规则。激活、连接和启采不在验证范围。本对文件不证明实际 TIA 导出兼容、PLC 地址或真实设备行为。YAML 一次性私有 receipt 与显式源码导入分开并保持不变。
