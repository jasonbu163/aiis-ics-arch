# PLC事实v1源码合同

**历史合同：** ARCH-ACQ-002 r2 后的当前 Core 不再提供这些 v1 路由或表。历史验证使用保全的清退前源码；以下机器工件保持不变。

方向：DAA原本地样本 → Backend事实provider → 后续SMA事实消费者。`ARCH-BE-009 r1`源码及获批隔离MySQL A+B已通过独立QA，见[当前核验](../../../../plans/ARCH-BE-009-backend-facts-integration/checklist.md)。Owner终验/provider-ready、实际目标采用、DAA上传器、联合验证和部署仍分别待定。目录名不代表已发布到外部服务。

固定版本：`plc-facts/v1`、`daa-local/v2`、`pf-json/v1`、`pf-cursor/v1`。

- [openapi.json](openapi.json)：只含三operation及递归components闭包。请求及200/403/409/410/413/415/422/429/503/500结果全部typed；Decimal wire只为JSON number，点Map保留原Unicode/大小写/下划线。
- [schema.json](schema.json)：JSON Schema 2020-12定义请求、严格query、回执、latest/changes/range和失败。
- [vectors.json](vectors.json)：独立stdlib规范字节、获批固定摘要、原v2材料及合成多PLC/多DB/组/固定片例子，无实际端点或数据库配置。

原v2文本是唯一可编辑点位体，原SHA覆盖原字节；content/cycle/request/projection/definition分别有独立域。固定片保留sampleId。完整样本/整轮须收到完整expected集合，收到数与quality另算。可靠证明120天有限且不续期。父拒绝token从持久原证明恢复，不受当前游标key轮换影响；父proof缺失/到期不授退休。

匿名声明可被冒用。默认关闭/空PLC scope在DB前拒绝，随意填写profile不能打开存储gate。运行须另行采用schema、上海DB时间、来源generation/定义集及签名key；不增删其他接口登录或权限。

相对[AW008](../../../../plans/ARCH-AW-008-stage-c-facts-contract/spec.md)，获批provider细化独立七表、原v2文本、固定片身份、9位事实时间、4MiB输入、显式来源采用、单例门闩发布序、有限拒绝proof及游标gap。切换来源递增sourceEpoch；无关context/revision变化而点定义不变时保留有效latest。逻辑原值最多三自然月；物理清理停机也须读时拒绝过期原值。一次性有界维护tick无调度器，无业务级联。

源真相：[历史机器工件](openapi.json)、[显式迁移](../../../../backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py)、[获批spec](../../../../plans/ARCH-BE-009-backend-facts-integration/spec.md)、[Development证据](../../../../plans/ARCH-BE-009-backend-facts-integration/tasks.md)。机器JSON由typed源码与独立向量生成，不是运行配置。
