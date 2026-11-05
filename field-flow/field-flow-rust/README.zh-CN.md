# Field Flow Rust

[English](README.md)

Rust是后续长期部署runtime的主要建设方向。当前独立工程已实现HTTP GET→严格命令→SQLite执行状态→标准DB INT，保留原有功能/测试。未来生产flow不强制双语言实现。语言定位不授予目标平台、现场、长稳或生产资格。

完整可照做步骤见[USER_GUIDE](USER_GUIDE.zh-CN.md)，包含自身环境/构建、空cwd帮助、显式init、人工夹具、分开的dry-run/execute教学、inspect/正常停止、真实方法与teaching01逐文件接线。

[BUILD](BUILD.zh-CN.md)说明产品release、test-fixture、native依赖、三平台限制与状态生命周期。产品自身以隐藏__driver启动child，不存在ff-driver二进制；Windows源码尚需适配，Linux本轮未测。

普通run默认dry_run，不建schema；state init --synthetic仅创建新私有目录。execute需独立匹配库，inspect只读。unknown保留原状态和身份，不清库/换ID/盲重发。应用写只走Execution.apply，YAML v1当前注册kind为demo01、plc_guard_get_int和get_value_guard_int；basic01复用demo01，teaching01仍只在教程副本练习。未知kind拒绝，无自动发现、demo02、POST/auth或BOOL/REAL。

可独立复制本目录并使用自身源码、清单/锁、配置、locale、夹具与状态，不依赖父/兄弟runtime。下面父任务链接仅为可选治理导航。

既有[FF-001 r4](../plans/FF-001-dual-runtime-demo01/spec.md)精确双版本交接已通过独立[QA2](../plans/FF-001-dual-runtime-demo01/checklist.md)，Human Owner终验、现场与长稳仍待；旧失败/证据原样保留。[FF-002](../plans/FF-002-user-guide-and-runtime-positioning/spec.md)手册有独立DEV/QA/Owner链，不继承FF-001验收。

[PLAN](PLAN.zh-CN.md) · [CODE_INDEX](CODE_INDEX.md) · [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.zh-CN.md)

三个基础案例及独立命令见[案例目录](examples/README.zh-CN.md)，对应[YAML配置说明](config/README.zh-CN.md)。

Rust YAML v2见[点目录教程](USER_GUIDE.zh-CN.md#catalog-v2)：每PLC独立ff.plc JSON，正式kind仅demo01/read_points，S7标准DB int16。Modbus仅结构validate；Python/C#尚未加载、DS尚未导出。
