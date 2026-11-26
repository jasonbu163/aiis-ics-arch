Task ID: ARCH-ENERGY-005
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: 隔离候选与可恢复补丁交 fresh-context Verification，正式 dev 采用等待独立批准
Workflow Mode: STD
Execution Mode: agent_team_same_session

# ARCH-ENERGY-005 r1 实施与开发自检

Human Owner 已明确批准 ARCH-ENERGY-005 r1 按 STD 开发。精确 [r1 规格](spec.md) 的 SHA-256 为 `3a5a70d3cc203b401a38eb099af0dae410dfe56f49d260a21c37b25047498916`。正式仓库位于 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基线 HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，候选基于该工作树含 ARCH-ENERGY-003、004 等未提交交付的 3,982 个文件。Development 对照了根及最近作用域的项目契约、模块文档、获批规格，采用 `backend-arch`、`frontend-ui`、`i18n-workflow` 和 `code-document-indexer`。

## 实施

- 能耗管理的「配置管理 → 表计指标配置」新增「管理表计」。复用登记管理的主卡、公共按钮、列表列宽偏好和紧凑弹窗。新增默认勾选系统管理员，编辑可变更中英文名称和可读角色。表计标识固定，旧自定义角色回填并保留。返回指标配置会重新获取当前可选表计。
- 登录管理员通过 `GET`、`POST`、`PATCH /api/v1/energy/meters` 维护表计定义，三个方法均归 Swagger 的 Energy / Management。新增 `energy_meters` 持久化名称和可读角色。同标识的数据库定义优先，未编辑的旧表计沿用 profile。首次编辑兼容表计时由 MySQL 唯一键建行及锁行并入本次字段，随后用数据库当前值合并部分更新。
- 选项、指标配置、样本、详情、复核及统计统一使用有效表计和登录角色范围。能耗来源登记仍单独维护。登记样本 POST 先按既有登记和回执判断重放，再对新报文使用有效表计。公有读样本与旧 v2 的机器 Bearer grant 继续使用各自的数据来源和认证合同。实时／过程与能耗没有跨域外键或任务号依赖。
- 迁移 `9e0c5d41b7a2` 是 `b52e9c416a07` 的唯一正式后继，仅创建 `energy_meters`。执行时检查目标 UUID、schema、准确前驱以及既有能耗依赖。迁移拒绝删除表计定义式 downgrade，回退应用须保留该表。
- 同步中英文能耗模块说明、合同索引、源码索引和 [表计管理发布合同](../../contracts/published/http-api/energy-meters-v1/README.zh-CN.md)，OpenAPI 由实际 FastAPI 应用生成。

## Development 自检

| 验收点 | 实际验证 |
| --- | --- |
| AC01 页面新增 | SQLite 夹具从空 profile 表计起步，创建默认管理员可读的表计，下一请求查询到新配置并成功配置指标。Chrome 从空表计页进入，验证读取失败后重试、空状态和无匹配状态、创建表计后返回指标页选择它并保存指标、列宽拖拽、跨页面保留和重置。 |
| AC02 编辑与角色 | MySQL 验证无 Token 和非管理员访问管理接口分别返回 401 和 403。撤销角色后下一请求的选项、指标、样本、详情／复核及统计按既有错误语义拒绝访问。SQLite 验证授予表计角色后还须具备现有能耗接口权限。 |
| AC03 旧配置兼容 | 隔离 MySQL 验证两份旧表计、角色范围及未改动自定义角色键。并发首次更新同表的两个不同名称字段均成功，合并结果保留两次修改与既有角色。并发同标识创建只成功一次，原 profile 未被写回。 |
| AC04 单源多表与旧 v2 | 隔离 MySQL 由一个来源在一包写入两个旧表计和一个新表计，保留零值与逐组回执。旧 v2 合法 grant 写入和重放正常，数据库新表计未被纳入旧 v2 grant。既有 ARCH-OBS-010 批次事务及重放回归通过。 |
| AC05 公有与数据边界 | 隔离 MySQL 验证表计角色修改前后的公有最新与历史 GET 回包相同，比对能耗指标、旧样本、回执和过程／实时等既有表数据。已有 ARCH-ENERGY-003 公有读取、既有 v2 及实时／过程调用回归通过。 |
| AC06 标识与异常 | MySQL 验证中文、斜杠、点、大小写、冲突、未知表计及稳定输入拒绝结果。临时隐藏表计表时，依赖表计范围的请求返回 503；来源登记、公有 GET 和已存在的合规回执重放仍可用。 |
| AC07 迁移及时间 | 独立 MySQL 8.4.6 使用真实 Alembic 入口，先拒绝错误 UUID，再分别升级未有样本及含旧样本的合成目标，表结构差异仅一张新表，无跨域外键。已保存旧行逐项相同。增加合成无关后继后，旧 v2、登记和受角色限制的读写照常。测试比对表计创建和实际更新时间，相关样本时间偏移由原测试复核。 |
| AC08 工程与界面 | 生产构建、本任务聚焦命令、OpenAPI 快照及新增链接一致。Chrome 使用候选生产资源与隔离模拟 HTTP，覆盖中英文、浅深主题及 1440 × 900、1024 × 768，验证表计弹窗标题、分组、页脚范围、遮罩取消、查询、新增、角色编辑和指标配置。 |

