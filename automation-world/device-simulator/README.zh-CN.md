# 设备模拟器

独立 S7 PLC 模拟器，派生并复用 DAA 适用桌面装配。六页面 Tauri/Vue 应用与测试宿主共用同一 Rust runtime。Rust 拥有配置、DB image、全部写入、规则与控制；有限 Snap7 适配层只负责协议、socket IO 和原生 worker 生命周期。不需要运行 DAA、SMA 或 Backend。

[完整操作手册](USER_GUIDE.zh-CN.md) · [构建与运行](BUILD.zh-CN.md) · [计划](PLAN.zh-CN.md) · [Runtime](runtime/README.zh-CN.md) · [原生适配](native/README.zh-CN.md) · [测试](tests/README.zh-CN.md) · [详细设计](../../docs/AIIS_DS_Detailed_Design.md)

产品从空配置和停止状态开始。配置 UUID 实例与 DB，显式选择 DB/UDT 声明导入或手工创建点，确认地址、名称、初值和策略，保存不可变版本，再停机应用；启动是独立动作。在线值、连接及有界日志显示实际运行事实；浏览器预览不能执行桌面操作。

每个 profile 拥有独立 `device-simulator-v1/config.sqlite`、OS profile 锁及持久 WebKit data-store UUID。默认使用 Tauri 的 DS 应用本地数据目录；可选 `DS_PROFILE_DIR` 接受显式绝对路径。未知、损坏、不兼容或只读数据库拒绝打开并保留原件。运行值、连接和运行意图不持久化：重开按 selected 版本初始化并保持 stopped。saved、selected、loaded 分开记录。


按[完整操作手册](USER_GUIDE.zh-CN.md)先跑手工DB31，再显式导入Alpha/Beta与UDT。手册标明当前非零初值/持续固定值输入限制，以显式0/false完成可执行案例，再用普通运行值写12示范。这个未关闭产品问题、文档核验与此前技术QA记录分别保留。

实现范围归 [ARCH-AW-005 r5](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)。[tasks](../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) 记录 DEV 执行及限制；最新独立 Verification 和 Human Owner 状态见 [owning checklist](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md)。废弃 G0 入口已在原字节持久归档及产品验证后退役；逐文件迁移和清后检查见所属 tasks，历史证据继续保留。DAA 应用 S7→SQLite 联调、阶段 C、真实设备、完整 PLC CPU 行为与跨平台打包不在本任务内。
