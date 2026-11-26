Task ID: ARCH-ENERGY-005
Revision: r1
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification
Handoff: Human Owner 最终验收
Workflow Mode: STD

# 独立验证记录

2026-11-25，Asia/Shanghai。fresh-context Verification 独立读取 r1 规格、交接、补丁与候选实现，以新建 MySQL、独立前端构建及浏览器会话复跑。正式树 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`。下表记录候选验证结果。

| 验收项 | 证据与结果 |
| --- | --- |
| AC01 | SQLite 空配置下管理员新增、默认 admin、下一请求选择和保存指标通过。Chrome 通过读取失败重试、空列表、无匹配、搜索重置、列宽拖动、恢复、返回指标配置后选择和保存。 |
| AC02 | MySQL 中未登录、非管理员维护分别返回 401、403。取消可读角色后，选项为空，指标、样本和统计接口拒绝，按记录 ID 修改备注返回 404。SQLite 单独撤掉角色接口权限后，已获表计角色仍被拒绝。 |
| AC03 | 两个 profile 表计与旧角色合并，原 profile 未变。并发首次 PATCH 中、英文名称均保留，localReviewer 等未提交角色保留；并发重复 POST 仅一次成功。 |
| AC04 | 同一登记来源一包三表返回三条记录；真实 MySQL 覆盖批次事务、重放及旧 v2 合法提交和重放。给数据库新表使用旧机器 grant 返回 403。 |
| AC05 | 修改登录角色前后，免 Token 公有最新与历史结果相同。前驱历史数据快照在迁移及角色修改后相等；新表无跨域外键，旧过程／实时兼容用例通过。 |
| AC06 | 中文、斜杠、点和仅大小写不同的标识可创建，部分更新、重复、未知、非法字段覆盖 200、409、404、422。临时隐藏表后依赖目录的请求返回明确 503，免 Token 公有读取、来源登记和既有回执重放仍可用。 |
| AC07 | MySQL 8.4.6 隔离实例，分别覆盖无业务样本和已有样本的前驱，错误 UUID 被拒；b52e9c416a07 到 9e0c5d41b7a2 仅新增 energy_meters。合成后继下测试兼容读写，创建与更新时间顺序、带 +08:00 的历史查询通过。 |
| AC08 | 生产构建、八组中英文／浅深色／PC 1440×900 与平板 1024×768 下列表、弹窗、遮罩取消通过。OpenAPI 三方法及 HTTPBearer 与发布快照一致，12 条链接通过。全量模块注册两项基线失败见下。正式源码尚未整合，交付树相等性待查。 |

## 命令、环境与复核边界

使用开发交接所列的锁定依赖与合成 HTTP harness；QA 独占的构建、浏览器会话、测试容器及重建目录均重新创建。浏览器使用实际 Vue 资源和模拟 HTTP；MySQL HTTP 集成使用实际路由和覆盖的合成身份。

- 候选 backend 执行 `uv run --no-sync python <handoff>/test-backend.py -p no:cacheprovider -q` 加 tasks.md 命令 1 的 11 个测试文件，退出 0，100 passed、1 skipped、1 warning。相同入口执行 `tests/test_openapi_router_tags.py -k energy`，退出 0，2 passed、3 deselected。
- `docker run --detach --rm --pull=never … -p 127.0.0.1::3306 … mysql:8.4.6` 分配 58329，UUID 为 `b62bf880-e87f-11f1-adb3-3245a7aa3902`。将两者与明确 ACK 传给独立的 tests_mysql/test_energy_meters_mysql.py、test_energy_registered_ingest_mysql.py、test_energy_public_reads_mysql.py，按同一 uv pytest 入口运行，退出 0，3 passed。未访问真实 dev MySQL。
- 前端运行 `pnpm --config.verify-deps-before-run=ignore run build --outDir <qa>/frontend-dist`，两项角色环境变量均为合成空数组，退出 0。以本机 headless Chrome 执行 `node <qa>/browser-check.cjs`，8/8 通过，退出 0。
- 正式前端与候选分别执行 `node --test tests/module-registry/*.test.mjs`，均退出 1，119/121。相同两项顺序断言为 “admin, supervisor, operator and unknown share route/menu/default decisions” 和 “actual source preserves Core route identity, shell locales and default-disabled demo”；本次没有新增失败。
- `uv run --no-sync python <handoff>/generate-openapi.py --check` 与 `python3 <handoff>/check-docs.py` 均退出 0。

## 工件与采用状态

精确规格 SHA-256 为 `3a5a70d3cc203b401a38eb099af0dae410dfe56f49d260a21c37b25047498916`，Development tasks.md 为 `44f4a797f2bc6ff0fff33fd12ecee564a1a0293487d918e3821d94f64fbe3c40`。独立核验 TSV 为 `d21cd98dc41e177c35c8827cfb73db33f02a8652ea5836f738f525407300acc3`，补丁为 `1b9cc1ce1bfc3feec2187a90e0f95bfc493fe17f8902aeb2667abb5552971f1a`。正式树 `git apply --check` 成功；将正式前像拷入独立空目录执行 `git apply --whitespace=error-all` 后，35/35 与清单后像及测试候选逐文件 SHA 相等。正式树 35 个路径本身仍是前像。3,982 个基线文件中另有四个非补丁文件已变更，为根 PLAN 双语和 plans/README 双语；整合应保留这些修改。

总判定 **qa_blocked**。候选的验收行为通过；AC08 正式工作树核对待完成。按规格 §7 及 Development 交接，运行中的 dev 后端自动加载正式源码；目标库迁移与服务采用须另行授权并由协调者执行。完成后独立复核清单后像、启动入口及实际采用状态，再移交 Human Owner 最终验收。

## 资源

QA 独占容器 energy005-qa-8j7hkd 已停止，名称查询为空。QA 临时目录 /private/tmp/energy005-qa.8j7hKD 在证据落盘后回收。Development 候选、补丁及运行记录仍由协调者保留于 /private/tmp/aiis-energy005-coordinator.Rr6SZu，待正式整合及复核后按交接回收。

## 2026-11-25 正式采用复核

**qa_passed，交 Human Owner 最终验收。** 上一阶段 AC08 的正式树一致性与运行入口阻塞已解除。复核对象为 ARCH-ENERGY-005 r1，采用交接 tasks.md SHA-256 为 `8f4de97d9dbeba6ca3558e2f1233e1dee7417047e8feeb5a370e033521194c8d`。

- 在正式仓执行 `shasum -a 256` 核对交接、补丁和 TSV，再用 TSV 第三列对正式文件执行 `shasum -a 256 -c`，35/35 后像相符。`git diff --check` 通过。`lsof` 确认 8000 两个监听进程 cwd 均为正式 backend，5190 监听进程 cwd 为正式 frontend-js。
- 用 `stat` 和 `shasum -a 256` 核对备份目录 0700、文件 0600、357385 字节，摘要为 `a249d7eb8765be2933a62bf3ec02a80d5a536f1c0f84235953c436e9b9ea1a7c`。验证范围为文件完整性，未做恢复演练。
- 正式 backend 的锁定 venv 执行只读 SELECT，核对回环 3307 目标库 revision 为 `9e0c5d41b7a2`，energy_meters 为 0 行。通过 Python urllib 对 8000 和 5190 分别请求：匿名表计目录均返回 401、公有最新与历史均返回 200。8000 的实时 OpenAPI 列出表计 GET、POST、PATCH，5190 实际前端入口返回 200。上述独立运行退出 0。
- 核阅协调者 dev-http-result.json 和对应检查脚本，两端管理员表计目录 200（空列表），写入登记、设备实时、过程历史及质量 GET 均 200。本轮独立复核使用上述协调者记录作为已登录请求证据。真实 dev 未执行表计业务 POST，也未独立复跑已登录浏览器弹窗；弹窗交互证据来自前一阶段候选 8/8。正式全模块套件仍有上述两项既有断言失败（119/121）。
- 协调者在独立 QA 后补测正式 dev，Verification 核阅了 `dev-browser-result.json` 和浏览器脚本。已登录 Chromium 在 5190 以 1440 × 900、中文浅色打开管理页，页面和表计 GET 均返回 200，响应数据为 `[]`，界面显示「暂无表计」。从「管理表计」进入「新增表计」，可见「基本信息」「可读角色」，默认勾选 admin，空表单的保存按钮禁用。点击遮罩关闭弹窗后成功返回指标配置。浏览器仅放行同源 GET／HEAD，写请求尝试为 0，脚本退出 0，临时浏览器已关闭。
- 本次 QA 无临时资源。候选目录由协调者在证据落盘后回收，独立授权的恢复备份由 Human Owner 确认保留期限。

## ARCH-ENERGY-005 r2 独立验证

**qa_passed，交 Human Owner 最终验收。** 2026-11-25（Asia/Shanghai），Verification 在 fresh context 从正式工作树重新构建并运行 Chrome。核验 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，批准规格 SHA-256 为 `669b9d996c18b60607a4ea2437880f1560fbcc907e2523efe4c0030b2d4e3abd`，Development 交接 tasks.md 为 `4365d1bfeab15e79bc4f2e984cc1990d24c35936a00ead6e8d2da158d49a9d2b`。r1 checklist 原文前缀摘要为 `fd1f8a3fd7db7e1f96014f61656d1b1a0673b872db2f8bedb43d2a5141177183`。

| 验收项 | 独立检查结果 |
| --- | --- |
| R2-AC01 | 真实 Vue 路由首次选中表计指标配置。上卡三个选项按表计管理、表计指标配置、写入登记排列，点击后所选项和下卡标题同步。指标卡无重复入口，表计卡头仅有新增和重置列宽。 |
| R2-AC02 | 1440×900 和 1024×768 各覆盖中英文、浅深色。标题区下方是全宽筛选区和 1px 主题分隔线，关键词左缘、操作组右缘与表格对齐。默认表格分别宽 1114、698 CSS px，五列表头及最后操作列铺满内容区。含旧偏好的平板组合在重置后再次核对此项。 |
| R2-AC03 | PC 首列从 269 拖至 345px，550×780 英文深色首列从 155 拖至 220px。切换工作区及整页重载后核对实际列宽，重置后恢复初始值。平板旧偏好也可恢复及清除。550px 视口的筛选按钮换行，252px 表格视区可横向浏览 685px 内容并点击行内编辑。 |
| R2-AC04 | 合成 API 返回首次读取失败后可重试，空目录和无匹配分别显示。遮罩取消写请求为零。首次保存冲突保留弹窗，重试创建成功；编辑名称及角色后列表刷新。再进指标配置触发新的 options 请求，新表可选并可保存指标；写入登记新增和编辑成功。 |
| R2-AC05 | 正式工作树的模块合同检查、聚焦测试、生产构建、双语键与 r2 链接通过。全模块套件仍有下述两项基线失败。协调者在本机 dev 核实当前入口，独立浏览器使用合成接口。 |

### 命令、交付与限制

- 正式 frontend-js 使用 `pnpm --config.verify-deps-before-run=ignore exec node --test tests/module-registry/energy-write-sources.test.mjs`，3/3 通过。两项角色环境变量 VITE_SUPERVISOR_PAGE_ACCESS_JSON、VITE_OPERATOR_PAGE_ACCESS_JSON 均设为合成空数组，执行 `pnpm --config.verify-deps-before-run=ignore run build --outDir <qa>/dist --emptyOutDir`，退出 0。prebuild 校验 32 个路由、10 个组，Vite 5.4.21 构建通过并给出既有 chunk 体积提示。
- 核读 Development 的浏览器脚本，将其复制到独立 QA 目录，执行 `node <qa>/browser.cjs`，使用 QA 新构建、全新浏览器上下文及合成身份。沙箱内 Chrome 启动失败，获准运行本机无头 Chrome 后退出 0，九组完成。该脚本拦截所有请求，仅读取本地静态资源并模拟 HTTP 响应。
- `pnpm --config.verify-deps-before-run=ignore run test:modules` 独立复跑退出 1，120/122。对照 r1 基线日志的 119/121，失败项均为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`。新增用例通过。
- `git diff --check` 退出 0。Python 对交接前基线 3,994 个路径逐个计算 SHA-256，并与当前 Git 路径集对照；追加本节前，仅 r2 批准的六个源码／测试文件及 spec.md、tasks.md 有差异。六项前后像均与交接清单相符，清单摘要 `d979741235f567b4028e8c15949581d142f3ac6fbb5a71d9594be1567baae30e`。双语 locale 的 161 个叶子键对称，r2 两处文档目标及标题锚点有效。
- 正式源码已整合。核阅协调者在本机 5190 的已登录只读浏览器结果，1440×900 浅色、1024×768 深色均可切换三项，表格与筛选边缘差值为 0px，写入登记及重新取得表计选项返回 200，遮罩关闭成功，两组写请求尝试均为零。本轮独立 QA 的新增、编辑与指标保存仅使用合成数据。最终验收待 Human Owner 决定。

QA 浏览器已关闭。独占目录 `/private/tmp/energy005-r2-qa.hvJeT9` 在以上证据落盘后回收。Development 与协调者的 `/private/tmp/aiis-energy005-r2.DiDJSj/` 由协调者在交接收尾时回收。

## ARCH-ENERGY-005 r2 · Human Owner 最终验收

Revision: r2
Status: owner_accepted

2026-11-25（Asia/Shanghai），Human Owner 明确确认「验收 ARCH-ENERGY-005 r2。」
