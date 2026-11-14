Task ID: ARCH-ACQ-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r1 源码及 dev 定向自检完成，交 fresh-context Verification；用户手工验收待执行。
Workflow Mode: STD
Execution Mode: agent_team_same_session

# Development 实施与交接

## 实施范围

Human Owner 批准 ARCH-ACQ-005 r1 并指定 dev 库验证，要求不要过度设计和过度测试。批准后 spec SHA-256 为 `526aaf69cacd2d02d42a6f831b084570a51dcb9b60c7fbd9c85c93b106513dd2`。交付工作树为 `main` HEAD `fd999224a8756feda314a33148304b4bf3461876` 加现有未提交差异。

- 来源管理沿用 PATCH：确认、预期身份和版本均正确时，在登记行事务锁内删除该行，保留删除前快照；拒绝无确认或旧版本。原来源上报在删除后被拒绝，已入库事实不删除。
- 历史列表和详情独立于当前登记，`options?view=history` 显示未过期历史中的 PLC/DB，默认 options 和实时保持原规则。前端增加带确认的删除操作、历史筛选模式及对称中英文文案；指南、双语合同和两份新 OpenAPI 快照同步。
- 未新增表、字段、数据库迁移或 DAA 源码/配置/队列。物理删除会清除该行退役代次，已无事实与最新值证据的旧代次无法保证识别；重新登记须使用从未用过的新代次。

## 自检与 dev 证据

- 私有候选 `/private/tmp/arch-acq005-dev.xJGP5L` 不含真实 `.env`、profile 或业务数据库，候选 `.env` 来自仓库 `.env.example`，`.venv` 和 `node_modules` 为指向既有依赖的符号链接。基线 SHA 核对无冲突后，25 个获批文件整合正式树并逐项匹配；下列清单 SHA-256 为 `c2b057e834bc1db5144040a61824f170450d6904a60f7d07200a9391f14d6349`。
- 候选后端 `uv run --no-cache --offline --frozen --no-sync pytest -q -p no:cacheprovider` 对来源管理及历史/分页/合同的明确测试节点退出 0：43 passed。新路由 OpenAPI 响应说明调整后，两个合同测试重跑退出 0：2 passed。没有运行旧合成 schema 的清理测试。
- 候选前端 `node --test tests/module-registry/acquisition-data.test.mjs`：退出 0，13 passed；新增 409 删除冲突刷新检查后，在正式树仅重跑对应测试，退出 0，1 passed。`pnpm_config_verify_deps_before_run=false pnpm build --outDir <自有临时目录>` 在正式入口退出 0；有既有大 chunk 提示。候选构建第一次因 pnpm 尝试验证并安装依赖而退出 1，随后关闭自动依赖检查重新构建成功；已有 `node_modules` 未被修改。
- Python 代码 compile 检查、四份 JSON 解析、90 个中英文 locale 叶键对称、62 个本地文档链接目标、`git diff --check` 均通过。未执行无关全仓测试或压测。
- 用户批准的 `127.0.0.1:3307/industrial_level_2_system`：只读核对 MySQL 8.4、上海时钟、UUID/schema、revision `7b9d1f3a5c7e` 和原两条迁移来源；另有一条既存登记，合计 3 条，全部保护。通过候选 API/service/CRUD 的进程内 ASGI 请求，使用独占测试 PLC 检查确认/409、上报与删除的两种行锁先后、删除后原身份与原样本重试 403、历史列表/详情和两个 options 模式、旧代次拒绝及新代次重新登记和上报。管理认证依赖在此进程内替身；匿名及非管理员行为另由无库路由测试覆盖。
- 两次成功的 dev 测试均按精确 PLC/instance/sample/point/DB 键清理：第一轮删除测试历史 1、最新值 1；补验新代次轮删除测试历史 2、最新值 1。两轮前后登记表 3 行、历史表 4 行、最新值表 3 行的非测试行全字段 SHA 均一致，分别为 `1a9a6b3d8a3b2895577f0b418ae1a40e0a80fd1431300ec5e4e4c276e6431ad0`、`a4b7b1831f56d94ea702499611e54c38c6fd65c2a9df478f1e21259481e77564`、`ca975202ec48561a465d1f3ae342f489a4b9e5b8cbeb532dd153bd73fc0a0e96`。首次测试脚本因从可编辑安装导入正式旧路由而三次得到 422，三次均只创建测试登记、失败时精确清理且同一摘要一致；修正候选路径并断言 API、Service、CRUD 和 schema 来源后成功。另一次候选路径断言因路径未规范化失败，发生在数据库连接前。未更改其他数据。
- 用户自行启动的 8000/5190 保持运行；热重载后后端 health、历史 options 与 Web 首页均返回 200，运行 OpenAPI 含删除动作及 `view`，Web 服务返回的新来源页与历史页源码均含对应候选。未在用户浏览器中操作；真正浏览器的 Web 交互留待独立 Verification 和 Human Owner 手测。

