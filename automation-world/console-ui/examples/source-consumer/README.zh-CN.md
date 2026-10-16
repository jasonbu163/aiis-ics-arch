# 公共 UI 源码消费者

[English](README.md)

本最小应用归 CU 管理，只把公共 UI 入口编译进自身 Vite 产物。不导入 CU 工作台、App、私有 locale 实例、IPC、Rust 或工业配置。文案和状态由消费端拥有，示例均标识为**设计样例**。

## 在本目录运行

```bash
pnpm install --frozen-lockfile
pnpm build                 # vue-tsc + 自身 dist
pnpm dev                   # strict 15194，需可访问源码
pnpm preview               # strict 14194，仅自身 dist
```

示例有自己的依赖声明、锁文件和 node_modules，不属于根 workspace，运行时不使用 CU node_modules。构建后可用任意静态服务器托管本目录 `dist`；先停止 CU 的浏览器/原生进程即可证明独立运行。运行时只复制 dist 即可，部署静态服务器不需要 CU 源码、依赖目录、pnpm、Cargo 或 CU HTTP 服务。

## 从已有 Vue/Vite 消费端开始

1. 编译时显式提供公共 `src/ui/` 源码，可以指向相邻 checkout，或仅复制公共目录进入消费端并保留内部相对导入。不要复制 CU App/main/workbench/locales/Rust。消费项目应在自身治理中固定源码版本；本任务没有 npm 包/版本发布流水线。
2. 安装本例 package.json 声明版本，或消费端已有兼容版本。验证版本：Vue 3.5.38、Element Plus 2.14.2、icons 2.3.2；Vite 5.4.21、plugin-vue 5.2.4、TypeScript 5.9.3、vue-tsc 2.2.12。示例私有使用 vue-i18n 9.14.5；公共组件不要求 i18n 实例。不要为 UI 再安装第二个 Vue/i18n app。
3. Vite 设置精确别名和 dedupe，按 checkout 调整相对路径：

```ts
resolve: {
  alias: {
    '@aw-ui': fileURLToPath(new URL('../../src/ui/index.ts', import.meta.url)),
    '@aw-ui-styles': fileURLToPath(new URL('../../src/ui/styles/index.css', import.meta.url))
  },
  dedupe: ['vue', 'element-plus', '@element-plus/icons-vue', 'vue-i18n']
}
```

`fileURLToPath`、`URL` 从 `node:url` 导入，完整写法见 [vite.config.ts](vite.config.ts)。开发态引用 Vite root 之外源码时，使用 `server.fs.allow` 显式允许源码目录。[tsconfig.json](tsconfig.json) 的 paths 把公共入口以及 Vue/Element Plus/icons 类型解析到本消费端声明。保持相同解析版本和单一运行实例，无需导入 CU 启动代码。

4. 自己的启动代码按顺序导入样式，只安装自己的 app/plugins：

```ts
import 'element-plus/dist/index.css'
import '@aw-ui-styles'
// createApp(YourApp).use(yourI18n).mount('#app')
```

5. 在自己的页面组合导出组件，完整实现见 [App.vue](src/App.vue)：

```vue
<AgentLayout :theme="theme">
  <template #sidebar>
    <AgentSidebar :items="items" active-id="sample" :brand="t('brand')" />
  </template>
  <template #topbar>
    <AgentTopbar :title="t('title')" :sidebar-label="t('sidebar')">
      <template #actions><!-- 消费端动作 --></template>
    </AgentTopbar>
  </template>
  <ConsoleCard :title="t('sample')">
    <StatusCapsule :label="t('sample')" tone="warning" />
  </ConsoleCard>
</AgentLayout>
```

上述组件从 `@aw-ui` 导入。`AgentLayout` 接收 `theme: 'light' | 'dark'`、`sidebarHidden`，提供 sidebar/topbar/default slots。`AgentSidebar` 接收翻译后的 `{id,label,icon?}` 导航，发出 `select(id)`。`AgentTopbar` 接收 title/subtitle/sidebarLabel，发出 `toggle-sidebar`。`ConsoleCard` 支持 actions/tools/default/footer slots 与 compact。`ConsoleActionButton` 接收已翻译 label/title 或 slot、tone、small/large 尺寸，发出 click。`StatusCapsule` 接收 label 及 neutral/success/warning/danger 展示色调；这些是展示值，不是设备状态。

语言安装完全归消费端：创建或复用自己的 vue-i18n，加载对称 locale，再传入 `t(...)` 结果。主题通过 AgentLayout 显式安装；单独使用组件时用 `.aw-ui` 与 `data-aw-theme="light"` / `"dark"` 包裹，Element Plus 控件也应置于该作用域。body reset 和样例间距由消费端 CSS 管理。公共代码/样式不写 storage、不创建 app、不联系 CU；本示例刻意不持久化偏好。

`ThemeToggle` 接收 `theme: UiTheme` 和翻译后的目标动作 `label`；`LanguageSwitch` 接收 `locale: 'zh-CN' | 'en-US'`、翻译后的 `zhLabel` / `enLabel`（通常为“中” / “EN”）及目标动作 `label`。二者均仅发出 `toggle`，不修改状态或写入 storage。label 同时提供原生 tooltip 与可访问名称，主题按钮还表达当前暗色状态。通过 `@aw-ui` 导入并放在公共样式作用域内，由宿主处理事件和更新 props。CU 保留既有 UI 偏好，消费者拥有独立状态且不持久化；消费者构建产物无需 CU 在线。

