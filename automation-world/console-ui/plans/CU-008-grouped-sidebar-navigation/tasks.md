Task ID: CU-008
Revision: r1
Status: developer_handoff
Owner Role: Development
Allowed Writers: Development
Handoff: Development -> new fresh-context QA / Verification; exact approved CU-008 r1 implementation and bounded DEV self-check recorded; QA and Human Owner final acceptance pending
Workflow Mode: STD
Execution Mode: agent_team_same_session

# CU-008 r1 Development

## 1. 批准、角色与工作树

依据 2026-10-17 Human Owner 精确批准的 [spec.md](spec.md)，批准版 SHA-256 `0577e02e9067f5564c2c3896cba6f657c3517ab0dc41d211c6b105ab3832e4d5`。实际命名 Development，读取 `.codex/agents/development.toml`；配置模型为 gpt-6.1-sol / high，运行中不可观测的配置应用不另作独立证明。profile 为 `contract_only`，不表示平台 ACL、强制路由或完整 Agent Team activation。

根 AGENTS、双语 README/PLAN、canonical lifecycle workflow、Development TOML、AW/CU 最近双语 README/PLAN、源码层次与消费者教程、完整已形成 bundle、公共/私有相关实现和当前 Element Plus 2.14.2 菜单实现已读。没有更近 AGENTS。采用 frontend-ui（既有设计及 FRAMEWORK 主题/EP 规则）、i18n-workflow、project-governance、aiis/CONTRACTS、code-document-indexer 的现有文件头维护规则；不增加产品文件或扩写源码结构索引。写前 bundle 只有 spec；批准后才创建 tasks，未创建或修改 checklist，四 CU 索引归主协调。

工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，HEAD `f85bea8bbf36b491968c3dc9a839518a1ed434a8` 仅作上下文，**没有相同字节的已发布 Git ref**。本轮没有创建 commit、branch、tag、worktree、推送或发布。现有其他会话 dirty/untracked 保留，未从 HEAD restore/reset。后续固定此导航源必须用本 r1 的实际工作树清单，并核对之后真实形成的独立 QA/Owner 依据；不能把本 DEV 自检或 HEAD 当源码定版与最终验收。

证据根 `/private/tmp/cu-008-r1-development-20261017` 是本轮专属目录，含 before/after 原字节、精确 15 文件 patch、全部 SHA、构建/preview 日志和临时夹具；关键事实与清单直接记录在本文件，临时目录不是唯一事实源。

## 2. 实施策略、参考与实际范围

1. R01–R04 / AC01–05：公共非递归 NavigationChildItem/NavigationItem、ElMenu/ElSubMenu/ElMenuItem 二级渲染，受控选择展示、父组展开与最小键盘补齐。
2. R05–R06 / AC06、08：CU 保留四平铺主导航；壳层预览加独立分组样例，消费者有平铺/分组、外部 active 和单次事件计数；两层 README pair、两套 locale 对称。
3. R07–R08 / AC07、09–10：原字节基线与保护检查，冻结全部实现/locale/说明后 CU/consumer 各一次最终 build，真实浏览器有限 GUI DEV 自检，精确 diff/SHA 交新的 fresh-context Verification。

Human Owner 随后明确要求“二级导航样式和设计直接复用 frontend-js 现有二级导航，不另做一套”。本轮只读参考：

- `frontend-js/src/components/navigation/ModuleNavigation.vue`：同一 Element Plus title 图标/label 与直接子叶的二级结构。
- `frontend-js/src/layouts/MainLayout.vue` 的 nav-menu 与菜单样式（约637–692行）：透明内联菜单、6px项间距、子项 min-width:0、箭头 margin-left:auto/flex-shrink:0、hover 背景。
- `frontend-js/src/styles/theme.css`（约948–966行）：42px项高、12px圆角、选中背景/文本；映射到既有 CU tokens，保留原平铺外观。

