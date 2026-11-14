Task ID: ARCH-ACQ-005
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Handoff: AC01–AC04 独立验证通过，交 Human Owner 最终验收。
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 独立验收记录

## 依据与环境

2026-11-13（Asia/Shanghai），fresh-context Verification 独立读取项目契约、作用域 README/PLAN、获批 [规格](spec.md)、[Development 交接](tasks.md) 及正式工作树的实现与测试差异。核对 `main` HEAD `fd999224a8756feda314a33148304b4bf3461876` 及以下 SHA-256。用 `shasum -a 256 -c manifest-final.txt` 核对了正式树 25 个文件，均一致。并行任务的工作树差异留在各自范围。

| 对象 | SHA-256 |
| --- | --- |
| 批准后规格 | `526aaf69cacd2d02d42a6f831b084570a51dcb9b60c7fbd9c85c93b106513dd2` |
| Development 交接 | `b82217444943e17a95a77c22ddf917d5b73d0867e6fbe59f6d418442936d726a` |
| 25 项交付清单 | `c2b057e834bc1db5144040a61824f170450d6904a60f7d07200a9391f14d6349` |
| 原 `openapi-acquisition-dev-r3.json` | `0dc2e762a7337bbdd969086ef161d949887f9364b10892c8ce48ae77184ffda7` |
| 原 `openapi-acquisition-sources-r3.json` | `46f8ff1ff7b4a75ac79ead3a7e5d824fbe2363df92c3a1767b51bb3c0e7b76d3` |

macOS arm64，项目锁定环境 Python 3.13.3、Node 22.19.0、已安装 Playwright 和 Chrome 157.0.8103.78。用户启动的 API `127.0.0.1:8000` 与 Web `127.0.0.1:5190` 进程工作目录分别为正式 `backend` 和 `frontend-js`，验前验后监听 PID 一致。默认沙箱回环访问失败，随后经批准对指定本机端口验证。浏览器使用任务私有上下文和已有管理员正常登录，普通用户走真实登录 API。

每次写入前都在获准的 `127.0.0.1:3307/industrial_level_2_system` 核对 MySQL 8.4.6、实际服务 UUID 与私有目标配置一致、会话偏移 28800 秒、唯一 Alembic revision `7b9d1f3a5c7e`。核对两条迁移来源的原身份及第三条既有登记，三张表的非测试记录全部纳入对账。

## 验收结果

| 验收项 | 结果与证据 |
| --- | --- |
| AC01 管理操作 | **通过。** Chrome 中文确认框包含目标 PLC 和历史保留期，点击取消的 PATCH 数为 0。英文确认框显示相同语义，确认实际发送三个预期值及 `confirmDelete:true`，HTTP 200 返回 `deleted` 和完整删除前快照，来源列表重新加载且目标行消失。真实 HTTP 匿名 401、普通用户 403、缺确认 422、实际编辑后持旧版本删除 409，旧请求未移除新登记。再次删除 404。既有新建和编辑走真实 API，前端定向测试核对新建、编辑、接管、复制参数及 409 自动刷新。 |
| AC02 并发与重登记 | **通过。** 两个事务顺序各使用不同 MySQL 会话。测试只在先行事务完成事实写入或登记删除语句后、真实提交前用屏障暂停，另一操作经现有 HTTP 服务发起。样本先提交时删除等待，样本得 `committed` 回执，随后删除 200，历史 2 行、最新值 1 行仍在。删除先提交时上报等待，随后得 403 `plc_facts_v2.scope_rejected`，历史和最新值的全字段摘要与竞态前一致。旧身份新样本及已提交样本原字节重试均 403。事实可核实的旧代次重新登记 409 `generation_reused`，新代次重新登记和上报 200，两代样本均可查。物理删除会清除登记行内的退役代次。旧代次的事实和最新值证据均消失时，可能无法识别曾用代次。 |
| AC03 查询与选项 | **通过。** 首个样本由真实 POST 写入。删除登记前后同一历史详情完整相等，保留原来源标签。真实历史 API 按 PLC、DB、时间查询，`pageSize=1` 分两页得到同一 PLC 的两份样本；未知 DB 返回空页，缺失详情 404，非法及重复 `view` 422。Chrome 删除后在历史页选择同一 PLC/DB60002，切换为每页 20 条，接口总数 2，打开样本详情 ID `21` 并看到原点位。定向单元测试核对从未登记 PLC 的列表、详情和选项。查询探针核对历史选项、列表及详情使用 `expires_at > now` 且没有登记表关联，空详情返回 404。默认 options 和两个实时 GET 的拒绝行为按规格通过。实时页删除前显示该 PLC，删除后完整重载触发默认 options 请求，下拉选项消失。页内「刷新」按钮沿用只刷新最新值的行为，完整重新加载页面才重取选项。 |
| AC04 一致性与清理 | **通过。** 运行 OpenAPI 的两组路径和快照所列组件逐项相等，分别 6 个事实/读取路径和 1 个管理路径。两份旧 r3 快照验前验后摘要一致。中英 locale 90 个叶键对称，浏览器实际切换文案。指南、后端及合同双语 README 的删除、历史保留、实时选项、代次限制及错误提示与接口相符。业务删除仅移除目标登记，三轮结束均按独占键清理测试事实；既有数据和三个相关表的结构摘要一致。 |

