# Field Flow Python 代码索引

- [src/field_flow/__init__.py](src/field_flow/__init__.py)：Field Flow Python独立运行时；导入无配置、网络或状态IO。
- [src/field_flow/__main__.py](src/field_flow/__main__.py)：模块入口仅委托CLI；导入无IO。
- [src/field_flow/app/__init__.py](src/field_flow/app/__init__.py)：仅注册已批准的手写demo01；无自动发现/DSL。
- [src/field_flow/app/demo01.py](src/field_flow/app/demo01.py)：单轮GET→严格typed条件→执行服务；无调度、SQL或PLC协议调用。
- [src/field_flow/cli.py](src/field_flow/cli.py)：双语CLI与组合根；无参/help无配置、状态或网络副作用。
- [src/field_flow/config.py](src/field_flow/config.py)：无隐式转换的有限YAML配置；所有外部地址须显式提供。
- [src/field_flow/domain.py](src/field_flow/domain.py)：严格INT命令、物理资源身份、来源时效和稳定错误。
- [src/field_flow/driver_process.py](src/field_flow/driver_process.py)：本工程专属driver子进程/匿名IPC；同步库唯一执行线程及总deadline回收。
- [src/field_flow/infrastructure/__init__.py](src/field_flow/infrastructure/__init__.py)：外部IO适配器；导入无IO。
- [src/field_flow/infrastructure/audit.py](src/field_flow/infrastructure/audit.py)：父状态线程唯一JSONL审计writer；完整行、轮转、sync与失败反馈。
- [src/field_flow/infrastructure/http.py](src/field_flow/infrastructure/http.py)：复用有界HTTP client；单次GET及整体deadline，不跟随重定向/环境代理。
- [src/field_flow/infrastructure/s7_int_pdu.py](src/field_flow/infrastructure/s7_int_pdu.py)：R15单item/2字节DB INT；公开raw返回后4096cap，严格关联正ACK。
- [src/field_flow/infrastructure/state.py](src/field_flow/infrastructure/state.py)：显式schema、实例锁、单SQLite/audit owner线程；父进程拥有执行事实。
- [src/field_flow/owner.py](src/field_flow/owner.py)：每PLC父FIFO监督owner；有界ready/queue、先持久T2再交单次permit。
- [src/field_flow/runtime.py](src/field_flow/runtime.py)：异步独立flow监督、每PLC持久owner及单global shutdown截止。
- [src/field_flow/services/__init__.py](src/field_flow/services/__init__.py)：父进程用例服务；不导入协议库或SQL。
- [src/field_flow/services/execution.py](src/field_flow/services/execution.py)：唯一执行服务：身份接纳、typed ACK后的T3及保守失败状态。
- [tests/__init__.py](tests/__init__.py)：FF-001 自身Python合成验证，不借兄弟fixture或运行环境。
- [tests/fixtures/__init__.py](tests/fixtures/__init__.py)：本机S7有限公开API预检夹具。
- [tests/fixtures/__main__.py](tests/fixtures/__main__.py)：显式本机夹具命令；无参/help只读自身locale，不创建服务。
- [tests/fixtures/cli_smoke.py](tests/fixtures/cli_smoke.py)：显式CLI init/fixture/run/inspect的两模式实际启动；自身进程全部wait。
- [tests/fixtures/processes.py](tests/fixtures/processes.py)：仅自建产品父进程/driver的崩溃、实例锁和真实停止证据。
- [tests/fixtures/public_api.py](tests/fixtures/public_api.py)：FF-001 r3：仅自身127.0.0.1 S7 Server/透传代理，有限候选公开API复核。
- [tests/fixtures/runtime.py](tests/fixtures/runtime.py)：Python自身有限HTTP/S7夹具；真实Server、透传故障、有限trace和实际join。
- [tests/fixtures/support.py](tests/fixtures/support.py)：本语言矩阵显式synthetic库、真实运行资源与持久报告；无兄弟依赖。
- [tests/python_api_preflight.py](tests/python_api_preflight.py)：FF-001 r3 有限公开API预检；保存证据/自然回收之后才断言错误操作必须拒绝。
- [tests/test_local_protocol.py](tests/test_local_protocol.py)：Python AC01–15真实loopback矩阵；每例私有库并实际释放，失败原报告保留。
- [tests/test_matched_ack_gate.py](tests/test_matched_ack_gate.py)：R15正式state/owner/driver/execution共用途径，110秒内部界限+外层120秒。
- [tests/unit/__init__.py](tests/unit/__init__.py)：本工程单元向量包，使pytest入口独立解析自身tests。
- [tests/unit/test_cli_config.py](tests/unit/test_cli_config.py)：CLI空目录无副作用、严格配置/来源时间与只读状态边界。
- [tests/unit/test_s7_int_pdu.py](tests/unit/test_s7_int_pdu.py)：固定请求/INT边界、逐长度截断、逐字段拒绝；不替代真实协议gate。

## 使用文档 / Usage documentation

- [USER_GUIDE.md](USER_GUIDE.md) / [中文](USER_GUIDE.zh-CN.md): 独立使用、真实方法与teaching01教程；示例接线仅在教程副本，不是正式已注册源码。
