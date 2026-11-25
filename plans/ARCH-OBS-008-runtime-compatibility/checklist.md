Task ID: ARCH-OBS-008
Revision: r1
Status: qa_passed
Owner Role: Verification
Handoff: QA2 已通过，交 Human Owner 最终验收

## 独立验证与候选

2026-11-24，macOS、项目 backend/.venv Python 3.13，独立上下文。已读取根契约、workflow、根及模块说明、spec 与 tasks。交付工作树 HEAD 为 7f654acd951171767bc253ea5bebdcda6435b608。按 tasks 的 15 个文件运行 git diff | shasum -a256 得 31ca3fe32f9d5e3ae442760fd093b585cdba08910fa365829079fc31c1328582；spec SHA-256 为 49ee8f255d84864f96469861de0ba4cdbe8f09c23e6cf8f9095817b8d728adbe。git diff --check 退出 0。候选均为既有文件，未涉及模块结构、迁移、采集源码或前端。

## F01 · 配置组名影响数据库错误合同

backend/app/equipment_observation/api/routes.py 第 34、51–54 行通过实际请求路径含有 /energy/ 判断能耗。设备配置 PATCH 的动态 group_key 允许 energy，数据库读取出错时该设备请求因此跳过观测 not_ready 处理。独立最小复查用 backend/.venv/bin/python、FastAPI.include_router(routes.router)、TestClient(raise_server_exceptions=False)；管理员依赖替换为通过、get_profile 返回空 dict、get_db 提供其 get 方法抛出 sqlalchemy.exc.OperationalError 的假会话。使用相同请求体 {"enabled":true} 对比：

| PATCH 路径（/api/v1 下） | 实际结果 |
| --- | --- |
| /equipment/metric-slot-bindings/latest/thermal/1 | 503，equipment_observation.not_ready |
| /equipment/metric-slot-bindings/latest/energy/1 | 500，Internal Server Error |

该验证经过实际路由和 update_binding 的首个数据库读操作，未连接 dev 或写记录。要求同一设备配置操作的错误协议独立于组名，同时保持真正能耗路由的既有错误语义。退回 Development。

## 验收结果

| 条目 | 证据与结果 |
| --- | --- |
| AC01 | dev 只读 SELECT version_num FROM alembic_version 返回 a1c307f8d2e4。管理员 GET 实时卡片、过程默认上下文、曲线、两类明细、卡片及曲线配置、来源管理均 200。检查 profile 和读写调用，设备／过程不再执行目标 revision、UUID、库名、MySQL 版本或结构预检。 |
| AC02 | 通过 dev 已有记录反查来源。无 Bearer GET 两目标均 200 且各返回一个指标组。移除只读字段后，通过 normalize 核对事件号和摘要均与原回执相同，再向公开 POST 重放，均为 200，latest 回执 293、记录 24，history 回执 294、记录 94；不存在的任务号分别返回 200 和空结果。新事件首次插入、业务拒绝与冲突分支由聚焦测试覆盖，DEV 首次线上插入记录见 tasks。 |
| AC03 | 本机 8000，匿名 GET 实时卡片、过程默认上下文、来源管理、旧机器指标定义均 401。通过既有 dev 配置和 /api/v1/auth/login 验证，admin 对 AC01 八个端点均 200，operator、supervisor 各八个均 403。凭据与令牌仅存于进程内。机器授权成功、作用域拒绝及受权读取由聚焦测试覆盖。 |
| AC04 | F01 失败。两目标在线可用及空结果已核对；聚焦验证另覆盖 UTC_TIMESTAMP(6) 转上海、来源身份冲突、事务／重试、旧 profile 及后继版本。 |
| AC05 | 能耗配置校验经 require_energy_target，严格 guard 仍核对原版本、库标识、时钟及结构。PLC facts 使用自身 v2_config、source_registry、v2 和 observation_evidence；git diff -- backend/app/plc_facts 为空。能耗、采集样本、浏览和维护边界由下列测试及源码验证。未向 dev 提交采集样本或能耗事件。 |
| AC06 | 使用原 dev 服务 127.0.0.1:8000；默认沙盒 curl 退出 7，获准本机访问后成功。SQL 仅 SELECT，重放 POST 前逐一核对摘要，使用既有测试任务 OBS008-DEV-4A30B83B3AC1。QA 未新增业务记录、执行 DDL、迁移或更新既有记录。 |

