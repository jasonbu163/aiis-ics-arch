# Control Agent app 模块

控制台采用垂直的 `src/app/<module>` 结构。每个模块拥有自己的视图、局部
组件、翻译和路由元数据；共享壳层与运行时适配器放在模块之外。

模块应保持局部导入，用户可见文案放在模块 locale 文件中。控制台是现场运维
界面，不复制 Core Web 应用的业务页面或整套 CSS。新增现场模块必须说明运行
边界，并在现场配置审核前保持关闭。

[流程编辑器](flow-editor/Workspace.vue)组织工作台与画布。[PLC 与点位](plc-catalog/PlcResources.vue)、[HTTP 连接](http-connections/HttpResources.vue)和[单节点测试](node-tests/NodeTester.vue)通过 `src/services` 调用对应 Rust IPC。
