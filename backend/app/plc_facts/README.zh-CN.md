# PLC事实owner

本模块提供`POST /api/v1/integration/plc-facts/batches`及GET `latest`/`history`。版本`plc-facts/v1`、来源`daa-local/v2`、摘要`pf-json/v1`。匿名来源可被冒用，PLC scope是数据准入，不是身份认证。

默认关闭、空PLC scope、unadopted profile、空HMAC key在DB依赖前拒绝。有效准入仍需显式已采用的MySQL 8.4 schema/上海时钟/来源binding；不创建表或接管来源。模块disabled重组后移除本三路，不影响旧monitor。七表接链f6→0a2；BE010另管1b3四表。两有限运行profile共享七表F7，后继升级后须显式schema-only再核验。

原v2 payload/manifest/context保持UTF-8原文和SHA；固定贪心分片、完整expected集合与content/cycle/request摘要分别校验。Service拥有事务，持stream singleton锁分配commitSerial；只有真实commit且yield依赖完整退出才发送成功。原批重放优先恢复稳定结果，拒绝proof/父token有限120天不续期；不明提交返回unknown。

latest按当前sourceEpoch逐点比较sourceSeq，bad替换good；维护切换来源清旧latest，定义不变的context/revision变化保留旧有效值。history changes按发布位置，range冻结H并按原observedAt半开筛选；过滤投影有独立摘要，过期有显式gap。游标分别24小时/15分钟/30秒，HMAC轮换要求显式重新基线。

原值默认保留3自然月，可采用1或2月；点观察时间+月，保留纳秒。所有读执行expiry guard；原payload按最早成员保守到期，latest按点到期。无自动清理调度。[维护CLI](../../scripts/plc_facts_maintenance/README.zh-CN.md)每tick有界删除，只触七表；物理清理SLA必须由另批运行验证。raw/proof删除无业务级联。

[固定机器合同](../../../contracts/published/http-api/plc-facts-v1/README.zh-CN.md)及[获批规格](../../../plans/ARCH-BE-009-backend-facts-integration/spec.md)为审阅入口。源码存在不等于provider-ready、数据库采用、DAA上传或部署。A阶段没有执行任何数据库、Docker或迁移；运行gate及真实结果只归任务bundle。