### 命令与结果

1. 在候选 `backend/` 使用 `UV_CACHE_DIR=<任务目录>/uv-cache uv run --no-sync python <任务目录>/test-backend.py -q <聚焦文件列表>`。合成夹具将数据库默认入口指向占位端口。选取 `test_equipment_observation_r10_flow.py`、`test_energy_meters.py`、`test_energy_registered_ingest.py`、`test_energy_public_reads.py`、`test_observation_retirement.py`、`test_acquisition_consumption_contract.py`、`test_observation_receipt_separation.py`、`test_mapping_migration.py`、`test_legacy_acquisition_retirement.py`、`test_equipment_temperature_migration.py`、`test_generic_task_migration_r3.py`，结果 **100 通过、1 跳过、1 项既有 SQLite 适配弃用提示**。另用同一入口执行 `tests/test_openapi_router_tags.py -k energy`，结果 **2 通过、3 未选择**。
2. `uv run --no-sync … alembic heads` 得唯一 head `9e0c5d41b7a2`。真实迁移和并发 HTTP 使用项目 `uv` 运行 `tests_mysql/test_energy_meters_mysql.py`、`tests_mysql/test_energy_registered_ingest_mysql.py` 和 `tests_mysql/test_energy_public_reads_mysql.py`，**3 通过**。复验创建唯一具名、`--rm`、`--pull=never`、随机回环端口的 MySQL 8.4.6 容器，由该容器查询 UUID。按 `target` 夹具传入 `OBS010_TEST_PORT`、`OBS010_TEST_UUID`、`OBS010_TEST_PASSWORD` 与 `OBS010_TEST_ACK=ARCH-OBS-010-r1:127.0.0.1:<port>:<uuid>`，夹具以新随机 schema 跑三套隔离场景并收尾。每次迁移由夹具根据新建独立目标设置对应的 `ENERGY_WRITE_EXPECTED_*` 和 `ENERGY_METER_EXPECTED_*`。
3. 在候选 `frontend-js/` 以合成的两个 `VITE_*_PAGE_ACCESS_JSON=[]` 变量执行 `pnpm --config.verify-deps-before-run=ignore run build --outDir <任务目录>/frontend-dist --emptyOutDir`。模块合同检查、Vite 生产构建均通过。参数禁止 pnpm 对候选的已锁定依赖链接尝试执行自动重装。构建有既有大 chunk 提示。模块套件脚本 `node --test tests/module-registry/*.test.mjs` 为 **119 通过、2 失败**，与正式基线的两项菜单／路由顺序断言完全一致（`admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`）。
4. `node <任务目录>/browser-check.cjs` 以本机 Chrome 加载构建静态资源和合成 HTTP，使用相同 locale、主题和真实 Vue 路由入口。浏览器日志和逐组合图像保存在任务目录。浏览器无需额外服务端口。
5. `uv run --no-sync python <任务目录>/generate-openapi.py --check` 对实际 OpenAPI 验证发布快照的三方法、响应、请求和 `HTTPBearer`。新增合同相关 12 个本地链接校验成功。基线 3,982 个文件哈希一致，`git apply --check --whitespace=error-all <候选补丁>` 校验通过。