已移除开发早期拟加的自定义父组边线及36px缩进，使用 EP 默认子项缩进；父标题强调色与当前叶项背景区分。必要差异来自 r1：宿主 active/翻译、多个组可同时展开、键盘焦点、长 label 换行与≤600px局部滚动；不复制 frontend-js 的 Router、权限、业务 i18n 或 unique-opened。**frontend-js 没有写入。** 公共设计 JSON/CSS、AgentLayout/其余七组件、主题方案、私有编辑器/写通道、依赖/锁/端口/config、Rust/Tauri 与其他 Agent 均没有写入。

Sidebar 只接收翻译后的 props。非空 children 为组，空 children 按叶项；组不 select；初始化/prop 变化不合成选择。active 高亮、aria-current 和含当前项父标题由 prop 派生；EP 的短暂交互 active 不作为页面状态。仅稳定叶项/父身份变化触发展开，label/主题不重开手动折叠组；手动展开仅实例内存。键盘只在 Sidebar capture 补齐，Enter/Space 阻止默认并统一发一次 EP click。关闭含焦点子树回父标题；Tab 不拦截、闭合子项 tabindex=-1。

消费者导航模式不替换/卸载已有表格、表单或弹窗；它们的状态及动作原样保留。CU 原四平铺页和参数编辑器保持。所有导航操作是纯内存，没有导航 storage、业务 API、IPC、文件写入或 DAA 业务名称。

## 3. 精确实现增量与逐文件摘要

下表路径均相对 `automation-world/console-ui/`。15个既有获批实现/说明路径全部有本轮增量，唯一新增仓内文档为本 bundle 的 tasks.md。before 是本轮开始时的实际工作树字节，after 是冻结实现；没有把其他会话原有改动算成本任务。精确 patch 包含每一行增量，不用根总 diff 归因。

| 文件 | before SHA-256 | after SHA-256 |
| --- | --- | --- |
| `src/ui/types.ts` | `c0a8873323245cab961169280fa2564997f8844dbeeb452485bde8c6e4f35c25` | `b0ea3bd1e8d31e4cf26b2068fde4d8199dcf82e23d2112d29db34187b50ae18f` |
| `src/ui/index.ts` | `d0c1715b266049b8b6485c36a5318c0ce9d0e7d39e4333b4aadfd9ab1e6c963c` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |
| `src/ui/components/AgentSidebar.vue` | `31a9f5410bc592c54e5ca8eec802cebcd90198d88275716d999d4e7f6298bc2a` | `b53495b30e589aed06ba51b470c582fcc1d7984a590c9b0d811e9bb0de629533` |
| `src/ui/styles/components.css` | `74eb7b1345a3cca69c316be059e6b16a69c8206d046f55eeeb395c05ab35b6fd` | `734cd1402a71ffe1e3500c128d392c38bcdf8404bc1d008e8098b06268206fbb` |
| `src/workbench/Workbench.vue` | `e4a261f14247ef1025d2d143eeb192ba9dc143159d45f2d2298f45b477b30188` | `323f7fe49a901869657691d1e59c7c4de92a7fc7de981547cf30d94a5ab50075` |
| `src/workbench/workbench.css` | `70b07aa9c55b8f7b55e7c15f4e23e83cad576755f288101350b216f89b5597ef` | `7fd30f00a5a19bec254cbe0ec5bad9fd1959ea6fea675f567e51d13ddb1ff9c4` |
| `src/locales/zh-CN/workbench.json` | `76e23e159b37a985d1bd5bb4c5031a1d91ec21ea0a8cb1c4d7b9a268e7152647` | `47ed4e4b38c5586e961ac8778578ee047f8ebcabbb4c498d8fb1048c0d7380b1` |
| `src/locales/en-US/workbench.json` | `460f532469ca9fc45d81172ee4f04fb67f6d6494b02fcb6f472301ea5b463ecb` | `99e7d3bff4b940666267706312db1a790b6235821398c9169c2e411ddad35161` |
| `examples/source-consumer/src/App.vue` | `306c279b52f8852de3b93fb25a0201e33a5feee07168f6f6567c50b7adc407ff` | `971f7333ea25426f4ccfc2518096afa6e1f2bf4b0ece1ac5d0466b8683531ef3` |
| `examples/source-consumer/src/locales/zh-CN.json` | `4f1e882ce2822305aa388e5deed26f7134f9c160b3db93394209e62496c2f5dd` | `626b5d8e11d1a6d1c10e393fb1c605b8e2ff1323a5581b5e9b14bfa463d8e699` |
| `examples/source-consumer/src/locales/en-US.json` | `a1c2d75cd2bd4a10a1bc37c8fa484a14e83231b64d66772f358e24353c3ec704` | `60e7009d9245ccb7ab375a314b30bdfa474d25161c0f4dcb235d2f26ccd33041` |
| `README.md` | `1a216b3b0f9e4f61a4a6d62dea566c637360692e0a4af6379362ef89619d4732` | `36095602d40a1bfb7e95ec5f1fef7a10aff59e9c38781d6ab360fde96ca23ca8` |
| `README.zh-CN.md` | `21f6c035c49d90f5a9c08fdc32087f593ce10bb1f80b589f15f34773b1405c04` | `8b066c7a8f8ab091df1102297510d349a005ce6c6f5ac8e8313f0b689739043a` |
| `examples/source-consumer/README.md` | `63a758ee505564cb40b54ca4ebdddfecc32fb65d48776f914bc5bbf25a857645` | `a6cdb5f46a4b8aa3240d96be6ea778973f9c85aafc436efcb8f8001313dfde38` |
| `examples/source-consumer/README.zh-CN.md` | `01eb05203daca2a1082a64c5488053c1aa76c94341a7b56f9af18924e316e0a2` | `c36090e35a14a22120006633e6fe6e35944118fb2ecaa70dfb1be5f2cf2744ba` |

