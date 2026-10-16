# Console UI 源码层次

[English](README.md)

CU 是设计工作台，不是工业业务模块宿主。来源副本的 `runtime`、`collection`、`plc`、`gates` 模块及其运行适配器已移除；当前没有 module manifest 发现、路由自动注册、API/mock 适配器或业务菜单自动组装。

公共展示归 `src/ui/`，只通过 `index.ts` / `styles/index.css` 导出。私有工作台归 `src/workbench/`，双语文案归 `src/locales/`。App.vue 只组合入口，main.ts 负责应用安装，Rust 只启动桌面窗口。公共源码不得导入工作台、应用启动、Tauri 或 CU locale 实例。

从零手工增加有边界的设计样例：先在两份 workbench JSON locale 加入对称键，再在 `Workbench.vue` 组合公共出口，样例布局放 `workbench.css`。独立样例页可在 `src/workbench/` 建私有 Vue 文件，由 Workbench 显式导入并增加显式导航；不宣称自动注册。复制样例时重命名组件与 locale 键，并检查双语。所有样例区域保留“设计样例”标识且无设备副作用。新业务/Agent 模块需另行批准任务。

新增获批公共原语：在 `src/ui/components/` 建 Vue 文件，以已翻译 props/slots/events 为合同，从 `src/ui/index.ts` 导出，并把 token 样式纳入公共样式入口。依赖只能在公共层或消费端拥有的 Vue/Element Plus 包内。构建 CU 与[消费示例](../../examples/source-consumer/README.zh-CN.md) 验证出口；源码路径、依赖单实例安装步骤见该教程。
