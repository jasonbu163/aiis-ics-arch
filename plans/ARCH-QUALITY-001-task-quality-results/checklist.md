Task ID: ARCH-QUALITY-001
Revision: r2
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner 已完成 r2 最终验收
Updated: 2026-11-24 Asia/Shanghai

# 第一次独立 Verification

**qa_failed。** 正式构建在质量列表和详情都会错误显示合法业务标识。QA 从 fresh context 消费 r2 规格、Development handoff、正式源码及独立数据库和浏览器验证结果，只写本清单。

## F1 · 列表和详情误改任务号及目标标识（AC07）

在合成接口返回同一条质量记录后，Chrome 从正式 Vite 构建打开质量列表并进入详情，两个界面的 DOM 文本一致地偏离接口原值。

| 字段 | 接口原值与期望显示 | 列表、详情实际显示 |
| --- | --- | --- |
| taskNo | `2026-11-23TASK-QUALITY-ALPHA` | `2026-11-23 ASK-QUAL` |
| targetKey | `2026-11-23TARGET-QUALITY-ALPHA` | `2026-11-23 ARGET-QU` |

`frontend-js/src/app/quality/views/results/QualityList.vue` 第 42、78 行把四个固定字段的值传入第 199 行的 `formatFixed(value)`。该函数对日期前缀匹配的字符串仅取前 19 位并把 T 替为空格。两项输入均满足规格第 2.1 节。复测须以字段身份区分时间与标识，并在两个入口同时验证这两个完整值及两个时间字段到秒的展示。证据只涉及显示层。

## 逐项核查

| AC | 结果与证据 |
| --- | --- |
| 01 | 通过本次新修订及质量独立性检查。迁移建立两表、初始单行空配置和唯一键，两表没有外键。CRUD 查询仅使用质量模型，SQLite、MySQL 中独立上报同号合并。 |
| 02 | 通过。管理员配置、不可变属性与完整集合、过期 revision、停用与重新启用保留值见正式质量专项。浏览器另验配置冲突后保留草稿。 |
| 03 | 通过所测边界。正式 HTTP 测试覆盖零、false、空字符串、null、缺失、精确键、数值精度、字符串长度和不合规链接，混合非法提交后核对原值。 |
| 04 | 通过。合成多请求创建及部分更新、目标冲突、原样重试与权威重读；SQLite 和 MySQL 实际并发写不同字段后均保留。 |
| 05 | 后端通过。精确筛选、分页、带偏移时间区间、404、启用字段投影及未赋值语义由正式专项核对。隔离文件数据库验证持久化；正式服务没有为测试重启。 |
| 06 | 通过所测角色及未登录、未授权请求。API 内部执行模块、角色和字段权限检查。集成路径使用可信网络合同；现场网络控制属于部署环境。 |
| 07 | **失败 F1**。其他已执行项目包括英文浅色桌面与中文深色 430px、收起侧栏后字段筛选区左右对齐、空态与错误态、详情、部分编辑、键盘打开链接、链接文字与 URL、拖拽列宽与刷新恢复和重置。 |
| 08 | 通过已验证路径。旧模块身份、facade 和控制页两个历史返回目标经源码核对。浏览器实际切换历史入口与返回；后端合成旧记录 CRUD、SPC API、旧数据与新静态路由专项通过。 |
| 09 | 通过本次修订范围。SQLite 和已核对空目标的 MySQL 8.4.6 都从合成单一前驱重复升级，五处严格门卫经源码与回归核对。完整历史迁移链、旧时间历史转换和正式库迁移未执行。 |
| 10 | 已执行。实际 OpenAPI 的 8 路径、9 操作、组件和发布请求通过专项校验；质量两份语言文件 274 个叶键对称，质量合同中英两份各 6 个相对链接均存在。模块注册检查、构建通过；全量模块前端测试有三项既有失败，见下。 |
| 11 | 通过。r2 七个文件只有八行对应替换，旧迁移和保护断言保留；七文件重跑无失败或 setup errors。正式文件 SHA 全部匹配。QA 容器可由协调者回收。 |

## 可复现环境与命令

