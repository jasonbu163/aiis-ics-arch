# DS 前端模块

`simulator/manifest.ts` 注册 DS locale；`console/sections.ts` 显式登记六页面导航。DAA 派生壳、CU 主题/语言控件和 Element Plus provider 保留为展示基础设施，不注册 DAA 采集、SQLite client、上传或历史模块。

六页面与有界编辑/确认组件消费 `services/deviceSimulator.ts` 的正常 21 命令 facade。`useDeviceSimulator` 是宿主状态 owner：dirty 草稿、saved 配置和实际 runtime 快照分开；可见时刷新不超过 1 Hz，stale 失败保留最后合法快照，实例/分页身份丢弃迟到响应。导入、布局、命名、策略、编码、规则与 CAS 均由 Rust runtime 执行，Vue 不重复业务算法。

用户文案归对称 `simulator/locales/en-US.json` 与 `zh-CN.json`。技术 UUID 及实际 DB/byte/bit/revision 按事实显示，不从可编辑草稿推断。浏览器没有桌面 bridge，不能返回模拟 IPC 成功。原生 driver 是非默认固定测试面，不是前端模块或产品控制 API。

版本列表消费Rust的canDelete与引用原因；表头只选当前页可处理项，翻页/刷新清空选择。共享RevisionOperationDialog列出批量清单和全部回退实例，须勾选确认放弃后才提交；不在Vue自行解除引用。宿主refreshRevisions只刷新版本事实、不覆盖本地草稿，丢弃迟到旧结果；取消或离开页面释放本页预览，迟到的预览响应也释放而不重新打开。重复加载保留回退记录的语义归Rust。手工确认步骤见产品手册§2.8，不以编译冒充原生验收。