## 命令与清理

- 在 `backend` 使用 `PYTHONDONTWRITEBYTECODE=1 uv run --no-cache --offline --frozen --no-sync pytest -q -p no:cacheprovider`，按测试节点分别运行管理 OpenAPI、确认与旧版本、默认 options SQL、未登记历史详情、正式路由、历史筛选、未登记历史 SQL、过期边界共 8 项，两次均退出 0。另以相同 uv 环境运行历史 SQL 编译和详情 404 的无库探针，退出 0。旧合成 schema 的全局清理测试未运行。
- `node --test --test-name-pattern='delete|options|history' tests/module-registry/acquisition-data.test.mjs` 及 `node --test --test-name-pattern='deleting a source|source form saves' frontend-js/tests/module-registry/acquisition-data.test.mjs` 各通过 2 项，退出 0。复核 Development 的定向测试与正式入口构建证据。本轮 `git diff --check` 退出 0。
- 在 `backend` 使用相同 uv 环境运行任务私有 `verify.py` 两次、`follow.py` 一次，实际使用 `web.cjs` 启动独立 Chrome。第一次组合运行通过真实管理、样本先提交和 API 读回，浏览器脚本点按 Element Plus 内部输入超时，退出 1。改用外层控件后第二次通过真实删除、历史筛选/分页和详情，脚本将实时页内「刷新」当作重新获取选项而等待超时，退出 1。末次仅补旧/新代次、删除先提交和实时页完整重载，退出 0。三轮各删除测试历史 2 行和最新值 1 行，来源已由业务删除，清理后该 PLC 在三表的残留均为 0。MySQL 自增编号随合成历史插入推进。
- 独占键共用后缀 `e586f296f0454edba1a2e9779302c5a2`。PLC `acq005-qa-plc-<后缀>`、实例 `acq005-qa-inst-<后缀>`、代次 `acq005-qa-g1-<后缀>` 与 `acq005-qa-g2-<后缀>`、样本 `acq005-qa-s1-<后缀>` 至 `acq005-qa-s4-<后缀>`、DB 60002、点 `acq005-qa-point-<后缀>`。三个清理 DELETE 均限定 PLC、实例、代次；历史再限定 DB 和样本键，最新值再限定 DB、样本及点位键。历史行 ID 为 19–24。
- 前后非测试全字段摘要如下。三个相关表的 `SHOW CREATE TABLE` 去除自增游标后的合并 SHA-256 均为 `656aa6a31a45574d6826652566410844c8e248109dbe32746ac001df5d32db00`。

| 表 | 非测试行数 | 前后相同 SHA-256 |
| --- | ---: | --- |
| `plc_source_registry` | 3 | `1a9a6b3d8a3b2895577f0b418ae1a40e0a80fd1431300ec5e4e4c276e6431ad0` |
| `plc_facts_history` | 4 | `a4b7b1831f56d94ea702499611e54c38c6fd65c2a9df478f1e21259481e77564` |
| `plc_facts_latest` | 3 | `ca975202ec48561a465d1f3ae342f489a4b9e5b8cbeb532dd153bd73fc0a0e96` |

## 结论与交接

`qa_passed`。真实 dev 验证限定在合成来源，未执行迁移、DDL、账号改动、用户服务启停、部署及 DAA 或设备操作。独立 Chrome 会话均已关闭。QA 自有临时目录 `/private/tmp/arch-acq005-qa.CD4bS4zC` 包含 `verify.py`、`follow.py`、`web.cjs`，当前无运行依赖。Development 私有目录 `/private/tmp/arch-acq005-dev.xJGP5L` 仍在。上述证据已写入本文件，协调者可按各自归属和后续依赖收尾。

Human Owner 最终验收待记录。

### 资源收尾

协调者确认两个临时目录无进程占用，先解除候选中的依赖符号链接，再回收目录。Verification 只读核实 `/private/tmp/arch-acq005-dev.xJGP5L` 和 `/private/tmp/arch-acq005-qa.CD4bS4zC` 均已移除，正式树的 `backend/.venv/bin/python` 与 `frontend-js/node_modules/vite/package.json` 均存在。
