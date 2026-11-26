# 能耗表计管理 v1

管理员通过表计指标配置维护表计标识、中英文名称和登录用户可读角色。三个方法均使用现有登录用户 Bearer Token 及管理员权限。

| 方法及路径 | 请求 | 成功回包 data |
| --- | --- | --- |
| `GET /api/v1/energy/meters` | 无 | 按 `meterId` 排序的表计定义数组 |
| `POST /api/v1/energy/meters` | `meterId`、`nameZh`、`nameEn`，可选 `readRoles` | 新建表计定义 |
| `PATCH /api/v1/energy/meters` | `meterId` 以及本次要更新的 `nameZh`、`nameEn` 或 `readRoles` | 更新后的表计定义 |

成功响应沿用 `{code, message, data}`。表计定义包含 `meterId`、`nameZh`、`nameEn`、`readRoles`。标识长度为 1–64 字符，区分大小写，如 `water/A.1` 和 `water/a.1` 是两个表计。名称长度为 1–128 字符。角色使用稳定键，保存时去重，新建时省略即默认 `["admin"]`。显式传入空角色数组后，所有登录角色均失去该表的读取权限。PATCH 省略的字段保留当前值，表计标识固定。

同标识的数据库定义优先。没有数据库行的旧表计沿用原 profile 的名称和角色范围。保存后从下一次相关请求开始生效，登录接口的原有访问权限继续生效。登记写入和公有读取按各自合同执行。旧 v2 机器授权继续来自兼容 profile。[能耗登记写入](../energy-registered-ingest-v1/README.zh-CN.md) · [能耗公有读取](../energy-public-reads-v1/README.zh-CN.md)

未登录或 Token 无效返回 401，缺少管理员权限返回 403，编辑未知表计返回 404，重复标识返回 409，非法请求返回 422，配置的数据库或必要结构不可用时返回 503。[OpenAPI](openapi.json) · [English](README.md)
