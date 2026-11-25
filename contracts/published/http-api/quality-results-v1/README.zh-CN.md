# 质量结果 API v1

[English](README.md) · [OpenAPI](openapi.json) · [合成请求示例](examples/requests.json)

每个归一化任务号对应一条质量结果。现场程序解析报告，把选取的值放入 `items` 提交，平台在质量管理中保存和读取。质量结果可以独立于计划和实绩存在。以下路径使用 `/api/v1` 前缀，写入使用 JSON。

| 方法和路径 | 访问范围和行为 |
| --- | --- |
| `POST /integration/quality/upsert` | 可信网络。创建或合并提交的字段。 |
| `GET /integration/quality/by-task/{taskNo}` | 可信网络。读取单条结果。 |
| `GET /integration/quality` | 可信网络。按条件分页。 |
| `GET /integration/quality/field-config` | 可信网络。读取已启用定义和配置版本。 |
| `GET /quality/results` | 有质量权限的登录用户。通过 `data.fields` 获取用于渲染的启用定义。 |
| `POST /quality/results` | 有质量权限的管理员、主管和操作员。新增单条结果，可填写目标及已启用且允许编辑的字段。 |
| `GET /quality/results/by-task/{taskNo}` | 有质量权限的登录用户。读取单条结果。 |
| `POST /quality/results/upsert` | 有质量权限的管理员、主管和操作员。编辑已有结果的可编辑字段。 |
| `GET /quality/field-config` | 管理员。读取包括停用项在内的完整定义。 |
| `PUT /quality/field-config` | 管理员。提交当前版本及完整定义。 |

私有 `/quality` 路由供平台 Web 前端使用，沿用登录和角色权限。公共 `/integration/quality` 路由供获准接入的 SMA、CA、FF 和第三方在可信网络内使用统一合同。部署侧负责网络隔离，现场程序负责报告解析和下游转发。

## 字段与更新

- `taskNo` 去首尾空白并转为 ASCII 大写，限 1–50 个 `A–Z`、`0–9`、`.`、`_`、`-` 字符。`targetKey` 可选，限 1–64 个同类字符（字母允许小写且区分大小写）。非空目标只可设定一次。
- `items` 的键与启用的定义精确匹配。支持最长 255 字符的字符串、整数部分最多十位及小数部分最多四位的有限 JSON 数、JSON 布尔值，以及最长 2048 字符且无凭据的绝对 HTTP(S) 链接。链接可自定义显示文本，留空时界面显示 URL。
- 省略 `items` 或提交空对象均不改字段。省略某个键保留原值，显式 null 清空可空字段。已启用但未赋值的字段读出 null。停用字段保留原值并从读取结果隐藏。`visible` 控制列表列，`editable` 控制人工输入。
- 定义包含稳定键、中英文标签、类型、可选单位、开关、顺序及可选的 `linkText`。同一部署最多 100 项，包含停用项。保存后的键、类型和单位不可改，每次提交完整定义均须保留已有键。只有内容发生变化时版本才递增。
- 两个列表入口均接受 `taskNo`、`targetKey`、`createdFrom`、`createdTo`、`page` 和 `pageSize`。按创建时间含下界、不含上界筛选，客户端须指定偏移或 `Z`。默认第 1 页，每页 20 条，最多 100 条。按创建时间和 ID 倒序，结果时间携带 `+08:00`。相同值的重试保留 `updatedAt`。

## 响应

成功信封为 `{code,message,data,timestamp}`，写入返回 `data.outcome`（`created`、`updated` 或 `unchanged`）和 `data.quality`。集成入口允许空结果，空结果本身没有报告完成语义。

人工新增须提供 `taskNo`，可省略 `targetKey` 和 `items`。成功时 HTTP 201，信封 `code: 200`，返回 `data.outcome: "created"` 和 `data.quality`。归一化后任务号已存在时返回 HTTP 409 和 `quality.task_no_conflict`，已有值原样保留。后续集成上报可按现有规则合并字段。

错误信封另有 `errorCode` 和 `details`。常见错误包括 `quality.unauthenticated`（401）、`quality.forbidden`（403）、`quality.not_found`（404）、`quality.target_conflict` 或 `quality.config_revision_conflict`（409）和 `quality.invalid_request`（422）。响应丢失或收到 `quality.commit_unknown`（503）时，先重读结果或配置并核对再决定是否重试。`quality.unavailable`（503）表示存储暂时无法服务。

参见[后端路由](../../../../backend/app/quality/api/results.py)、[数据结构](../../../../backend/app/quality/schemas/results.py)、[基础规格](../../../../plans/ARCH-QUALITY-001-task-quality-results/spec.md)和[人工新增规格](../../../../plans/ARCH-QUALITY-002-manual-results-and-legacy-retirement/spec.md)。
