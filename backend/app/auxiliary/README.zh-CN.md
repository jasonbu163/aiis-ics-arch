# Auxiliary 辅助业务模块

[English version](README.md)

auxiliary归属ShiftTeam、Shift、ShiftRule、StopRecord及既有/shift-teams、/shifts、/shift-rules、/stop-records接口。
唯一权限key为auxiliary，不授权价格；价格由[energy](../energy/README.zh-CN.md)唯一归属。
历史[模块PLAN](PLAN.zh-CN.md)及已验收价格bundle保留原owner/时点事实。

普通GET不生成班次或默认规则；规则空表返回共享成功信封data:null。前端显示“未配置”，无真实id时不开放编辑/保存。
本模块没有创建规则API，首次初始化仍为另行明确授权的数据/配置操作；已有规则GET/PUT保持。
CRUD只查询/add/flush，显式写事务由Service commit/rollback。StopRecord通过app.auxiliary.models:StopRecord
公开给显式model_requires消费者，详见[模块合同](../MODULE_CONTRACT.zh-CN.md)。42表后继包含这四实体；
源码/recorder检查不代表结构已应用或真实运行可用，实际迁移和数据操作分别经过后续gate。
