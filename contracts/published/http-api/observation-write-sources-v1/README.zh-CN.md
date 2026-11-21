# 观测写入登记与最新值

[English](README.md) · [OpenAPI](openapi.json) · [合成向量](vectors.json) · [使用说明](../../../../docs/equipment-status-process-monitoring-guide.zh-CN.md#写入登记来源)

使用接口前配置数据库目标和仓库外私有 profile。profile 必须匹配 MySQL 8.4 的服务标识、库名与 revision `e9f3b5d7c021`，并通过 `OBSERVATION_ENABLED=true` 和 `OBSERVATION_PROFILE_FILE` 启用。登记来源无需在 profile 中配置设备或生产者，`devices` 和 `producers` 可为空数组。[原 v2 机器接口](../equipment-observation-v2/README.zh-CN.md) 保留 Bearer、授权范围和原回执语义。

`sourceKey` 是大小写敏感的来源标识，可使用 1–64 个 ASCII 字母、数字、下划线、点或连字符。每个发送系统应使用稳定的标识。它可以被复制，不能证明身份；无需 token 的路由应部署在访问已受控的内网。

## 登记管理

使用用户 JWT 并通过 admin 校验。`GET /api/v1/equipment/write-sources` 返回未删除登记。POST 接受 `sourceKey`、可选的 `name`（1–128 个字符或 null）和 `enabled`（默认启用）。PATCH `/api/v1/equipment/write-sources/{sourceKey}` 至少提供 `name` 或 `enabled` 之一，标识不可修改。同路径 DELETE 停止写入并隐藏来源，保留样本和回执，永久占用标识。停用可恢复。重复或冲突返回 409，PATCH／DELETE 未知或已删除项返回 404，非法参数返回 422。浏览器请求修改或删除字面标识 `.` 和 `..` 时，分别使用段 `%252E` 和 `%252E%252E`，避免 URL 规范化消去该路径段。

持设备或过程读权限的用户可查看所有未删除登记来源的数据，包括停用的来源。旧设备使用原读范围。管理员在数据管理中可继续查看已删除来源的保留记录。

## 第三方接口

`POST /api/v1/integration/observations` 接受最多 65,536 字节的 UTF-8 JSON，只发送 `sourceKey`、`target`（`latest` 或 `history`）、`taskNo`、`observedAt` 和 `items`。任务号以 ASCII 输入，服务端去首尾空格后转大写。观测时间携带偏移，服务端规范为 +08:00、六位小数。至少提供一个指标。每个提交区域都要启用，指标要有该目标的启用槽位，且值须符合指标配置的类型。0、false、空字符串均为有效值，null 无效。服务端将质量保存为 `unknown`。

较新的实时包覆盖同来源、同任务的完整快照；未见过的较早样本返回 `stale` 回执及当时的快照 ID。每个通过校验的历史样本按包追加。观测时间超过数据库时钟未来 30 秒时拒绝。已有实时值超过 60 秒显示为陈旧。历史曲线按已保存的值和缺测显示。

来源、目标、规范任务号、规范时间及规范内容完全相同时，只要来源仍启用，即使槽位后来被停用，也重放原回执。相同身份的不同内容返回 409。收到 503（包括 `equipment_observation.commit_unknown`）后用原内容原时间重试。未登记、已停用或已删除来源写入返回 403 `equipment_observation.source_not_enabled`。请求超限 413、媒体类型不支持 415、字段或当前配置非法 422、目标不可用或核验失败 503。

`GET /api/v1/integration/observations/latest?sourceKey=sma-demo-1&target=history&taskNo=000042` 返回一条记录的实际保存指标。省略 `taskNo` 时按观测时间降序、任务号升序、记录 ID 降序选取一条。来源存在而无匹配记录返回 `data: null`。停用来源仍可读，未知或已删除来源返回 404。响应沿用项目成功信封，公开 GET 不暴露内部映射和回执标识。
