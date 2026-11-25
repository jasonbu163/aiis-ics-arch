Task ID: ARCH-OBS-008
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r1 已修复 QA1 F01 并完成 DEV 复验，交 fresh-context Verification 复核

# 开发记录

## 实施

- DEV01（AC01、AC04）解除过程／实时的运行时库 revision、UUID、库名、MySQL 版本、会话时钟偏移及预检依赖。查询按原数据范围访问，真实数据库错误返回现有 `not_ready` 错误。保留私有 profile 开关、已配置业务范围及旧身份冲突保护。
- DEV02（AC02、AC03）保留公开登记读写的无 Bearer 合同、旧机器 Bearer 和前端私有权限。来源启用校验、指标及槽位验证、重复提交与事务沿用。使用数据库 `UTC_TIMESTAMP(6)` 并在写入及计算快照新鲜度时转成上海业务时间。实际修改的备注或复核标记也使用该时间更新。
- DEV03（AC05、AC06）能耗入口继续执行原 profile 目标校验及严格 guard。采集源码、数据库模型、迁移脚本和私有配置未改。用现有 dev 服务热加载后的工作树验证。

开发文件为 `backend/app/equipment_observation/` 中的 `api/routes.py`、`profile.py`、`services/{guard,ingest_v2,reads,registered_ingest,write_sources}.py` 和双语 README。已修改的聚焦测试为 `backend/tests/test_equipment_observation_{domain,r10_flow,r8}.py`、`test_generic_task_revision_guards.py`、`test_observation_write_sources.py`、`test_quality_revision_guards.py`。

## DEV 自检

| 检查 | 实际结果 |
| --- | --- |
| `git diff --check`、用项目 Python 执行 `ast.parse` | 均退出 0，13 个任务相关 Python 文件语法通过。README 原有链接保持。 |
| 项目环境下的观测、能耗与采集聚焦回归 | 226 通过、2 跳过，退出 0。有一条 SQLite datetime adapter 弃用提醒。跳过为已冻结的 BE012 B 独立候选及要求独立任务 fixture 的采集测试。 |
| dev 实际版本及匿名 GET | 只读确认实际 revision 为 `a1c307f8d2e4`。现有登记来源的 `latest` 和 `history` 均返回 200 且有数据。不存在的来源返回 404，修复前同类请求因旧 guard 返回 503。 |
| dev 公开写入 | 无 Bearer 的 `latest` 和 `history` 都返回 200 和 `stored`。同一事件重试返回原回执，改值复用同一事件返回 409，错误槽位返回 422。按测试任务 GET 返回写入指标，两条不带任务过滤的最新查询仍返回原有默认记录。 |
| dev 私有权限 | 未登录请求实时卡片、过程默认上下文和登记管理均返回 401。授权读取、管理员配置和权限分组通过聚焦 HTTP 测试验证。本次自检未使用 dev 登录凭据验证授权后的页面接口。 |
| 回归范围 | 能耗读写、原严格 guard 和旧机器权限通过聚焦测试。采集 V2 与浏览通过无库测试，其中独立任务 fixture 跳过。本次自检未向 dev 写入采集样本。 |

执行的聚焦命令，在 `backend/` 下使用自有临时 pytest 目录：

```bash
uv --no-cache run --locked --no-sync pytest -q --basetemp "$test_dir/pytest" -m no_db \
  tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r8.py \
  tests/test_equipment_observation_r10.py tests/test_observation_write_sources.py \
  tests/test_equipment_observation_domain.py tests/test_quality_revision_guards.py \
  tests/test_generic_task_revision_guards.py tests/test_observation_receipt_separation.py \
  tests/test_observation_retirement.py tests/test_plc_facts_v2.py tests/test_acquisition_data_browse.py
```

首次候选的预检指出时钟函数须通过已公开的 `to_storage_time` 导入，已调整。初次范围测试的一个既有测试要求 pytest fixture 路径位于 `/private/tmp`，通过指定自有 `--basetemp` 后，上表最终复跑通过。沙盒默认连接不到本地服务，dev 验证使用已获准的本地主机连接。项目未运行数据库迁移或重置服务。

## QA1 F01 返工

QA1 复现了路由根据实际 URL 中的 `/energy/` 片段判断接口类别的问题。对采样组名为 `energy` 的观测槽位执行 PATCH 时，数据库失败错误进入能耗异常分支。现按已匹配的路由模板识别对应入口。公开写入鉴权和机器 Bearer 的入口分类也沿用匹配模板。

聚焦测试 `test_database_error_routing_uses_template_not_group_key` 验证 `energy` 和 `thermal` 两组的观测 PATCH 在相同数据库异常下都返回 `503 equipment_observation.not_ready`，能耗的原分支仍保留。使用上文相同聚焦命令复验，227 通过、2 跳过，退出 0，原 SQLite 弃用提醒仍在。`git diff --check` 退出 0。dev 服务按现有开发入口热重载。本轮复验未新增 dev 记录。

QA1 对应初次候选 diff SHA-256 为 `31ca3fe32f9d5e3ae442760fd093b585cdba08910fa365829079fc31c1328582`。本次返工后候选的任务限定 diff SHA-256 为 `b0bdf2091c197026a64e946198ab558cc99f1941468732689ad8b89663af776b`。

## 精确交接

- 候选为当前共享工作树，Git 基线 `7f654acd951171767bc253ea5bebdcda6435b608`。未提交。上述实现和聚焦测试路径的当前 `git diff` SHA-256 为 `b0bdf2091c197026a64e946198ab558cc99f1941468732689ad8b89663af776b`。规格批准记录后的 SHA-256 为 `49ee8f255d84864f96469861de0ba4cdbe8f09c23e6cf8f9095817b8d728adbe`。工作树中有并行任务修改，均不属于本交接候选。
- dev 测试任务 `OBS008-DEV-4A30B83B3AC1` 使用既有启用来源和早于已有样本的采集时刻，通过公开接口新增两条记录。实时记录 ID `24`、回执 `293`，过程记录 ID `94`、回执 `294`。两条记录和回执保留，独立验证可用此任务号读取。现有业务记录未被覆盖。若后续要移除测试记录，由 Human Owner 另行确认。
- 已回收自建 pytest basetemp 以及初次运行生成的任务 pytest 目录和指向它的链接。无保留临时文件或服务。8000 是已有 dev 服务。
