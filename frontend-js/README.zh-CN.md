# AIIS ICS Architecture 前端（JavaScript）

English version: [README.md](README.md)

这是 JavaScript 形态的 Vue 3 + Vite Core 前端模板，只包含登录、认证壳层、系统页面和共享基础设施。使用方项目在 src/app/<module>/ 下增加业务模块。

## 稳定边界

- src/app/moduleRegistry.js 是唯一 manifest/locale 发现与校验装配入口。
- src/router/index.js 与 src/locales/index.js 消费其活动路由和双语文案。
- src/layouts/ 只承载壳层结构；业务页面逻辑归属各自模块。
- src/api/ 只承载 auth/request/mock-mode 基础设施；业务 API facade 归属模块。
- 侧栏根据 manifest navigation 生成，与路由/默认入口使用相同 access provider。必需 system 保持启用，可选模块可退出全部四个 consumer。

## 命令

~~~bash
pnpm install
pnpm dev
pnpm check:modules
pnpm test:modules
pnpm build
~~~

只能使用 pnpm。Vite 只在进程启动时读取 .env，修改环境后需要重启进程。VITE_* 是公开浏览器配置，不得写入 secret。

## 模块手册

创建模块前先阅读 [src/app/README.zh-CN.md](src/app/README.zh-CN.md)。其中说明最小 manifest、API facade、mock、locale、路由和权限/菜单边界。

## 验证

源码检查使用 Node contract matrix 与 pnpm build（含 prebuild manifest 校验）。新增/删除模块需要 dev 重启或生产重建。这些检查不启动 Docker、不连接 backend 真实数据库、不访问 PLC，也不发布版本。

已批准的 `ARCH-DOCKER-001` frontend 镜像使用固定 Node/pnpm lockfile 构建阶段，并把 dist 复制进 Nginx
runtime。runtime 不挂载源码或 `node_modules`，`/api/v1` 反向代理到 Compose 的 `backend` 服务；它只是
可丢弃的 MySQL smoke 表面，不是生产发布产物。

## 预构建 dist 部署

根 `docker-compose.prod.yml` 使用固定版本 Nginx 和本目录现有 `nginx.conf`，把 `dist` 只读挂载到 `/usr/share/nginx/html/current`。启动前使用已提交的 pnpm 锁文件构建；缺少 `dist/index.html` 会明确启动失败。生产构建使用 `/api/v1`，关闭 mock 和演示账号。前端 Dockerfile 保留为独立镜像构建配方；prod 使用宿主机构建的 dist。详见[部署准备](../INITIALIZATION.zh-CN.md#单机部署)。
