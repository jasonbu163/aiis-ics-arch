# DAA app 模块

[English](README.md)

垂直 `src/app/<module>` 模块拥有视图、翻译与纯导航元数据。`runtime/manifest.ts` 注册工作台，`plc/manifest.ts` 注册 PLC 配置，`plc/points-manifest.ts` 注册点位/采集组，`collection/manifest.ts` 注册上报/存储。`console/sections.ts` 显式组装四叶页，宿主经 CU 把后三页归入配置中心；没有 Vue Router 或自动权限/菜单组装。原 collection status 保持工作台面板；旧授权界面与运行PLC选取组件退役。

`App.vue` 只实例化 `useLocalAcquisitionConsole`；`useAgentConsoleShell` 只管导航/主题/语言，无IPC/fetch。四叶注入同一local owner；Layout/Sidebar只用安全bootstrap身份/版本。浏览器无桥预览与原生bootstrap失败分开，无假库/假保存或Backend health请求。YAML迁入归锁后的启动服务，普通编辑导入只接.db/.udt。正常四页及运行/版本详情不展示迁入历史或入口。仅持久化unknown（优先）或failed且Rust返回retryAllowed=true时显示紧凑当前故障入口和小弹窗；unknown无重试，安全重试沿busy/dirty/editing门禁及ETag/attempt双CAS。开关弹窗零写，正常/null摘要卸载弹窗。

从零建立模块时，创建 `views/<page>/index.vue`、`locales/zh-CN.json` / `en-US.json` 及纯 `ConsoleSectionManifest`；在另获批准范围内向 `console/sections.ts` 显式注册、更新有限 section ID 与根组合，并说明运行边界。复制模块时同步更名目录、manifest ID、导入及 locale namespace；复制不会自动注册页面或授权运行调用。保持模块局部导入，产品视图不放长期 demo/mock 数据。

用 DAA `pnpm build`、locale 键/占位符/literal-key 核对及挂载前阻断 IPC 与健康探测的隔离浏览器验证导航/状态。新现场能力须单独实施和审核。

本地模式由 `useLocalAcquisitionConsole` 持有草稿编辑基线 ETag、版本/快照、有限结果、历史和唯一 1Hz 刷新。后台轮询不替换编辑基线，避免自动取得新 ETag 后覆盖旧编辑。四个叶视图注入同一 owner；新 `services/localAcquisition.ts` 只调用具名 Tauri IPC，不提供浏览器假桥。Rust 为源结构和派生字段权威，页面确认不替代服务校验。原生证据及交付状态见 owning DAA-002 tasks。

本地页面复用CU卡片/动作/表格薄适配及Element Plus表单。PLC与点位编辑弹窗的“保存草稿”与顶部入口使用相同Rust/CAS调用提交完整候选；仅成功回执后收起，失败保留输入，取消不写入，激活仍显式独立。版本身份、完整源树、地址辅助与物理空间按需展开；未保存编辑会阻止导入/偏移确认，避免服务端回执静默替换当前候选。

点位来源区域复用私有`plc/components/SourceImportPanel.vue`；唯一local owner持有严格字节解码/证明、自动Rust识别、跨页逐块映射和预览/ETag资格。组件仅展示，不另建parser/轮询/IPC。主区保持紧凑，导入差异/定位诊断/完整树使用弹窗，偏移详情另用弹窗；关闭预览零写并保留选择。弹窗内一次显式确认保存草稿，人工保护/来源身份仍由Rust重核；映射/编辑/重载冲突使确认失效。稳定流程及语法/布局边界见[DAA README](../../README.zh-CN.md)。

普通`pnpm tauri dev`使用本仓package→Tauri beforeDevCommand→Vite15191与`src/main.ts`及本仓`src-tauri`入口。验收不自动复制临时代码或更新安装包。`yaml_migration_skipped`伴随persisted的imported状态表示既有receipt阻止重扫；`runtime_started` stopped和`runtime_stopped` clean描述启动意图和正常关闭，不表示失败。

Point.name为ASCII技术名，sourcePath原路径与稳定ID分开；唯一可选JSON nameMode为缺失legacy或pending/auto_path/auto_address/manual。legacy读取零写回，转换需明确勾选及预览。pending为空且停用，既有地址确认原子成名。唯一owner持有选择/预览/token，私有分页PointNamePreviewDialog及原编辑/offset弹窗展示差异；无第二owner/DDL/key。普通save不能去除/伪造mode或绕过改名预览。历史JSON/receipt原bytes保持，旧binary降级另核。
