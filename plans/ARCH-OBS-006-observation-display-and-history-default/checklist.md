Task ID: ARCH-OBS-006
Revision: r2
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: r2 独立验证通过；Human Owner 于 2026-11-23 完成最终验收。

# 独立验证 · 第一次交接

正式工作树 HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，批准 spec SHA-256 为 `d146f31bbb33a0235f1a18ee31027d1e22f46b9e2e560e6a5eb1422abe0a601b`。验证对象为 tasks.md 列明的未提交候选。环境为 macOS、Node v22.19.0、pnpm 11.11.0、uv 0.7.8、仓库 Python 3.13 环境。

## 阻止通过的问题

1. AC04 相同默认查询堆积。在 `curves.vue:211`，恢复默认始终调用 supersede，清除 loading 后调用 refresh。通过 Node 的 vue/compiler-sfc 编译正式组件，调用 setup，注入非空设备列表、temperature 类别及一直 pending 的 historyDefaultContext；同步连续调用 restore 12 次，取得 **12 个尚未完成的请求**。按钮仅在设备列表为空时禁用。对照实测：相同固定条件连续 12 次 submit 只产生 1 个 historyCurves；设备页连续 12 轮 restore/apply 只产生 1 个 latestCards。返修应合并相同的在途发现请求，并允许真正改变条件的操作抢占旧请求。
2. AC04 全局默认范围会意外固定。按源码状态转换，手动选来源后再清空并恢复默认，selectSource 将 sourceChosen 置 true，第一次 restore 使用空串执行全局发现。syncDraft 将发现的 A 写回 draft.equipmentId；再按恢复默认时，仍为 true 的 sourceChosen 导致 defaultSource 被改为 A，此后 B 的更新无法参与发现。返修应单独保留用户明确指定的范围，并覆盖“清空 → 全局发现 A → 再次恢复 → B 更新”的回归场景。

## 复核记录

| 项 | 已取得证据与边界 |
| --- | --- |
| AC01 | 核对共享组件的三段模板、筛选与默认开关；恢复默认交互受上述缺陷影响。 |
| AC02 | 专项套件通过，模板区分布尔、缺测和时间，并提供独立时钟按钮。独立浏览器查验留待返修。 |
| AC03 | 真实 FastAPI 路由与隔离 SQLite 的专项套件通过，核对授权集合、数字筛选、稳定排序、100 条建议与八小时端点。无 MySQL 现场执行证据。 |
| AC04 | 失败。原有迟到响应测试通过，相同默认发现请求仍会堆积，全局范围也会意外改变。 |
| AC05 | 核对图卡绘制门槛、区域和独立图例逻辑，现有专项套件通过。窄屏布局及悬停留待独立浏览器复验。 |
| AC06 | 后端专项回归通过，检查 JSON 线型保留及配置／历史读取投影。 |
| AC07 | 观测、写入来源、回执与退役测试通过，前端观测专项通过。 |
| AC08 | 后端和前端专项、模块检查通过。全量前端套件有三项基线失败；本轮因 AC04 退回，独立生产构建及隔离浏览器交互留在下一次交接。 |

## 命令和结果

