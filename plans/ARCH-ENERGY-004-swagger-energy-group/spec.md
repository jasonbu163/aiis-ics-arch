Task ID: ARCH-ENERGY-004
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: Human Owner 已批准精确 r1，交 Development 按 STD 实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch
Classification: independent_fix
Capability: 能耗接口在 Swagger 中独立、完整可发现
Owner: Core 能耗管理
Acceptance Chain Reference: Human Owner 精确范围批准 → Development handoff → fresh-context Verification → Human Owner 最终验收
Related Task: ARCH-OBS-007、ARCH-OBS-010、ARCH-ENERGY-003、ARCH-ENERGY-005

# 能耗 Swagger 分组 · r1

## 1. 背景与目标

Human Owner 在通过 Swagger 测试能耗接口时反馈接口分组不易查找，希望能耗作为独立分组。2026-11-25（Asia/Shanghai），Human Owner 对先整理 Swagger 分组、再单独起草表计管理规格的建议表示「好的 按你的建议来做 批准」。本文件将分组调整整理为独立规格。Human Owner 已批准精确 r1 的 Development 范围。

当前 [观测路由](../../backend/app/equipment_observation/api/routes.py) 的能耗方法与实时／过程共同使用 `Equipment observation` 标签。[单价路由](../../backend/app/energy/api/energy_price.py) 的三项方法使用 `Auxiliary - Energy Price`。`ARCH-ENERGY-003 r1` 的两条公有 GET 已独立验证，当前状态和事实记录见其 [验证记录](../ARCH-ENERGY-003-public-energy-reads/checklist.md)。

本任务让实际 FastAPI OpenAPI 和 Swagger UI 将现有能耗接口集中显示在一个 `Energy` 分组，方便区分能耗与其他模块的接口。匿名公有和管理员操作的标题分别使用 `Public —` 和 `Management —` 前缀，便于在同一分组内识别。调用路径、权限和数据行为沿用各自已交付合同。

## 2. 目标接口清单

以下路径以 `/api/v1` 为前缀。实现前以正式工作树实际启用的 OpenAPI 为基线，并按 HTTP 方法分别核对。同一路径的 GET 与 POST 各为一个操作。

| 用途 | 现有方法和相对路径 |
| --- | --- |
| 公有最新与历史查询 | `GET /integration/energy/latest`、`GET /integration/energy/samples` |
| 已登记来源批量写入 | `POST /integration/energy/registered-samples` |
| 旧机器发现与写入 | `GET /integration/energy/metric-definitions`、`POST /integration/energy/samples` |
| 来源登记 | `GET /energy/write-sources`、`POST /energy/write-sources`、`PATCH /energy/write-sources/{sourceKey}`、`DELETE /energy/write-sources/{sourceKey}` |
| 表计选项和指标定义 | `GET /energy/consumption/options`、`GET /energy/consumption/definitions` |
| 表计指标配置 | `GET /energy/metric-configs`、`POST /energy/metric-configs`、`PATCH /energy/metric-configs/{meter_id}/{group_key}/{metric_key}` |
| 统计和样本 | `GET /energy/consumption/samples`、`GET /energy/consumption/summary`、`GET /energy/admin/consumption-samples`、`PATCH /energy/admin/consumption-samples/{identity}` |
| 能源单价 | `GET /energy/current`、`GET /energy`、`POST /energy` |

以当前源码和模块启用状态为基线，现有清单包含 21 个操作。验收还按路径边界覆盖实际注册的能耗操作，不把 21 固化为未来功能的全局限制。匹配准确覆盖 `/api/v1/energy`、`/api/v1/energy/` 下的方法及 `/api/v1/integration/energy/` 下的方法，不误匹配近似前缀。

## 3. 要求和兼容合同

1. 每个现有能耗操作在完整应用生成的 OpenAPI 中只有 `Energy` 这一标签，并在 Swagger UI 的 `Energy` 分组出现一次。现有非能耗设备和过程接口仍可在原分组找到。
2. 元数据调整采用现有 FastAPI 路由机制。价格路由和能耗观测路由继续由现有 manifest 注册，业务逻辑、模型和数据归属沿用当前实现。禁止把模块目录移动作为分组的前置条件。
3. HTTP 方法、URL、`operationId`、参数及默认值、请求／响应 schema、状态码、错误信封、端点启停和依赖的授权规则保持当前合同。两个路径相同但方法不同的 `/integration/energy/samples` 必须都保留。
4. 登记多表 POST 和 `ARCH-ENERGY-003` 的两条公有 GET 保留无需 `Authorization` 的现状；旧机器指标发现与旧单表 POST 保持机器 Bearer；页面查询、来源登记、指标管理和单价接口保持现有用户 Bearer 与权限。Swagger 的锁标记和 OpenAPI `security` 应与实际方法一致。
5. 在同一个 `Energy` 分组中，对匿名公有 GET／POST 的 OpenAPI `summary` 使用 `Public —` 前缀，对管理员的来源登记、表计指标配置和样本管理使用 `Management —` 前缀。后面用英文动词和对象说明操作，沿用现有 Swagger 英文风格。旧机器 Bearer 与普通 Web／价格方法保留原标题和认证标识，不按前缀改变实际权限。
6. 现有价格与能耗公开合同及示例继续可查。对照运行态后，仅同步能耗登记写入 v1 和能耗公有读取 v1 快照中受影响操作的 `tags` 及第 5 条允许的 `summary`。不得改变快照中的路径、方法、`operationId`、认证、参数、schema 或样例。现有旧 v2 快照没有相关 `tags`，保留原内容。需要时仅在现有中英文说明中补充 Swagger 的 `Energy` 分组位置。
7. 实时／过程和能耗的数据域保持独立。沿用各自来源、样本、回执和权限；此任务不引入表计配置数据、跨域外键、跨域 JOIN 或 `taskNo` 要求。
8. 浏览器或 OpenAPI 展示属于源码验证。dev 的代码是否自动加载应在实际交付时核对；独立验证通过不自动表示实际服务完成切换。