6. 执行 `pnpm build`，停止 CU，然后 `pnpm preview`。编译后的 JS/CSS 全在自己的 dist，无 chunk 指向 CU dist 或开发端口。实际 Agent 接入、发布与业务配置属于另行批准工作。

归属见 [CU README](../../README.zh-CN.md)，本基础任务由 [CU PLAN](../../PLAN.zh-CN.md) 索引。

## Element Plus 页面组合

CU 私有的**页面样例**演示表格、校验表单、编辑弹窗及手动选择的正常/加载/空数据/失败状态。数据与重试/提交/编辑反馈只在内存中，刷新会重置样例。八个公共组件及 API 保持不变。独立消费者直接用自身 Element Plus 依赖组合更小的表格/表单/弹窗，拥有自己的 locale 与状态，不导入 PageSamples 或工作台文件。

先导入 Element Plus CSS，再导入 `@aw-ui-styles`。`ElTable` 使用 `aw-data-table`，`ElForm` 使用 `aw-sample-form`，动作区使用 `aw-form-actions`，状态内容使用 `aw-page-state`。公共 CSS 将 Element Plus 变量映射到当前作用域的 `--agent-*` tokens；页面布局由各宿主负责。这些类是样式约定，不是新增公共 Vue 组件。

脱离布局的弹窗需要显式主题作用域。本例用 Vue `Teleport to="body"` 包裹 `<div class="aw-ui aw-sample-overlays" :data-aw-theme="theme">`，其内嵌套 `:append-to-body="false"` 的 `ElDialog`。每个 `ElSelect`（包括弹窗内）使用 `:teleported="false"`，使下拉继承该作用域。主题容器持续绑定宿主主题，并通过 `ElConfigProvider` 提供宿主 Element Plus 语言；不设置全局 html/body 主题变量。标签、校验、反馈及所有状态切换归宿主负责。此样例不保存业务数据、草稿或生成样式方案。

## 样式方案：预览、草稿与共享源码

CU 参数页编辑有限的 schemaVersion 1 方案：明暗 palette 各有 background、surface、surfaceMuted、text、textMuted、border、accent、accentStrong、onAccent（仅 `#RRGGBB`，规范化为小写）。共享整数为 cardPaddingPx 12–32（默认24）、actionGapPx 4–24（12）、cardRadiusPx 8–28（20）、controlRadiusPx 4–20（14），单位均为px；tableDensity 为 standard（默认，单元格垂直padding为8px）或 compact（4px）。compact卡片内边距/圆角及small控件圆角由其派生。默认配色值仅归公共JSON；状态色、装饰玻璃/阴影、布局与44px顶栏控件保持固定。

有效编辑同步预览于工作台根和页面样例显式弹层作用域，不改变宿主theme/locale。无效字段保留上一次有效预览，禁用保存/导出。首次打开始终使用编译时公共默认。保存/恢复/重置均显式执行，只触达 `cu.design-profile.draft.v1`；主题/语言键和业务样例分离。草稿仅属于当前CU浏览器/WebView/origin，消费者及其他Agent不读取。缺失/损坏草稿回到公共默认并反馈，存储失败如实提示。重置恢复公共默认并仅删除本草稿。JSON导出为可复制文本，不是原生文件写入或源码更新。

[design-profile.json](../../src/ui/styles/design-profile.json) 是唯一可编辑的公共默认源；[design-profile.generated.css](../../src/ui/styles/design-profile.generated.css) 是确定性生成结果，不可手改。纯JS校验/映射由预览和CLI复用，固定主题tokens保留在theme.css。公共样式按固定主题→生成方案→组件顺序加载，消费者继续用同一公共样式入口和组件API。

在CU目录执行：

```bash
pnpm design:profile                         # 仅帮助，无读写
pnpm design:profile --help                  # 同上
# 先将导出JSON复制到明确的本地文件：
pnpm design:profile --import /absolute/path/profile.json
pnpm design:profile --generate              # 从公共JSON重新生成固定CSS
pnpm design:profile --check                 # 只读一致性检查
pnpm build                                 # 先check，不隐式生成
```

所有字段必填；未知字段、路径、任意CSS/脚本、非法类型/颜色/范围/版本在目标写入前拒绝。导入只通过单文件安全替换更新固定CU公共JSON/CSS，不承诺两文件事务。CSS缺失/stale时执行 `--generate` 再 `--check`；公共JSON损坏时先从有效备份恢复，再生成。I/O失败返回非零，应检查两个目标、必要时恢复有效JSON，再generate/check；导入前自行备份有效公共方案。

共享流程为导出→显式工程导入→generate/check→宿主开发刷新或重构建。既有消费者源码不变，通过正常公共样式入口消费生成CSS，自身dist不需要CU在线且不读CU草稿。DAA/SMA本任务未接入；后续宿主自行同步与构建，已安装桌面二进制须重构建及分发，不承诺实时传播或依赖在线CU。
