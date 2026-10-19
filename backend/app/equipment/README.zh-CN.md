# 设备模块

[English version](README.md)

Equipment管理既有传动、温控、生产看板三GET和三张旧表。仓库原8个本地Projection descriptor及调用方business/cursor/audit同事务保持独立，不借新HTTP接收器更换writer。

## 完整温控样本

`POST /api/v1/equipment/temperature-samples`接收不可变完整观测：equipmentId、稳定sampleId、带时区sampledAt、quality="good"，以及zone1Set/zone1Act至zone5Set/zone5Act十个°C JSON number。设定值是观测，不是控制命令。0有效；缺失/null/bool/字符串/非有限数、未知/重复字段和snake_case替代均HTTP422。实际prefix沿API_V1_PREFIX。

温度使用精确NUMERIC(30,10)：绝对值小于10^20，最多10位小数；非整数还须JSON number序列化往返后十进制值不变，超出即拒绝，不舍入。这是技术可表示域，不是物理温度阈值。原始JSON先解析Decimal，再决定读回形式。1/1.0、0/-0规范化SHA256 fingerprint相同。

sampledAt归一UTC，保存DATETIME(3)，拒绝非零亚毫秒尾数和非法时区offset；UTC年份范围1000至9999。输出YYYY-MM-DDTHH:mm:ss.sssZ。创建时间另取数据库UTC_TIMESTAMP(3)，不修改engine/session时区，不用到达时间替代来源时间。

HTTP200共享成功信封data返回recordId/equipmentId/sampleId/sampledAt/outcome；首次created，重放或等价现存样本duplicate。业务unique为(equipment_id,sampled_at)，投递unique为(actor_user_id,equipment_id,sample_id)。key区分大小写（utf8mb4_bin）；标识1–128字符、无控制字符和首尾空白。fingerprint不含actor/sampleId/token/到达时间。同投递改payload为409 equipment.temperature_sample_id_conflict；同来源时刻异内容为equipment.temperature_sample_time_conflict；投递冲突优先。样本不覆盖，新的等价投递只补回执。

async Service在同事务写样本及receipt/actor审计，成功前commit；CRUD只查询/add/flush。仅MySQL1062且真实constraint key命中本业务/投递unique时rollback后最多重试2次，以新事务快照重读；其他Integrity不当duplicate。不可用/提交结果未知为503，保留同sampleId重试。已提交后响应/日志失败为脱敏500，同键重试恢复原recordId。receipt用复合FK同时引用样本和equipment，不新增user FK改变账号删除规则。

`GET /api/v1/equipment/temperature-samples`接受可省equipmentId（默认配置key）、正recordId及limit（默认100，1–1000）。SQL先设备scope再recordId，按sampled_at DESC,id DESC并真实limit。返回equipmentId/items；每项含recordId、来源时间、quality、完整十值及数据库createdAt，不暴露actor/receipt/sampleId。不存在ID返回空数组。同小时不同时刻及晚到样本分别保留；limit=1只定义新表最近已接受来源时间，不保证物理当前状态。

## 权限与配置

POST复用active User认证、admin角色及equipment-temperature-ingest；GET独立equipment-temperature-read，admin恒权，supervisor/operator须显式grant，未知角色拒绝。两permission不互授，也不授予旧equipment API；公开grants仍为空。

所有caller含admin须经过模块本地唯一EQUIPMENT_TEMPERATURE_PILOT_ID精确scope；空/非法key只拒绝新两API为403，旧GET保持。公开example为空；合成文档/测试用temperature-pilot-01。本地BaseSettings依赖懒用公开settings.resolve_env_file()，源码backend/.env、冻结可执行同目录.env、既有Docker /app/.env。显式参数优先process env，process优先dotenv；测试_env_file=None或合成文件，每应用首次访问时懒固定独立配置实例，无跨应用共享缓存；后续dotenv/process变更须重启采用。manifest.enabled=False经重组/重启统一移除equipment新旧routers。

仅新两route局部适配真实HTTP401/403/409/422/500/503和稳定equipment.temperature_*错误，DEBUG也不回显SQL、秘密或输入。既有全局业务错误HTTP200及旧API不变。JSON Lines只记录受控actor/对象/结果，不记完整样本或凭据。

## 持久化与采用gate

显式后继[e4f6a8b0c2d4](../../alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py)接d2f4a6b8c0e2，仅新增equipment_temperature_samples及equipment_temperature_sample_receipts两表（完整fixture60表，原58受保护）。import/GET/启动不DDL/seed。downgrade先撤回执再样本，会丢新增观测，仅供另批可丢弃演练，不是已采用数据默认回退。

旧GET /equipment/temperature-control继续读取equipment_temperature，包含原limit行为；旧前端数据源保持，不自动展示新HTTP样本。不union、不双写、不迁移旧行、不停writer、不伪造PLC provenance。前端/writer统一、保留期、聚合及现场采用另案。

A源码/no-DB和offline DDL不能证明MySQL持久化、约束、精度或并发。[独立MySQL入口](../../tests_mysql/test_equipment_temperature.py)位于共享破坏性conftest之外，必须另批精确disposable目标与动作后才运行。数据库（含SQLite）、Docker、部署和真实设备分别gate。见根[spec](../../../plans/ARCH-BE-003-mapping-service-api-pilot/spec.md)、[Development](../../../plans/ARCH-BE-003-mapping-service-api-pilot/tasks.md)及本地[PLAN](PLAN.zh-CN.md)。


## HTTP看板来源

新增POST/GET `/equipment/drive-samples`与`/equipment/production-parameter-samples`使用独立HTTP域。
传动20项至少提供1项；生产参数须精确coilNo及grade/entryTime/thickness/width/totalTime/weight/speed至少1项，processSteps不可写。
同设备/业务键/来源毫秒只补原NULL指标，任何已有异值整次409。GET须equipmentId，可选正recordId及1–1000的limit（默认100），
items与dashboard来自同一选中来源行；缺测不产生零偏差或normal状态。

新增GET `/equipment/temperature-sample-dashboard`只读BE003完整样本，保持独立温控read/scope，原POST/GET不变。
历史保留recordId与完整来源时间。设备三页在URL保存`dataSource=legacy|http`与`equipmentId`，默认旧表来源；外部上报须设备键，
不fallback到旧表/mock。切换清空前来源数据并忽略晚响应；不能借PLC身份猜旧数据设备。TV/KM单位仍未定义，set仅为观测，不是控制命令。
