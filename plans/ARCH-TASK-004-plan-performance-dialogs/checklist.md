Task ID: ARCH-TASK-004
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Workflow Mode: STD
Execution Mode: agent_team_same_session
Handoff: Human Owner 已完成精确 r1 最终验收
Updated: 2026-11-23 Asia/Shanghai

# 独立验证 QA1

精确 r1 通过独立 QA，提交 Human Owner 最终验收。八个候选文件在测试前后与 Development 交付清单逐字节匹配。正式工作树全量模块测试有三项失败，另在干净 HEAD 快照复现了相同的三项 monitor 菜单顺序断言。未发现 r1 阻断项。

## 候选与审计

独立上下文在 developer_handoff 后读取项目契约、前端 README/PLAN、任务两份文档、实现、差异及开发证据。正式源码位于 /Users/jason/Desktop/DreamCode/aiis-ics-arch，main 基线 ee942c8b82cf5b3e502872d8d6ee5c7820b2314e。批准规格 SHA-256 为 6a26a2d58ef7359307fb1c1d01996a96e7b19964addce3422dd85542aef07863，Development 记录为 db7743342f6f30c7d4184eb854b02391117b51be412386f4f7cfbe29d71d3be9，八文件清单为 24965760b7fda3c11818bf50315d2c5249d7aede85b864da700c92970b0e00fa。清单逐项 SHA 见 [开发交付](tasks.md)。

TaskPage 模板差异从列表之后的弹窗开始。四条字段管理路径共用的单项布局由 editMode/deleteMode 限定。对照 HEAD，列表操作列仍为原始详情按钮，批量编辑器和批量动作请求沿用原处理。工作树包含开工前已有的 equipment、monitor、theme.css 和项目文档改动；此次交付八文件均在批准范围。QA 只写本 checklist。

## 对照批准规格的结果

| 编号 | 独立观察 |
| --- | --- |
| AC01 | 两模块的 deferred 专项覆盖 A 记录或必要配置慢、成功及失败；B 的记录、字段、按钮和 loading 保持一致。Chrome 检查最新记录 404 只显示错误及重试，重试成功恢复编辑入口。 |
| AC02 | 专项控制旧实绩计划配置最后成功及失败，覆盖新实绩已有计划、可补建、计划配置失败及角色或页面访问不足；当前实绩仍可读，补建入口随本次配置和权限开放。 |
| AC03 | 专项覆盖关闭、卸载和双向切换。Chrome 在真实 Escape 离场动画期间重新打开 B；补充夹具又使用实际 Vue Router 离开列表、在新建计划读配置时打开详情、详情未完成时切到新建计划。旧响应分别返回 200 与 422，均保持新界面且无过期提示。 |
| AC04 | 两模块专项覆盖 A 保存后离开、切 B、B 已开始保存、重复点击和当前草稿保留。Chrome 额外将旧保存的 200 或 422 延后到 B 打开，B 均可编辑，无 A 提示。当前有效保存关闭刷新，取消为零写入。 |
| AC05 | 按四类角色运行真实组件 setup 并核对提交体，检查已有目标锁定、空目标、人工/自动字段、nullable、数值零与布尔 false、补建条件及默认回填关闭。Chrome 两模块保存仅发送当前 taskNo 和已改备注。 |
| AC06 | Chrome 检查每个模块的三段内容、实际配置产生的动态项、备注、0、false、缺失和上海业务时间。通过中英文、两种主题、1280×730 与 375×590 的交叉组合，检查标题 16px/590、正文局部滚动、窄屏边界、按钮间距、Tab/Shift-Tab 与返回触发点；编辑、取消以及实绩补建正常。 |
| AC07 | 四个管理入口各在四组浏览器环境走新增、编辑、删除，共 48 次单项场景。共享显示两侧设置，本地仅本侧；已保存定义的标识控件禁用。检查真实目标、外部引用提示、删除拒绝及各 scope 的新增和标签差量，结合专项复核槽位占用、设置联动和清空值。 |
| AC08 | 补充 Chrome 对实绩本地单项编辑和删除各测试权限拒绝、校验拒绝、修订冲突、commit_unknown、连接中断。每次连点两次只捕获一次写入。草稿或目标保留，未知结果显示权威重读后的现状并禁止直接重发。专项覆盖跨页选择和批量请求/保护，四条浏览器路径均实测批量弹窗未应用单项样式。 |
| AC09 | 已从交付树独立执行以下命令，构建与开发最终构建的目录内容一致。任务 Markdown 相对路径及锚点、双语 dialog 键、候选清单和 diff 已核对。 |

