Task ID: ARCH-ENERGY-003
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: 交 Human Owner 最终验收
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 能耗公有读取独立验证

2026-11-25（上海）在 fresh context 中核对[已批准规格](spec.md)、[Development 交接](tasks.md)、正式工作树差异、查询实现、测试及发布合同。正式源码已整合于工作树，基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。规格 SHA-256 为 `7a0d129ec3853e1ae9ee8ec14c328836c663bd9805eadb9cefa2a5a7497efcee`，交接记录为 `ea242d526cb4234e92d435d922751caddcfa8d1c2a6f43bc13e7e53400a80844`。使用 shasum -a 256 -c 对清单逐项校验，18/18 相符。清单 SHA-256 为 `c19258b3db99c514e310ed1794638b31cb56fc1658cb9f9b3c609c73d91a087f`。

| 标准 | 独立结果 |
| --- | --- |
| AC01 | 两条 GET 的无头回包与空 Authorization、Basic、无效 Bearer、自定义值逐一相等。相同 samples 路径下旧 POST 缺少或使用无效机器 Bearer 均为 401，有效机器 Bearer 成功。登记 POST 免 Token，Web 样本、指标配置和登记管理保留登录校验。发布快照逐方法对应运行时 OpenAPI。 |
| AC02 | 四种筛选、大小写及未知组合通过。乱序写入后仍选实际最大采集时间，同刻由较大 ID 决胜，返回 bad／unknown 原质量。五个组的顺序与预期一致。窗口按表计与组分区，返回查询未设分页或上限。 |
| AC03 | 13 点样本保留数值 0，未混入 12 点累计值。无配置槽位被略过，保留定义的停用指标可读；不同表计、组及旧 v2 数据按各自定义解读。区间仅在两个端点齐备时出现，验证六位小数与 +08:00。 |
| AC04 | 复核必填、可选组、起止端点、等时刻、时区等价、降序、默认及 1/100 页大小、越界页仍有总数、空结果零页和 422 信封。MySQL READ COMMITTED 下，样本 SELECT 后由独立连接插入；该页样本数和总数均为 3，下次均为 4。 |
| AC05 | 从发布文档提取标准库 Python，在真正的回环 Uvicorn HTTP 服务上读取最新与两页历史，输出 0 和历史累计值。另选缺少 activePower 的表计，实际打印“缺测”。固定表计与组的 SMA 路径从回包读取数值 0、采集时刻和 bad；未知表计为空数组，缺指标时无该键。对照 SMA 源码核查 pointer 处理。 |
| AC06 | 登记多表写入与重放、旧 v2 写入及 Web 读取、设备与过程入口及重放均通过。隔离库推进合成无关后继版本后 GET 仍可用；实际依赖表不可用及连接不可达时两个 GET 均为 503 并返回 not_ready。目标 UUID 错配亦拒绝读取。 |
| AC07 | 比较读取前后的能耗样本、回执、配置及旧设备／过程数据快照，行值一致。查询使用既有能耗样本与指标配置，未要求任务号或跨域 JOIN。核查 backend/alembic 工作树，无变更。 |

## 环境与复核命令

macOS，backend 项目 uv 环境（Python 3.13）。以下命令均退出 0。基础 MYSQL_PORT 固定为 1，MySQL 测试另行指定专属回环端口、随机 schema、密码、实例 UUID 和确认串。

1. 在 backend 运行 `uv run --no-sync pytest -q -p no:cacheprovider -m no_db tests/{test_energy_public_reads,test_energy_registered_ingest,test_equipment_observation_domain,test_equipment_observation_r10_flow,test_equipment_observation_r8,test_observation_write_sources,test_observation_receipt_separation,test_observation_retirement,test_role_api_permission_startup}.py`。126 passed，1 个已有 SQLite datetime adapter 弃用提示。交接前协调者基线日志为 74 passed。
2. 使用已审阅的 start-mysql.sh 创建 QA 独占 MySQL 8.4.6，镜像禁止拉取、绑定 127.0.0.1:50103。由 run-mysql.sh 运行 `uv run --no-sync pytest -q -p no:cacheprovider tests_mysql/test_energy_public_reads_mysql.py tests_mysql/test_energy_registered_ingest_mysql.py`。2 passed，含独立 Uvicorn、标准库及并发测试。
3. 在 backend 运行 `PYTHONPATH=. MYSQL_PORT=1 uv run --no-sync python /private/tmp/aiis-energy003-dev.HUDulA/unreachable.py`，验证两个真实连接失败响应。另用 `uv run --no-sync python -` 启动内存 SQLite 夹具与随机回环 HTTP，追加请求逐项比较四种认证头、分页上下限、SMA 数值／时间／质量路径及发布示例缺测输出，全部通过。
4. 根目录 `git diff --check`、交付 Python 文件内存 compile、两个 JSON 解析、24 个相关 Markdown 本地链接目标检查通过。源码索引含新增读服务、合同与测试。

## 交付与资源

独立结论为 qa_passed，AC01–AC07 均通过，无 blocker。正式 dev、生产服务可用性和真实 SMA／CA／FF 现场接入未经验证；本次使用合成数据，真实数据库及服务没有执行变更。等待 Human Owner 最终验收。

已停止 QA 回环服务，移除专属 MySQL 容器 c1a5090ae579、临时 schema、连接凭据及 QA 缓存目录。Development 与协调者日志目录分别为 /private/tmp/aiis-energy003-dev.HUDulA 和 /private/tmp/aiis-energy003-coordinator.8tJqJ2，已完成取证，交协调者回收。
