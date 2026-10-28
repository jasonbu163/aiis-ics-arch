# Field Flow Rust Code Index

- [src/app/demo01.rs](src/app/demo01.rs): 文件：src/app/demo01.rs；手写单轮GET→typed条件→执行服务，无循环、SQL或协议IO。
- [src/app/mod.rs](src/app/mod.rs): 文件：src/app/mod.rs；只注册已批准demo01。
- [src/bin/ff-fixture.rs](src/bin/ff-fixture.rs): 文件：src/bin/ff-fixture.rs；独立本机合成夹具入口，无参仅帮助。
- [src/commands.rs](src/commands.rs): 文件：src/commands.rs；双语CLI解析与装配；无参/help无配置读取及状态IO。
- [src/config.rs](src/config.rs): 文件：src/config.rs；拒绝未知字段与隐式类型的配置/资源边界校验。
- [src/domain.rs](src/domain.rs): 文件：src/domain.rs；严格命令、物理INT资源、来源时间及身份摘要。
- [src/driver_process.rs](src/driver_process.rs): 文件：src/driver_process.rs；单PLC常驻子进程、私有有界IPC与总deadline内真实回收。
- [src/fixture.rs](src/fixture.rs): 文件：src/fixture.rs；仅test-fixture编译的本项目loopback HTTP/透明TPKT夹具。
- [src/infrastructure/audit.rs](src/infrastructure/audit.rs): 文件：src/infrastructure/audit.rs；tracing JSONL格式化及有失败回执的同步持久审计。
- [src/infrastructure/http.rs](src/infrastructure/http.rs): 文件：src/infrastructure/http.rs；HTTP有界输入服务；无业务重试、代理或重定向。
- [src/infrastructure/mod.rs](src/infrastructure/mod.rs): 文件：src/infrastructure/mod.rs；外部IO adapter汇总。
- [src/infrastructure/posix.rs](src/infrastructure/posix.rs): 文件：src/infrastructure/posix.rs；实例锁、短临界区开始闸门与磁盘容量。
- [src/infrastructure/s7_int_pdu.rs](src/infrastructure/s7_int_pdu.rs): 文件：src/infrastructure/s7_int_pdu.rs；唯一单item/2字节DB INT的S7 payload codec，连接由原库负责。
- [src/infrastructure/state.rs](src/infrastructure/state.rs): 文件：src/infrastructure/state.rs；显式schema和单线程SQLite/持久审计actor。
- [src/lib.rs](src/lib.rs): 文件：src/lib.rs；FF运行时装配入口与模块边界，不执行IO。
- [src/main.rs](src/main.rs): 文件：src/main.rs；只启动CLI/私有driver入口，无业务或设备IO。
- [src/runtime.rs](src/runtime.rs): 文件：src/runtime.rs；独立flow调度、每PLC FIFO监督owner、停止与真实join。
- [src/services/execution.rs](src/services/execution.rs): 文件：src/services/execution.rs；父执行状态编排、意图/确认事务及失败保守分类。
- [src/services/mod.rs](src/services/mod.rs): 文件：src/services/mod.rs；执行用例入口，HTTP协议封装归基础设施。
- [tests/ack_rejection_matrix.rs](tests/ack_rejection_matrix.rs): 文件：tests/ack_rejection_matrix.rs；AC15每行真实S7响应字段/长度故障，保留三份报文与原状态。
- [tests/cli_contract.rs](tests/cli_contract.rs): 文件：tests/cli_contract.rs；CLI无参/双语、严格配置和显式schema的低影响边界检查。
- [tests/confirmed_audit.rs](tests/confirmed_audit.rs): 文件：tests/confirmed_audit.rs；真实confirmed后持久sink故障不降级，原身份重启十轮不重发。
- [tests/local_protocol.rs](tests/local_protocol.rs): 文件：tests/local_protocol.rs；真实HTTP/S7、唯一会话、故障和恢复矩阵，逐版串行。
- [tests/process_lifecycle.rs](tests/process_lifecycle.rs): 文件：tests/process_lifecycle.rs；仅本程序自建父/driver进程的崩溃、存活锁与正常退出证据。
- [tests/remaining_matrix.rs](tests/remaining_matrix.rs): 文件：tests/remaining_matrix.rs；INT逐值独立读回、过期队列、审计故障、容量轮转与ref维护。
- [tests/s7_int_pdu.rs](tests/s7_int_pdu.rs): 文件：tests/s7_int_pdu.rs；固定payload及逐长度截断/字段拒绝，不替代真实协议gate。
- [tests/support/mod.rs](tests/support/mod.rs): 文件：tests/support/mod.rs；本机协议矩阵的有界进程与状态夹具。

- [tests/runtime_regressions.rs](tests/runtime_regressions.rs)：QA1返工真实FIFO dispatch预算、原anchored clock queued/precall闭闸、匹配started统计及fault归零。

## 使用文档 / Usage documentation

- [USER_GUIDE.md](USER_GUIDE.md) / [中文](USER_GUIDE.zh-CN.md): 独立使用、真实方法与teaching01教程；示例接线仅在教程副本，不是正式已注册源码。
- [BUILD.md](BUILD.md) / [中文](BUILD.zh-CN.md): 产品/夹具构建、native依赖与目标平台未测边界。