`before/`、`after/`、`15-files-manifest.json`、`15-files.patch` 保存15文件原字节及差异。`frozen-sha256.json` 是 GUI 开始前冻结清单。`repo-tracked-before.json` 与 `git-status-before.txt` 记录写前全仓起点；`concurrent-outside-changes.json` 在冻结时为 `[]`，说明此轮快照区间全仓 tracked 新变化只有上述15路径（主协调之后的机械索引更新单独归因）。原有 dirty/untracked 没有被撤销。

## 4. 公共源码/样式与传递本地依赖清单

唯一公共代码入口 `src/ui/index.ts` 传递导入八组件及 types，共10个本地文件；唯一公共样式入口 `src/ui/styles/index.css` 按 theme → generated profile → components 导入另3个CSS，共4个样式文件。以下17文件覆盖完整 src/ui：14个实际公共入口本地闭包，另加保护 JSON 与不被组件出口导入的纯映射 js/d.ts。没有 CU 私有工作台、locale、启动或 IPC 传递导入。

| 公共文件（CU 相对路径） | 实际 SHA-256 |
| --- | --- |
| `src/ui/components/AgentLayout.vue` | `177f6fe8e009c73fb08a629929ea5260dcffc6bb2210b8acde6ab70941ec85b9` |
| `src/ui/components/AgentSidebar.vue` | `b53495b30e589aed06ba51b470c582fcc1d7984a590c9b0d811e9bb0de629533` |
| `src/ui/components/AgentTopbar.vue` | `25b334b9c88b223d1bd069407f13a517db9cac04527b01bcc15f06c2903f9157` |
| `src/ui/components/ConsoleActionButton.vue` | `7ec106be7d3e3789fcd93e966a5a25bfb1c58e528ca51f3556cf04daf46b7fdb` |
| `src/ui/components/ConsoleCard.vue` | `54e2ce46d726e0eb424aacd5f28df3d5921e5f61a81b0c799ccfac4ddcabf3b4` |
| `src/ui/components/LanguageSwitch.vue` | `e36844e9f693eb6527e76603e6b6d04e8f93f2c3ccabf9013f6b831a99f8c5a1` |
| `src/ui/components/StatusCapsule.vue` | `62e605544f911759b6134482c9c251575fd24a9505d8dd1e336a8b62262439ed` |
| `src/ui/components/ThemeToggle.vue` | `a7429753eee5abb9b8cc04b4a201f4230004c236176ff49bc8c378d73c95c1a2` |
| `src/ui/design-profile.d.ts` | `b21ba90f57fa92e98c61bed14e3922eacb12c167c53c96049dccc95c69f828cf` |
| `src/ui/design-profile.js` | `c36901caa5048df7f6a94fe26cabeec7ea9e527a98ca9c84ebd203d426f4f2c0` |
| `src/ui/index.ts` | `38dcc6404c84144a8da84fc1fc3985f028e1335443261ce68a3a487f798b39b7` |
| `src/ui/styles/components.css` | `734cd1402a71ffe1e3500c128d392c38bcdf8404bc1d008e8098b06268206fbb` |
| `src/ui/styles/design-profile.generated.css` | `ac270f6c0658fe400d356497727bfae865472cdb307d6fb28234cda8c1fb70f2` |
| `src/ui/styles/design-profile.json` | `9591913678f8fd22d6455456c63c8697df68d1210d926475ad4f6271c8d96bf3` |
| `src/ui/styles/index.css` | `4d7113c32d88e12e85a598076eb608e395ef578e5417aeccbe351d4b0e6acdc5` |
| `src/ui/styles/theme.css` | `1c631f285a29f98db9778644c4e95f7311ca1c9ea7bc65b1a62160769914a160` |
| `src/ui/types.ts` | `b0ea3bd1e8d31e4cf26b2068fde4d8199dcf82e23d2112d29db34187b50ae18f` |

