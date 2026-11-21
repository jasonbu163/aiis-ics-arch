Task ID: ARCH-OBS-004
Revision: r1
Status: qa_passed
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: 正式源码交付核对通过，交 Human Owner 启动服务并最终验收。

# 第一轮隔离候选独立验证（qa_failed）

2026-11-20，macOS，fresh-context Verification。候选目录为 `/private/tmp/arch-obs-004-candidate.BnilRdCD`。独立计算 spec、tasks、补丁 SHA-256，分别为 `d7aeb782a7b578f62d200da4aebeacb412d43c3bea58072768c58ab1f8978971`、`18cfda32ae7bd237fc5469b529c4e4908609d94fb5b4abf469289be4e8087c61`、`5bd115b117456cbfea940eadd2d81b4ae4ba618107b3034d2b9e462c62542323`。对 source-manifest.json 所列 14 个候选文件逐一重算，均一致。

| 验收项 | 独立结果 |
| --- | --- |
| AC01 | **失败**。默认中文、390×844、真实 Chrome、打开设备页切到槽位。两个卡片边界均为 x=248..378、宽 130px。「重置列宽」边界 x=346.73..440.19，越过卡片与视口，BaseCard 的 overflow 为 hidden。查询、重置仍可点击。转入过程页，曲线行正常加载；普通指针点击「表计指标配置」重试 30 秒超时。Playwright 命中顶栏 user-info 或 header-utility-capsule 拦截。未强制点击，窄屏表计筛选未能到达。 |
| AC02 | 1260×900 桌面真实浏览器通过槽位默认全量、英文名称查询、重置和表计默认全量、组查询、重置。六类穷举交互待修复后补验。 |
| AC03、AC04 | 隔离后端 HTTP 套件全部通过，含新增的槽位可选条件及表计授权范围用例；桌面编辑 meterB 命中准确 PATCH 路径 /energy/metric-configs/meterB/electricity/energyInterval。 |
| AC05 | 模块自动回归全部通过，含查询乱序及共享能耗组件既有行为。桌面保存回执关闭对应弹窗。 |
| AC06 | 源码和模块回归包含公共列宽及首次使用时间路径。设备重置列宽按钮在窄屏被裁切，六表逐项拖动及明暗、英文外观尚未完整实测。 |
| AC07 | 候选源码核对、双语手册本地链接、隔离 HTTP、前端回归、模块检查和生产构建通过。正式整合及一致性尚待后续交接。 |

## 命令和环境

- 候选 backend 使用正式树锁定 .venv，执行 `UV_NO_CACHE=1 UV_PROJECT_ENVIRONMENT=/Users/jason/Desktop/DreamCode/aiis-ics-arch/backend/.venv uv run --no-sync --offline python -m pytest -q -p no:cacheprovider tests/test_equipment_observation_r10_flow.py`，退出 0，22 passed，1 条 SQLite datetime 弃用提示。使用内存合成 HTTP fixture。
- 候选 frontend-js 设置 VITE_SUPERVISOR_PAGE_ACCESS_JSON、VITE_OPERATOR_PAGE_ACCESS_JSON 均为 []，执行 `pnpm --config.verify-deps-before-run=false run test:modules`，93 passed；增加 VITE_API_BASE_URL=/api/v1 后执行 `pnpm --config.verify-deps-before-run=false run build`，模块检查及 Vite 构建完成，有大包提示。
- 候选根执行 `node browser-smoke.cjs`，桌面退出 0。该脚本使用离线静态构建、合成管理员、两个表计、三条槽位和本地路由拦截。独立第二次运行从 stdin 载入同一脚本，将 viewport 从 1260×900 换为 390×844，采集卡片及操作按钮 getBoundingClientRect 后继续原交互，退出 1，复现 AC01。
- 未访问正式运行服务、设备或真实数据库。此轮失败返回 Development。正式源码整合、后续独立复验及 Human Owner 最终验收待办。

## 第二轮独立验证 · r1 rework1

2026-11-20，macOS，新的 Verification 上下文。正式交付状态为 `qa_blocked`。本轮针对原 AC01 的两个失败及对应 AC06 操作，隔离候选复验通过。

