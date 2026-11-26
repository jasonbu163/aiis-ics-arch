Task ID: ARCH-ENERGY-002
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification
Handoff: Human Owner 已最终验收 ARCH-ENERGY-002 r1，交协调者同步任务索引。
Workflow Mode: STD

# 能耗曲线设置独立验证

2026-11-25，Asia/Shanghai。Verification 使用 fresh context 从正式工作树独立重建候选。AC01–AC07 通过，AC08 的候选工程检查通过；正式工作树仍为改动前的源码，整体为 **qa_blocked**。

## 验证对象

| 工件 | 实测 SHA-256 |
| --- | --- |
| [获批规格](spec.md) | 7c1daf6fee1a97760d9d9beb2834e4d405ba8bad533a6bfc4ebea1aaa81671f3 |
| [Development 交接](tasks.md) | 415aa0f756bd4a7946512eec0a0774624d4b604604126894130822f32005e9b5 |
| ARCH-ENERGY-002-r1.patch | 49dde2571d416bed576904855a52b85f7ca8dd855fe0653cdbcec2b5cb141c4e |
| ARCH-ENERGY-002-r1.sha256.tsv | c85d929afd8fdd01b57f4e2cc52ec6d0d952737df13a03ebb20adae252ea0273 |

正式 HEAD 为 9c30258358f169792d4cd0faeae3b80a41b43b81。独立 Python hashlib 核对基线 3,994 项，正式差异为已批准的 spec、四份双语 PLAN／任务索引与另一个工作流的 SMA HttpTable.vue、styles.css。上述两处 SMA 源码位于本补丁范围外。正式树执行 git apply --check --whitespace=error-all 成功，隔离副本实际 git apply 成功。33 个路径逐一核对正式前像、重建后像、Development 候选及 TSV，全部相符，其中 14 个新增，19 个更新。

## 验收记录

| 验收 | 独立实测 |
| --- | --- |
| AC01 通过 | Chrome 真实登录管理员创建、重开、编辑及启停，验证表计／关键词筛选、重置、原配置入口。表头首列 165→243 px，切换再重载后保持，恢复为 165 px。运营角色管理读取和请求越权表计均为 403，统计下拉仅展示可读组。 |
| AC02 通过 | 四个分组与排序、线型、开关保存且可重读。点击遮罩丢弃编辑。1440×900、1024×768 各覆盖中英文和明暗主题，八组均检查长正文独立滚动及首尾位置，标题按钮可达。 |
| AC03 通过 | 校验重复、非法指标、混合量纲或单位、缺省单位，以及历史停用指标。将合成指标单位改为 W 后，统计页提示不可用、管理页保留原引用，随后恢复 kW。 |
| AC04 通过 | 实际图表与有序配置、实虚线一致，汇总注明首条启用指标；瞬时 7.00 kW，区间用量 5.00 kWh，累计读数下降时后端 amount 为空并显示原因。图例开关保留汇总选择。 |
| AC05 通过 | 空曲线配置、曲线列表返回模拟 503 时，真实手动样本分页仍可查询。重试、恢复默认、范围及无数据状态由浏览器与聚焦用例覆盖。 |
| AC06 通过 | ECharts 实例保留零值、断点、同刻点和缩放；延迟送达的旧汇总未覆盖新组。两个真实浏览器会话独立。同键并发创建返回 200／409，同时 PATCH 三组字段均保留。 |
| AC07 通过 | 一次性 MySQL 8.4.6 的真实 Alembic 执行验证错误 UUID、中断标记表、升级前驱 9e0c5d41b7a2、唯一后继 af6d8b2c4e90；新表为空且无跨域外键，旧能耗、实时／过程数据和回执保持。无关后继后继续完成曲线与原有能耗业务读写。回退保护保留配置。 |
| AC08 部分通过 | 锁定依赖的聚焦用例、实际 OpenAPI、双语链接、模块注册和生产构建通过。正式 33 个路径尚处于前像，实际 dev 采用及正式启动入口验证待完成。 |

## 命令与环境

QA 副本位于 /private/tmp/energy002-qa.1wOOtl/candidate。依照项目锁文件复用已安装依赖。QA 独占 MySQL 回环端口 56256，UUID a67fc3fc-e896-11f1-aa18-a6866e93834b；浏览器使用独立新建的合成 schema、账号和新生成的样本。Uvicorn 在 127.0.0.1:56358 提供本次构建和实际 API。

- 后端运行以下命令，41 passed、2 deselected、1 项 SQLite 适配弃用提示，退出 0。包含真实 router 生成的 OpenAPI 与发布合同一致性以及监控错误路由。
  ```sh
  uv run --no-sync pytest -q tests/test_energy_curve_groups.py tests/test_energy_meters.py tests/test_energy_registered_ingest.py tests/test_energy_public_reads.py tests/test_equipment_observation_r10_flow.py tests/test_monitor_frontend_permissions.py tests/test_openapi_router_tags.py -k 'not test_openapi_contains_only_public_core_operation_tags and not test_openapi_excludes_disabled_hr_routes_and_c2_stays_clean'
  ```
  第一项排除对应 Development 正式基线中已有的 Quality - Defects 标签断言失败。另一项依赖冻结 C2 及历史 Git 来源，在本次独立副本未执行。
