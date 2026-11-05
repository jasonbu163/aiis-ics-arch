Task ID: SMA-003
Revision: r1
Status: owner_approved
Owner Role: PM
Allowed Writers: PM, Human Owner
Handoff: PM -> Development; exact SMA-003 r1 已获 Owner 批准，SMA-002 依赖 gate 已据其 owner_accepted / qa_passed checklist 核定，可按本 r1 开始实施
Workflow Mode: STD
Execution Mode: agent_team_same_session
Task Namespace: aiis-ics-arch.aw.sma
Classification: child_inherited
Capability: SMA HTTP映射桌面应用的分阶段交付
Owner: AIIS Automation World / SMA 模块 Human Owner
Acceptance Chain Reference: SMA-001 总交付链：各任务精确 Task ID / Revision 范围批准 -> Development developer_handoff -> fresh-context Verification -> Human Owner 分阶段及总体最终验收
Scope Slice: 清理后工作台的 CU 公共 UI 接入与统一展示
Parent Task ID: SMA-001
Same Capability: yes
Same Owner: yes
Same Acceptance Chain: yes
Depends On: SMA-002

# SMA-003：CU 接入

## 1. 目标、依赖与批准边界

本任务是 [SMA-001 r2 总规格](../SMA-001-cu-integration-and-scope-cleanup/spec.md) 阶段②：使清理后的连接、只读源事实、目标接口/API材料、映射任务/合法值规则、映射运行/诊断五类职责页消费CU公共UI，统一明暗、中英、弹层、表格与时间展示，保留HTTP映射语义。

与父任务为同一SMA能力/Owner/总验收链的范围切片，三项Same均为yes，只复用上下文。2026-11-04 Human Owner先授权“拆出‘职责清理’和‘CU 接入’两个子 spec……暂时不改代码”（完整原话见总规格§1），当时本r1为draft；同日随后对明确包含已链接SMA-003 r1的执行顺序回复“好的，批准”，本次精确软件范围批准见§7，不继承父任务或SMA-002的批准/QA/验收。

**软件进入gate：** [SMA-002](../SMA-002-scope-cleanup/spec.md) 完成精确范围批准、实施、fresh QA和Human Owner清理基线最终接受，固定其候选、偏好兼容与helper交接后，本任务才可实施。该依赖现已由其[独立checklist](../SMA-002-scope-cleanup/checklist.md)核定为 `Status: owner_accepted` / `QA Verdict: qa_passed`，只对原af7140候选生效；本r1自身批准也已登记，现可交Development。依赖要求未豁免，不能靠父任务标题、软件范围批准或未来占位文件替代；精确依据见§7。

CU公共合同来自 `../console-ui/src/ui/index.ts`、`src/ui/styles/index.css`，CU-008二级导航已有owning接受证据；这些不等于SMA已接入。当前SMA自写壳、依赖/alias/样式待本任务实施。

## 2. 范围与要求

### R1. 只消费 CU 公共入口

复用 `AgentLayout`、`AgentSidebar`、`AgentTopbar`、`ConsoleCard`、`ConsoleActionButton`、`StatusCapsule`、`ThemeToggle`、`LanguageSwitch`及公共类型/样式。SMA自有兼容依赖、锁文件、alias/dedupe和受限源码访问；不复制整套CU、不借CU node_modules，不导入私有workbench、locale或设计写入通道。

基础Element Plus CSS先于 `@aw-ui-styles`；SMA自行挂载、管理状态/布局，不改CU公共profile/默认值/生成CSS/组件API。自身dist无需CU进程在线；构建时公共源码可用与运行时独立分别说明。

### R2. 工作台、主题与语言

- 使用稳定非翻译ID组织五类职责的有限二级导航；组只展开/折叠，叶项选择归SMA。侧栏/顶栏/卡片/按钮/状态和保留页组合接入CU，不增客户页、编排器、设计工作台或帮助/模拟占位。
- SMA拥有明暗主题、语言及UI偏好，使用隔离 `sma.*` 键；保持现有双语机制，不为换壳重建国际化框架。切换主题/语言不触发业务请求、不丢映射草稿或运行状态。
- 页面、Teleport弹窗与下拉位于跟随主题的明确作用域，宿主提供Element Plus locale。字段说明、校验/反馈、正常/加载/空/失败/HTTP关闭态中英齐全且可键盘操作；不在全局html/body覆盖CU主题。
- 保持产品/窗口 `AIIS Semantic Mapping Agent`、identifier `com.aiis.aw.semanticmappingagent`、15192/14192 strictPort、独立dist、普通 `pnpm tauri dev`、原配置发现和默认 `SMA_HTTP_ENABLED=false`。

### R3. 保留映射与退役结果

基于清理后的组件/状态，保留只读选点、API材料/手工目标、字段/常量绑定、合法值/类型校验、纯预览、JSON/XLSX配置/通用保存、明确单次投递及持续运行控制/诊断；不得恢复事实写入、Simulation、HelpCenter或隐藏入口。

