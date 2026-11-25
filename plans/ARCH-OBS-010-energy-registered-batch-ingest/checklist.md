Task ID: ARCH-OBS-010
Revision: r1
Status: owner_accepted
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: Human Owner 已最终验收 ARCH-OBS-010 r1
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 独立 Verification · 2026-11-24（Asia/Shanghai）

验证对象为正式交付工作树 HEAD `7f654acd951171767bc253ea5bebdcda6435b608` 叠加已交接候选。[批准规格](spec.md) 规定的 AC01–AC08 通过。fresh context 在 Development 交接后独立执行，项目内仅写本 checklist。候选 45 项逐文件 SHA-256 与交付树一致，归档 SHA-256 为 `7fb8cee20038c7d78c4ae259c05132d2709946f463ebe02a1abd5b130f8cc020`，[Development 记录](tasks.md) SHA-256 为 `5020c49c998fb7a9b8694489fa4f87280f05bd9907195eecb70213575ffc823b`。

| 验收项 | 结果及独立证据 |
| --- | --- |
| AC01 | 通过。管理员 Bearer 可查询、新增、编辑、停用、恢复、删除。真实 JWT 路径证明无凭据及无效凭据为 401，普通用户管理为 403。验证大小写、点标识、编辑标识只读、删除后无法复用及历史样本保留。实际 Chrome 中八组配置均完成五次有效变更，键盘查询／操作、空态、无匹配、重试和遮罩取消工作正常。普通列宽 185→219 px，重载后保留，重置恢复 185 px。 |
| AC02 | 通过。无 Authorization 的两表 POST 返回一份回执、两条排序记录，均引用同一回执。通过原读 API 核对 120 kWh、累计 9820 和瞬时 0，校验时区、采样组和登录表计范围。附带无效 Bearer 的合成新包也写入成功。 |
| AC03 | 通过。无效来源、指标、质量、数值、区间、重复 JSON 键、超限请求和错误介质按约定拒绝；非法第二项使两表均无残留。额外 HTTP 场景在一包加入 meter2/gas 增量 7，保存 meter1 区间起点 11:00 与 gas 区间起点 11:30；good 组统计为 120，bad 组与默认 unknown 组统计 amount、latest 均为空。 |
| AC04 | 通过。等价时刻、数值及键序得到原回执与记录 ID；拆包／改值冲突。实际 InnoDB 并发相同包得到相同成功响应，竞争不同正文得到 200／409。第二表插入触发故障后全表快照一致。模拟提交已完成而确认丢失返回 503 commit_unknown，原包重试两次返回同一完整回执。 |
| AC05 | 通过。独立 MySQL 中停用／删除与提交并发，写入成功时对应两行，停用后重试 403，恢复后重新允许写入。历史导入内部身份冲突返回 409；合法 v2 与登记包在相同外部身份／事件键下并发分别成功，回执合同版本独立。 |
| AC06 | 通过。合成前驱结构上用原 HTTP 写入旧能耗、设备和过程记录，错误迁移目标被拒绝，正确升级后逐行快照一致。旧 v2 回执重放、发现接口、用户样本／统计、越权表计拒绝、实时和历史写路由重放通过。 |
| AC07 | 通过。实际 Alembic 从前驱 a1c307f8d2e4 升至 b52e9c416a07 再运行合成无关后继，旧 profile revision 保持 e9f3b5d7c021。能耗读、登记、旧 v2 和新 POST 均可用。移走设备来源表后仍可写入，移走能耗配置表后管理读取返回 503 not_ready。拒绝降级且样本、登记和回执保留。 |
| AC08 | 通过，保留两项已知前端基线失败。实际路由与发布 OpenAPI 的五项操作相符，管理四项使用 HTTPBearer，机器 POST 可省略令牌。中英文合同链接与请求／回执向量通过检查。源码及模型表明新事务使用能耗登记、指标、样本和回执，无跨域外键、JOIN 或任务号依赖。 |

## 命令、环境与限制

- Darwin arm64、uv 0.7.8、Node v22.19.0、pnpm 11.11.0。后端于 backend 执行 [Development 记录](tasks.md) 所列 15 个测试文件的 `uv run --no-sync pytest -q -p no:cacheprovider`，退出 0，163 passed、1 skipped、1 warning。`uv run --no-sync alembic heads` 退出 0，单一 head 为 b52e9c416a07。
- 复制并核阅交接夹具，为本次验证创建随机凭据、回环端口、独立容器 aiis-obs010-qa-GgTddJ，镜像 mysql:8.4.6。执行 `sh start-mysql.sh`、`sh run-mysql.sh`，均退出 0。底层 `uv run --no-sync pytest -x -q -p no:cacheprovider tests_mysql/test_energy_registered_ingest_mysql.py` 的隔离场景 1 passed，10.34 秒。另用 `uv run --no-sync python -` 调用 SQLite 内存 HTTP 夹具验证 AC03 三组同包场景，退出 0。
- 于 frontend-js 执行 `pnpm check:modules` 与 `pnpm build --outDir /private/tmp/aiis-obs010-qa.GgTddJ/frontend-dist --emptyOutDir`，均退出 0。`pnpm test:modules` 退出 1，119 passed、2 failed；page-access.test.mjs 与 registry.test.mjs 的系统／维保排序期望与交接前既有基线相同，新增登记测试通过。
- `node /private/tmp/aiis-obs010-qa.GgTddJ/browser.cjs` 退出 0。1440×900 与 1024×768 各跑 zh-CN／en-US、light／dark，八次均无意外请求。浏览器使用本轮从交付源码构建的资源及合成 API；真实鉴权和持久化由独立 HTTP／MySQL 测试覆盖。
- 从 backend 执行 `PYTHONPATH="$PWD" uv run --no-sync python /private/tmp/aiis-obs010-qa.GgTddJ/check-contract.py` 退出 0。`git diff --check` 退出 0。MySQL 验证从合成前驱结构起步；实际 dev／生产采用和 Human Owner 验收另行记录。

## 临时资源收尾

专属 MySQL 容器经 stop --rm 生命周期回收，已关闭 Chrome 并清理 QA 的构建、截图、日志、缓存、测试临时目录和凭据。Development 交接资源 /private/tmp/aiis-obs010-dev.Witcd1/ 仍归协调者，独立验证落盘后可按其所有权回收。

## Human Owner 最终验收

2026-11-24（Asia/Shanghai），Human Owner 明确表示：“验收 ARCH-OBS-010 r1”。独立 Verification 结论为 **qa_passed**，据此条 Owner 确认记录最终状态为 **owner_accepted**。

协调者已确认 QA 临时目录已回收，并已回收 `/private/tmp/aiis-obs010-dev.Witcd1/` 和 `/private/tmp/aiis-obs010-coordinator.swH5gY/`。本次验收记录无新增临时资源。
