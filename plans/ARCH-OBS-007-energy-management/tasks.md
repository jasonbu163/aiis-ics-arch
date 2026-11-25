Task ID: ARCH-OBS-007
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: r1 A 第一次返工完成，交新的独立 Verification；B 待合同及批准
Workflow Mode: STD
Execution Mode: agent_team_same_session

# 能耗管理页面归并 · r1 A 开发交接

## 批准范围与执行计划

依据 [r1 规格](spec.md) 所载 Human Owner 2026-11-24 的精确批准，只实施 §3、§4、§7.1、§8.1 的 A。使用具名 Development 角色与项目 `development.toml` 约定。工作分三步完成。

1. 迁移能耗菜单和四页，验证旧路径、路由名、pageId 及权限。
2. 复用统计、单价、表计指标和样本逻辑，验证浏览器数据交互、布局和进出页行为。
3. 核对中英文、源码一致性和受影响文档，完成模块测试、构建及隔离浏览器自检。

## 实施范围

| 面 | 交付内容 |
| --- | --- |
| 入口与菜单 | [能耗 manifest](../../frontend-js/src/app/energy/manifest.js) 按「能耗统计／能耗单价／数据管理／配置管理」装配。既有 `/monitor/consumption`、`MonitorEnergy`、`monitor.energy` 与 `/auxiliary/price`、`AuxiliaryPrice`、`auxiliary.price` 原样提供。新管理地址为 `/energy/observations/data` 和 `/energy/observations/admin`，两页均需 admin。 |
| 统计 | [三段式统计页](../../frontend-js/src/app/energy/views/consumption.vue) 复用过程曲线与现有 API。卡头刷新，工具区查询和恢复默认，结果区使用接口单位、最新读数、用量和状态。上海时段须填写完整有效区间。保留真实零、缺测空值、旧响应作废及请求错误反馈。 |
| 单价 | [单价页](../../frontend-js/src/app/energy/views/price.vue) 在同一内容宽度放三张等宽价格卡和独立历史卡。保留现有辅助 API facade 与 mock 模式，浏览器隔离验证关闭 mock。原整组小时写入、价/备注精度、上海自然日与报文逻辑复用。历史表增加公共列宽偏好及重置。 |
| 样本与配置 | [EnergyAdmin](../../frontend-js/src/app/energy/components/EnergyAdmin.vue) 保留既有表计/组、配置字段、分页、列顺序与样本复核；沿用 `observation.energy.config` 和 `observation.energy.samples` 原列宽键，详情指标表独立使用 `observation.energy.detail`。配置上卡仅有真实表计指标配置。 |
| 过程与样式 | 过程配置、数据原路径分别保留曲线设置和过程样本单选上卡。共用曲线组件默认使用原过程文案，能耗传入自有命名空间。价格、能耗样本、表计指标、过程曲线配置弹窗采用共享紧凑三段式，遮罩点击按取消处理，保存处理中保留既有提交保护。 |
| 文档与装配 | 新模块有自有中英文 locale，随模块发现。过程与辅助 locale 移去迁出文案。更新前端双语 README、观测双语说明和操作指南、根 CODE_INDEX 中的现行入口引用。阴影、主题和操作尺寸均复用现有项目样式。 |

本次交付为正式工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch` 的未提交源码。基准 HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`。包含 `frontend-js/src/app/energy/` 内 9 个文件和批准范围内过程、辅助目录的迁出，其中旧价格页、旧统计页和旧 EnergyAdmin 路径随源码迁移退出。测试改动限于 `tests/module-registry/{equipment-observation-columns,page-access,price-page,registry}.test.mjs`。并行的质量管理与 SMA 改动留在工作树。后端、数据库、机器接口及 B 各项继续以 r1 范围记录为准。

## Development 自检

2026-11-24（上海），macOS，Node `22.19.0`、pnpm `11.11.0`。运行产物使用合成账号、表计、价格、采样及公共路径，浏览器 fixture 拦截整个 API 前缀并核对现有 Bearer，拒绝外部 origin，请求改动只更新进程内 stub。未连接后端、真实数据库或现场设备。

