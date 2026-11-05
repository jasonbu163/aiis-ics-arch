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


## 匿名业务集成准备

[ARCH-BE-010 r1 A0](../../../plans/ARCH-BE-010-anonymous-business-integration/spec.md)新增 `/integration/` 下八条 typed 匿名 POST 准备及有限[公共原语](../MODULE_CONTRACT.zh-CN.md#匿名集成原语)。旧认证接口和权限保持。三个模块开关默认关闭、设备和 producer scope 默认空、storage profile 默认 `unadopted`。关闭/越界请求403；A0准入合格仍在数据库依赖或业务访问前503。任何profile值均不能在本准备阶段接通业务写入。模块 `enabled=False` 经重组统一移除新旧整组路由。

四个新Model声明描述三张模块永久最小回执和生产观察事件索引，不执行DDL、不代表结构已迁移。共享表上海时间采用、精确Alembic接链、业务接线和可丢弃MySQL验证仍分别有gate。匿名producer/来源声明可被冒用，scope仅数据准入而非认证。[任务记录](../../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md)保存待确认的源码时区/迁移提案。


## 有界业务集成（r2）

匿名integration Service/CRUD接入本owner既有业务表，连同永久最小回执及typed [provider](../../../contracts/published/http-api/business-integration-v1/README.zh-CN.md)。默认关闭/空scope/未采用；有效外部凭据及事务内UUID/schema/revision/DB时钟匹配缺一不可。显式schema后继为BE009 0a2后的BE010 1b3。旧HTTP/Projection时间适配局限owner固定列，unadopted走原路径。真实历史转换/目标采用及数据库/Docker/B仍需另批，不改变raw/latest保留或PLC writer。

既有曲线created_at同时承载系统/Projection来源时间，旧读接口没有可靠逐行wire基准判别。本实现对monitor的legacyNaive与systemWire不相等明确拒绝采用，不凭equipment/device的NULL推测。更细来源标签/cohort须另立范围。