- uv run --no-sync alembic heads 返回 af6d8b2c4e90。PYTHONPATH=. uv run --no-sync pytest -q tests_mysql/test_energy_{curve_groups,meters,registered_ingest,public_reads}_mysql.py 返回 4 passed（49.84 s），退出 0。
- pnpm exec node --test tests/module-registry/{energy-curve-groups,energy-write-sources,equipment-observation,equipment-observation-columns}.test.mjs 返回 36 passed。pnpm run build --outDir 指定独立 dist，退出 0，10 组、32 路由，保留既有大 chunk 提示。两种角色页权限使用 monitor.energy。
- pnpm run test:modules 返回 123 passed、2 failed，和 Development 正式基线 120 passed、2 failed 的失败名称相同，分别为 admin, supervisor, operator and unknown share route/menu/default decisions 和 actual source preserves Core route identity, shell locales and default-disabled demo。
- 使用项目 Python 对本次副本运行 curve-link-check.py，10 条本地文档链接均存在，发布 OpenAPI JSON 解析通过。独立构建后以 CURVE_FIXTURE_BROWSER 指向 QA 专属端口运行 node browser-check.mjs，退出 0。复用了交接场景脚本，在本次服务重新生成数据、请求及截图；仅 503 和延迟场景使用受控网络响应。独立浏览器结果日志 SHA-256 为 287add084560029bbe9413a54bc88d93e7193ea9e3c1cd34e607e1cd5713b38d。

## 阻塞与交接

第 6 节规定实际 dev 备份、迁移与服务切换须独立授权。交接时只读预检记录 dev 为 9e0c5d41b7a2、新表缺失，正式服务会热加载。正式整合需协调迁移和服务切换。Human Owner 决定采用后，由实施方执行获批步骤并交回正式源码，Verification 复核 33 个后像、正式启动入口及目标环境结果后更新本清单。当前没有 Human Owner 最终验收。QA 全程仅使用合成库，未执行真实 dev 迁移或部署。

## 临时资源收尾

QA Chrome 会话、Uvicorn 及一次性 MySQL 容器 energy002-qa-1wootl 已关闭，独立 QA 副本、构建、合成数据、日志及截图随 QA 临时目录回收。Development 保留 /private/tmp/aiis-energy002-r1.brHaWJ 中的候选、补丁及证据，待采用整合并复核或按交接约定转存补丁后回收。

## AC08 正式采用补核 · 2026-11-25

原隔离 QA 清单 SHA-256 为 `180ea4e736f82fee44e7a915a4631f8b39c1eb16f88ab74451ddb74b7f870347`。独立复核的 spec、补记后 tasks SHA-256 分别为 `7c1daf6fee1a97760d9d9beb2834e4d405ba8bad533a6bfc4ebea1aaa81671f3`、`5c0d57986cfa897bdd5b3b18707cca16aeea6aa98daeab517435b2863e865858`。上文保留第一次验证的历史结论。

- 在正式工作树核对 HEAD `9c30258358f169792d4cd0faeae3b80a41b43b81`。逐行读取交接 TSV，以 Python hashlib 对正式文件计算 SHA-256，33/33 符合候选后像。补丁及 TSV 摘要与首次 QA 一致。`git diff --check`、`git apply --reverse --check --whitespace=error-all` 和正式 backend 的 `uv run --no-sync alembic heads` 均通过，唯一 head 为 `af6d8b2c4e90`。
- 通过 stat 和 SHA-256 核对真实开发库备份，父目录权限 0700，文件权限 0600、358442 字节、摘要 `19b7779ffce4a29f576b3d28e25e732e5a51e21041518f3ee36ef8ab2887edca`。迁移记录显示前驱 `9e0c5d41b7a2`，原 69 张表定义一致。未执行恢复演练。
- lsof 确认 8000 和 5190 的监听进程工作目录分别为正式 backend 和 frontend-js。首次沙箱 TCP 被拒；获准在沙箱外，从正式 backend 用 `uv run --no-sync python -B -` 运行经审阅的本机验证脚本数据库和 GET 段，增加曲线表 COUNT 查询，退出 0。通过 UUID 和库名核对 3307 目标身份，实查唯一 revision 为 `af6d8b2c4e90`，曲线组 0 行。两个端口管理与统计读取均为管理员 200、匿名 401，脚本中的相邻读接口通过。8000 健康检查及 Swagger 为 200，四个曲线操作均声明 Energy 与 HTTPBearer。未执行业务写入或重启。
- 复核正式构建及测试日志，沿用已记录的全量测试基线例外。协调者浏览器证据 SHA-256 为 `3e3f17971096b9422f6e75f16241fd69dee683d10ebc74b9bade99e0ac2d9a21`，覆盖 PC 浅色及平板横屏深色、四个页签、管理与统计 GET 和默认手动模式，两种场景均无写请求。浏览器结果来自交接证据，本轮独立重跑了数据库和 HTTP 检查。

AC08 原 blocker 已关闭，整体 verdict 为 **qa_passed**。正式源码已整合，本机开发环境可用，等待 Human Owner 最终验收。

本轮 Verification 无临时资源。协调者保留的 `/private/tmp/aiis-energy002-r1.brHaWJ` 可在必要证据持久化且无后续依赖后回收。受限备份 `/private/tmp/aiis-energy002-dev-backup.Uhk8JT/` 由 Human Owner 确认无恢复需要后回收。

## Human Owner 最终验收

2026-11-25（Asia/Shanghai），Human Owner 明确表示「验收 ARCH-ENERGY-002 r1。」，随后确认「先验收 002，后面001别动，先不做」。据此记录 ARCH-ENERGY-002 r1 为 **owner_accepted**。验收范围为上文 AC01–AC08 及已核实的本机开发环境，独立 QA 结论保留为 **qa_passed**。

协调者已核实原候选目录 `/private/tmp/aiis-energy002-r1.brHaWJ` 已回收。受限备份 `/private/tmp/aiis-energy002-dev-backup.Uhk8JT/` 继续保留作恢复资料，待 Human Owner 确认无恢复需要后回收。本次验收记录无新增临时资源。
