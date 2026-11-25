Task ID: ARCH-OBS-009
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification, Human Owner
Handoff: Human Owner 已最终验收 ARCH-OBS-009 r1
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 首轮独立验证记录（当时结论 qa_passed）

2026-11-24（上海），fresh-context Verification 独立复核 [批准规格](spec.md) 和 [Development 交接](tasks.md)。正式源码工作树 HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`，候选身份同时包含下列未提交源码。核对了根项目契约、前端及任务目录文档、workflow、角色合同和交接边界。macOS，Node 22.19.0，pnpm 11.11.0，本机 Chrome。

| 正式候选（frontend-js 相对路径） | SHA-256 |
| --- | --- |
| src/app/energy/views/consumption.vue | 02cfa4787af02ef2f8ca304b2584289d8fdc5e1418c8222b85833873feb3dcad |
| src/app/energy/components/EnergyAdmin.vue | 8ca7b8f03a30daf41e40c2665ae5103c0cb0d9a8e3ba647c68a2ab8b1c53c46e |
| src/app/energy/locales/zh-CN.json | 9376489f6843b608351cca2f1d3804ca6ed989544f46546093ae35f93f279b29 |
| src/app/energy/locales/en-US.json | a6d5934fb8384ba3943317276399e0f44e3b757da8a5a311554edec73db057c8 |
| tests/module-registry/equipment-observation-columns.test.mjs | 077625036079dc7f6a0a7c187548a9c661579451fd4a8467ffd918940949b071 |

`shasum -a 256 -c` 对交接清单五项全部通过。独立隔离副本五项一致。Development 旧副本的四项构建输入一致，内含测试文件早于正式交接，其差异包括缺少离页测试。本轮测试从正式候选及其独立副本执行。

| 标准 | 独立验证结果 |
| --- | --- |
| AC01 统计空态 | 浏览器拦截实际请求，分别返回延迟、成功空选项、空指标、HTTP 503、有效空样本及全缺测。无时间、选定时间待查询和成功无曲线可区分。空态无曲线容器、图面及 EmptyAxes。读取失败可重试。 |
| AC02 有值与汇总 | 真实组件和时间输入生成带 +08:00 的范围。合成读数 0 可画，汇总显示 0 kWh；缺测样本和空样本显示无数据，同时保留后端不完整状态及边界读数缺失原因。严格递增时间校验、真实采样时间、微秒顺序、同刻样本及缺测断点由组件测试覆盖。恢复默认清除范围。 |
| AC03 样本状态 | 空选项显示联系管理员，零条样本显示独立空查询提示。选项及样本请求 503 后均隐藏旧表并允许重试，重试分别恢复空结果或新记录。延迟配置、切换表计／组／页的测试通过。 |
| AC04 筛选与列表 | 四组 PC／平板浏览器检查通过，筛选项宽度落在 180–240 CSS px 且按钮与输入底对齐。详情遮罩取消没有 PATCH，保存生成精确的 remark、reviewMark；换页、重置、拖动表头、重载列宽与仅清除样本键通过。配置页通过现有接口读取；配置查询、编辑目标、保存和列显隐顺序由组件测试覆盖。 |
| AC05 权限与共享组件 | 双语各 129 个叶键一致。管理员进入样本页，操作员跳转获准统计页，匿名跳登录。检查请求带测试 Bearer，原路由名 MonitorEnergy、pageId monitor.energy、管理员 meta 与后端 energy_reader / get_current_active_admin 依赖一致。温度、传动、清洗共用过程组件。正式温度测试以及临时以 drive、cleaning 各自分类参数运行的同组件时间查询夹具通过；共享图表的数值、零值、缺测及图例由 Vue/ECharts 测试覆盖。 |
| AC06 异步与工程 | 在途查询切换表计、范围、组／页和离页后，迟到结果或失败未覆盖新结果。独立时间夹具先提交第二个时间的 0，再释放首个时间的 123，最终仍为 0。命令与基线见下。 |
| AC07 浏览器 | 实际 Chrome 于 1440×900、1024×768 分别完成中文浅色、英文深色整套统计与样本流程，包括无数据后恢复、翻页、详情、备注复核和列宽。600×800 两组语言／主题确认控件边界、样本状态与查询／重试可达。弹窗沿用原组件。 |

## 主要命令与结果

- `pnpm --dir frontend-js check:modules` 退出 0，32 路由、10 菜单组。
- `pnpm --dir frontend-js exec node --test tests/module-registry/equipment-observation-columns.test.mjs` 通过 24/24。独立副本的 drive、cleaning 分类补充测试通过 8/8，时间乱序补充测试通过 1/1。
- `pnpm --dir frontend-js test:modules` 退出 1，117 通过、2 失败。与协调者运行前的 115 通过、2 失败逐项核对。page-access 的 “admin, supervisor, operator and unknown share route/menu/default decisions” 及 registry 的 “actual source preserves Core route identity, shell locales and default-disabled demo” 均为 maintenance 与 system 预期顺序差异。
- 独立复制正式前端（排除 .env、node_modules、dist），链接项目已安装依赖，设置 VITE_API_BASE_URL=/api/v1、关闭 mock、操作员及主管仅启用 monitor.energy，禁用 pnpm 启动时依赖重核。`pnpm --dir /private/tmp/obs009-qa.uFxGPM/frontend build` 成功，保留既有 chunk 体积警告。`git diff --check` 退出 0。
- `node /private/tmp/obs009-qa.uFxGPM/browser.cjs` 使用上述独立构建、随机回环端口与合成 API，通过全部六组基本场景及四组完整流程，退出 0。首次沙箱监听 EPERM，经批准运行。扩展英文流程时更正夹具中缺测原因、列宽按钮的预期英文后通过。所有浏览器 PATCH 均由夹具接收。
- 本轮无实现阻塞。证据覆盖合成前端交互与源码合同；真实业务数据、数据库、部署或设备运行均不在本次范围内。交 Human Owner 最终验收。

## 临时资源

Chrome 及回环服务已经退出。QA 自有隔离副本、构建、夹具、日志位于 `/private/tmp/obs009-qa.uFxGPM`，供协调者核对本次交接后与 Development 目录 `/private/tmp/arch-obs009-dev.iykQ9e` 和基线目录 `/private/tmp/aiis-obs009-coordinator.zXplBu` 一并回收。关键摘要、命令与结果已持久化于本记录。

## 最终验收前补充复核 · F-001

2026-11-24，Human Owner 在最终验收前指出能耗样本页筛选控件紧贴列表分隔线。复核其 22:26 截图，表计、采样组、查询及重置的底边均贴着横线，横线下方才出现留白。

- 源码依据：[能耗样本工具栏](../../frontend-js/src/app/energy/components/EnergyAdmin.vue)使用 `config-toolbar sample-toolbar`，其边框内只设水平 padding，16px 的底部 margin 位于边框外。[过程样本工具栏](../../frontend-js/src/app/equipment/components/observations/RecordList.vue)在分隔线上方另设 16 CSS px 底部 padding。
- 判定：r1 §2.2、AC04 的过程样本工具栏视觉对齐未满足。首轮 AC07 检查了控件互相底对齐和可达性，漏检控件至分隔线的距离。保留首轮运行事实，当前候选结论更新为 **qa_failed**。
- 交接：退回 Development 在样本筛选区修正底部留白。重新交接后，fresh Verification 应在 PC、平板及窄屏核对末行控件到分隔线的实际间距、换行与按钮底对齐，并复核配置页。
- 本次只检查 Owner 截图和两处正式源码，更新本 checklist。无新增临时资源。

## F-001 修复后独立复验

2026-11-24（上海），fresh-context Verification 复核同一 r1 的 Development 再次交接。正式 HEAD 与首轮一致。运行 `shasum -a 256 -c`，正式源码及隔离构建源码各五项全部匹配交接清单，清单 SHA-256 为 `1493f15df84a3feec1314fd972640c9ab67fc738b62bda6de0664b6b9700640e`。对照首轮摘要匹配的 EnergyAdmin.before.vue 执行 `diff -u`，唯一新增行为是样本工具栏的 `padding-block-end: var(--space-md)`。当前 EnergyAdmin.vue SHA-256 为 `69eb858211ec885590a17b1d9283b79152c9e45461d0204e515b0429e35bcbe4`，其余四项沿用首轮摘要。

在 macOS 本机 Chrome 独立运行 `node /private/tmp/obs009-f001-dev.uAa1jQ/browser.cjs`。首次随机回环端口监听返回 EPERM，获批后退出 0。下列数据均为本轮 DOM 实测，单位 CSS px。间距从末行控件底边量到 1px 分隔线内缘，每个尺寸均验证中文浅色、英文深色。

| 视口 | 能耗／过程间距 | 首个输入／末个按钮底边 Y | AC04、AC07 |
| --- | --- | --- | --- |
| 1440×900 | 16／16 | 243／243 | 两项输入均宽 200，四控件底边对齐 |
| 1024×768 | 16／16 | 243／243 | 两项输入均宽 200，四控件底边对齐 |
| 600×800 | 16／16 | 433／477 | 按钮换行，查询与重置底边对齐，四控件均在视口内 |

六组均验证标题、首控件和列表左边缘对齐，临时撤销底部 padding 可复现原间距 0。配置分支成功读取合成配置项，其工具栏底部 padding 仍为 0。正式源码执行 `pnpm --dir frontend-js exec node --test tests/module-registry/equipment-observation-columns.test.mjs` 通过 24/24，`git diff --check` 退出 0。其余 r1 验收项沿用首轮记录，包括全量模块测试两项既有失败。

**qa_passed**。F-001 已关闭，交 Human Owner 最终验收。浏览器验证使用隔离构建与合成只读 API。Chrome 和回环服务已退出。QA 无新增临时目录；复验覆盖写入 Development 目录中的两张合成截图。证据已落盘，协调者可回收 `/private/tmp/obs009-f001-dev.uAa1jQ/`。

## Human Owner 最终验收

2026-11-24（Asia/Shanghai），Human Owner 明确表示：“验收 ARCH-OBS-009 r1。”据此记录最终状态为 **owner_accepted**。

协调者已确认回收 F-001 的 Development 和协调临时资源，包括 `/private/tmp/obs009-f001-dev.uAa1jQ/`。本次记录无新增临时资源。