- `shasum -a 256` 核对规格与第一轮一致。tasks 为 `e8788f7142904f8fe5a5dbac7bf2e1f17495e55b00ff8f9cff116e902f405afb`，返工补丁为 `c5b692af7786f1fbf756fd00fe4ffecb2fa57b83ec866a295ca5f32774c9335f`，清单为 `66fe758bbc73e445e07b0591508233c4ec200e11ee5dcacb89dd65481f03465b`。Python hashlib 逐项核对正式树 14 个基线、隔离树 14 个候选文件。`git apply --check` 成功。两次补丁的差异仅为设备和过程配置页 scoped CSS。
- 在候选根执行 `node browser-narrow.cjs`、`node browser-smoke.cjs`。默认沙箱启动 Chrome 收到 SIGABRT，工具批准独立 Chrome 进程后两项均退出 0。静态候选资源及合成 HTTP 请求由 Playwright 路由拦截，浏览器未访问正式服务。
- 390×844，展开侧栏，槽位、曲线及表计配置的「重置列宽」均可普通点击。按钮 x=257..350.45 完全落在卡片 x=248..378 内。过程页顶栏底 y=290，类别控件 y=379..443。点击「表计指标配置」进入表格。折叠侧栏后额外顶距归零，按钮仍能点击。桌面 1260×900 同样通过两页的默认全量、槽位英文关键词、表计组查询、重置及 meterB 精确 PATCH 检查。
- 候选 frontend-js 设置两项角色页面权限变量为 []，运行 `pnpm --config.verify-deps-before-run=false run test:modules`，93 项通过、0 失败。AC03、AC04 后端、AC05 行为和手册沿用第一轮同字节候选证据。六表逐列拖动、六类所有筛选组合以及英文和深色外观未在此次真实浏览器脚本中穷举。
- Human Owner 确认允许正式前后端热重载后，由协调者安排源码整合，再核对正式工作树与本轮候选清单及实际入口。正式运行验收与最终接受仍待 Human Owner。本轮仅更新本 checklist。

### AC06 代表场景补验

在同一静态构建的 1260×900 合成 Chrome 页面，通过 Node stdin 载入 desktop smoke fixture 并插入 Playwright 鼠标操作。首次拖动没有激活表头缩放，未生成偏好；随后将「写入目标」表头滚入视野，悬停至边界，确认真实光标为 col-resize 后拖动。实测列宽 120 → 185px，存储键 `aiis-ics-architecture:table-widths:observation.slots` 的 target=185。浏览器整页刷新后重新选择槽位，实测 185px；点击「重置列宽」后恢复 120px。点击顶栏语言按钮后两张卡片实际显示 “Metrics and snapshots” 和 “Slots”；点击主题按钮后页面 data-theme 从 light 变为 dark，随后切回中文与亮色，继续原有查询与编辑通过。补验退出 0。该场景覆盖槽位表的真实拖拽、重载恢复、重置以及语言和主题切换；其余五表的逐列拖动及多主题视觉细节仍以源码/公共组件证据和上述限制为准。

## 第三轮独立验证 · 正式源码交付

2026-11-20，macOS，fresh-context Verification。Human Owner 已授权合入；正式工作树 HEAD 为 `cc9ebd7bdc7b17f6a7774e7f653723c38edeaf81`，交付为该树的未提交修改。`lsof -nP -iTCP:8000 -iTCP:5190 -sTCP:LISTEN` 无输出，退出 1。本轮未启动服务或连接真实数据库。

- 以 Python hashlib 独立重算交接 tasks、返工清单及补丁 SHA-256，分别为 `6197b79daca31c9f81162340e4649d0a59f22b1fc7a8d9e679f62d54a2142b5c`、`66fe758bbc73e445e07b0591508233c4ec200e11ee5dcacb89dd65481f03465b`、`c5b692af7786f1fbf756fd00fe4ffecb2fa57b83ec866a295ca5f32774c9335f`。14 个不同路径的正式文件、隔离候选文件和清单候选摘要逐一相符。`git apply --reverse --check` 对返工补丁退出 0，`git diff --check` 对清单 14 项退出 0。
- 正式设备和过程模块 manifest 将原有可见管理员菜单分别指向 `equipment/observations/admin`、`monitor/observations/admin`，并加载清单内的两个 admin.vue。后端两个 GET 的签名均保留管理员依赖，槽位 target / groupKey 可选并执行目标检查，表计 meterId / groupKey 可选，显式表计执行 allowed_meter，省略时取角色 meterReadScopes。
- **结论为 qa_passed**。正式源码与前两轮已验证的返工候选一致，原窄屏问题和交付阻塞均已关闭。AC01–AC07 的行为依据及覆盖限制见前两轮，本轮仅核对交付。正式服务联机行为与当前账号实际可见数据尚待 Human Owner 启动 8000、5190 后，通过两个配置管理菜单自行验收。Human Owner 最终决定待记录。
- 本次核对所需的摘要、路径、检查命令和结果均已留存在任务 bundle。协调者确认没有其他进程或任务占用后，可回收本任务专用候选目录。