仅做展示组合，不改固定POST snapshot、保存的Backend base URL、`/api/tss/v1`、发送/lease/审计/幂等标识、失败/ambiguous/停止或v1偏好语义；不交付现Backend配套、通用GET→POST、业务保存与可靠恢复。

### R4. 表格与日历时间

统一本任务触达的五类保留页普通业务表：经SMA公共工具提供拖拽/合理最小宽/横滚、翻页/筛选/刷新/切页保持、重载/重启恢复和每表重置；选择/序号/操作列可固定。按应用+表/字段稳定ID隔离本机偏好，非法/失效项回默认，不写业务版本或跨设备同步。

触达业务日历时间经统一helper按 `Asia/Shanghai`、24小时 `YYYY-MM-DD HH:mm:ss` 显示，原值/底层精度与日志保留不变。实际更新/执行/确认按已有字段事实标注，缺失不猜测、无时区无法确认时显示未明确；刷新时刻/单调计数不冒充日历事实，不迁移数据或更改HTTP合同。

复用SMA-002已触达的列宽/时间helper、稳定ID与回归，缺少的展示范围在本任务完成，不重复两套机制。可参考DAA/DS tableWidths，不改其它应用或扩展CU公共API。两任务均遵守根AGENTS，不把已触达规则留空。

## 3. 排除与保护

不重做职责清退，不改运行时/IPC/Backend合同；不做配置独立化、SQLite、GET源、新目标地址、历史/outbox、并发容量、认证或CU自身设计迭代，不改原TSS/旧CA/DAA/DS。

不修改/删除真实配置、profile、数据库和历史；不连接真实HTTP/DB/PLC、不运行其它应用/Docker/OS托管、不部署/签名分发/Git发布。未来验证仅隔离本机；当前只写spec。

## 4. 候选 allowlist

仅在依赖gate和精确软件批准后生效，路径相对SMA根；各项限定R1–R4展示职责，Development固定清理后实际候选文件。

| 表面 | 允许路径 / 目的 |
| --- | --- |
| 依赖/入口 | `package.json`、`pnpm-lock.yaml`、`vite.config.ts`、`tsconfig.json`、`src/vite-env.d.ts`、`src/App.vue`、`src/main.ts`：CU自有依赖/alias/dedupe/类型及装配。 |
| 导航/公共展示 | `src/app/{navigation.ts,registry.ts}`、`src/styles.css`、`src/app/styles/{shell.css,shared.css,responsive.css}`、`src/styles/app.css`、`src/components/{BackToTopButton.vue,PaginationBar.vue,usePagination.ts}`；可新增/复用 `src/console/`内仅主题/语言偏好、列宽、时间的有限helper，不建框架/新公共包。 |
| 保留业务页 | `src/app/connection/{manifest.ts,components/*.vue,views/ConnectionModuleView.vue,styles.css}`；`src/app/twin-facts/{manifest.ts,components/*.vue,views/TwinFactsModuleView.vue}`，仅清理后保留的展示/组合，不新建retired页。 |
| 文案 | `src/locales/index.ts`、`src/locales/common/{zh-CN,en-US}.json`、`src/app/{connection,twin-facts}/locales/{zh-CN,en-US}.json`，含Element Plus语言作用域。 |
| 验证/文档 | `tests/*.test.mjs`及最小UI fixture/证据；模块 `README.*`、`src/app/README.*`、`PLAN.*`、`plans/README.*`、根 `CODE_INDEX.md`与AW对应索引行最小同步。 |
| 角色 | PM仅本spec，获批DEV创建本目录tasks，handoff后fresh Verification创建checklist，不互写权威。 |

Rust运行源码/配置与Cargo、前端业务API/store/文件合同、Tauri identity/capabilities/图标不在写入表面，构建/回归可读取。若换壳需改变这些合同或扩大allowlist，停止该部分返回PM修订，不自动授权。

## 5. 验收设计（尚未执行）

原合并r1的AC01–AC03、AC10/11主要归本任务，AC12/13按切片适用；清退/偏好完整证据归SMA-002，此处核对候选连续性，不伪造重复验收。