**单列原字节保护：** `src/ui/styles/design-profile.json` 与 `src/ui/styles/design-profile.generated.css` 的 before/after SHA 分别为上表 `9591913678f8fd22d6455456c63c8697df68d1210d926475ad4f6271c8d96bf3`、`ac270f6c0658fe400d356497727bfae865472cdb307d6fb28234cda8c1fb70f2`，均完全一致；cardPaddingPx=18、tableDensity=standard。`cu-protected-before.json` 的110个 CU 文件冻结时全部字节一致，包含依赖/锁、配置、AgentLayout/其他公共组件、主题、私有方案实现及原生源码；不执行 apply/import/generate。

外部直接公共导入为 Vue、Element Plus、icons；vue-i18n 仅宿主使用。Node v22.19.0，pnpm 11.11.0；两工程实际解析 Vue 3.5.38、EP2.14.2、icons2.3.2、i18n9.14.5、Vite5.4.21、plugin-vue5.2.4、TypeScript5.9.3、vue-tsc2.2.12。第三方传递包由各自 pnpm-lock 固定（含包 integrity），本轮没有安装或升级依赖。下表是28个依赖/编译边界输入及元数据/CSS的实际 SHA，不冒充整个 node_modules 的逐文件审计；`dependency-inputs-sha256.json` 还保存每个路径的真实解析绝对位置。