## 精确交接与采用边界

候选根目录为 `/private/tmp/aiis-energy005-coordinator.Rr6SZu/candidate`。相对于正式工作树基线修改 25 个文件，新增 10 个文件。全部路径与每文件前后哈希由下表清单固定。任务 `tasks.md` 在正式仓库记录，规格与验收清单不属于候选变更。

| 工件 | SHA-256 |
| --- | --- |
| `/private/tmp/aiis-energy005-coordinator.Rr6SZu/ARCH-ENERGY-005-r1.patch` | `1b9cc1ce1bfc3feec2187a90e0f95bfc493fe17f8902aeb2667abb5552971f1a` |
| `/private/tmp/aiis-energy005-coordinator.Rr6SZu/ARCH-ENERGY-005-r1-files.tsv` | `d21cd98dc41e177c35c8827cfb73db33f02a8652ea5836f738f525407300acc3` |

交 fresh-context Verification 独立核验精确 r1 及以上候选。本任务源码在隔离候选，现有本机 dev 继续使用原始正式源码。由于正式后端开启自动重载，按获批规格，协调者须在获得独立真实迁移许可后先按目标库身份及准确前驱迁移，再按清单核对正式工作树并整合精确候选，最后核对启动入口和现有 dev 使用状态。当前无本任务 Git 提交、无真实库迁移、无测试业务数据写入真实库、无 dev 服务切换或重启。真实环境使用仍待该采用步骤及独立查证。

### 临时资源收尾

任务独占 MySQL 容器 `aiis-energy005-r1-Rr6SZu` 已停止并由 `--rm` 回收，查询无该容器。根目录下候选、生产构建、浏览器截图、日志及复验脚本保留供独立验证和后续正式整合。Playwright 各会话关闭。协调者在 Verification 证据落盘并完成候选整合，或明确将补丁转存至稳定保留位置后，回收该任务目录。测试过程中使用候选环境与项目锁定依赖目录的链接，无额外依赖安装。


## Human Owner 独立授权后的本机 dev 采用记录

Human Owner 明确授权「批准备份本机 `3307` dev 库，从 `b52e9c416a07` 迁移到 `9e0c5d41b7a2`，并将 ARCH-ENERGY-005 r1 整合到正式工作树并验证。」本节记录协调者执行结果，更新上文候选交接时的采用状态。精确 r1 及其候选文件清单保持一致。

