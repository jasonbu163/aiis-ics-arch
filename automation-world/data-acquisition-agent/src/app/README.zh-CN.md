# DAA app 模块

[English](README.md)

垂直 `src/app/<module>` 模块拥有视图、翻译与纯导航元数据。`runtime/manifest.ts` 注册工作台，`plc/manifest.ts` 注册 PLC 配置，`plc/points-manifest.ts` 注册点位/采集组，`collection/manifest.ts` 注册上报/存储。`console/sections.ts` 显式组装四叶页，宿主经 CU 把后三页归入配置中心；没有 Vue Router 或自动权限/菜单组装。原 collection status 保持工作台面板；旧授权界面与运行PLC选取组件退役。

`App.vue` 只实例化 `useLocalAcquisitionConsole`；`useAgentConsoleShell` 只管导航/主题/语言，无IPC/fetch。四叶注入同一local owner；Layout/Sidebar只用安全bootstrap身份/版本。浏览器无桥预览与原生bootstrap失败分开，无假库/假保存或Backend health请求。DAA-007 r2已将YAML迁入退出普通启动、reload和save，配置栏不挂接迁入故障弹窗/重试。既有SQLite私有receipt/source归档保留，显式兼容summary只读且retryAllowed=false，retry写前拒绝；普通结构导入仍仅接受.db/.udt。

从零建立模块时，创建 `views/<page>/index.vue`、`locales/zh-CN.json` / `en-US.json` 及纯 `ConsoleSectionManifest`；在另获批准范围内向 `console/sections.ts` 显式注册、更新有限 section ID 与根组合，并说明运行边界。复制模块时同步更名目录、manifest ID、导入及 locale namespace；复制不会自动注册页面或授权运行调用。保持模块局部导入，产品视图不放长期 demo/mock 数据。

用 DAA `pnpm build`、locale 键/占位符/literal-key 核对及挂载前阻断 IPC 与健康探测的隔离浏览器验证导航/状态。新现场能力须单独实施和审核。

本地模式由 `useLocalAcquisitionConsole` 持有草稿编辑基线 ETag、版本/快照、有限结果、历史和唯一 1Hz 刷新。后台轮询不替换编辑基线，避免自动取得新 ETag 后覆盖旧编辑。四个叶视图注入同一 owner；新 `services/localAcquisition.ts` 只调用具名 Tauri IPC，不提供浏览器假桥。Rust 为源结构和派生字段权威，页面确认不替代服务校验。原生证据及交付状态见 owning DAA-002 tasks。

本地页面复用CU卡片/动作/表格薄适配及Element Plus表单。PLC弹窗保存完整候选，点位弹窗通过Rust命名预览/确认保留校验与CAS；仅成功回执后收起，失败保留输入，取消当前单点编辑不提交该点。页面已有未保存组名、周期或分组时，行按钮显示“保存草稿并编辑”，先CAS保存现有草稿，成功后才打开点位副本；新回执、重载及关闭同步释放编辑状态。激活仍显式独立。版本身份、完整源树、地址辅助与物理空间按需展开；未保存编辑会阻止导入/偏移确认，避免服务端回执静默替换当前候选。

点表勾选统一用于技术名预览和批量分组/停用，同一PLC内跨页、DB及搜索筛选保留。批量动作只处理有效勾选ID，零选择禁用，不回退为全部筛选点；选择数量在点表及采集组区域显示。忙碌或单点编辑期间禁止修改组，保存本身不激活或连接PLC。

点位来源区域复用私有`plc/components/SourceImportPanel.vue`；唯一local owner持有严格字节解码/证明、自动Rust识别、跨页逐块映射和预览/ETag资格。组件仅展示，不另建parser/轮询/IPC。主区保持紧凑，导入差异/定位诊断/完整树使用弹窗，偏移详情另用弹窗；关闭预览零写并保留选择。弹窗内一次显式确认保存草稿，人工保护/来源身份仍由Rust重核；映射/编辑/重载冲突使确认失效。稳定流程及语法/布局边界见[DAA README](../../README.zh-CN.md)。

普通`pnpm tauri dev`使用本仓package→Tauri beforeDevCommand→Vite15191与`src/main.ts`及本仓`src-tauri`入口。验收不自动复制临时代码或更新安装包。`yaml_migration_skipped`伴随persisted的imported状态表示既有receipt阻止重扫；`runtime_started` stopped和`runtime_stopped` clean描述启动意图和正常关闭，不表示失败。

Point.name为ASCII技术名，sourcePath原路径与稳定ID分开；唯一可选JSON nameMode为缺失legacy或pending/auto_path/auto_address/manual。legacy读取零写回，转换需明确勾选及预览。pending为空且停用，既有地址确认原子成名。唯一owner持有选择/预览/token，私有分页PointNamePreviewDialog及原编辑/offset弹窗展示差异；无第二owner/DDL/key。普通save不能去除/伪造mode或绕过改名预览。历史JSON/receipt原bytes保持，旧binary降级另核。

DAA-007由`console/time.ts`统一历史、陈旧快照及最老pending的上海墙上时间/秒显示。历史表和样本点位结果表消费`console/tableWidths.ts`，分别按稳定字段key设置最小宽、本机记忆与恢复，不更改业务配置/版本。原JSON精度和SHA保留。不支持的时间profile保留无engine原生诊断壳并显示具体bootstrap拒绝。新profile兼容边界及Owner原生步骤见[联调手册](../../JOINT_TEST_GUIDE.zh-CN.md)。

“查看样本”依次展示只读摘要、点位结果表（默认每页20条，可选10/20/50）及默认折叠的样本/manifest/配置JSON。`LocalSampleDetail.vue`从冻结配置上下文取名称，从原始点位事实取值、地址、质量和时间，不读取当前草稿补写历史。上报pending显示为“待上报”，与采集质量分开。`console/sampleDetails.ts`仅格式化JSON字符串以外的空白，保留数字词法及转义；显示的SHA-256仍对应原始字符串。展开后才渲染JSON正文。展示辅助不调用IPC、不写持久化数据，也不确认样本上传。
