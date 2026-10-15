# Monitor 事实与业务历史

[English version](README.md)

Core collector/status与realtime/latest保留原三Model和monitor权限。
app.monitor.models:PlcDbBlockRawSnapshot是提供给显式model_requires消费者的只读Model出口，不公开采集writer或新API。
独立/monitor/temperature、/monitor/energy两GET只需monitor-business-read，两个key不相互授权。
查询读取两张业务历史表，不持久化诊断样本，即使业务mock配置开启亦不写入；空曲线保持空。
过程曲线同步Projection descriptor保留本地调用方事务，发现不会启动运行或发布mapping。
仅HistoryProcessCurve、HistoryEnergyConsumption补充Core三模型，不包含旧12个HMI/deprecated/报警/tracking模型。
详见[公共合同](../MODULE_CONTRACT.zh-CN.md)。显式后继与源码检查之后仍需MySQL/真实运行gate，不隐含CA/PLC操作。
