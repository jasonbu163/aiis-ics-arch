# SMA app 模块

[English](README.md)

connection拥有通用Backend bootstrap/OpenAPI；twin-facts拥有HTTP事实、材料、目标API、值规则、映射和Simulation辅助；help只读取本地双语说明。registry手工装配这三个归属，locale在根显式合并，无菜单/路由自动生成承诺。

新增页先在对应模块创建views/components和对称locale，再显式更新manifest/registry及locale入口；复制模块时改owner/id/import/locale键，不携带客户资源或后端合同变更。API facade是外部调用入口，默认关闭gate，不建立长期mock API。执行pnpm build、pnpm test和相关Rust回归；生命周期统一由AW PLAN管理。
