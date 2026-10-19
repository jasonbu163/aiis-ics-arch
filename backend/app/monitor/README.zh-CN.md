# Monitor 事实与业务历史

[English version](README.md)

Core collector/status与realtime/latest保留原三Model和monitor权限。
app.monitor.models:PlcDbBlockRawSnapshot是提供给显式model_requires消费者的只读Model出口，不公开采集writer或新API。
独立/monitor/temperature、/monitor/energy两GET只需monitor-business-read，两个key不相互授权。
查询读取两张业务历史表，不持久化诊断样本，即使业务mock配置开启亦不写入；空曲线保持空。
过程曲线同步Projection descriptor保留本地调用方事务，发现不会启动运行或发布mapping。
仅HistoryProcessCurve、HistoryEnergyConsumption补充Core三模型，不包含旧12个HMI/deprecated/报警/tracking模型。
详见[公共合同](../MODULE_CONTRACT.zh-CN.md)。显式后继与源码检查之后仍需MySQL/真实运行gate，不隐含CA/PLC操作。


## 外部过程曲线

POST/GET `/monitor/process-curve-samples`采用独立`monitor-curve-ingest/read`及`MONITOR_MAPPING_INGEST_ID`。
POST逐样本不可变追加，既有33指标至少提供1项，其中12温度为有符号整数、21项为FLOAT，coilNumber可省略。
同来源毫秒内容或字段存在集合不同409，不覆盖已接收曲线，不写能耗汇总、不创建实绩父记录。

GET必需equipmentId与精确YYYY-MM-DD上海自然日，将边界转UTC过滤sampled_at；可选recordId与1–1000的limit（默认1000），
先取最近样本再升序输出完整items/trends/latest。空结果为[]/[]/{}，四图缺测保留断点/缺测符号。
曲线页URL保存legacy/http与设备，HTTP scope/空态/故障不fallback。旧温度GET只读设备键NULL域，沿原created_at日期语义；
collector/raw/latest及energy来源与权限保持。
