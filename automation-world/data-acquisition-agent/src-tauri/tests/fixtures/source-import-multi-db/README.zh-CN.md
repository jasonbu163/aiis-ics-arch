# 手写多 DB 来源样例

[English](README.md)

归[DAA PLAN](../../../../PLAN.zh-CN.md)及[DAA-005 r1](../../../../plans/DAA-005-multi-db-source-import-and-nested-offsets/spec.md)。文本独立手写，不复制Owner真实输入。`multi.db`有6DB，`types.udt`有3UDT，`expected.json`人工定义叶路径/类型及disabled/未分组/address=null默认值。DB501–506及布局测试DB701–704均为合成映射，不从文本猜真实块号；无现场endpoint或客户数据。

`layout-oracle.json`在新算法前冻结，记录Siemens STEP7 V20（11/2024）精确官方链接/段落、有限非优化standard-word profile、手写声明及每叶byte/bit、数组stride、总长度。其后`layout.db`转写这些声明，期望地址不由算法生成。ARRAY英语起点描述与自身even-address子句矛盾，以官方padding页和3单BYTE+7BYTE数组明确例裁定起止边界；嵌套STRUCT/UDT及BOOL打包对照官方STRUCT/BOOL规则。

仅运行相应Rust `tia_source::tests`、`plc_layout::tests`、`local_store::source_import_tests`过滤器。Engine/store测试新建自有系统tmp profile与cfg(test)历史种子，不用已有profile或旧样本。oracle只证明此有限来源profile，不代表TIA编译、全部CPU/固件或真实PLC地址；STRING/优化/未知/不完整布局不推算。真实私有源不属此公开fixture，继续忽略/只读。