| AC | 必须可核验的结果 |
| --- | --- |
| AC01 | 实施前有SMA-002候选、fresh QA/Human Owner接受及本r1精确软件批准；实现与清理候选连续，帮助/模拟/事实写入口未恢复。 |
| AC02 | 实际消费两公共入口/所列组件，自有依赖/alias/dedupe，无私有或CU node_modules import、无CU修改；自身dist在CU不在线时正常，身份/端口/入口/gate保持。 |
| AC03 | 五类职责可达，分组/选中/键盘焦点/单次select正确；主题/语言不合成业务调用或丢草稿；侧栏收展、外部active、本地偏好无跨应用污染。 |
| AC04 | 中英×明暗覆盖五类页/表单/弹窗/下拉及正常/加载/空/失败/关闭态；桌面与浏览器390×720动作可达、表格横滚、弹层局部滚动，Tauri原窗口限制保持。 |
| AC05 | 每张触达普通表实测拖拽/最小宽/横滚、各类刷新/切页/重载/重启恢复；稳定ID隔离、每表重置、失效回默认有效，复用已有helper。 |
| AC06 | 不同宿主时区下同一合法带时区值均显示上海到秒，原精度不变，事实标签准确，缺失/无时区不猜测；无数据迁移或新运行时间合同。 |
| AC07 | 纯组包/类型/合法值/JSON-XLSX/保存链既有回归保持；预览无HTTP，gate=false含旧mapping autostart=true时零外发；单次/持续UI动作与原语义对应，不需真实目标写入证明换壳。 |
| AC08 | pnpm check/test/build、Rust fmt/test --locked和默认无I/O本平台Tauri有界smoke通过或有精确blocker；清理基线Rust/API/偏好合同未改，文档/diff/资源符合allowlist。 |

## 6. 后续验证、风险与 handoff

以下为依赖gate解除后Development / Verification的必要命令要求；本次PM只登记批准，未执行这些检查：

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm build
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo test --manifest-path src-tauri/Cargo.toml --locked
```

UI/native用可丢弃绝对 `SMA_PROFILE_DIR`、空Backend、`SMA_HTTP_ENABLED=false`及普通 `pnpm tauri dev`。交互数据只用本机隔离fixture，不建立交付应用常驻mock或访问真实Backend；既有HTTP回归仅专用loopback fixture显式开gate。记录候选diff/hash、命令/退出码、视觉/操作/无I/O证据、依赖来源和资源收尾；浏览器不冒充原生，DEV自检不是QA。

风险为依赖冲突、旧CSS覆盖暗色弹层和清理候选漂移；由消费端兼容依赖、公共主题作用域、交接清单及回归控制。公共组件缺口记blocker/新范围，不直接改CU。回退仅本任务补丁，不恢复退役能力、不reset/clean他人dirty、不改真实偏好/数据。

获批DEV/QA按范围使用 `frontend-ui`、`i18n-workflow`、`desktop-tauri`；公共入口/模块治理用 `aiis` / `project-governance`，结构文档用 `code-document-indexer`。无Rust运行时改动；发现必要变化回PM，不以换壳扩展技术范围。

DEV给精确SMA-003 r1、已接受SMA-002候选、交付工作树/文件、UI/兼容检查限制及资源形成developer_handoff；主协调再启动命名fresh-context Verification（支持时 `fork_turns="none"`）创建checklist。Human Owner最终接受仅表示阶段②完成，不表示SMA整体或GET→POST/业务闭环完成。

## 7. 修订与当前决定

2026-11-04（Asia/Shanghai）：先从SMA-001未实施r1拆出本r1，当时仅文档创建获准、软件范围仍draft。此历史状态与以下当前批准分开保留。

同日随后，主协调提出的完整推进顺序为：先由Owner处理SMA-002已披露日志副作用/取证限制，经QA复核B1后完成清理验收；再批准并实施已链接的SMA-003 r1（CU布局、导航、主题、双语、表格、弹窗，保留映射并独立验证）；CU验收后规划配置独立化、Backend并行准备；API就绪后推进单目标闭环，再做历史与批量。Human Owner直接回复原话：

> 好的，批准

批准来源为主协调转交的该完整提议及直接回复。本记录将其中明确指向本spec的决定登记为精确SMA-003 r1软件范围批准，`Status: owner_approved`，Revision仍r1，R1–R4、排除项、allowlist、AC01–AC08及风险未变；不是SMA-001总规格或尚无精确spec的后续阶段软件批准。

批准登记时曾等待SMA-002清理验收依赖；2026-11-04（Asia/Shanghai）原独立Verification已核定该checklist为 `Status: owner_accepted`、`QA Verdict: qa_passed`，B1关闭及Owner条件性基线接受仅原候选 `af7140357f2a81fa6a2870aed1c2d092dfe4e64ab7795dbf472cf62cdbcff6e2` 生效。PM只读核对checklist SHA-256为 `c631ec1781502a0236d7d9cbbbf41eecb2d341d65c64385b18f329ffe5412f16`，据已形成的QA/Owner事实登记依赖gate满足，现将本r1交Development，不由PM另授验收。

该已披露风险的条件性处理及基线接受证据继续归SMA-002 checklist/Owner事实面；候选漂移、新缺陷或新风险不在该既有接受内。本次PM交接时SMA-003尚无实施/独立QA/最终验收；后续依本r1独立履行DEV handoff与fresh Verification，不恢复真实profile测试权限或放宽原保护要求。