| 依赖/编译输入（CU 相对路径） | SHA-256 |
| --- | --- |
| `package.json` | `c3ea10cf9f109683b462792412b669f9171144d8ce591062b1c05d0f74dd53f9` |
| `pnpm-lock.yaml` | `498dca5fc98d502a7d941c3ce821404268e4c787333b7f4c8213545fe71cd421` |
| `vite.config.ts` | `59335177203dba7acea32487f74d2931556f07c36d28cf2af486dea83f5aef96` |
| `tsconfig.json` | `ce374876c5454a081318e28a100fbcbf90daf5904dfcc8deadb74af4a3ea16dc` |
| `src/env.d.ts` | `b46e6fbaefa78bfc4f7341a150e2e737de7b2452298b6d53fb1bb2e191dc7b31` |
| `examples/source-consumer/package.json` | `a299b70c6e7d3d321e21e59da58e6b120776527ca2c6d26fc0891dc877fb0b21` |
| `examples/source-consumer/pnpm-lock.yaml` | `22bf320a65bdef5fbe5092d5675efb0edd1e36f92896d5ac7827ac3fe1552685` |
| `examples/source-consumer/vite.config.ts` | `c2784e4045cb0d71f892c2867add7da932e9d96d97d5755298ce6bf71fe9efdd` |
| `examples/source-consumer/tsconfig.json` | `6e67c5045ff97274cb1b26432081270f1bd975197ac798926a30935f9f8dd19e` |
| `examples/source-consumer/src/main.ts` | `f337a8cc1930f1b8b83ef3a48551f52f766cc6689bab661384ac2034e25b3ea3` |
| `node_modules/vue/package.json` | `7bb90bc1ad93ef2ce102d4252eaef820270eb44c80f4b1018c0f033642bac781` |
| `node_modules/element-plus/package.json` | `48c5111bc6cd8d68f00f325599f3170d6284f372a54a79a52550de19f040ae48` |
| `node_modules/@element-plus/icons-vue/package.json` | `bef1df5b66af31c0cb3164857d70f0db4b768617780dc87a5c7a642b127e9325` |
| `node_modules/vue-i18n/package.json` | `e517320c538239858f1e21aade4fc1ed798313b97a005781bfb4bda35b564ca7` |
| `node_modules/vite/package.json` | `e9802045cdc313b6da55ec2e2dd79312074645816089d64f6021f567c10c0a03` |
| `node_modules/@vitejs/plugin-vue/package.json` | `fe2bf32e4fa92a72b463584da6940b5766b23dfe283a66a80ed1680cefe442b2` |
| `node_modules/typescript/package.json` | `822ef7ca6452205657b6288b066481ecf508bfbf43455d715cf7d3ec457561e6` |
| `node_modules/vue-tsc/package.json` | `1651176df561df8cac64bd333e1bf500923af5e089f13627b370f0ca6c7f6479` |
| `node_modules/element-plus/dist/index.css` | `500a6c15a4d2ccac13d505bc74db7479940a93e0a5f7e606bc5f768c9e2295a9` |
| `examples/source-consumer/node_modules/vue/package.json` | `7bb90bc1ad93ef2ce102d4252eaef820270eb44c80f4b1018c0f033642bac781` |
| `examples/source-consumer/node_modules/element-plus/package.json` | `48c5111bc6cd8d68f00f325599f3170d6284f372a54a79a52550de19f040ae48` |
| `examples/source-consumer/node_modules/@element-plus/icons-vue/package.json` | `bef1df5b66af31c0cb3164857d70f0db4b768617780dc87a5c7a642b127e9325` |
| `examples/source-consumer/node_modules/vue-i18n/package.json` | `e517320c538239858f1e21aade4fc1ed798313b97a005781bfb4bda35b564ca7` |
| `examples/source-consumer/node_modules/vite/package.json` | `e9802045cdc313b6da55ec2e2dd79312074645816089d64f6021f567c10c0a03` |
| `examples/source-consumer/node_modules/@vitejs/plugin-vue/package.json` | `fe2bf32e4fa92a72b463584da6940b5766b23dfe283a66a80ed1680cefe442b2` |
| `examples/source-consumer/node_modules/typescript/package.json` | `822ef7ca6452205657b6288b066481ecf508bfbf43455d715cf7d3ec457561e6` |
| `examples/source-consumer/node_modules/vue-tsc/package.json` | `1651176df561df8cac64bd333e1bf500923af5e089f13627b370f0ca6c7f6479` |
| `examples/source-consumer/node_modules/element-plus/dist/index.css` | `500a6c15a4d2ccac13d505bc74db7479940a93e0a5f7e606bc5f768c9e2295a9` |

## 5. 最终公共 API 示例

实际消费者从 `@aw-ui` 导入 NavigationItem/NavigationChildItem 与组件，从 `@aw-ui-styles` 加载样式，已随最终消费者构建编译：

```ts
export interface NavigationChildItem { id: string; label: string; icon?: Component }
export interface NavigationItem extends NavigationChildItem { children?: NavigationChildItem[] }
const activeId = ref('panel-a')
const items = computed<NavigationItem[]>(() => [
  { id: 'overview', label: t('navigationSample.overview') },
  { id: 'panels', label: t('navigationSample.group'), children: [
    { id: 'panel-a', label: t('navigationSample.alpha') },
    { id: 'panel-b', label: t('navigationSample.beta') }
  ] }
])
```

```vue
<AgentSidebar :items="items" :active-id="activeId" :brand="t('brand')"
  @select="activeId = $event" />
```