- 协调者先备份本机 MySQL 8.4.6 的 `127.0.0.1:3307/industrial_level_2_system`，使用已核对指纹的候选迁移推进 Alembic。数据库实际 revision 从 `b52e9c416a07` 到 `9e0c5d41b7a2`，正式源码的 Alembic 图只有该新 head。新增 `energy_meters`，迁移后为 0 行、0 外键。原有 68 张表的定义一致。能耗指标、回执、样本和写入登记仍各为 0 行，设备实时、过程历史及质量分别保持 5、23、2 行。
- 迁移完成后，协调者把精确 r1 补丁整合至正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`。变更后 35 个文件与候选 SHA-256 逐个一致，`git diff --check` 通过，HEAD 仍为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，整合已在正式源码中并待提交。
- 正式后端使用 `UV_CACHE_DIR=<任务目录>/formal-uv PYTHONDONTWRITEBYTECODE=1 uv run --no-sync python -B <任务目录>/test-backend.py -p no:cacheprovider -q tests/test_energy_meters.py tests/test_energy_registered_ingest.py tests/test_energy_public_reads.py tests/test_equipment_observation_r10_flow.py`，**34 项通过**，退出 0，保留既有 SQLite 日期适配弃用提示。正式前端执行 `pnpm --config.verify-deps-before-run=ignore run build --outDir <任务目录>/formal-frontend-dist --emptyOutDir`，退出 0，保留既有 chunk 体积提示。
- 本机正式后端与前端入口均已自动重载。健康检查、Swagger UI、前端入口返回 200，OpenAPI 列出表计管理的 GET、POST、PATCH。在后端 `8000` 和前端代理 `5190` 上，已登录的表计列表、表计选项、指标、写入登记，及实时、过程、质量、采集数据抽查均返回 200。匿名表计管理查询返回 401，公有能耗最新和历史 GET 返回 200。表计目录为真实空列表，当前 dev 可进入表计管理并开始配置。协调者以只读请求核验服务，无业务数据写入、无手动重启。
- 证据保存在任务目录 `/private/tmp/aiis-energy005-coordinator.Rr6SZu/` 的 `dev-migration-result.json`、`formal-integration-result.json`、`dev-http-result.json`。以上为协调者实际采用证据，交 fresh-context Verification 独立核验正式工作树和本机 dev。

### 采用后的资源收尾

本机 dev 的数据库备份位于 `/private/tmp/aiis-energy005-dev-backup.XrAqZ9/dev-before-9e0c5d41b7a2.sql`，357,385 字节，SHA-256 为 `a249d7eb8765be2933a62bf3ec02a80d5a536f1c0f84235953c436e9b9ea1a7c`。目录权限 0700，备份权限 0600，同目录 `backup-verification.json` 记录验证摘要。备份保留作恢复用途，待 Human Owner 确认无需保留后回收。协调者与 Development 共享的候选、构建和验证目录继续保留，待正式环境的独立验证完成且关键证据落盘后由协调者回收。

---

## ARCH-ENERGY-005 r2 · Development 实施与自检

Revision: r2  
Status: developer_handoff  
Owner Role: Development  
Allowed Writers: Development  
Handoff: 正式工作树的精确 r2 已交 fresh-context Verification

Human Owner 已批准「批准 ARCH-ENERGY-005 r2，按 STD 启动 Development」。精确 [r2 规格](spec.md) 的 SHA-256 为 `669b9d996c18b60607a4ea2437880f1560fbcc907e2523efe4c0030b2d4e3abd`。本节追加在 r1 采用记录之后，原记录逐字节保留，前缀 SHA-256 为 `8f4de97d9dbeba6ca3558e2f1233e1dee7417047e8feeb5a370e033521194c8d`。实现直接落在正式源码 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD 为 `9c30258358f169792d4cd0faeae3b80a41b43b81`，叠加既有未提交交付。

上卡继续使用 `card-action-segmented`，按「表计管理」「表计指标配置」「写入登记」切换，首次打开默认进入表计指标配置。删除旧入口、返回按钮与对应事件。表计管理下卡使用统一标题区、全宽筛选区和表格／状态区，关键词伸展，查询和重置靠右，分隔线横跨卡片，筛选控件与表格外框使用同一内边距。普通列按最低偏好宽度分配剩余空间，行内编辑复用 `row-actions`，拖拽和重置继续使用原表格字段键。窄屏在局部复用设备和过程配置页的上卡留位，避免应用多行顶栏覆盖表计工作区。保留 r1 的表计表单、权限、接口及数据合同。

| 验收项 | 开发自检 |
| --- | --- |
| R2-AC01 | 在真实生产构建的 Vue 页面检查三个上卡选项、顺序、初始选中与下卡标题联动。没有指标卡嵌套入口或表计卡返回按钮，写入登记与指标配置均可进入。 |
| R2-AC02 | Chrome 在 1440 × 900、1024 × 768 下分别覆盖中英文、浅深主题八组组合。核对标题、筛选、结果纵向排列，分隔线跨满卡片，关键词控件左侧、查询组右侧与表格外框对齐，默认表头及各列填满内容区，操作列可用。 |
| R2-AC03 | 桌面和 550 × 780 验证列宽拖拽、切换后恢复、页面重新加载后恢复、重置。1024 × 768 夹具预置一份 r1 列宽偏好，核对进入、切换、重载后的实际渲染宽度。550 × 780 上卡位于应用顶栏下方，筛选区换行，表格可横向滚动到操作列并打开编辑。 |
| R2-AC04 | Chrome 合成接口覆盖表计读取失败重试、空列表、无匹配、筛选清除、遮罩取消、重复标识冲突、新建、编辑名称及角色。重新进入指标配置后下拉显示新表计并保存指标。写入登记合成新增和编辑通过。 |
| R2-AC05 | 聚焦测试、模块检查、正式源码构建、r2 规格链接校验、变更路径审计通过。开发浏览器使用静态构建和合成 HTTP。协调者另以真实本机 dev 对 1440 × 900 浅色及 1024 × 768 深色做只读抽查，会话仅放行 GET／HEAD，写请求次数为 0。 |

### 命令及结果

- 正式 `frontend-js/` 执行 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='[]' VITE_OPERATOR_PAGE_ACCESS_JSON='[]' pnpm --config.verify-deps-before-run=ignore run build --outDir /private/tmp/aiis-energy005-r2.DiDJSj/dist --emptyOutDir`。模块合同检查及 Vite 生产构建退出 0，保留既有 chunk 体积提示。
- `pnpm --config.verify-deps-before-run=ignore exec node --test tests/module-registry/energy-write-sources.test.mjs` 退出 0，3 项通过。全量 `pnpm --config.verify-deps-before-run=ignore run test:modules` 为 120 通过、2 失败，退出 1。新增的工作区切换用例通过，两项失败与 r1 基线相同，分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 与 `actual source preserves Core route identity, shell locales and default-disabled demo`。
- `node /private/tmp/aiis-energy005-r2.DiDJSj/browser.cjs` 使用 Playwright 启动本机无头 Chrome，所有 HTTP 请求由浏览器路由隔离，服务端端口和真实数据库均未被该脚本访问。九组完成，退出 0。实际组合、布局数据、合成操作和截图位于同一目录的 `browser.log` 与 PNG。协调者实机只读抽查落在 `live-result.json`。
- `git diff --check` 通过。用 Python 检查 r2 规格的本地链接与标题锚点，并对协调者预备的 3,994 路径基线逐项比对。业务源码和测试仅以下 6 条 r2 路径变化，批准规格的变化由 PM 写入，原 QA 记录未改。