| 验收 | 自检与结果 |
| --- | --- |
| A01/A06 菜单、授权和双语装配 | `pnpm --dir frontend-js check:modules` 退出 0，32 路由、10 菜单组。前端目录的 `VITE_SUPERVISOR_PAGE_ACCESS_JSON='["monitor.energy","auxiliary.price"]' VITE_OPERATOR_PAGE_ACCESS_JSON='["auxiliary.price"]' pnpm check:access --mode production` 退出 0。两项能耗专项测试通过，覆盖只授予统计／只授予价格、admin 管理入口、旧地址与路由名、其他可选模块禁用时能耗 locale 装配。 |
| A02/A04/A05 既有业务及异步回归 | 前端目录执行 `node --test tests/module-registry/{equipment-observation,equipment-observation-columns,price-page}.test.mjs`，37 通过，退出 0。含真实零、缺测、定义及数据响应竞态、采样列顺序、现有过程曲线与设备行为、价格录入校验和现价／历史独立刷新。另运行 `node --test --test-name-pattern='energy (navigation\|titles)' tests/module-registry/{page-access,registry}.test.mjs`，2 通过，退出 0。 |
| A03/A06 构建 | 在无项目 `.env` 的任务副本，用现有依赖链接，执行 `pnpm_config_verify_deps_before_run=false VITE_API_BASE_URL=/api/v1 VITE_FRONTEND_MOCK_ENABLED=false VITE_SUPERVISOR_PAGE_ACCESS_JSON='["monitor.energy","auxiliary.price"]' VITE_OPERATOR_PAGE_ACCESS_JSON='["auxiliary.price"]' pnpm --dir /private/tmp/arch-obs007-a-dev/frontend build`，退出 0。Vite 提示 ECharts、Element Plus 等静态包过大。 |
| A01–A07 浏览器 | `node /private/tmp/arch-obs007-a-dev/browser.cjs` 退出 0。Chrome 验证 1440×900 和 1024×768 各浅色／深色组合。每组检查三张单价卡同宽、与历史卡齐边和四个业务弹窗，核对标题、页脚可达、正文可滚动与遮罩无提交。功能补充走过实际上海时间范围输入、`0 kWh`、恢复默认、样本列实际拖动／刷新回显／重置、样本与指标 PATCH、价格 POST、旧过程路由、英语与管理员限制。循环地址仅由隔离 fixture 服务。 |
| A07 静态一致性 | `git diff --check` 退出 0。迁移入口引用检查通过；构建副本与正式工作树的 19 个候选源码逐字节核对通过，排序后的 SHA-256 清单摘要为 `34b90e0fc1d0fb312f5ee6e1c8b97d785705185200ce5d34ac49a84e2f9b36dc`。旧地址和后端 API 路径继续可用，价、配置、采样在隔离浏览器内以服务端合同结构返回。 |

全模块 `pnpm --dir frontend-js test:modules` 退出 1，114 通过、2 失败。协调者在 A 改动前的基线为 112 通过、3 失败。现存两条失败分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 和 `actual source preserves Core route identity, shell locales and default-disabled demo`，都由既有 `maintenance` 与 `system` 顺序断言漂移触发。A 迁移中只改动相关期望，第三条旧过程菜单顺序断言已随实际源配置对齐。上述全量状态仍需由 Verification 独立核对。

## 交接限制和临时资源收尾

- 正式交付基于上述工作树文件和对等构建输入。浏览器用例的后端行为来自合成夹具，时间解析、客户端请求、导航与互动均在真正 Chrome 上运行。
- 已回收首轮重复的 `/private/tmp/arch-obs007-modules-first.log`，所有自检 Chrome、测试服务器与构建进程已退出。
- 暂保留 `/private/tmp/arch-obs007-a-dev/`，其中 `browser.cjs`、不含 `.env` 的前端候选、构建与日志、源码摘要供独立复核。独立复核和必要证据记录完成、且无后续返工依赖时由协调者回收。

## 第一次返工与再次交接

2026-11-24（上海）。根据 [首轮独立验证的 A02 发现](checklist.md#可复现失败)，修改能耗模块两份 locale 的 `observation.invalidHistoryRange`，明确结束时间必须晚于开始时间。统计页的严格 `from < to` 和后端合同沿用原实现。新增一项实际统计页 SFC 回归，覆盖中英文提示、起止相等和倒序未发送查询、有效一秒区间以 `+08:00` 查询并识别零值。

- 前端目录执行 `node --test tests/module-registry/{equipment-observation,equipment-observation-columns,price-page}.test.mjs`，38 通过，退出 0。全模块测试 115 通过、2 失败，退出 1，剩余失败仍为上述两条 `maintenance` 与 `system` 顺序断言。
- `pnpm --dir frontend-js check:modules` 和 `git diff --check` 均退出 0。使用初次交接相同命令和参数重新构建隔离候选，退出 0。
- `node /private/tmp/arch-obs007-a-dev/rework-range-browser.cjs` 在 Chrome 和隔离 API 夹具中退出 0。中英文相等时间均显示严格提示，倒序不发送数据请求。有效一秒范围发送两个预期请求，起止带上海时区偏移，显示 `0 kWh`。网络限回环与合成响应。
- 正式工作树 HEAD 仍为 `7f654acd951171767bc253ea5bebdcda6435b608`。19 个候选源码与重新构建的隔离输入逐字节一致，新清单为 `/private/tmp/arch-obs007-a-dev/rework1-source-sha256.txt`，清单 SHA-256 为 `6e61d2de5d8e41176174888d8374f350bea77f758c17693d19510d9320a8d91b`。首轮摘要留作历史。

本轮测试服务器、Chrome 和构建均已退出。继续保留 `/private/tmp/arch-obs007-a-dev/`，含返工脚本与日志、现行构建和两次源码清单，供新的独立 Verification 核对。独立复核及必要证据记录完成且无返工依赖后由协调者回收。首轮 QA 脚本由其所有者管理。