Vue Component 来自消费端 Vue 类型；原 UiTheme/UiTone/ActionTone、八组件出口以及 activeId/items/brand/detail/select 均保留。全树稳定非空唯一 id、无递归组、空 children/空 items/unknown active、选择/开合区别、active/焦点寿命、宿主翻译/状态及独立编译边界已记入两层 README pair；不用额外必填参数、Router 或新依赖。

## 6. DEV self-check：真实命令、环境与结果

这些是 Development 自检，主协调 GUI 观察也属于同一 DEV 证据，不是独立 QA verdict。

| 命令 / cwd | 结果与证据 |
| --- | --- |
| 写前 `pwd && git status --short` / 仓根 | exit0；现有其他会话 dirty/untracked 记录在 git-status-before.txt。 |
| Python 标准库 before 快照 / 仓根 | exit0；精确批准 spec SHA 匹配，15文件原字节/全仓tracked SHA/CU保护摘要保存。只作Agent证据辅助，不把helper安装进项目环境。 |
| `pnpm exec vue-tsc --noEmit` / CU | exit0；必要定向类型预检。工具首次shell有只读Homebrew ps权限提示，不影响类型命令结果。 |
| `pnpm exec vue-tsc --noEmit` / source-consumer | exit0；公共新增类型/调用从消费端解析成功。 |
| Python locale/链接/保护定向检查 / 仓根 | exit0；CU154键、consumer42键中英对称且占位符相同；实际两个宿主分别50/39个literal key解析；四README共44个链接核本地目标存在；保护110文件原字节一致；18/standard。static-checks.txt。 |
| `pnpm build` / CU | **最终一次 exit0**；design:profile --check 报 Design profile and CSS are consistent；vue-tsc及Vite成功，1629模块。cu-build.log。 |
| `pnpm build` / source-consumer | **最终一次 exit0**；vue-tsc及Vite成功，1619模块。consumer-build.log；只从公共出口编译，无运行CU前提。 |
| `<CU>/node_modules/.bin/vite build --config /private/tmp/cu-008-r1-development-20261017/fixture/vite.config.mjs` / fixture | exit0；1599模块；使用既有Vite/依赖构建同一个临时正常合同夹具，产物仅/private/tmp。fixture-build.log。 |
| `lsof -nP -iTCP:25193 -iTCP:25194 -iTCP:25195 -sTCP:LISTEN` / 仓根，启动前 | exit1且无输出：三端口均无监听，不停止未知进程。ports-before-start.txt。 |
| `python3 -u /private/tmp/cu-008-r1-development-20261017/launch-preview.py cu` / 仓根，默认沙箱 | exit1；listen EPERM 127.0.0.1:25193，日志保留cu-preview-first-attempt.log。 |
| 同一launcher启动cu/consumer/fixture，已授权require_escalated | 三个own preview服务运行，监听表见下一节；不改配置，未发生自动审批拒绝。默认沙箱CLI HTTP连通探测亦connect EPERM，未把该探测当浏览器结果。 |
| `python3 /private/tmp/cu-008-r1-development-20261017/capture-evidence.py` / 仓根 | exit0；15文件before/after精确patch、17公共文件和28依赖输入SHA、110保护文件一致，冻结源未漂移。 |

构建的非失败提示：两工程/夹具均出现 @vueuse/core PURE annotation 被Rollup移除提示；CU仅有>500kB chunk提示。本轮不为提示改依赖/分包或扩大回归。最终CU产物：index-vKn4p9PQ.css、index-BBVLbv5P.js；consumer：index-C4-vHlK4.css、index-Pr0Z097H.js；fixture：index-DTmXcKaS.css、index-BO2xFOYp.js。

### GUI DEV 自检

2026-10-17 Asia/Shanghai，主协调完成真实 IAB（CUA）辅助 Development 自检并回交完整观察，Development 已完整读取 `/private/tmp/cu-008-coordinator-n9j5lt7c/gui/observations.md`。这不是独立 Verification；没有给 QA verdict。源码、locale、README在操作前全部冻结，三处均消费最终构建preview，没有源码/profile写入。

