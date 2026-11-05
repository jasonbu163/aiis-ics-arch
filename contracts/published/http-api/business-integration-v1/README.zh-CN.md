# 业务集成v1 provider

English: [README.md](README.md)。

[openapi.json](openapi.json)从backend正常模块注册应用提取精确八路匿名POST及闭合组件引用；[examples.json](examples.json)保存八份规范请求、请求/业务摘要、完整成功/错误例与冻结bi-json/v1向量。wire仍为aiis.business-integration/v1，r2只是任务Revision。

这是source_ready_unadopted源码，默认关闭/空scope/未采用。准入先于采用校验和session创建；shanghai-v1另要求精确外部business-time-adoption/v1凭据、有限basisProfile及事务内UUID/schema/revision/DB时钟匹配。配置字符串不能单独启用写入。真实schema/时间采用、数据库/Docker/B及Owner接受仍是独立gate。

| 资源 | 数值/技术存储域 |
| --- | --- |
| temperature | 十项完整set/actual °C；精确NUMERIC(30,10)，abs<10^20，最多十位小数。 |
| drive | 20项至少一项binary32；TV/KM量纲未定义，露点°C、氧ppm、压力Pa、气体流量m³/h、五组张力kN。 |
| production_parameters | 精确卷号，grade/entryTime/thickness/width/totalTime/weight/speed至少一项；非负binary32数量，mm/分钟/吨/m/min，不生成工步。 |
| production_observation | 明确在产/非在产/unknown；在产必有卷号，可携十三观测。重量/output/qualified为(10,4)、长度(10,2)、直径(8,2)、density(5,3)、rate/score(5,2)，均非负。quantity/density/qualityScore量纲未定义，不猜换算或添加≤100限制。 |
| process_temperature | 四温度NUMERIC(8,2) °C及0..9999999999整数工艺段**分钟**，至少一项。 |
| process_tension / process_speed | 非负NUMERIC(10,2)，kN/m/min，至少一项。 |
| process_curve | 33项至少一项：十二int32 °C温度、其余21项binary32。速度m/min，unc/rec张力P为%，四项张力Kg沿原kg标签，风机Hz，N₂累计m³，电耗累计kWh，气流m³/h，氧ppm，露点°C，压力Pa。累计观测不派生财务/能耗汇总。 |

JSON只收number/integer，不收数字字符串或测量null。省略是缺测并保存SQL NULL，0是有效观测。Decimal超scale/范围拒绝，不舍入。FLOAT只规范一次到binary32：finite、abs≤3.4028234663852886e38、相对误差≤1e-6、绝对误差≤max(1e-6,abs(input)×1e-6)，非零下溢拒绝；摘要使用该存储值的精确十进制。温度/张力min/avg/max及速度avg/max须在完整补NULL后仍有序。

来源时间接受显式Z/offset，拒绝非零亚毫秒，一次归一+08:00，不能超过注入DB时钟五分钟。回执sourceTime/committedAt固定三位毫秒及+08:00，sourceRefs时间保留必要精度。生产DATE与秒/分钟耗时分别处理。受控采用后旧HTTP UTC wire/摘要/JSON结果仍通过兼容view保留。

投递身份为module+producerId+eventId；同内容重放仅outcome变duplicate，其余首次事实稳定。同身份改路由/父/data存在集合/映射/来源先返回event_conflict。温控/曲线不可变，drive/参数/过程仅补NULL；生产复用设备水位并另存永久历史事件。过程父id须来自本通道可靠在产回执；父missing404，跨设备/卷或legacy父409。人工重量含0和有效人工时间pair优先。

成功回执确认业务事务或持久stale决定；stale恒decision_only/applied=false/目标null/影响集合空。committedAt是获胜事务commit前最后DB时钟采样，不冒充引擎物理提交完成瞬间。调用方核对版本/身份/双摘要/目标/confirmation后再持久保存ACK。单独200、flush、日志或raw事实ACK均不够。

错误真实HTTP为403/404/409/413/415/422/503/500，使用模块局部code/message/data:null/errorCode壳；404/parent_mismatch仅过程，observation_time_conflict仅生产观察。commit_unknown/unavailable/internal或响应丢失时保留原冻结身份/内容并重发核实；修复内容是新逻辑事件，仍受业务键约束。raw到期不清业务/source/mapping/最小回执，后者无自动TTL。生产聚合可演进，不承诺所有旧值自动版本历史。

生成通过guarded正常create_app(testing=True).openapi()，只选八路equipment/performances/monitor POST并递归闭合ref。实际argv/hash/DEV检查见[任务记录](../../../../plans/ARCH-BE-010-anonymous-business-integration/tasks.md)，生成不运行listener/lifespan/DB/Alembic/Docker。静态链为BE009 0a2（71应用表）→BE010 1b3（75），不含alembic_version。本provider与事实provider独立，也不授予旧API身份/权限。


生成工件SHA-256：openapi.json = `d92bf03a9e8b3e4575fddc9caa68233e6b415210a6965c0a29b6b99264727562`；examples.json = `2255e6752cb8079d813ddc65773f07460cbfdedc0c00d10faaec63064d7cc724`。
