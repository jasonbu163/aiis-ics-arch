# AIIS TIA 导入核心

[English](README.md)

`aiis-tia-import-core` 0.1.0为publish=false、edition2021、仅标准库本地crate。唯一任务权威为[DAA-006 r3](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/spec.md)；DAA以`../../shared/tia-import-core`真实path依赖消费。不建workspace，不依赖registry/runtime/serde或I/O。

[src/lib.rs](src/lib.rs)公开`scan_sources(&[SourceInput], ImportProfile)`，保留调用方UTF-8/BOM/CRLF原字节、安全分界及块级定位诊断；`expand_db(catalog, DeclarationRef, closure)`逐DB使用显式闭包；`layout_standard(ExpandedDb, LayoutProfile)`输出理论byte/bit/长度；`plan_names(NameBatch)`对完整namespace同时命名；`validate_manual_name`与`type_suffix`复用固定规则。低层parser DTO/函数仅用于DAA原来源适配，不构成来源证明或持久化API。

profile固定为`tia-subset-v1`、`siemens-step7-v20-standard-word-v1`、`tia-point-name-v1`，命名黄金版本v1。见[fixture](fixtures/README.zh-CN.md)、[DTO](src/model.rs)、[命名](src/naming.rs)和[独立消费者测试](tests/contract.rs)。

支持命名DATA_BLOCK/TYPE、有界STRUCT/UDT闭包、负/非零下界的一维标量/STRUCT/UDT数组、注释、VERSION、NON_RETAIN/RETAIN和既有布尔S7_SetPoint属性；展开≤8层/4096叶、数组≤1024。UTF-8/源预算明确。初值/BEGIN跳过，不导入或执行。未知语法/类型/属性、声明歧义、缺失/循环UDT、嵌套/多维数组与超限拒绝。STRING[1..254]可导入但整DB拒推；布局要求明确非优化完整结构，oracle不代表真实PLC地址。

命名基于结构化Field/Index、固定suffix、1–100 ASCII字节、全namespace flatten冲突及一次地址兜底，pending无名称。ConfirmedAddress由消费者负责证明确认和DB边界；一个batch必须代表一个PLC，包含停用/legacy/manual保留项。核心不分配ID、不确认或保存地址。

DAA保留raw hash/proof、不可变版本闭包、稳定ID、保守重导、SQL/CAS、receipt、激活及历史。DS自行适配instance/region/identity，校验内存边界，实现初值、大端编码、内存、权限和生命周期；消费固定清单/ref，不fork期望。本crate不实现DS、不关闭阶段B；DAA–DS协议联调及C另批。

基线HEAD=`0af5b91177f3bca63f9f3c2bef9f14004ea49944`，交付为dirty工作树增量，不是发布/ref。原parser SHA、完整文件hash、锁差异、命令raw与限制归[DAA-006 tasks](../../data-acquisition-agent/plans/DAA-006-point-naming-and-import-reuse/tasks.md)；消费者固定完整清单或后续真实ref，不能仅引用“最新DAA”。

```bash
CARGO_TARGET_DIR=/private/tmp/owned-tia-core-target cargo test --manifest-path automation-world/shared/tia-import-core/Cargo.toml --locked
```
