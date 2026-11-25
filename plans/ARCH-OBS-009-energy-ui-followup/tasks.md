Task ID: ARCH-OBS-009
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r1 修复 F-001 后已在正式工作树完成自检，交 fresh-context Verification 复验。
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 能耗统计与样本页面跟进 · r1 开发交接

## 实施与交付

依据 [r1 规格](spec.md) 所载 2026-11-24 Human Owner 批准。按 `frontend-ui`、`i18n-workflow`、`code-document-indexer` 实施，保留现有模块结构和文件头风格。

1. 统计空态和曲线 → 隔离验证加载、失败重试、无表计、无指标、待查询、成功空结果及真实零值。
2. 样本筛选与状态 → 隔离验证布局、错误恢复、换页、复核和本机列宽。
3. 工程回归 → 核对双语、原路由和权限、受影响模块测试、构建和正式源码一致性。

| 文件 | 交付 |
| --- | --- |
| [consumption.vue](../../frontend-js/src/app/energy/views/consumption.vue) | 以状态文字取代空坐标轴。只在图组包含可绘制的有限数值时使用共享 `CurveChart`，保留缺测点和成功返回的统计汇总。分辨表计、指标、样本加载和失败，过时请求不回写当前视图。 |
| [EnergyAdmin.vue](../../frontend-js/src/app/energy/components/EnergyAdmin.vue) | 样本筛选项采用 200 CSS px 的弹性基准宽度，查询、重置与输入底边对齐，窄屏可以换行。无表计、读取失败和已查询的空列表分别呈现，读取失败可按已提交条件重试。沿用样本详情、复核和列宽键。 |
| [中文语言](../../frontend-js/src/app/energy/locales/zh-CN.json) · [英文语言](../../frontend-js/src/app/energy/locales/en-US.json) | 增加待查询与样本空结果文案，沿用能耗和全局已有文案。 |
| [受影响模块测试](../../frontend-js/tests/module-registry/equipment-observation-columns.test.mjs) | 补充无可绘制曲线时保留统计汇总、图组零值和缺测保留，以及离页后迟到汇总无效的断言。 |

首次浏览器检查发现全局桌面布局的 `1280px` 最小宽度会在 1024×768 隐藏样本筛选按钮。两处能耗页面按自身选择器解除该限制。在 600px 或更窄时沿用现有过程曲线的导航叠放方式。共享壳层、过程曲线相关源码、能源单价和后端未修改。本次没有源码结构变化。

交付在正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，基准 HEAD `7f654acd951171767bc253ea5bebdcda6435b608`，包含本表五个授权文件的工作树改动。已有未提交的能耗迁移及其他任务改动原样保留。四个构建输入文件逐字节核对与正式源码一致。含正式五个文件的 SHA-256 清单在 `/private/tmp/arch-obs009-dev.iykQ9e/source-sha256.txt`，清单摘要 `f6e3921571f99f240076835308cae7f38f6b3645a168a67e483de0cf9516ca7c`。

## Development 自检

2026-11-24（上海），macOS、Node 22.19.0、pnpm 11.11.0。浏览器使用本机 Chrome 和隔离构建，临时服务器仅监听随机回环端口，浏览器合成 API 并阻断外部源。合成页使用正式请求层发送测试 Bearer。

| 验收 | 命令、结果与证据 |
| --- | --- |
| AC01–AC03 | `node /private/tmp/arch-obs009-dev.iykQ9e/browser.cjs` 退出 0。Chrome 验证选项加载、无可访问表计、选项失败重试后无指标、需要时间、待查询、样本为空或值缺测、失败后重试、`0 kWh` 与一条可绘制图组。检查空态没有图框，成功空结果仍保留服务端完整性原因。样本页验证无表计无表格、选项失败恢复至有效空表、样本读取失败恢复至记录。 |
| AC04、AC07 | 同一 Chrome 命令通过 1440×900、1024×768、600×800 各浅色zh-CN和深色en-US组合。核对表计、采样组、查询和重置在屏内及底对齐，桌面和平板筛选项宽度为 200 CSS px。另检查样本换页、重置、实际拖动和重载后恢复列宽、遮罩关闭无写入、备注与复核产生准确 PATCH，及配置管理仍取现有接口。样本/配置弹窗未改动。 |
| AC05、AC06 | 同一 Chrome 命令验证普通操作员被拒绝进入管理员样本路由、未登录跳登录页、原统计页地址有效、现有接口携带 Bearer，提交上海时间 `+08:00`，切换表计后旧响应不恢复图表。执行 `pnpm --dir frontend-js exec node --test tests/module-registry/equipment-observation-columns.test.mjs` 退出 0，24 项通过，覆盖时间和请求竞态、离页、有效零值、过程曲线与样本/配置既有逻辑。 |
| AC06 工程 | `pnpm --dir frontend-js check:modules` 退出 0（32 路由／10 菜单组）。`git diff --check` 退出 0。全量 `pnpm --dir frontend-js test:modules` 退出 1，117 通过、2 失败。开工基线为 115 通过、相同的 2 项失败，分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 和 `actual source preserves Core route identity, shell locales and default-disabled demo`，均为维保与系统的排序断言。 |
| AC06 构建 | 用 `rsync -a --exclude node_modules --exclude dist --exclude '.env*' frontend-js/ /private/tmp/arch-obs009-dev.iykQ9e/frontend/` 准备源码，链接既有项目 node_modules。执行 `pnpm_config_verify_deps_before_run=false VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='["monitor.energy"]' VITE_OPERATOR_PAGE_ACCESS_JSON='["monitor.energy"]' pnpm --dir /private/tmp/arch-obs009-dev.iykQ9e/frontend build` 退出 0，仅报告原有包体积警告。首次构建探测因临时依赖链接触发 pnpm 启动依赖核验失败，复用项目已安装依赖后通过，未安装新软件包。 |