## 执行记录

环境为 Darwin arm64、Node v22.19.0、pnpm 11.11.0、Google Chrome 157.0.8103.79。本次浏览器通过临时 Chrome profile 和 Playwright 管道运行，静态资源取自 QA 构建，全部应用网络请求由合成夹具处理。实际业务数据库、认证服务、后端写入及设备不在证据范围。已发出的写请求仍可能在服务端生效。

| 目录和命令 | 实际结果 |
| --- | --- |
| frontend-js · pnpm exec node --test tests/module-registry/generic-task.test.mjs | 22/22，退出 0 |
| frontend-js · pnpm check:modules | 29 路由，9 组，退出 0 |
| frontend-js · pnpm test:modules | 103/106，退出 1 |
| frontend-js · pnpm build --outDir /private/tmp/arch-task004-qa/final-dist --emptyOutDir | 退出 0，Vite 提示部分 chunk 大于 500 kB |
| HEAD 的 frontend-js 临时快照 · pnpm --config.verify-deps-before-run=false test:modules | 96/99，退出 1。同名三项失败如下。首次直接运行 pnpm 因临时目录依赖校验退出 1；复跑沿用现有依赖并成功执行测试。 |
| node /private/tmp/arch-task004-qa/browser.mjs | 退出 0。独立构建上复跑开发浏览器场景，8 个详情、48 个单项、20 个合成写请求、7 张截图、0 个页面异常。沙盒内启动 Chrome 曾因 SIGABRT 退出 1，获批后完成。 |
| node /private/tmp/arch-task004-qa/lifecycle.mjs | 退出 0。QA 补充实际路由/新建双向切换/旧保存，各测延迟成功和失败，共 8 种。 |
| node /private/tmp/arch-task004-qa/faults.mjs | 退出 0。独立补充单项字段写入故障 10 种。初次将删除核对区定位为编辑核对区而超时，改为查找真实删除目标的当前存在提示后全数通过。 |
| 根目录 · git diff --check、shasum -a 256 -c、diff -qr 两份最终构建 | 均通过，八项文件散列相同，构建内容一致。 |

两次全量失败均为以下既有断言，本次新增七项全部通过。

- admin, supervisor, operator and unknown share route/menu/default decisions
- actual source preserves Core route identity, shell locales and default-disabled demo
- five adapted modules retain order, owned bilingual titles and current visible leaves

QA 临时目录 /private/tmp/arch-task004-qa/ 包含独立构建、三个浏览器夹具、截图、测试输出及 HEAD 基线副本。专用 Chrome 随测试结束关闭。临时材料交协调端在最终验收取证结束后统一回收；任务结论保存在本记录。下一步由 Human Owner 审阅精确 r1。

## Human Owner 最终验收 · ARCH-TASK-004 r1

2026-11-23（Asia/Shanghai），Human Owner 明确确认「ARCH-TASK-004 r1 最终验收通过」。Verification 依据该决定登记为 `owner_accepted`。以下为 Human Owner 在开发环境手动操作并确认的结果。

| 场景 | 人工验证结果 |
| --- | --- |
| 补建计划，未勾选回填 | 对 `QA-SUPPLEMENT-20261123-A01`，操作前计划及实绩详情 GET 均返回 404。集成 POST 返回 200，创建的实绩为 `hasPlan=false`。Human Owner 从实绩详情补建计划，未勾选回填。随后计划详情显示同一任务号、产品 `QA-PRODUCT-A01`、目标长度 100 m；实绩显示「有计划」，补建按钮消失。 |
| 补建时一次性回填 82.5 m | 对 `QA-BACKFILL-20261123-A01`，集成 POST 返回 200，已启用回写的共享字段 `completedLength` 值为 82.5。补建前实绩为 `hasPlan=false`，`planSync` 显示 `skipped/no_plan`。Human Owner 悬停问号查看说明，勾选一次性回填并保存。随后同号计划详情显示「已生产长度」82.5 m，实绩已关联计划，补建按钮消失。 |

问号悬停提示和后续列表操作按钮拆分及样式调整均属另行授权的 DIRECT 改动；上表的问号观察作为补充手验记录。QA1 的命令、散列及候选一致性结论仅对应当时的开发交付。最终验收时累计工作树的八个历史清单文件中有七个与该候选不同，包含后续 DIRECT 及其他编辑。本次登记沿用上文的独立验证证据及 Human Owner 的操作记录，未重新运行测试、修改实现或操作测试数据。
