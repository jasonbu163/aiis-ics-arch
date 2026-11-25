# SMA app 模块

[English](README.md)

`connection` 维护已保存的后台地址与 OpenAPI 目录。`http-mapping` 提供 GET 来源和点位、目标和映射操作，以及采集与上报独立控制。`configuration-management` 集中管理本地文件交换。`App.vue` 显式装配八个工作区及其中英文导航。

配置编辑器保留打开时的 revision，保存与确认导入均需匹配这一 revision。`twin-facts/api/localConfiguration.ts` 委托 Rust 原生配置命令。HTTP 来源测试、快照和 POST 预览使用 HTTP 映射命令。已冻结的请求和来源版本由 Rust 持有，操作人确认预览后才发送。原采集只读适配器继续提供采集选项与历史检查。

使用 CU 公共 UI 入口，并复用 `src/console/tableWidths.ts` 中的 SMA 表格列宽偏好。界面偏好与最新事实不进入配置交换。用户可见文案使用对称的中英文键。
