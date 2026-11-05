# SMA app 模块

[English](README.md)

`connection`拥有唯一的本地Backend连接和显式门禁OpenAPI检查；`twin-facts`拥有只读源检查、本地材料/目标/规则/映射、文件交换与运行诊断。事实生产、Simulation和帮助继续退役。根registry与locale合并显式装配，不宣称菜单自动生成。

业务链为组件 → 模块store → `twin-facts/api/localConfiguration.ts` → 薄Tauri commands → Rust service/domain → SMA自有SQLite singleton。UI缓存是已观察快照和未保存表单。编辑器保留加载时revision，文件/资源预览保留规范内容和revision；保存不得先读新revision掩盖旧草稿。历史`*FromBackend`配置facade名称现在仅委托本地IPC。只有显式源事实/OpenAPI刷新通过HTTP gate读远端，不fallback到TSS配置或审计。

材料工作区先做本地OpenAPI JSON preview/apply，再保存选择。原资源JSON/XLSX helper仍为纯文件适配器。整包备份/恢复在原配置操作区，先显示替换/删除并显式确认。已保存映射预览使用Rust当前保存revision，不接收编辑器bindings。源身份是`sourceKey + factName`；最小元数据保存来源证据，不含事实值，缺值保持缺失。

新增页先建立模块组件与对称locale，再显式更新manifest/registry及locale装配。复制模块改owner/id/import/key，不携带客户资源。不交付常驻mock API。执行`pnpm check/test/build`与匹配Rust回归；模块交付gate归SMA PLAN和任务bundle。

`store/mappingStartup.ts`保留Mapping技术启动偏好及惰性v1磁盘兼容；本阶段原生准入拒绝全部正常投递。`src/console/tableWidths.ts`统一稳定ID本机列宽与每表重置，`src/console/time.ts`按上海时区格式化明确日历时间。主题、语言与列宽不改业务revision、不进备份。

CU装配留在App.vue，组件仅导入公共`@aw-ui`；挂载ElDialog前保留主题弹层宿主。原生SQLite验证、内存IPC测试与浏览器UI检查分别记录，不能互相冒充。
