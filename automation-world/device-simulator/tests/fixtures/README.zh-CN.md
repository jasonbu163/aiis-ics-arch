# 合成输入与独立期望

- `protocol-workspace.json` 只为原 W/C/D/X 回归保留 DB41（1024 字节）、DB57（64 字节）、DSG0A001/B001 marker、绝对 offset 及权限向量；产品没有这种默认拓扑。测试先经真实配置/布局/命名/确认/apply 服务装配，再启动。
- `product-workspace.json` 在两个批准端口配置 UUID A 的 DB71/88/109 和 UUID B 的 DB94/130；通过真实 S7 写/读独立整数、finite REAL 与完整 STRING bytes，A reset/stop/新版本 apply 时 B 持续读取。
- `typed-vectors.json` 包含手写 min/zero/max 大端期望；REAL 按预期 IEEE f32 位比较，不与无关 f64 十进制舍入残差直接比较；STRING 核完整两字节头和补零尾部。
- `rules-vectors.json` 固定独立 SHA-256 输入消息及确定随机规则期望，另有周期/phase/floor 测试。规则使用模拟单调时钟，pause/stop 冻结该时钟。
- `invalid-cases.json` 列合成边界与来源拒绝组；清单本身不是执行证明，结果必须由 Rust 消费者测试与 raw 建立。

DS 测试直接只读原共享/DAA 夹具路径的 v1 `names.db`、`names.udt`、`expected-v1.json` 与四个 layout oracle，不复制、规范化、重生成或改写。TIA 声明/BEGIN 初值继续忽略；DS 初值须显式确认。夹具没有真实客户端点或工程源。