- backend 下使用 `uv run --frozen --offline --no-sync pytest -p no:cacheprovider -q -m no_db` 执行 tests 下的 test_equipment_observation_r10_flow.py、test_equipment_observation_r10.py、test_equipment_observation_r8.py、test_observation_write_sources.py、test_observation_receipt_separation.py、test_observation_retirement.py。106 passed，1 条 SQLite datetime adapter 弃用警告。
- frontend-js 下执行 `pnpm check:modules`，退出 0，29 routes、9 groups。`node --test tests/module-registry/equipment-observation*.test.mjs`，24/24 通过。
- `pnpm test:modules` 报 104/107 通过。用 `git archive HEAD frontend-js` 获取隔离基线并复用锁定依赖，再运行 `node --test tests/module-registry/*.test.mjs` 得 96/99。两边失败的三个名称一致，分别为 `admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。临时基线已回收。
- 两个共享页面和后端观测目录的 `git diff --check` 退出 0。未操作 Docker、运行中的服务、业务库或 PLC。

本次正式结论为 **qa_failed**。Development 返修后须重新交接精确候选，再由独立 Verification 完成余下验证。

## 独立验证 · 第二次交接 QA2

**结论为 qa_failed。** 正式工作树 HEAD、批准 spec SHA-256 与 QA1 记录一致。重新计算 curves.vue 与专项测试的 Git blob 分别为 `8058bcb2bbc3a1a2cf8ed0ecd8af5c1cde69385f`、`2ce95df31d0e6b924e958ce04c44abf28bf7c6f3`，均匹配 QA2 developer_handoff。保留上述 QA1 历史记录。

| 检查 | QA2 实测与判断 |
| --- | --- |
| AC01、AC08 | 使用正式生产构建，Chrome 157.0.8103.79，macOS 15.7.7，中文浅色 1400×950 和英文深色 390×950。七个正式路由共用实际页面组件和观测 HTTP 路由，合成身份与内存 SQLite 隔离。设备和过程页具有标题、筛选与内容。根文档未出现横向溢出，但默认窄屏过程图的可用性见 F04。 |
| AC02 · F03 阻断 | 生产参数页四卡在桌面两列、窄屏一列。首卡时钟按 Enter 单独展开五项，真实 Tooltip 和双语名称正确，5 秒轮询后仍展开，Space 收起。布尔 false 为标签，缺测时间为破折号。**实际按钮缺少规定的 aria-expanded**。在 `cards.vue:45` 的 Element Plus Tooltip 包裹下，确认展开时 `document.querySelector('.clock-action').getAttribute('aria-expanded')` 为 null，真实 DOM 只有相应的 aria-label、aria-describedby；中文与英文均复现。模板有绑定，故仅检查源码或 stub 不能代替真实 DOM 断言。 |
| AC03 | 后端资格用例独立通过，含 140 条合成样本、授权来源、同刻、unknown、零值与更新但不可绘制的样本。浏览器另取 289 条八小时历史样本，两系列各 289 个点，HTTP 参数保留跨日微秒端点。MySQL 方言编译结果和 SQLite EXPLAIN 范围见下。 |
| AC04 · QA1 F01/F02 关闭 | 独立 Chrome 在首次默认 GET 返回前对可用的“恢复默认”连续点击 12 次，仅收到 1 个在途默认 GET。采用可控默认上下文响应，选 second 并恢复后请求限定 second，清空后全局发现 line，下一次恢复全局发现 second。五次上下文 GET 的 equipmentId 顺序为省略、second、second、省略、省略（两次 second 含选项查询）。正式组件的乱序与不同条件抢占专项亦通过。 |
| AC05 · F04 阻断 | 中文桌面跨日曲线宽 1044px，悬停得到真实日期、时刻和值；实线与虚线、独立图例、全部隐藏及恢复、刷新保留隐藏、区域全取消与全选恢复均实测可用。空配置过程页不画轴。**390px 的首次默认布局下，保留项目默认展开侧栏时曲线不可读。** 真实画布宽 62px，`CurveChart.vue:116` 绘图区左右留白为 58px 与 14px，合计 72px。图卡滚入视口后，在高度 135px、横向 30%、50%、70%、90% 依次悬停均无采样提示，同一批 289 条有值样本在桌面正常。 |
| AC06、AC07 | 重新运行线型创建、缺省、保留、重排、非法值、投影，以及同刻、迟到、缺口、写入来源、回执与退役相关用例；后端综合专项 106 项通过。浏览器双系列使用配置的实／虚线。 |

### QA2 命令与证据

- 在 backend 以 `uv run --frozen --offline --no-sync pytest -p no:cacheprovider -q -m no_db` 运行 QA1 列出的六个文件，106 passed，1 条既有 SQLite datetime adapter 弃用警告。uv 0.7.8，项目 Python 3.13。
- MySQL 方言对单来源单槽实际编译为下列 SQL。SQLite 同形索引的单来源 `EXPLAIN QUERY PLAN` 断言命中 `ix_obs_history_equipment_time_v2`。SQLite 使用 JSON 函数适配。实际 MySQL 的计划、跨多来源排序成本及高频生产吞吐尚未测量。

```sql
SELECT monitor_main.equipment_id, monitor_main.task_no, monitor_main.observed_at
FROM monitor_main
WHERE monitor_main.equipment_id IN ('line')
  AND json_type(json_extract(monitor_main.local_values, '$."heatZone1"."07"')) IN ('INTEGER', 'DOUBLE', 'DECIMAL')