所有测试 PLC 均使用 `acq005-dev-inst-<suffix>` 的实例、`acq005-dev-gen1/2-<suffix>` 的代次及 `acq005-dev-sample1/2/3-<suffix>` 的样本，DB 为 60001，点为 `acq005-dev-point-<suffix>`。各轮使用的独占 PLC 如下，执行后均确认三表中此 PLC 行数为 0：
- `acq005-dev-plc-34bd63f8e99349d1a1c2fa0b168a93c6`
- `acq005-dev-plc-8ed2493dd1184947aef87417babfbdad`
- `acq005-dev-plc-b32d942be5144c178713dc243811617f`
- `acq005-dev-plc-bbed3a0136034f68babc743ea3ab2413`
- `acq005-dev-plc-cad87e8fa00c48a5957f758fb418008b`

## 精确候选清单

```text
4287368d837dbaad6649dc97de99faa39938f78db2759686430187df805dc000  backend/app/plc_facts/api/source_registry.py
318e00e00da497c8e31a738d25dc45c771a5118c23f1c046576ab7953db0ba6d  backend/app/plc_facts/schemas/source_registry.py
a9bca7b583a81777e8469f458f64baae0b13234e315b189bf3da906d4978ec6e  backend/app/plc_facts/crud/async_source_registry.py
40515de4b5b83e65802287e217558aa467569e100305e431c6262c591cb6fde4  backend/app/plc_facts/services/async_source_registry.py
d7952ed61f8fe970a6b718ae4cd980a537ecf662197a272c70b48b78a547f2b8  backend/app/plc_facts/api/v2.py
e51c03f347028cb3b7e0eaf943b974a1a4e581bace285bd41dcdb64b52c47668  backend/app/plc_facts/crud/async_v2.py
ea0c6aa1489fb627ed106fac6960325a26bb883e100fca14fcd5703b25f307da  backend/app/plc_facts/services/async_v2.py
49e26aef345d17d962b6851afebcce389666f037b44f34950395f372458bb1ec  frontend-js/src/app/acquisition-data/api/index.js
50354f27ee8d5a7617c8f809c1b8716b542e502c564534115ced099a1d3c8e15  frontend-js/src/app/acquisition-data/composables/useAcquisitionScope.js
59b73c580ee17ec1a0e0f66e32d29fa6f0e9acfda33d6b084283bec86b6f35b7  frontend-js/src/app/acquisition-data/views/sources/index.vue
76817ce2f604a9a2d3a15c788b8ecc34fe2f7227934024505a50e8b982ad3cfb  frontend-js/src/app/acquisition-data/views/history/index.vue
614ca23a3966984348b36afedad8085bdef5530b6604ff1dd19d177acff2c659  frontend-js/src/app/acquisition-data/locales/en-US.json
e4695ec8acc2d14d7f20c3fc5457e6afb5866264163b7857c0c1e8f2c827de8c  frontend-js/src/app/acquisition-data/locales/zh-CN.json
512770799444bec65b1e97b07c14139ba954ecd423b42e010444dde17546b98b  docs/acquisition-data-guide.zh-CN.md
78fc0b6b1e1dd809db7549812bfdcdd4f36f314c8397dd493a2e1f856e392e10  backend/app/plc_facts/README.md
7f0680d7e8da6665388e742a64439ba42a9ca8da1cfef291755d5d07092e4a23  backend/app/plc_facts/README.zh-CN.md
1ebd96c44da17be2c172d07f0df0e4d89c259a1343c5658e77266a7c3792f831  contracts/published/http-api/plc-facts-v2/README.md
cbc920b4d53f839c877a641d8cb264499489a9d019dafbec8b003c8d835942e9  contracts/published/http-api/plc-facts-v2/README.zh-CN.md
7c87f409caf704f02e2d018e2c1c9a37e9e8803febbcd98b6bd61db13495f13f  contracts/published/http-api/plc-facts-v2/openapi-acquisition-dev-r4.json
be7e8243f9217ce1a5edf9b8741d2a3dde826e8a404f6fbfa733a8494a1c0e51  contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json
d08e7a4bc413759eb50f463cd6da684fc2e6bfdc334e7cb0872b0a0bb60373ba  backend/tests/test_acquisition_source_registry.py
638ddc78b3218ca303a2acb5b546edbba4304433b76d93fc0664723c1c7360f8  backend/tests/test_acquisition_data_browse.py
d0b2cb90466a6bf6de15cadf9e6d7cf6060e6f4c01587cce80d7e1ea28375e8d  backend/tests/test_plc_facts_v2.py
de349be19acb4de260caa87c5ef90b05537b0088af3fc8fed25a3e70f2afe9ce  frontend-js/tests/module-registry/acquisition-data.test.mjs
d3f9f54bad8ae31e420ea9e3151d48b7feddd204d7a6d7f5c9a03ff70d07306d  CODE_INDEX.md
```

## 交接与资源

Development self-check 不等于独立 QA 或 Human Owner 验收。请 Verification 使用 fresh context、不同测试身份和用户批准的同一 dev 目标核对 AC01–04；用户保留手动测试权。候选源码、合成测试脚本与前端构建暂留在上述自有临时目录供独立验证；验证完成且无依赖后由协调者按归属回收。未停止或启动用户服务，未触碰真实 PLC、DAA、本次以外的配置或历史；未提交、合并或发布 Git 内容。
