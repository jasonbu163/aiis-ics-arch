# 能源单价 v1

所有接口使用登录用户的 Bearer token。价格读写权限独立，维护项目还需管理员角色。

| 方法和路径 | 权限 | 成功时的 `data` |
| --- | --- | --- |
| `GET /api/v1/energy/pricing/items` | `energy-price-read` | 所有项目定义，含停用项目 |
| `POST /api/v1/energy/pricing/items` | `energy-price-manage` 和管理员 | 新增项目 |
| `PATCH /api/v1/energy/pricing/items/{itemKey}` | `energy-price-manage` 和管理员 | 更新后项目 |
| `GET /api/v1/energy/pricing/current` | `energy-price-read` | 启用项目各自最近适用的价格及相关信息 |
| `GET /api/v1/energy/pricing/hours` | `energy-price-read` | 分页的实际小时更新及独立的列集合 |
| `POST /api/v1/energy/pricing/hours` | `energy-price-manage` | 记录小时与本次提交的项目单价 |

成功使用共有的 `code`、`message`、`data` 和 `timestamp` 信封。未认证为 401，权限不足为 403，项目键重复为 409，输入无效为 422。

项目定义包含 `itemKey`、`nameZh`、`nameEn`、`unit`、`sortOrder` 和 `enabled`。项目键区分大小写，去首尾空白，保存后不可改。至少填写一个名称，界面当前语言缺失时显示另一名称。PATCH 时对项目键做 URL 百分号编码。字面键 `.` 与 `..` 分别使用 `%252e` 与 `%252e%252e`，字面键 `%2e` 与 `%2e%2e` 分别使用 `%25%32%65` 与 `%25%32%65%25%32%65`。PATCH 省略字段保留原值。项目已有单价时其单位不可更改。项目按排序与稳定项目键升序返回。

`items` 是项目键到 `{price, remark?}` 的非空映射。价格接受 JSON number 或十进制字符串，范围 0–999999.9999，有效小数位最多四位，超限拒绝。响应中的价格为 JSON number。本次未提交的项目保留该小时原值。已提交项目省略 `remark` 时保留该项目的原备注，null 或空串清除。顶层 `remark` 使用相同规则。`observedAt` 为带偏移的 ISO 时间，可带秒及最多六位小数；省略或 null 取一次服务端当前时刻，拒绝未来时刻。

现价数组包含 `itemKey`、`nameZh`、`nameEn`、`unit`、`price`、`remark`、`observedAt`、`updatedAt` 和 `operator`；无价格时后五项为 null。小时历史的 `date` 可省略，指定时使用 IANA `Asia/Shanghai` 自然日 `YYYY-MM-DD`。默认 `page=1`、`pageSize=24`，每页数量范围 1–100。每行包含 `hourStart`、`remark` 和以项目原始键为键的 `values`。各项含 `price`、`remark`、`observedAt`、`updatedAt` 和 `operator`。缺少项目键表示该小时未录该项目，真实零作为价格返回。`columns` 始终含启用项目及查询范围内有记录的停用项目，独立于分页与空结果。API 时间统一固定偏移 `+08:00`。

旧三个 `/energy` 路由沿用原请求和响应，共用项目小时记录。旧视图可从更早小时继承某项价格，并只返回完整三价。迁移与恢复见[后端模块](../../../../backend/app/energy/README.zh-CN.md)。

[OpenAPI](openapi.json) · [新增项目示例](examples/item.json) · [单项录价示例](examples/price.json) · [English](README.md)
