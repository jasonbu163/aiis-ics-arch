Task ID: ARCH-ENERGY-003
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 精确 r1 已进入正式工作树并完成 Development 自检，交 fresh-context Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-ENERGY-003 r1 实施与开发自检

## 实施范围与结果

依据获批准的 [r1 规格](spec.md)，SHA-256 为 `7a0d129ec3853e1ae9ee8ec14c328836c663bd9805eadb9cefa2a5a7497efcee`。正式源码目录为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。开发直接在正式工作树完成，保留已有其他任务改动，当前为未提交的工作树交付。

- 在现有观测路由新增免 Token 的 `GET /api/v1/integration/energy/latest` 和 `GET /api/v1/integration/energy/samples`。两条 GET 使用既有响应信封和错误码；同路径旧 POST 保持机器 Bearer，登记 POST 和 Web 鉴权保持现行合同。
- 最新查询按表计与采样组分区，按采集时刻及记录 ID 取各自最新的一条，按两个标识的 UTF-8 顺序返回。历史范围含两个端点且按采集时刻和 ID 降序。总数与当前页来自同一 SQL 语句，读已提交下也一致，越界页仍保留匹配总数。
- 公有回包只投影当条事实的可解读数值，保留零、真实质量及两个完整区间端点。值不从较早样本补入；定义保留的停用指标历史可读。数据库访问仍核验实际能耗库身份，依赖已有能耗样本、指标表及索引。没有新增表、索引或 Alembic 版本。
- 编写了双语公开合同、与当前路由一致的 OpenAPI、合成回包及 Python／SMA 示例。SMA／CA／FF 产品源码、Web 页面、实际部署和环境配置没有纳入此次实施。

## 交付文件

| 范围 | 位置 |
| --- | --- |
| 路由与接口合同 | `backend/app/equipment_observation/api/routes.py`、`api/energy_public_read_contract.py` |
| 查询和回包 | `backend/app/equipment_observation/services/energy_public_reads.py` |
| 聚焦验证 | `backend/tests/test_energy_public_reads.py`、`backend/tests_mysql/test_energy_public_reads_mysql.py` |
| 公有合同 | [能耗公有读取目录](../../contracts/published/http-api/energy-public-reads-v1/README.zh-CN.md) 内双语 README、`openapi.json`、`examples/reads.json` |
| 入口说明 | `backend/app/equipment_observation/README{,.zh-CN}.md`、`contracts/README{,.zh-CN}.md`、`docs/equipment-status-process-monitoring{,-guide}{,.zh-CN}.md`、`CODE_INDEX.md` |

## Development 自检

| 项目 | 执行结果 |
| --- | --- |
| AC01 鉴权与接口形状 | SQLite／MySQL 合成 HTTP 均可无头读取，附带无效 Authorization 的结果一致。MySQL 旧同路径 POST 无令牌／坏令牌都为 401，有效机器令牌写入成功；已登记免 Token POST 一包两表成功且可重放。Web 样本、配置和写入登记的登录约束保留。OpenAPI 对比真实路由，GET 为 `security: []`，POST 和 Web 保留各自 Bearer。 |
| AC02 最新值 | 四组筛选、空数组、大小写、排序、乱序到达、采集时间相同时 ID 排序及 bad／unknown 质量已覆盖。 |
| AC03 样本 | 验证真零、缺值、存量停用定义、无法解读的槽位、真实区间及旧 v2 样本；回包按上海六位小数且没有回执、备注、操作者或任务号。 |
| AC04 历史 | 验证两个边界、相同时间、时区等价、默认及越界页、空结果与非法参数。MySQL 在 READ COMMITTED 下于样本读取语句之后、字段投影之前并发插入一行，正在返回的总数和页保持 3，下次请求同时为 4。 |
| AC05 示例 | 用真实回环 HTTP 执行发布文档的标准库 Python 例程，将页大小调为 2 以覆盖翻页；验证零和旧累计值。对同一回包核对 SMA 固定路径、空数组和缺字段。此为合同示例验证。 |
| AC06 回归与工程 | 两类既有能耗写入、设备／过程旧 POST 和重放、Web 权限、模拟无关 Alembic 后继及目标错配回归通过。移走合成库的指标表或连接无监听的回环端口时，两条 GET 均返回 503。 |
| AC07 数据边界 | 在读取前后比较能耗样本、回执、指标及旧设备／过程数据，行一致。并发检查的写入由隔离夹具显式发起。检查迁移改动为空，公有读查询只访问能耗域。 |

执行证据：

1. 运行仓库 `uv run --no-sync pytest -q -p no:cacheprovider -m no_db` 加 `tests/test_energy_public_reads.py`、`tests/test_energy_registered_ingest.py`、`tests/test_equipment_observation_domain.py`、`tests/test_equipment_observation_r10_flow.py`、`tests/test_equipment_observation_r8.py`、`tests/test_observation_write_sources.py`、`tests/test_observation_receipt_separation.py`、`tests/test_observation_retirement.py`、`tests/test_role_api_permission_startup.py`。基础连接参数固定不可能连接的端口 1。退出 0，126 项通过，1 个既有 SQLite datetime adapter 弃用提示。协调者另存既有五套聚焦基线 74 项通过。
2. 使用现成 MySQL 8.4.6 本机镜像，经 `docker run --rm --pull=never` 仅绑定随机回环端口。使用已有显式隔离夹具在专属随机 schema 建立合成前驱结构、执行已存在的能耗登记迁移及合成无关后继。项目 `uv run --no-sync pytest -q -p no:cacheprovider tests_mysql/test_energy_public_reads_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py` 退出 0，两项通过。连接信息由脚本仅从本次临时目录传入。
3. `git diff --check`、Python 编译检查、JSON 解析及 24 条新增本地文档链接均通过。`backend/alembic` 下无本任务变更。
4. `PYTHONPATH="$PWD" MYSQL_PORT=1 uv run --no-sync python /private/tmp/aiis-energy003-dev.HUDulA/unreachable.py` 在 `backend/` 下退出 0。通过真实 DBAPI 连接错误验证两条 GET 的稳定 503 信封，端口由测试预留且从未启动服务。

## developer_handoff

正式工作树已集成，验证覆盖隔离 HTTP、MySQL 8.4.6 和标准库示例。正式 dev、生产及现场调用方的当前运行状态未经调试或探测；未执行实际库迁移、服务启停、部署或设备联调。没有新的结构迁移需要应用。本记录是 Development 自检，待独立验证。

候选源码的 18 文件清单为 `/private/tmp/aiis-energy003-dev.HUDulA/source.sha256`，该清单 SHA-256 为 `c19258b3db99c514e310ed1794638b31cb56fc1658cb9f9b3c609c73d91a087f`。在正式工作树执行 `shasum -a 256 -c /private/tmp/aiis-energy003-dev.HUDulA/source.sha256` 已全部匹配。此清单仅包含本任务的实现、测试和合同面；以同一基线和已批准规格进入 fresh-context Verification。

## 临时资源收尾

隔离 MySQL 容器及专属 schema、临时密码、连接信息已回收，回环 HTTP 测试服务已停止。保留 `/private/tmp/aiis-energy003-dev.HUDulA/` 中的开发日志、候选源码指纹和复验用的 fixture 启停及测试脚本，供 Verification 复现和核对。独立验证记录落地且不再需要返工样件后，由协调者回收该目录。无本任务 Git 分支、worktree 或提交。