ORDER BY monitor_main.observed_at DESC, monitor_main.id DESC
LIMIT 1
```

- 在 frontend-js 以 Node v22.19.0、pnpm 11.11.0 运行 `pnpm check:modules`，29 routes、9 groups；`node --test tests/module-registry/equipment-observation*.test.mjs` 通过 26/26；对 `equipment-observation-columns.test.mjs` 使用 `--test-name-pattern='process page discovers'` 单独重跑通过 3/3。`pnpm test:modules` 为 106/109，失败三项名称与上方 QA1 独立 clean HEAD 对照一致。
- `VITE_API_BASE_URL=/api/v1 pnpm build --outDir /private/tmp/obs006-freshqa2-build --emptyOutDir` 退出 0，有 vendor chunk 体积提示。浏览器通过临时 uvicorn、正式 FastAPI 观测路由、内存 SQLite 与同源静态构建运行，数据含四卡、两来源、两区域与 289 条跨日记录。F01/F02 单独用 Playwright 控制默认上下文响应时序。未操作 Docker、用户服务、真实数据库或 PLC。
- Development 应在批准范围内处理 F03/F04，再交接精确候选。建议真实浏览器分别断言时钟收起／展开的 DOM 属性、默认窄屏的有效绘图范围及悬停。Human Owner 最终验收待定。
- F04 对照：保持相同 390px 英文深色视口，手工收起侧栏后，画布由 62px 增至 298px。此时悬停读取到 `2026-11-16 19:06:40`，区域全取消与恢复、图例切换及位置检查均通过。复验须覆盖普通首次进入时的默认布局。

## 独立验证 · 第三次交接 QA3

**ARCH-OBS-006 r1 为 qa_passed，交给 Human Owner 最终验收。** fresh-context Verification 在正式工作树重新计算 HEAD、批准规格 SHA-256 和三项 Git blob，分别与 QA3 developer_handoff 一致。保留 QA1、QA2 的历史判断。本轮针对三项前端返修验证。七路由、桌面浅色、隔离 HTTP 与历史数据矩阵沿用 QA2 独立证据，并在当前候选重跑相关测试。

| 标准 | 当前候选证据 |
| --- | --- |
| AC01、AC05 | macOS 15.7.7 arm64，真实 Chrome 157.0.8103.79。中英文各以全新 390×950 深色上下文访问生产构建的温度页。默认展开导航高 150px，画布宽 298px。每系列 289 点跨日，鼠标悬停显示上海时间 2026-11-17 23:45:00，两系列分别为 120、121。使用同一 SPA 会话切换到设备生产参数页，侧栏恢复 236px，验证样式随路由退出。F04 关闭。 |
| AC02 | 两种语言实际时钟按钮初始 aria-expanded=false，鼠标悬停能看到与可访问名称一致的 Tooltip。聚焦按钮按 Enter 后属性变为 true，旁卡仍为 false；经历第二次实时卡片请求后保持 true，按 Space 收起为 false。F03 关闭。 |
| AC03、AC06、AC07 | QA2 所列六个后端测试文件以相同 pytest 参数重跑，106 passed，1 条既有 SQLite datetime adapter 警告。覆盖授权来源内可绘制锚点、八小时与精度、线型与原有数据语义。MySQL 证据限于方言 SQL 编译，查询计划证据来自 SQLite，实际 MySQL 执行计划和产线吞吐仍未测量。 |
| AC04 | 对首个默认请求保持响应在途，实际页面按钮触发 12 次仅发一个 GET。选择 B、按 B 恢复、清除来源、全局发现 A、再恢复发现 B。两种语言上下文记录的 equipmentId 顺序均为省略、B、B、省略、省略。F01、F02 维持关闭。 |
| AC08 | frontend-js 运行 pnpm check:modules 为 29 routes、9 groups；node --test tests/module-registry/equipment-observation*.test.mjs 为 26/26；pnpm test:modules 为 106/109，失败名称与 QA1 已验证的三个基线项完全一致。VITE_API_BASE_URL=/api/v1 pnpm build --outDir 指向 QA3 独立临时目录，退出 0，有 vendor chunk 大小提示。三个返修文件 git diff --check 退出 0。 |

独立 Chrome 通过 Playwright 加载本次构建，所有页面资源和 HTTP 响应均由本地文件及内存 fixture 提供。首次 Chrome 启动受沙箱限制，获准使用隔离临时配置后，完整浏览器验证退出 0。未访问用户正在运行的服务、真实数据库、Docker 或 PLC。

Human Owner 可在已准备的验收环境先打开设备生产参数页，用 Tab、Enter、Space 操作首卡时钟，观察轮询前后与旁卡状态。随后以 390px 宽度保留展开导航进入温度页，悬停有数据的曲线并核对时刻和值；用已知样本核对首次默认查询与选定来源后的恢复默认，确认结束时刻对应最新可绘制观测，开始时刻早八小时。最终验收由 Human Owner 记录。

## ARCH-OBS-006 r2 · 独立 Verification

**Verdict：`qa_passed`。** 2026-11-23，在独立上下文从正式工作树核验 `developer_handoff · r2`。HEAD 为 `ee942c8b82cf5b3e502872d8d6ee5c7820b2314e`，批准 spec SHA-256 为 `436244bcd110fafc32276414bc41d65a286f773cd3515721919be41cbd398f62`。九份 r2 交付文件逐项运行 `git hash-object`，全部匹配 tasks.md 的候选表。保留上方 r1 验证记录。工作树含 r1 和并行变更，整树相对 HEAD 的改动不能全归于 r2。

| 标准 | 独立证据 |
| --- | --- |
| R2-AC01 | Chrome 加载正式温度页，默认任务 QA-A，控件显示 11 月 23 日 00:00–08:00。保留自动时间并输入 ` qa-b `，发现 GET 仅带类别与规范化 QA-B。在 second 上最近可绘制采集时间为 `2026-11-22T06:00:00.321987+08:00`，曲线 GET 起点为 `2026-11-21T22:00:00.321987+08:00`，终点与采集时间完全相同。响应值为 [4, 0, 1.5]，覆盖开始端点和两个同刻结束点。后来同任务的文本值未占据锚点；切 QA-C 后结束时间变为 11 月 20 日 08:00:00.321987。 |
| R2-AC02 | 显式选择 line 后，查仅存在于 second 的 QA-B，最后一个 GET 严格带 line、页面显示空样本且无曲线网格。清除来源后同一任务重新命中 second。后端专项覆盖无权与已删除来源 403、授权来源同刻决胜。 |
| R2-AC03 | 用户手输上海时间 11 月 20 日 01:00:00 至 03:00:00，再查 QA-B，仅发一个 history-curves GET，from/to 为手输时间加 +08:00，锚点 GET 为零。分别验证清空按钮后的双空时间、无匹配任务返回后的双空时间，查询 QA-B 均触发发现并恢复相同微秒八小时范围。部分输入在页面报错、不发请求、原任务保留。手动刷新并开启轮询超过 5 秒，只重读固定曲线端点。倒置范围由范围校验及交接浏览器证据覆盖。 |
| R2-AC04 | 运行正式路由的 ASGI 合成专项，覆盖缺省与规范化任务、非法输入 422、0、unknown、同刻与微秒、来源及目标错误。MySQL 方言编译断言任务谓词先于排序；同形 SQLite 索引计划通过。 |
| R2-AC05、06 | 页面真实无匹配任务时清空原曲线。组件专项控制响应顺序，12 次在途等价提交只发一次、后发查询与未提交草稿均保留，覆盖恢复默认、固定范围、区域和图例回归。结合组件错误分支和后端 403、422、503 响应检查错误与空样本区分。 |
| R2-AC07 | macOS 15.7.7、Chrome 157.0.8103.79、uv 0.7.8、pnpm 11.11.0。隔离 Chrome 和 uvicorn 使用随机环回端口，正式 Vue 构建与 FastAPI 观测路由同源，独立构造六条样本、合成身份、内存 SQLite、目标 guard 与 MySQL JSON 兼容夹具。浏览器检查通过，服务、浏览器及临时构建已回收。 |

**命令与结果**

- backend 下执行 `PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/obs006-qa-uv uv run --frozen --offline --no-sync pytest -p no:cacheprovider -q -m no_db tests/test_equipment_observation_r10_flow.py tests/test_equipment_observation_r10.py tests/test_equipment_observation_r8.py tests/test_observation_write_sources.py tests/test_observation_receipt_separation.py tests/test_observation_retirement.py`，106 passed，1 条 SQLite 适配器弃用警告。
- frontend-js 下执行 `node --test tests/module-registry/equipment-observation*.test.mjs`，27/27；`pnpm check:modules` 通过（29 routes、9 groups）；`VITE_API_BASE_URL=/api/v1 pnpm build --outDir /private/tmp/obs006-r2-freshqa-dist --emptyOutDir` 构建成功，有既有 chunk 体积提示。范围文件的 `git diff --check` 通过。
- `pnpm test:modules` 107/110。三个失败与 r1 已核对的基线同名，涉及路由与菜单角色、Core 路由/locale/demo 默认值和五模块顺序，不计作本次专项通过。
- Chrome + Playwright 操作页面并记录 HTTP 请求。另观察到逐端用键盘删除已输入的时间时，日期控件在提交前可重显旧文字；实际请求正确转为按任务发现，使用控件的清空按钮时立即显示双空并得到相同结果。

**交接 Human Owner。** 无 r2 验证阻塞。上述结论适用于所列源码与隔离数据。真实 MySQL 运行计划、用户服务、PLC、部署及现场业务效果未经本轮验证。最终验收待 Human Owner 决定。

## ARCH-OBS-006 r2 · Human Owner 最终验收

状态：`owner_accepted`。2026-11-23，Human Owner 明确确认 ARCH-OBS-006 r2 最终验收通过。确认的行为包括：

- 仅输入任务号查询时，页面显示该任务最近可绘制样本及其向前八小时的曲线。
- 手工指定时间时，查询使用所选范围。
- 刷新保留已应用的范围，不跳回默认时间。

Verification 根据协调方转达的 Human Owner 决定登记本条。独立 QA 证据见上方 r2 验证记录。
