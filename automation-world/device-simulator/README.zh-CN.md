# 设备模拟器

独立 S7 PLC 模拟器，派生并复用 DAA 适用桌面装配。六页面 Tauri/Vue 应用与测试宿主共用同一 Rust runtime。Rust 拥有配置、DB image、全部写入、规则与控制；有限 Snap7 适配层只负责协议、socket IO 和原生 worker 生命周期。不需要运行 DAA、SMA 或 Backend。

[完整操作手册](USER_GUIDE.zh-CN.md) · [构建与运行](BUILD.zh-CN.md) · [计划](PLAN.zh-CN.md) · [Runtime](runtime/README.zh-CN.md) · [原生适配](native/README.zh-CN.md) · [测试](tests/README.zh-CN.md) · [详细设计](../../docs/AIIS_DS_Detailed_Design.md)

产品从空配置和停止状态开始。配置 UUID 实例与 DB，显式选择 DB/UDT 声明导入或手工创建点，确认地址、名称、初值和策略，保存不可变版本，再停机应用；启动是独立动作。在线值、连接及有界日志显示实际运行事实；浏览器预览不能执行桌面操作。

13处页面/预览表格共用Element Plus薄封装，消费DAA/CU主题与密度。普通列拖拽调整，按应用、稳定表格ID及字段键在本机WebView记忆；每表有“恢复默认列宽”。偏好不进入业务SQLite或保存版本，不改变筛选、选择、分页和权限判断。普通长文省略悬停查看，表内滚动；窄容器取消右侧冻结以免遮挡。操作见[手册§1.1](USER_GUIDE.zh-CN.md#11-所有表格的列宽与查看操作)。

每个 profile 拥有独立 `device-simulator-v1/config.sqlite`、OS profile 锁及持久 WebKit data-store UUID。默认使用 Tauri 的 DS 应用本地数据目录；可选 `DS_PROFILE_DIR` 接受显式绝对路径。未知、损坏、不兼容或只读数据库拒绝打开并保留原件。运行值、连接和运行意图不持久化：重开按 selected 版本初始化并保持 stopped。saved、selected、loaded 分开记录。

源码开发在 `automation-world/device-simulator/.env` 仅可选填写 `DS_PROFILE_DIR`，由Owner手工从本目录 `.env.example` 复制后编辑，已有文件不覆盖。选择顺序为非空进程 > 自身.env非空值 > Tauri原默认目录；空键表示未设，不等于新空目录。绝对字面路径不展开`~`/变量、不允许父目录穿越或既有symlink，非法选择在锁/库/日志前拒绝，不降级默认。简单KEY=VALUE仅去一层配对引号，重复键首项生效，不搜索父目录/另一个应用.env或执行shell。一次配置后正常启动仅 `pnpm tauri dev`，Tauri沿用`native-s7`；UI+SQLite管理实例/点位/策略，保存、停机加载、工作台启动分开，启动/重开仍stopped。dev/build不会自动隔离数据；安装版.env发现/分发不在本次支持承诺内。DAA-007 r2新增bootstrap合同仍待本任务独立核验，不倒记为DS旧验收。

日历时间统一按 Asia/Shanghai（UTC+08:00）显示到秒，不跟随电脑时区，原始毫秒保留。在线值的 `updatedAt` 表示初始化或最近成功提交的日历时间，`updatedNs` 继续保留单调计数；刷新或规则值未变时不推进更新时间。新日志带有 `+08:00` 的 RFC3339 `timestamp`；`monotonic_ns` 仍是独立的排序/耗时计数。未记录日历时间的旧日志明确标识，不推算日期。版本界面使用真实序号摘要及一致/待加载提示，完整身份、三类状态和解释收在问号悬停提示中。既有 SQLite `*_utc` 字段和版本内容保留原 UTC 格式，显示时转换一次；本次不做数据库结构或历史数据迁移。新增原生时间字段在开发进程重新编译/启动后生效。


按[纯文字操作手册](USER_GUIDE.zh-CN.md)先做手工DB31，再显式导入Alpha/Beta/Measure。当前草稿策略表支持PLC/DB筛选、稳定ID的全筛选跨页选择、单点副本弹窗与三态批量覆盖/全量预校验。手册覆盖普通键入初值7/20.5、fixed12、继承、失败恢复与版本选择。[DS-001 tasks](plans/DS-001-policy-table-and-usability/tasks.md)保留原Development自检及当时的人工交接边界，[Owner验收记录](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)另记真实最终决定；既有图片保留为历史资料。

现有实现及历史核验范围归 [ARCH-AW-005 r5](../../plans/ARCH-AW-005-ds-g0-prototype-validation/spec.md)。[tasks](../../plans/ARCH-AW-005-ds-g0-prototype-validation/tasks.md) 记录 DEV 执行及限制；最新独立 Verification 和 Human Owner 状态见 [owning checklist](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md)。废弃 G0 入口已在原字节持久归档及产品验证后退役；逐文件迁移和清后检查见所属 tasks，历史证据继续保留。DAA 应用 S7→SQLite 联调、阶段 C、真实设备、完整 PLC CPU 行为与跨平台打包不在本任务内。

后续产品迭代由本工程 [PLAN](PLAN.zh-CN.md) 与 [任务目录](plans/README.zh-CN.md) 管理。Human Owner已于2026-10-27（Asia/Shanghai）最终接受DS当前版本、DS-001 r1及ARCH-AW-005 r5；[DS-001验收](plans/DS-001-policy-table-and-usability/spec.md#owner-acceptance-ds001)及[r5验收/收尾](../../plans/ARCH-AW-005-ds-g0-prototype-validation/checklist.md#owner-acceptance-r5)分别保留原开发自检、历史独立QA与Owner决定。DS-001独立QA仍按明确例外未执行，本次只收尾、未追加功能或整套QA。历史证据和仍在使用的开发资源保留；DAA–DS读取至SQLite联调另批，阶段C暂不开展。