- **CU / AC02–03、05–06：** 初始中文/light的shell保留四平铺主菜单；独立分组样例初始A、父组展开、count0。选B后count1；点可见组标题折叠，B/count不变，焦点回组。外部按钮B→A并展开父组，不增加选择次数；原Components主导航可进既有页，回Shell正常。切换dark/en保留状态。窄窗经只读DOM确认innerWidth390/innerHeight720后，长英文B可见、可达、可选，当前/count更新B/1。
- **消费者 / AC02–06：** 初始英文/light平铺A/count0；选平铺B再切Grouped保持B/count1并自动展开，旧表格/表单样例保持挂载可见（未做业务回归）。手动折叠在dark+中文切换后仍折叠，B/count1保留，焦点留在语言按钮。外部切A展开父组但count仍1。顶栏hide/restore后重新展开active父组，DOM确认焦点留在顶栏侧栏开关，没有被菜单抢走。
- **键盘 / AC02、04：** 消费者从Overview按Down到组、Right进入A；Enter令count1→2恰一次、Space令2→3恰一次；Left从子项回父组，再Left折叠，焦点留父组且无隐藏tabindex0子项。Tab离开导航到顶栏侧栏开关，Shift+Tab返回可见组。焦点轮廓与当前叶项背景可区分。
- **窄窗日夜双语 / AC05：** 消费者390×720的dark/中文中组和末子项可达，点末项B/count4；切light/en保持B/count4，长英文label可见且周边内容换行。CU另有dark/en桌面与390×720观察。只取这些代表性路径，没有组合矩阵或全量回归。
- **同一有限夹具 / AC01–03：** 初始active-child自动开A、events0；移到Group B保持active/events0并开B，A此前展开保留。unknown/group active无选中叶或合成事件。emptychildren可选，点击只发1次empty-leaf；emptyitems只有品牌区无menuitem、events0。Reset后取消Accept host selection，再点Other child，active仍active-child、events1/last other-child，实际选中仍Initial active child，无持续高亮漂移。

代表性截图/AX/DOM记录在主协调专属 `/private/tmp/cu-008-coordinator-n9j5lt7c/gui/`：cu-desktop-dark-en、cu-narrow-dark-en、consumer-narrow-dark-zh、consumer-narrow-light-en、fixture-host-reject，以及consumer-keyboard-dark.txt、fixture-boundaries.json；关键结果已如上落入本文件。截图不是独立QA替代。主协调目录由主协调拥有，不由Development清理。

真实工具限制一并保留：一次AX点包含子项的submenu未动作，重新定位可见title后成功；一次旧AX index改用当前DOM的semantic locator；浏览器临时tab被会话移除后在同URL重开。视口override起初未传播，DOM仍1280，该批不计窄窗证据；reload后确认390×720才计。均未修改产品源码、改VM状态或清storage。只读DOM检查focus/expanded/active/layout；没有业务/私有端点请求。浏览器viewport最终已reset，tab inventory为空；三服务仍留给freshQA。

GUI后最终冻结摘要、批准spec、110保护文件及whitespace再次核对；结果见final-static-checks.txt，未产生产品修补或额外构建。

## 7. 自有服务、资源与限制

| 服务 / URL | exec session | 实际listener PID / wrapper / launcher | 当前用途 |
| --- | --- | --- | --- |
| CU `http://127.0.0.1:25193/` | 54371 | 74443 / 74421 / 74422 | 最终dist preview；新origin初始中文/light、shell，样例active panel-a，四平铺主导航保留。 |
| consumer `http://127.0.0.1:25194/` | 89874 | 74528 / 74521 / 74522 | 最终独立dist；初始英文/light/flat、panel-a，Grouped radio/外部active/计数/隐藏恢复。 |
| 同一临时fixture `http://127.0.0.1:25195/` | 56982 | 74536 / 74535 / 74536 | 正常合同边界：初始active-child/Group A，空children、空items、active改组/外部/unknown/group、宿主接受/拒绝回写、事件计数。 |

