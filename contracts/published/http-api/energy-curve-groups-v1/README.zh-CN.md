# 能耗曲线组 v1

管理员在「能耗管理 → 配置管理 → 曲线设置」选择一块表计和一个采样组，配置一张曲线图。能耗统计可选已保存的曲线组，也可按表计查询。

| 方法与路径 | 权限 | 成功返回的数据 |
| --- | --- | --- |
| `GET /api/v1/energy/curve-configs` | 管理员及表计范围 | 范围内全部组，含停用组 |
| `POST /api/v1/energy/curve-configs` | 管理员及表计范围 | 新建的组 |
| `PATCH /api/v1/energy/curve-configs/{curveGroupKey}` | 管理员及更新前后两块表计的范围 | 更新后的组 |
| `GET /api/v1/energy/consumption/curve-configs` | `energy-consumption-read` 及表计范围 | 范围内启用的组 |

四个方法均使用登录用户 Bearer。两个 GET 都可传 `meterId`，按 `sortOrder`、`curveGroupKey` 升序返回。成功信封为 `{code, message, data}`，`code` 为 200。以下使用合成标识举例。

```json
{
  "curveGroupKey": "meter01-power",
  "titleZh": "1号电表功率",
  "titleEn": "Meter 01 power",
  "meterId": "meter-01",
  "groupKey": "electricity",
  "sortOrder": 10,
  "enabled": true,
  "series": [
    {"metricKey": "phaseAPower", "enabled": true, "lineStyle": "solid"},
    {"metricKey": "phaseBPower", "enabled": true, "lineStyle": "dashed"}
  ]
}
```

至少填写一种语言的标题。缺失标题返回空字符串，界面回退至已有标题。曲线组键沿用 1–64 个字符的标识规则，区分大小写、全局唯一且创建后固定。PATCH 将键按单个路径段做百分号编码。键为 `.` 或 `..` 时，分别用 `%252e` 或 `%252e%252e`，避免浏览器移除点段。字面键 `%2e` 和 `%2e%2e` 分别用 `%25%32%65` 和 `%25%32%65%25%32%65`。PATCH 保留省略字段，传入 `series` 则整体替换有序曲线数组。

曲线引用所选表计和采样组的已有数值指标。同一指标在组内出现一次，组内至少启用一条曲线。启用曲线须共享物理量与单位，缺省单位可相互匹配。停用指标的写入不影响已有样本的历史读取。统计页使用第一条启用且有效的曲线调用现有汇总接口，名称、小数位和单位取自能耗指标定义。

登录认证无效或缺失时返回 401，权限或表计范围拒绝时返回 403，更新未知曲线组时返回 404，键冲突返回 409，字段、指标引用或单位不合法返回 422，数据库不可用或结构不兼容返回 503。失败信封为 `{code, message, data, errorCode}`。

[OpenAPI](openapi.json) · [English](README.md)
