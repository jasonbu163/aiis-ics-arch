# Field Flow Python 配置

[English](README.md)

人工审阅的YAML v1合同；不是JSON PLC目录、schema平台或现场地址。每次只运行一份配置，每份只写一个物理target。上层PLAN管理此README-only目录。

| File | flow.id / kind | instance_id |
| --- | --- | --- |
| [loopback.yaml](loopback.yaml) | demo01 / demo01 | ff-python-demo01 |
| [basic02.yaml](basic02.yaml) | basic02 / plc_guard_get_int | ff-python-basic02 |
| [basic03.yaml](basic03.yaml) | basic03 / get_value_guard_int | ff-python-basic03 |

三份均使用source_id=demo01-feed、GET http://127.0.0.1:32880/demo01/command、plc_demo/DB1/16 bytes/offset0/INT、interval500ms、input_max_age10000ms。proxy/server为32102/32103，仅loopback，不用102或wildcard。business_name分别为synthetic_command_to_int、negative_target_get_to_int、positive_bounded_command_to_int。case/flow/kind/source/command/instance角色不同；unknown/非法target/重叠写仍拒绝。

完整逐字段预算与typed输入见[自身指南](../USER_GUIDE.zh-CN.md)，完整两模式命令和计数见[案例目录](../examples/README.zh-CN.md)。build/sync/init先于fixture生成命令；dry/execute分库。现场地址/target改动不属于这些合成例。保留原命令时间/身份、原库和unknown，不靠改名/换库恢复；标准DB INT两字节有符号大端，非BOOL/REAL/优化DB。