## 4. 实施边界

允许的最小变更面为：

- `backend/app/equipment_observation/api/routes.py` 与 `backend/app/energy/api/energy_price.py` 中直接相关的路由／Swagger `tags` 和第 3 节第 5 条限定的 `summary` 元数据。保留现有处理函数、路由类、鉴权依赖、接口行为和 manifest 装配。
- `backend/tests/test_openapi_router_tags.py` 中现有分组期望及直接相关的回归断言。必要时在 `backend/tests/test_energy_public_reads.py`、`backend/tests/test_energy_registered_ingest.py`、`backend/tests/test_energy_price_api.py` 增加或调整本任务直接相关的 OpenAPI、Swagger 分组与认证断言。其余测试优先作为既有回归执行。
- `contracts/published/http-api/energy-public-reads-v1/openapi.json` 和 `contracts/published/http-api/energy-registered-ingest-v1/openapi.json` 中受影响方法的 `tags` 和第 3 节第 5 条限定的 `summary`。相关双语 README 仅在需要帮助定位 Swagger 分组时作最小同步。
- 任务 bundle 按 STD 分阶段记录。索引由协调者在角色文档更新后同步。

不新增接口、表、迁移、项目依赖、前端页面或运行时配置，不重命名或移动已有模块。表计管理由独立规格处理。本任务不执行真实数据库写入／迁移、服务重启、部署、现场设备操作或发布。

本任务 Development 按范围使用 `backend-arch`、`code-document-indexer`，遵循现有项目工具链和公开合同规范。实现应基于当前交付工作树，保留并行任务未提交改动。

## 5. 验收标准

| ID | 验收结果 |
| --- | --- |
| AC01 能耗操作集中 | 枚举完整应用 OpenAPI 的能耗路径及方法，逐项确认 `tags = ["Energy"]`，Swagger UI 的 `Energy` 分组完整显示且每个操作只出现一次。显式覆盖精确 `/energy` 根路径和同路径 GET／POST，核对匿名公有及管理员方法标题分别带 `Public —` 和 `Management —`。 |
| AC02 既有分组保留 | 对照完整应用调整前后 OpenAPI 的所有设备状态、过程监控和其他模块方法，确认原分组及可发现性保持。模块禁用、缺席和已注册路由行为按原合同回归。 |
| AC03 认证区分 | 用合成 HTTP／OpenAPI 检查公有 GET、登记 POST 免 Token；同路径旧 POST 与发现接口仍要求机器 Bearer；Web、管理和价格接口保持原有 Bearer 及权限。 |
| AC04 HTTP 合同与快照 | 逐操作比较调整前后路径、方法、`operationId`、参数、请求／响应、`security` 和错误契约。两个能耗公开 OpenAPI 快照与运行态受影响操作一致，快照差异限于相应 `tags` 和第 3 节第 5 条限定的 `summary`。旧 v2 公开合同及合成样例保留。 |
| AC05 工程与交付 | 项目声明的 `uv` 环境运行聚焦 OpenAPI、能耗公有读取、登记写入和单价回归；必要的合成 Swagger UI 检查与文档链接检查通过。记录实际命令、退出码、正式工作树与验证目标及未覆盖的运行环境。没有新增数据库结构变更。 |

## 6. 风险、回退与交接

路由拆分或重新装配可能改变顺序、`operationId`、路由类和依赖；应以现有正式工作树的完整 OpenAPI 和实际请求行为对照，优先采用范围内的最小元数据调整。Swagger 标签与标题变化只改变接口文档的展示，实际服务需加载调整后的源码才能显示新分组。应用回退时恢复原有标签和相关标题即可，业务数据和接口合同沿用现状。

| 日期 | 记录 |
| --- | --- |
| 2026-11-25（Asia/Shanghai） | Human Owner 同意先整理 Swagger 能耗分组，再单独起草表计管理方案。PM 起草本 r1；精确 Development 范围与最终验收待批准。 |
| 2026-11-25（Asia/Shanghai） | Human Owner 明确表示「批准 ARCH-ENERGY-004 r1，按 STD 启动 Development」。据此批准本任务精确 r1。 |

Human Owner 已批准精确 r1。由 Development 按 STD 建立实施记录与自检，再交 fresh-context Verification；最终验收由 Human Owner 决定。

本次规格起草无临时资源。