自检中默认沙箱拒绝本地监听，获得审批后同一浏览器脚本在合成数据条件下通过。未调用真实后端、数据库、设备，未执行部署、迁移或后端服务切换。

## 临时资源与交接限制

浏览器和回环服务已退出。保留 `/private/tmp/arch-obs009-dev.iykQ9e/` 内隔离源码副本、构建、`browser.cjs`、日志和摘要供独立 Verification。验证证据落盘且无返工依赖后由协调者回收。未创建分支、worktree 或写入应用的环境配置。

## F-001 修复与再次交接

2026-11-24（上海），依据 [F-001](checklist.md#最终验收前补充复核--f-001) 在 r1 §2.2 内修复。[EnergyAdmin.vue](../../frontend-js/src/app/energy/components/EnergyAdmin.vue) 的 `.sample-toolbar` 增加 `padding-block-end: var(--space-md)`，与过程样本工具栏一样在分隔线上方留 16 CSS px。分隔线后的 16px 保留。实际差异仅为这一行样式及本交接记录。

| 自检 | 本轮结果 |
| --- | --- |
| AC04、AC07 浏览器 | `node /private/tmp/obs009-f001-dev.uAa1jQ/browser.cjs` 退出 0。隔离构建的实际能耗样本页、过程样本页、能耗配置页在 1440×900、1024×768、600×800 上分别通过中文浅色及英文深色检查。能耗及过程样本页的最末控件底边距分隔线均为 16 CSS px。测试暂时撤销样本页内间距时再现 0px。PC 及平板两项输入维持 200 CSS px、查询／重置与输入底对齐。600px 时工具栏换行，按钮互相底对齐且所有控件完整可达。样本页标题、首控件与列表左边缘一致。能耗配置页读取合成配置表，工具栏底部内间距仍为 0px。 |
| AC06 构建与工程 | `pnpm_config_verify_deps_before_run=false VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='["monitor.energy"]' VITE_OPERATOR_PAGE_ACCESS_JSON='["monitor.energy"]' pnpm --dir /private/tmp/obs009-f001-dev.uAa1jQ/frontend build` 退出 0，仍有原包体积警告。临时副本用 `rsync -a --exclude node_modules --exclude dist --exclude '.env*' frontend-js/ /private/tmp/obs009-f001-dev.uAa1jQ/frontend/` 准备并链接已有 node_modules。前一次构建因遗漏合成测试角色的显式页面授权配置失败。能耗样本源码与正式版本逐字节相同。正式目录的 `pnpm --dir frontend-js check:modules`、`pnpm --dir frontend-js exec node --test tests/module-registry/equipment-observation-columns.test.mjs`（24 项通过）及 `git diff --check` 均退出 0。 |

正式候选 HEAD `7f654acd951171767bc253ea5bebdcda6435b608` 加本任务工作树改动，`EnergyAdmin.vue` 的 SHA-256 为 `69eb858211ec885590a17b1d9283b79152c9e45461d0204e515b0429e35bcbe4`。本轮五项源码及测试清单为 `/private/tmp/obs009-f001-dev.uAa1jQ/source-sha256.txt`，清单 SHA-256 为 `1493f15df84a3feec1314fd972640c9ab67fc738b62bda6de0664b6b9700640e`。全量模块沿用首轮自检记录。本轮只用本机随机回环端口和合成的只读 API，浏览器阻断外部请求及写操作。未接触用户的运行服务、真实后端、数据库和设备。

上一轮临时目录已回收。本轮 Chrome 及回环服务已退出，保留 `/private/tmp/obs009-f001-dev.uAa1jQ/` 内隔离构建、只读夹具、日志、两张 PC 截图及摘要供 Verification 复验和核对。独立结果落盘且无返工依赖后由协调者回收。