## 聚焦命令与环境限制

在 backend 目录执行，pytest 退出 0，226 passed、2 skipped、1 条 SQLite datetime adapter 弃用提醒。跳过项对应冻结的 BE012 B 和需独立任务 fixture 的采集用例。复核公开读写用项目 Python、SQLAlchemy 和 httpx 直连本机既有服务；私有登录首次按 snake_case 取返回值遇 KeyError，改用实际 accessToken 后三组登录均成功。

```sh
PYTHONDONTWRITEBYTECODE=1 uv --no-cache run --locked --no-sync pytest -p no:cacheprovider -q --basetemp /private/tmp/obs008-qa.iB7w1YMU/pytest -m no_db tests/test_equipment_observation_{r10_flow,r8,r10,domain}.py tests/test_{observation_write_sources,quality_revision_guards,generic_task_revision_guards,observation_receipt_separation,observation_retirement,plc_facts_v2,acquisition_data_browse}.py
```

已回收 /private/tmp/obs008-qa.iB7w1YMU。无保留的 QA 临时文件或服务。dev 的既有两条 DEV 测试记录及其回执保留，由 Human Owner 决定清理时点。

## QA2 独立复验 · 2026-11-24

QA1 判定为 `qa_failed`，上文保留原始证据。QA2 在新的 Verification 上下文复核 r1。HEAD、spec 摘要与 QA1 相同。按 tasks 的 15 个文件运行 `git diff -- <路径> | shasum -a 256`，结果为 `b0bdf2091c197026a64e946198ab558cc99f1941468732689ad8b89663af776b`，与返工交接一致。`git diff --check` 退出 0。

- **AC04 / F01 通过。** 在 backend 以 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -` 独立重跑上述 QA1 故障注入步骤，保持真实路由和 update_binding 调用，只替代鉴权、profile 和数据库会话。相同 PATCH 请求体分别用于 thermal 和 energy，两者均返回 503 和 equipment_observation.not_ready，退出 0。路由现在通过已注册模板 self.path 分类，机器依赖也使用匹配模板；真正能耗路由保留原异常传播，聚焦测试覆盖其 500 分支。
- **AC01、AC02、AC03、AC05、AC06 通过。** 沿用 QA1 表中现有 dev 后继版本、两种公开读写、三组角色及范围证据。本轮在 backend 重跑上文完整 no_db 命令，basetemp 替换为 /private/tmp/obs008-qa2.mk8ZKjUQ/pytest。退出 0，227 通过、2 跳过、1 条 SQLite 弃用提醒，10.02 秒。两项跳过原因见 QA1。未在线追加能耗或采集样本。
- **当前服务。** 沙盒内 curl 退出 7。获准访问既有 127.0.0.1:8000 后，匿名 GET /api/v1/equipment/latest-cards 返回 401，GET /api/v1/integration/observations/latest?sourceKey=obs008-qa2-missing&target=history 返回 404 和 equipment_observation.not_found，curl 退出 0。HTTP 探测确认服务可达与合同响应，未从运行进程提取源码指纹。F01 异常在交付工作树的测试进程注入。QA2 无在线写入、迁移、服务重启或新增测试记录。

**Verdict** 为 `qa_passed`。F01 关闭，交 Human Owner 最终验收。

已回收 /private/tmp/obs008-qa2.mk8ZKjUQ，无保留的 QA2 临时资源。沿用的 DEV 测试任务及回执见上文。