两个项目preview均CLI覆盖host/port，夹具配置只在/private/tmp；没有修改产品端口、Vite/tsconfig或依赖。监听日志 `<name>-preview.log`、启动命令/cwd/PID/session的 `<name>-service.json` 和 services.txt 均在专属证据根。preview没有CU源码写入通道，使用新origin避免干扰用户原15193偏好；不清除用户storage。服务在handoff后留给新的fresh-context QA亲自代表性交互复查，主协调在QA/终验后的适当时点核对并停止本任务服务。没有停止未知或其他任务进程。

专属临时目录中的 fixture/（App.vue/main.ts/index.html/vite.config.mjs、dist、指向既有CU node_modules的symlink）、before/after、launcher/capture helper、SHA与日志均属本轮。两项目自身未跟踪dist为本轮构建产物，预览/QA仍使用，不提前删除。资源回收只归本轮；未新建分支/worktree，通知execution window由主协调拥有，不重复启动或结束。临时证据需在QA/Owner审阅前保留；不将其可能长期存在视为保证。

未运行全量页面/表格/表单/主题编辑回归、Tauri/Cargo/native构建启动、后台/DB/PLC/长稳/跨平台/发布部署。无已批准范围外改动；文案/主题切换及隐藏恢复只按限定导航路径验证。已知限制：合法输入仅二级且全树非空唯一id；不建设树校验器。EP菜单内部DOM类用于最小键盘/焦点适配，未来依赖升级应复查这些有限路径。手动展开随实例卸载丢失，恢复只按active展开父组，符合r1。公共消费是实际工作树字节；源变化后必须重新核对清单，旧hash不能证明新字节。

## 8. Developer handoff

**状态：developer_handoff。** 精确目标为 `aiis-ics-arch::CU-008 r1`，批准spec SHA与第1节一致；工作树 `/Users/jason/Desktop/DreamCode/aiis-ics-arch`，上下文HEAD仍 `f85bea8bbf36b491968c3dc9a839518a1ed434a8`，没有新的commit/ref。实际实现面为第3节15既有路径及本 tasks.md；四索引由主协调在角色事实形成后机械同步。

Development完成R01–R08授权面与上述有限DEV self-check：两处最终build各一次exit0；临时单夹具build exit0；定向类型/locale/链接/保护/whitespace通过；真实GUI代表性导航/焦点/窄窗与合法边界观察已记录。known limitations与未运行范围见第7节，构建非失败warning保留。不把这些写成独立QA或Owner接受。

交新的 `agent_type="verification", fork_turns="none"`：完整读取批准spec、本tasks、当前实现、`15-files.patch`、新增tasks全文（handoff时另存tasks.full.md/tasks.full.patch）、before/after快照与逐文件manifest，核对第4节公共闭包SHA和保护源；可审阅两最终build实际日志，只有证据缺失/疑点时才复跑。QA需亲自代表性交互复查，三个own preview及同一夹具仍运行；不以DEV观察/截图替代。允许主协调四CU索引的后续真实状态同步，其他并发改动须与本轮基线区分。

证据根：`/private/tmp/cu-008-r1-development-20261017`。最终外部receipt `developer-handoff-receipt.json` / `developer-handoff-receipt.sha256` 将保存spec/tasks、15文件patch/manifest、公共源manifest、依赖输入manifest及日志/GUI观察的摘要；tasks自身SHA仅在外部receipt记录，避免自引用。临时资源仍由第7节归属，主协调在QA/终验后核对占用与证据依赖再收尾，不提前停止服务或清资料。

下一gate为新的fresh-context Verification创建checklist并给独立verdict，再由Human Owner final acceptance。DAA接入继续其独立任务；本交接不宣称DAA D02/D04完成、上线、native验证或发布授权。

## 9. 返工与历史

2026-10-17 r1：批准后实际Development实施，收到Owner要求复用frontend-js后在原15路径内收敛视觉，源码冻结前完成；两宿主最终构建成功并冻结，主协调完成有限GUI DEV自检，无产品缺陷或源码返修。旧AX句柄/视口传播/临时tabs问题如第6节记录，未归成产品失败。当前无未解决的批准范围内Development阻塞；QA/Owner gate仍pending。
