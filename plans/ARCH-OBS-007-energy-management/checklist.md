Task ID: ARCH-OBS-007
Revision: r1
Status: owner_accepted
Owner Role: Verification
Allowed Writers: Verification
Handoff: Human Owner 已最终验收 r1 A；B 的精确合同及开发仍待批准
Workflow Mode: STD
Execution Mode: agent_team_same_session

# r1 A 首轮独立验证 · 2026-11-24 上海

**结论为 `qa_failed`。** A02 的中英文错误提示允许起止时间相等，统计接口和页面校验都要求结束时间晚于开始时间。Human Owner 最终验收待后续交接，B 的合同与实施仍待批准。

## 可复现失败

进入能耗统计，两个上海时间输入框均填 `2026-11-23 00:00:00`，Enter 确认后点击「查询」。独立 Chrome 实测两框保留同一秒，页面拒绝查询并显示「请填写完整有效的起止时间，结束时间不得早于开始时间」。英文资源同样写为 “at or before the end”。用户按提示保留相等时间会继续收到相同错误。

[统计页](../../frontend-js/src/app/energy/views/consumption.vue) 第 72、117 行分别判断 `from < to`、选择错误文案。[中文](../../frontend-js/src/app/energy/locales/zh-CN.json) 和 [英文](../../frontend-js/src/app/energy/locales/en-US.json) 的 `observation.invalidHistoryRange` 均须说明严格先后关系。[既有服务](../../backend/app/equipment_observation/services/energy_reads.py) 的 summary 在 beginning >= ending 时拒绝。返工复核须覆盖相等、逆序及有效正区间，并核对两种语言。

## 验收记录

| 验收 | 结果及证据 |
| --- | --- |
| A01 | 授权和路由专项通过。保留 MonitorEnergy、AuxiliaryPrice、旧 pageId 和两个旧地址。角色授权单测覆盖单独授权及管理员限制；Chrome 验证旧地址、英文、未登录和普通用户访问管理页的重定向。 |
| A02 | 失败项见上。其余抽查通过。Chrome 的美国洛杉矶宿主时区下，上海输入发送 +08:00，结果为 0 kWh，可恢复默认。源码从 samples、summary 分别取曲线及统计；受影响套件覆盖缺测、失败及异步选择刷新。 |
| A03 | PC、平板各明暗主题下，三张卡同宽同排并与独立历史卡齐边（误差 <1 CSS px）。600×800 额外实测三卡 x=267、宽302，y 依次为224、404、584。价格页组件测试覆盖选日、表单校验、失败处理、上海时间及整组 POST 后重读。浏览器录入 2.125 后显示 2.1250。小时覆盖与读写权限约束沿用现有服务，本轮后端行为由隔离夹具模拟。 |
| A04 | 样本页 PATCH 仅含 remark、reviewMark；浏览器复核样本备注、指标编辑及回显。源码核对筛选、分页、配置新增／编辑、槽位、显示顺序与累计规则。配置上卡仅表计指标。每个已拦截 API 请求均断言携带合成用户 Bearer。 |
| A05 | 两张过程上卡在对应旧地址各声明一个选项，分别为曲线设置和过程样本。过程编辑弹窗真实打开并取消，温度／传动／清洗曲线、过程样本及设备路由由 Chrome 打开，组件回归覆盖数据与时间语义。 |
| A06 | 模块装配与专项测试通过。独立运行 energy 可选模块测试，禁用 monitor、auxiliary、equipment 后，统计、单价及共用图表文案可解析。样本列真实拖拽、重载、重置通过。检查配置、样本、详情、价格历史各自的表宽键与重置绑定。四种设备／主题组合均验证新增单价、指标编辑、样本详情、曲线编辑的标题及页脚、滚动和遮罩取消，取消无写入。中英时间错误提示的语义缺陷归 A02。 |
| A07 | 使用正式源码和原有前端 Bearer 请求层。价格、配置和样本的既有路径及相应响应字段保持一致；路由与授权兼容见 A01。无现场调用或真实数据写入。 |

## 环境、命令与差异核对

