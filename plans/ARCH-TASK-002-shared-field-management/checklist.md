Task ID: ARCH-TASK-002
Revision: r1
Status: qa_passed
Owner Role: QA / Verification
Allowed Writers: QA / Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner final acceptance pending
Updated: 2026-11-20 Asia/Shanghai

# 独立验证 QA1

正式交付树 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`。独立读取[批准规格](spec.md)和[开发交接](tasks.md)，核对提交清单 22 个文件，逐项 SHA-256 全部一致，校验段摘要为 `6eee086cb4505d8c9a0bd8b8bd8cc82e7b6597850de6264f6802a09addcd9028`。结论为 **qa_failed**。AC05 存在可经普通管理员操作触发的原字段覆盖。

## 返工证据

1. 合成配置包含已启用的 `shared_sync / 5 / field5`，类型 string、单位 null。在任一共享字段管理入口点击「新增字段」，将建议空槽改为 5，填写同一稳定键、相同类型和单位，输入新的中英文显示名。其他开关保留新建表单的默认值。
2. 点击保存。Chrome 捕获到 PUT，而弹窗关闭。其 `changes[0]` 包含原字段身份、新双语名称、`enabled:false`、`planEditable:false` 等。将实际捕获的变更用于内存 SQLite 中带原定义的正式 ASGI 路由，使用当前修订提交，实际 HTTP 200。复读实绩配置，总数仍为 1，字段从启用变成停用，版本和修订均由 2 变为 3。
3. 原因可追溯到共享页 `validDraft()` 对新增槽位只检查数值范围，`changes()` 在新建模式提交全量默认值。既有 `save_config()` 按 scope/slotNo 合并，同稳定身份合法更新。返工请使新增只接受当前共享组空槽，保留既有 PUT 编辑合同；验收应覆盖占用槽同名与异名、原字段/版本均保持、真实空槽仍可新增及合法修订冲突。

## 验收检查

| 项 | QA1 独立结果 |
| --- | --- |
| AC01 | 两个正常浏览器路由各自发出对应 module GET。后端定向测试覆盖共享/本地定义、角色、管理写入边界；同一合成字段经计划入口请求后可由实绩 GET 复读。 |
| AC02 | 真实配置路由及前端消费分别通过，浏览器查询、结果及两种语言可用。组件测试验证组合条件、刷新失败保留状态与重试。浏览器 HTTP 层使用合成响应。 |
| AC03 | 25 项合成字段的前端测试及浏览器测试均通过；默认 20，翻页选择 1、21，确认体仅这两项。修订前后刷新、查询重置和切换页大小后的越界收敛通过组件检查。10/100 页大小选项由模板复核。 |
| AC04 | 计划及实绩各在 1440px 中文浅色与 375px 英文深色实测，窄屏收起已有侧栏。页面与弹窗未超视口宽度。桌面两入口各用真实鼠标拖动主表和批量表表头，主表刷新后恢复；批量表重置保留草稿且不干扰主表偏好；主表重置单独清除偏好。帮助聚焦后出现提示。未逐个组合手工遍历键盘操作。 |
| AC05 | **失败**。新增占用槽可覆盖已有字段。其余定向测试覆盖差异 PUT、显式 null、版本语义及无变更；实际界面单项修改只提交对应行标签。 |
| AC06 | 原单删路由仍接受既有请求，HTTP 测试覆盖保护，组件测试覆盖单删确认、两个本地编辑器的分组与草稿。主表和批量表列宽使用不同键。 |
| AC07 | HTTP 定向测试检查 1/2/100 项成功、数量和身份非法、鉴权、修订冲突、404 索引和历史快照数，合同用例对照注册 OpenAPI 与响应。 |
| AC08 | 计划/实绩/历史下发引用、停用、使用证据缺失、配置历史不一致及两种顺序的拒绝通过；GET 无使用写入。浏览器批量拒绝仅定位返回的第二项。全局批量历史错误使用 fields。 |
| AC09 | QA 专属 MySQL 8.4.6、UTC+08:00，配置首锁的真实等待由 performance_schema 证实。计划/实绩创建及更新、保存、单删各与批删交换先后顺序，加上物理提交前故障，13 通过，无测试重试。随机 task002_qa 库由夹具 finally 删除。 |
| AC10 | Chrome 对延迟 350ms 的保存双击注入 503 task.commit_unknown，对删除双击注入连接中断；每入口一轮共两次写入、三次 GET（含首次加载），草稿保留、核对状态出现、重复提交禁用。冲突及拒绝由定向测试覆盖。MySQL 提交前注入后，两个字段均保留且未留下新快照。 |
| AC11 | 见下方命令。本次部分模块套件失败已用剔除候选的独立对照复现。构建及合同检查通过。 |

## 命令、环境与边界

- macOS 正式工作树，backend 锁定环境：`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py`，64 passed，退出 0。
- 专属 QA 参数从私有 test.env 加载，执行相同 pytest 命令针对 `tests_mysql/test_generic_task_shared_batch.py`。默认沙盒回环被拒；允许回环后 13 passed，退出 0。
- frontend-js：`pnpm check:modules` 退出 0，27 条路由；`pnpm test:modules` 93/96 通过，退出 1。对照复制当前前端 src/scripts/tests，单独将候选前端文件恢复为 HEAD 内容（移除 HEAD 无对应文件的候选项），仅在临时副本运行三条失败断言，仍为相同三处 monitor 菜单次序差异：`admin, supervisor, operator and unknown share route/menu/default decisions`、`actual source preserves Core route identity, shell locales and default-disabled demo`、`five adapted modules retain order, owned bilingual titles and current visible leaves`。
- `pnpm build --outDir /private/tmp/task002-qa-dist --emptyOutDir` 退出 0，有已有 chunk 大小提示。以独立构建执行 `node verify.cjs`、`node width.cjs`、`node unknown.cjs`（QA 临时目录，Chrome + Playwright），均退出 0。verify 含断言证实错误覆盖，脚本成功代表成功复现。
- `shasum -a 256 -c` 对交接校验段全部通过；Python 核验校验段 SHA-256 和候选合同/指南的 20 个本地链接，退出 0。`git diff --check` 退出 0。QA 未编辑候选实现。
- QA 自有构建、临时对照、脚本、截图和测试日志可于本轮交接后回收，证据已记录于此。专属 MySQL 进程/私有参数由创建者在全部测试结束后收尾。

请 Development 在 r1 范围内返工并列出新候选摘要，随后启动 fresh-context QA2。Human Owner 最终验收待定。

## 独立验证 QA2

**qa_passed**。ARCH-TASK-002 r1 的 AC05 返工通过，AC01–AC11 的结果由本轮复验及上方 QA1 中可沿用的检查共同支持。下一步由 Human Owner 决定最终验收。

- 正式工作树 HEAD 同 QA1。以 Python 从 tasks.md 两个校验段逐项对照，并重算当前文件及含末尾换行的清单 SHA-256。最新 22 项全部匹配，清单摘要为 `6ce3c9c994f40238359e06e35303650c4cc43fdf1c310dad86a77799e628a52d`。与 QA1 的 22 项相比仅共享页 index.vue、计划和实绩四个 locale 以及 generic-task.test.mjs 变化。复核保存入口在构造 PUT 之前检查完整 shared_sync 组，编辑模式仍可提交原槽位。
- AC05 在 QA2 独立构建上复跑 Chrome。基于任务自有 verify-rework.cjs 通过标准输入切换构建路径、省略截图，追加查询 field9、断言 field5 行消失、保存前后比对全部配置的检查。计划中文浅色 1440px、实绩英文深色 375px 两个正常路由都通过，退出 0。筛选隐藏槽 5 时，新增使用同键 field5 或异键 otherField 均显示槽位提示、零 PUT、草稿保留、夹具全部定义与修订不变。真实空槽 26 提交一次，已有槽单项编辑只发送标签差异，槽 27 遇 409 保留草稿且禁止重复保存。浏览器使用合成 HTTP；停用共享槽和同号本地槽另由组件套件复验。
- AC01–AC04、AC06、AC10 沿用 QA1 对两入口、列宽、权限、删除保护和未知结果的实测。本轮两个浏览器入口同时复验跨页勾选、编辑、取消及批量删除成功/拒绝。前端 `node --test tests/module-registry/generic-task.test.mjs` 13/13，通过。AC07–AC08 及版本语义重跑后端 `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generic_task_flow.py tests/test_generic_task_source.py`，64/64 通过。包含合同 15 个路径的方法集、响应、请求体、安全声明、已发布组件及实际请求示例对照。
- AC09 专属 QA MySQL 8.4.6，初次沙盒回环连接在 setup 失败。放行本机回环后，从任务私有 test.env 加载参数，以相同 pytest 参数执行 `tests_mysql/test_generic_task_shared_batch.py`，13/13 通过，1.55 秒，覆盖两种锁顺序与物理提交前回滚。数据库夹具按测试清理，实例由协调者收尾。
- AC11 在 frontend-js 运行 `pnpm check:modules`，27 条路由通过；`pnpm build --outDir /private/tmp/task002-qa2-dist --emptyOutDir` 退出 0，有 chunk 大小提示。`pnpm test:modules` 94/97 通过，退出 1，三项失败名称与 QA1 的独立基线完全一致。Python 复查 20 个合同/指南本地链接有效，`git diff --check` 退出 0。当前无本任务阻塞。
- 本轮 QA 自有资源为 `/private/tmp/task002-qa2-dist`、`/private/tmp/task002-qa2-build.log`、`/private/tmp/task002-qa2-mod.log`，交接后可由协调者清理。此次写入仅本 checklist。