### 正式文件核验与资源

| 正式文件 | r2 SHA-256 |
| --- | --- |
| `frontend-js/src/app/energy/components/EnergyAdmin.vue` | `69eb858211ec885590a17b1d9283b79152c9e45461d0204e515b0429e35bcbe4` |
| `frontend-js/src/app/energy/components/EnergyMeters.vue` | `362607c9d48a41262d74d31804c5c97f979d2ebe69441f99049f45b22b0c269d` |
| `frontend-js/src/app/energy/locales/en-US.json` | `fa058e533cc3f2e2dc7e3e73bebdbb5ea508d78e4265a5f0e5e95f0179c5a628` |
| `frontend-js/src/app/energy/locales/zh-CN.json` | `9ecff45952b373418a60a7ba64ec959d1ff5328bc5112a84e9ac98d4cd67b6c5` |
| `frontend-js/src/app/energy/views/admin.vue` | `2e29a74c8948f3658fa658eb682ca55c54e872ce521233f62ef7a44cd80d27ff` |
| `frontend-js/tests/module-registry/energy-write-sources.test.mjs` | `ded2d248dd77ce320d760f6c419b2b7d4b0f27bb3e6296a7c9d2bbe33188c583` |

变更前后文件指纹位于 `/private/tmp/aiis-energy005-r2.DiDJSj/r2-files.tsv`，清单 SHA-256 为 `d979741235f567b4028e8c15949581d142f3ac6fbb5a71d9594be1567baae30e`。以上 r2 已整合至正式工作树，协调者证据显示本机 dev 前端在运行入口可以加载。等待独立 Verification 核对正式工作树和采用状态。未手动重启服务，未访问数据库实施迁移，未写入真实业务数据，未 commit 或 push。

Chrome 会话均已关闭，复验期间的中间失败截图已回收，无自建 HTTP 监听或数据库容器。协调者与 Development 共享的 `/private/tmp/aiis-energy005-r2.DiDJSj/` 保留静态构建、运行日志、截图、指纹及复验脚本供独立验证，待独立证据落盘并确认无需继续保留时由协调者回收。