正式根目录为 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`。已复算规格 SHA-256 `452664c62b4ebf805a5ecfe1fa71c2d7fe6057c843ece8c250a94119eae52afd`、48 路径清单 SHA-256 `8e8885b1df840c97fe6dc00fc41489c0af94bac9f186dc9e0ff9c6820752c0d4` 并逐路径比较 after SHA，0 处差异。清单范围与第 6、6.1 节核对；正式树另有并行工作。`git diff --check` 退出 0。QA 执行目录 Q 为 `/private/tmp/arch-quality-qa-r2-13412`。

- `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python $Q/qa.py -q -rs -p no:cacheprovider` 加 r2 七个文件，66 passed、1 skipped、退出 0。跳过固定在 f85bea8 的历史 BE003/60 用例。
- 同启动器加七文件、两个质量专项、五个原门卫/观察专项及 business_integration_storage，173 passed、8 skipped、退出 0。其余七个跳过为已退役的 coil production/performance 既有用例。启动器禁用本地 dotenv，非 MySQL 专项的默认数据库指向合成不可达端口 1。
- `docker exec arch-quality-001-r2-qa-13412 cat /var/lib/mysql/auto.cnf` 独立读取 UUID。经明确匹配该 UUID、空 schema、专用账号、版本与时区的启动器 `PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python $Q/qa.py --quality-mysql` 实际执行正式 MySQL 测试：1 passed，退出 0。MySQL 8.4.6，127.0.0.1:13412，arch_quality_fixture_13412，UUID 97f85ec6-e753-11f1-ae5a-2ed4ab29b7a5，会话偏移 +28800 秒。前驱哨兵保留、重复升级、规范化及并发部分写入通过。
- 在正式 frontend-js 执行 `pnpm check:modules`，9 模块、30 路由、9 分组，退出 0。`pnpm test:modules` 为 110 passed、3 failed，退出 1。与整合前基线日志逐项核对，同名三项均因 monitor.energy 的原菜单或 route 顺序断言失败（page-access 一项、registry 两项）。质量专项通过。
- 同一目录用合成 VITE 配置，API 前缀 /api/v1，关闭前端 mock，主管及操作员页面许可 quality.list，`pnpm build --outDir $Q/dist --emptyOutDir` 退出 0。QA 用 Playwright 和已安装的 Chrome 在独立临时 loopback 服务器加载此产物，所有业务接口和身份均为合成夹具。
- `node $Q/browser.cjs` 退出 0，四张合成截图和独立构建在 Q。额外的 `node $Q/identity.cjs` 断言两个标识的列表及详情原值，退出 1，实际值见 F1。专用断言脚本 SHA-256 为 `f12a0f5caef762423a361d555d1207d4f330d2f7e1bfdcea527f97940e416616`。

## 移交与资源

Development 收到 F1 后修复并记录新的正式文件摘要、自检和 handoff，再进行 fresh-context Verification。协调者持有一次性 MySQL 容器和临时凭据的回收责任，QA 已通知其可清理本轮 QA 容器。Q 内无运行中的 QA 浏览器或临时服务；保留到返修复验取得可持久化证据后由协调者回收。核对正式 8000 无监听，本轮没有启动该服务、操作实际数据库或执行部署。最终验收由 Human Owner 决定。

## 第二次独立 Verification · r2

**qa_passed。** fresh-context QA2 在正式工作树复核再次交接。首轮 F1 已关闭，AC07 通过。AC01–06、08–11 沿用上列独立 QA1 的证据及其限制。本轮按清单复算全部 48 个文件 SHA-256 并与首次交接逐项比对，46 个文件相同，差异仅为 QualityList.vue 和 quality-results.test.mjs。后端、迁移、合同、后端测试及语言文件摘要一致。规格 SHA-256 与首轮一致，返修 manifest SHA-256 为 `79f6179dd819562df7372ed232cb63d42b46166c53fa5367935783893e8e31c6`。

在正式 frontend-js 使用 tasks.md 的合成 VITE 参数独立执行 `pnpm build --outDir $Q/dist --emptyOutDir`，成功。Q 为 `/private/tmp/arch-quality-qa2.mhLwwj`。以本机 headless Chrome 和 Playwright 拦截接口、启用真实路由，从 DOM 按顺序采集每个列表单元格和详情字段。QA2 为四个字段分别指定期望值。旧构建执行 `node $Q/verify.cjs /private/tmp/arch-quality-qa-r2-13412/dist` 退出 1，两个界面均复现上述 F1。返修正式构建执行 `node $Q/verify.cjs` 退出 0。

| 字段 | QA2 列表实际值 | QA2 详情实际值 |
| --- | --- | --- |
| taskNo | 2026-11-23TASK-QUALITY-ALPHA | 2026-11-23TASK-QUALITY-ALPHA |
| targetKey | 2026-11-23TARGET-QUALITY-ALPHA | 2026-11-23TARGET-QUALITY-ALPHA |
| createdAt | 2026-11-23 09:15:10 | 2026-11-23 09:15:10 |
| updatedAt | 2026-11-23 09:32:11 | 2026-11-23 09:32:11 |

- QA2 浏览器同时通过部分编辑、空态与错误态、实际拖拽列宽及刷新恢复和重置、历史入口与返回、配置冲突、英文浅色桌面与中文深色 430px 对齐回归。返修验证脚本 SHA-256 为 `09ff02f97b5ef085b9d7dbd5905c3176e9047d6128980743813f185654358462`。
- 在正式根目录执行 `node --test frontend-js/tests/module-registry/quality-results.test.mjs`，4 passed。正式 frontend-js 执行 `pnpm check:modules`，9 模块、30 路由、9 分组通过。`pnpm test:modules` 为 111 passed、3 failed，退出 1，与上列首轮相同的 Monitor 排序三项。质量专项无失败。`git diff --check` 退出 0。
- QA2 未重跑后端或 MySQL，未访问开发库。前后两次核对 8000 无监听。临时 Chrome 与回环服务已结束。QA2 临时目录内的构建、脚本、截图和日志可由协调者回收。当前无本任务 QA blocker，移交 Human Owner 决定最终验收。

## Human Owner 最终验收 · r2

2026-11-24（Asia/Shanghai），Human Owner 明确确认：“验收通过 ARCH-QUALITY-001 r2 和 ARCH-QUALITY-002 r1”。据此记录 ARCH-QUALITY-001 r2 为 `owner_accepted`。

Human Owner 在开发环境的质量列表创建了 `TEST-P-01`，随后在 Swagger 通过公开接口执行 upsert 和 GET。回读结果包含 `defectCount=7`、`reportUrl=https://example.com/quality/test-p-01`，目标标识为 `null`，创建时间和更新时间分别返回。

本次仅登记验收决定及手工证据。无临时资源。
