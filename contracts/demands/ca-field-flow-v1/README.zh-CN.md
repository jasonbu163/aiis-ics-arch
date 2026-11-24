# CA 到 Field Flow 的候选流程 JSON v1

[English](README.md)

状态为 `proposed`。CA 读写此候选格式，Field Flow 独立接受门槛仍待验证。

- [JSON Schema](schema.json) 定义闭合的文件结构，[示例](examples/status-gate.json)及[向量](vectors.json)记录参考流程及结果。
- 流程有且只有一个入口，所有节点可达，无环。互斥分支可以汇合，流程没有并行执行语义。普通节点使用一个 `next` 出口，条件节点使用 `true` 与 `false`，结束节点无出口。引用字段须来自抵达当前节点的所有路径均已执行的上游节点。读取输出 `value`，条件输出 `matched`，HTTP 输出 `status`。条件比较和模拟写入要求输入类型匹配。
- 示例读取逻辑点位 `plc_line_a/task_status`。有效 INT 值为 1 时执行 GET 并以 `matched` 结束。其余有效 INT 值以 `not_matched` 结束。读值缺失、质量异常或类型错误时，本轮报错结束。后续调度在一轮完成后等待设定间隔，同流不重入，不补跑错过的周期。
- 流程文件只携带逻辑引用。地址、凭据、本机路径和运行值留在文件外。使用前在当前 CA 工作区确认资源绑定。此版本仅支持配置和模拟 PLC 写入。
- 文件 SHA-256 对原始 UTF-8 字节计算。语义 SHA-256 仅取去除 `revision` 的 `flow` 对象，排除文件外层和布局。节点按 ID 排序，边按源 ID、端口、目标 ID 排序。递归排序对象键，使用紧凑 UTF-8 JSON，无结尾换行，省略可选的空 HTTP 映射。字符串转义和数值格式以当前候选的 [Rust 序列化实现](../../../automation-world/control-agent/src-tauri/src/domain/ca_flow.rs) 为准。
- 除结构校验外，编辑器检查节点版本、ID 唯一性、连通性、端口、坐标、相对路径、类型及逻辑资源。文件上限 1 MiB，最多 16 层。

后续 FF 独立验证用同一文件摘要关联两条分支、下一轮重新读取及 CA 回导。
