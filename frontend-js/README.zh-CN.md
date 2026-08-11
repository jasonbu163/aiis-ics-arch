# AIIS ICS Architecture 前端（JavaScript）

English version: [README.md](README.md)

这是 JavaScript 形态的 Vue 3 + Vite Core 前端模板，只包含登录、认证壳层、系统页面和共享基础设施。使用方项目在 src/app/<module>/ 下增加业务模块。

## 稳定边界

- src/router/index.js 是路由组合根，自动发现模块 manifest.js。
- src/locales/index.js 是 i18n 组合根，自动发现模块 locale JSON。
- src/layouts/ 只承载壳层结构；业务页面逻辑归属各自模块。
- src/api/ 只承载 auth/request/mock-mode 基础设施；业务 API facade 归属模块。
- 当前侧栏只暴露 Core system 页面。完整 manifest 菜单自动组装由 ARCH-FE-001 单独跟踪，本仓不提前实现。

## 命令

~~~bash
pnpm install
pnpm dev
pnpm build
~~~

只能使用 pnpm。Vite 只在进程启动时读取 .env，修改环境后需要重启进程。VITE_* 是公开浏览器配置，不得写入 secret。

## 模块手册

创建模块前先阅读 [src/app/README.zh-CN.md](src/app/README.zh-CN.md)。其中说明最小 manifest、API facade、mock、locale、路由和权限/菜单边界。

## 验证

源码基线使用 pnpm build 和 JavaScript 语法检查，不启动 Docker、不连接 backend 真实数据库、不访问 PLC，也不发布版本。

已批准的 `ARCH-DOCKER-001` frontend 镜像使用固定 Node/pnpm lockfile 构建阶段，并把 dist 复制进 Nginx
runtime。runtime 不挂载源码或 `node_modules`，`/api/v1` 反向代理到 Compose 的 `backend` 服务；它只是
可丢弃的 MySQL smoke 表面，不是生产发布产物。