- 本次由独立 Verification 在 fresh context 消费 spec 和 developer_handoff。正式工作树为 macOS 上的 aiis-ics-arch，HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`，Node 22.19.0。交接源文件 `shasum -a 256 -c /private/tmp/arch-obs007-a-dev/source-sha256.txt` 19 项全通过；`diff -qr frontend-js/src /private/tmp/arch-obs007-a-dev/frontend/src` 无差异。使用 Development 已构建的无项目 .env 副本运行浏览器，未重新生成 dist。
- `pnpm --dir frontend-js check:modules` 退出 0，32 路由、10 菜单组。前端目录下 `node --test tests/module-registry/{equipment-observation,equipment-observation-columns,price-page}.test.mjs` 37/37 通过；`node --test --test-name-pattern='energy (navigation|titles)' tests/module-registry/{page-access,registry}.test.mjs` 2/2 通过。`git diff --check` 退出 0。
- `pnpm --dir frontend-js test:modules` 报 114 通过、2 失败。对照协调者事前保存的 modules-before（112 通过、3 失败），两条同名失败分别为 `admin, supervisor, operator and unknown share route/menu/default decisions` 和 `actual source preserves Core route identity, shell locales and default-disabled demo`，断言将 maintenance 放在 system 后，实际相反。基线的第三条旧菜单期望已通过。质量、SMA 的并行变更不计入 A 的交付和结论。
- `node /private/tmp/arch-obs007-a-dev/browser.cjs` 首次因沙箱拒绝监听 127.0.0.1 退出 1，经审批后原命令退出 0，四组布局与功能、路由断言通过。`node /private/tmp/arch-obs007-first-qa.cjs` 在同一隔离构建和拦截条件下退出 0，其断言实际重现上文错误并量测了窄屏三卡。夹具成功重现缺陷计为业务验收失败。
- 环境限制为隔离 UI、组件和合同验证，不连接真实后台、数据库、设备，也未运行发布、迁移或部署。

## 临时资源

测试服务器与 Chrome 已退出。`/private/tmp/arch-obs007-first-qa.cjs` 为本轮 QA 的窄屏与相等时间复现脚本，供 Development 复现及下一轮 QA 对照；下轮记录完成后由协调者回收。Development 候选目录和协调者的事前基线由原所有者保留至返工与独立复核完毕。

## QA2 · 第一次返工独立复核 · 2026-11-24 上海

**ARCH-OBS-007 r1 A 为 `qa_passed`，交 Human Owner 最终验收。** 首轮 A02 发现已关闭。A01、A03–A07 沿用上文首轮逐项验证，返工差异隔离及本轮回归如下。B 仍待合同和批准。

| 检查 | 本轮独立证据 |
| --- | --- |
| 来源与构建 | 正式工作树 HEAD 为 `7f654acd951171767bc253ea5bebdcda6435b608`。比较两次交接的 19 项源码摘要，仅能耗中英文 locale 两项变化。执行 `shasum -a 256 -c /private/tmp/arch-obs007-a-dev/rework1-source-sha256.txt` 全部通过，清单摘要为 `6e61d2de5d8e41176174888d8374f350bea77f758c17693d19510d9320a8d91b`。正式 src 与副本递归 diff 一致，package.json、vite.config.js 一致。macOS、Node 22.19.0、pnpm 11.11.0，以 tasks.md 自检所列同一合成环境重跑副本 `pnpm build`，退出 0，仅有大包警告。 |
| A02 | 独立查验统计页 `from < to` 和 summary 服务 `beginning >= ending` 拒绝条件。运行 `node /private/tmp/arch-obs007-a-dev/rework-range-browser.cjs`，本机 Chrome、回环服务、合成 API，退出 0。中英文相等输入分别提示「结束时间必须晚于开始时间」和 “The end time must be later than the start time.”。相等及倒序均未发送 samples 或 summary。倒序浏览器断言容许日期控件清除非法输入后显示表单错误；真实 SFC 测试另断言保留倒序值时两种语言均显示精确文案。一秒有效范围发出两个查询，起止为 2026-11-23 上海零时到 00:00:01，均含 +08:00，显示 0 kWh。 |
| A01、A03–A07 回归 | 正式 frontend-js 中执行 `node --test tests/module-registry/{equipment-observation,equipment-observation-columns,price-page}.test.mjs`，38/38 通过；执行 `node --test --test-name-pattern='energy (navigation|titles)' tests/module-registry/{page-access,registry}.test.mjs`，2/2 通过。两命令退出 0。模块检查 `pnpm check:modules` 退出 0（32 路由，10 菜单组）。QA1 浏览器布局、主题、列宽、弹窗及业务交互的证据继续适用于本次仅调整提示的候选。 |
| 全量及限制 | `pnpm test:modules` 退出 1，115 通过、2 失败。逐项与事前 modules-before.txt（112 通过、3 失败）对照，首轮已记录的两项 maintenance/system 顺序断言均早于 A，实际 maintenance 在前。本轮无新增失败。`git diff --check` 退出 0。验证仅使用合成数据和本地构建，无真实后端、数据库或设备调用。 |

**临时资源。** 本轮重新生成原候选目录内的 dist，浏览器和测试服务已退出，未新增独立临时目录或脚本。上述 Development 候选目录、首轮 QA 脚本及协调者基线目录 `/private/tmp/aiis-obs007-coordinator.SJp4jS/` 交协调者在证据记录完毕且无其他依赖时回收。

## Human Owner 最终验收

2026-11-24（Asia/Shanghai），Human Owner 原话：“验收 ARCH-OBS-007 r1 A。” 据此记录 A 为 `owner_accepted`。B 的精确合同及开发仍待批准。

临时资源已回收。协调者报告回收上述 Development 候选目录、QA1 脚本及协调者基线目录，本次逐项核对三个路径均已不存在。
