<!--
  File Path: /backend/app/aiis_demo/README.zh-CN.md
  Description: AIIS Demo 参考模块中文说明
  Main Features:
    - 说明默认关闭的项目本地参考模块
    - 定义复制改名、权限与 migration 边界
    - 记录 restart 与 no-hot-unload 语义
-->
# AIIS Demo 参考模块

[English version](README.md)

`aiis_demo` 是当前后端模块形态的项目本地参考。它只用于 reference，不是业务能力、第二份
`backend/templates`、也不是 AIIS shared skill/template 的项目内镜像。该 package 受 Git 管理，
用于让真实模块可以对照一个可执行样例复制并有意识地改名。

## 默认组合语义

- `manifest.enabled` 固定为 `False`，因此正常应用组合不包含它的 router、OpenAPI 路径或
  Projection owner。
- manifest 仍声明 `models_package="app.aiis_demo.models"`。Registry 为 metadata 检查导入这个
  空 package；导入不会新增 SQLAlchemy table，也不会执行 DDL、migration、数据库、seed、mock
  或外部 I/O。
- 唯一路由是无害的参考 `GET /api/v1/aiis-demo/ping`。只有在隔离测试/应用中显式使用内存 enabled
  override 时才暴露。
- `permissions=("aiis_demo",)` 只是复制改名示例的 metadata，不是授权、ACL 授予，也不能替代
  真实路由依赖与业务权限设计。

ping 严格保持 `API -> services/async_ping.py -> schemas/ping.py`，返回统一 `code/message/data`
响应，稳定数据包含 `module="aiis_demo"`、`status="ok"` 与 `reference=true`。它不打开 session，
不读取 settings 或文件，不访问网络/PLC/Control Agent，不启动 task，也不写审计事件。

## Package 职责

该 package 保留标准 `api/`、`models/`、`schemas/`、`crud/`、`services/`、`mocks/`、`seeds/`
入口。空的 `models`、`crud`、`mocks`、`seeds` 是诚实 placeholder：不放注释 ORM、伪 CRUD、
写库 helper、mock provider 或 seed runner。空 placeholder 不能被当作已经实现的业务能力。

## 复制 / 改名检查清单

只有在独立业务任务定义了新的 owner 与验收合同后，才能把本模块作为参考起点：

1. 将 `backend/app/aiis_demo/` 复制为新的 package 名，并从 Python、路由、Schema 与文档中删除
   所有 `aiis_demo` / demo / reference-only 含义。
2. 将 `manifest.name` 改为目录名，有意识地决定 `enabled`、`order`、router 路径、model package
   与业务权限 key；manifest 导入必须无数据库、网络和 runtime 副作用。
3. 用真实 API -> Service -> Schema 行为替换静态 ping。API 保持很薄；只有 capability 真正拥有
   持久化时才增加 CRUD 与 model。不得把 demo payload、placeholder 权限或伪成功路径留在真实模块。
4. 重新设计授权。manifest 的 `permissions` 不会授予访问权；在获批业务范围内添加并测试真实的
   dependency/role policy。
5. 如果引入真实 model、table、index、constraint 或 column，必须新增并复核显式 Alembic migration。
   Model import 不替代 migration，也不授权 `create_all` 或隐式写入。
6. 增加 route、response、service、授权、metadata 与 migration 聚焦测试；没有新的治理决定时，
   不要把模块加入第二份 registry 或 generator。

## Enabled 与 restart 语义

修改 `manifest.enabled` 可能让开发 source watcher 触发整个 backend 进程 autoreload；这只是开发
重载，不是进程内 hot plugin 合同。若 watcher 未触发，必须手动重启 backend。

新增、删除、改名模块/package，或改变 Router/models/services 拓扑时，必须重启 backend 进程或对应
容器，使 discovery 与 composition 从零重建。正式/生产环境任何源码或 package 变化都必须
restart/redeploy。已经组合的 FastAPI app 不支持 hot unload：运行中的 manifest 从 enabled 改为
disabled 不会动态移除已挂载 router；必须重启后重新计算暴露面。

本参考不会在真实应用中启用 `aiis_demo`，不授权发布、部署或生产使用。
