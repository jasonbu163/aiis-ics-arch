# AIIS ICS Architecture 前端（JavaScript）

English version: [README.md](README.md)

这是 JavaScript 形态的 Vue 3 + Vite Core 前端模板，包含登录、认证壳层、系统页面、dashboard/plan 首批接入模块和共享基础设施。使用方项目在 src/app/<module>/ 下增加业务模块。

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

## 项目页面配置

宿主机 `pnpm dev` 与 `pnpm build` 共用 Git 忽略的 `.env`，不需要 `.env.production`。
Docker dev 沿用 `.env.docker.dev`；复制对应 example 后调整项目值。Vite 在启动时读取 `.env`、
`.env.local`、`.env.[mode]`、`.env.[mode].local`（后者覆盖前者），现有进程变量优先。
`dev` 默认 development、`build` 默认 production；已有 mode/local 文件仍按此规则生效。

```dotenv
VITE_SUPERVISOR_PAGE_ACCESS_JSON='["dashboard.home","plan.list"]'
VITE_OPERATOR_PAGE_ACCESS_JSON='["dashboard.home"]'
```

数组填写 manifest 的 `meta.pageId`；operator 必须是 supervisor 子集。`[]` 不授权页面，
admin 内置且不在 env 配置。仅允许已启用的有效 leaf 页面，重复、未知、未启用、admin 专属页面、
非法 JSON 或缺失数组均明确失败；未知角色拒绝访问。配置只控制菜单、路由与默认入口，API 仍须后端授权。
模块 `enabled` 控制装配，`navigation` 和 leaf `visible` 控制菜单；模块 `order` 控制组顺序，
leaf `navigation.order` 控制组内顺序。当前 dashboard 10、plan 20、system 80，aiis_demo 保持关闭。

旧 `VITE_ROLE_PAGE_ACCESS_JSON` 对象要将 supervisor/operator 数组原样迁到两个新变量，保留成员、
顺序和其他设置。旧 JSON 在 README 历史节留档，实际 env 只保留活动配置与用途说明。不能同时保留活动旧 key；checker 会明确报迁移错误。
旧对象缺少角色时迁为 `[]`；非法对象、额外角色或新旧冲突须先人工处理，不能静默清空。
旧授权引用未迁入模块时应保留原值，启动/构建会报未知 pageId，待模块迁入或明确调整授权后恢复。

```bash
pnpm check:access --mode development
pnpm check:access --mode production
```

这两个命令与 dev/build 共用有效 env 校验。`pnpm check:modules` 只校验模块合同，不读取 env；
两个 checker 裸调用仅显示帮助。修改 env 后重启 dev；交付时重新 build dist，单独重启 Nginx
不会改变已编译权限。生产构建应核对 API 地址并关闭 mock/演示账号，测试 fixture 不作为交付产物。

## 环境变量用途

两份已跟踪 example 提供公开默认值；实际 `.env` / `.env.docker.dev` 继续被 Git 忽略，不要把整份
真实 env 复制到文档或提交。下表说明当前读取方，不涉及后端凭据或 API 授权。Vite 在启动时读取
配置，被前端消费的值会写入浏览器构建产物。修改后重启 dev；消费的构建值变更后重新构建正式
`dist`。修改 env 或单独重启 Nginx 都不会改写已有 bundle。

| 配置项 | 用途与适用范围 |
| --- | --- |
| `VITE_API_BASE_URL` | 浏览器 HTTP API 基础地址，由 `src/config/api.js` 读取。默认 `/api/v1` 为同源请求：开发时由 Vite 代理，部署时由现有 Nginx 配置代理。绝对 URL 必须是浏览器能访问的地址，不能只在容器网络内可达。 |
| `VITE_PROXY_TARGET` | `vite.config.js` 中开发 `/api` 代理的目标。宿主机与 Docker dev 的网络环境不同，应填写 Vite 进程可访问的目标；此值不设置正式 Nginx upstream。 |
| `VITE_APP_PORT` | Vite 开发服务端口；缺失或无法解析时回落到 `5190`。它不设置 Nginx 监听端口。 |
| `VITE_REQUEST_TIMEOUT` | HTTP 请求超时，单位毫秒；默认 `10000`，由 API 配置读取。 |
| `VITE_FRONTEND_MOCK_ENABLED` | 精确为 `true` 时使用前端本地诊断 mock；其他值走真实 API facade。mock 结果不验证后端行为，交付时保持 false。 |
| `VITE_SUPERVISOR_PAGE_ACCESS_JSON` | supervisor 的 JSON 授权数组，元素为已启用、非 admin 专属 leaf 的 `meta.pageId`。`[]` 不授权页面；数组不改变模块 `enabled` 或后端权限。 |
| `VITE_OPERATOR_PAGE_ACCESS_JSON` | operator 的 JSON pageId 授权数组，必须是 supervisor 子集。未知、关闭、admin 专属页面或非法数组会阻止 dev/build。admin 内置，没有 env 授权数组。 |
| `VITE_LOGIN_DEMO_ACCOUNTS_ENABLED` | 精确为 `true` 时显示登录页的演示账号提示；它不创建账号、不完成认证、不开启 mock，也不授予页面权限。交付时保持 false。 |
| `VITE_OPEN_BROWSER`（可选，四文件当前未配置） | 精确为 `true` 时在 Vite dev 启动时打开浏览器；缺失或其他值不自动打开。仅用于开发，由 `vite.config.js` 读取。 |

### 品牌 Logo 配置

登录页和认证壳共用 `BrandLogo.vue`，通过 `src/config/brand.js` 消费以下五项配置。组件按照图片
自然比例 contain 显示，支持左/中/右对齐，并用 ResizeObserver 更新布局。光晕使用已有主题 token：
日间模式隐藏、夜间模式显示，不修改全局主题。

| 配置项 | 支持值与回退 |
| --- | --- |
| `VITE_BRAND_LOGO_FILE` | 已打包 `src/assets/brand/*` 中的文件名，默认 `demo-organization-logo.svg`，去除首尾空白。缺失、不存在的文件及非法路径/URL 回退中性 demo SVG；仅解析本地已打包资产。 |
| `VITE_BRAND_LOGO_ALIGN` | `left`、`center`、`right`，默认 `center`。空白与大小写规范化，非法值使用默认值。 |
| `VITE_BRAND_GLOW_LEFT` | 左段：`light`、`high-light`、`accent`、`none`，默认 `light`。 |
| `VITE_BRAND_GLOW_CENTER` | 中段：相同四种模式，默认 `accent`。 |
| `VITE_BRAND_GLOW_RIGHT` | 右段：相同四种模式，默认 `accent`。 |

光晕值规范化空白与大小写，兼容历史拼写 `hight-light`，等价于 `high-light`。`light` 为白色光晕，
`high-light` 为更强白色光晕，`accent` 使用主题强调色，`none` 为透明；三个区域独立配置。
图片 alt 使用当前语言的 `common.systemTitle`。公共回退图只有通用 demo 标识，不含客户 Logo。

使用项目 Logo 时，将经审核资产放入 `src/assets/brand/`，填写文件名后重启 dev 或重新构建 dist。
带路径分隔符、穿越或 URL 的值会被拒绝；只把图片复制到 `dist` 不会注册到源码 glob。实际品牌
配置值原样保留，如果当前 Core 中没有对应文件，则按设计显示 demo。公开 example 和独立 Dockerfile
ARG/ENV 使用中性图片、center 对齐和 light/accent/accent 光晕默认值。Docker dev 未配置这五项时
使用相同源码默认值；正式 Nginx 继续读取宿主机预构建 dist。

### 旧角色配置历史记录

以下是 Owner 提供的仅含 pageId 的旧 JSON 对象，从实际 env 注释移入文档。它们仅为历史参考，
**当前应用不读取这些记录**；活动配置仍只使用两个新数组。为测试当前模块，Owner 已授权将旧数组与已启用、非 admin 专属
leaf 页面取交集并保留顺序：宿主机 supervisor 当前 3 项（dashboard.home、plan.list、system.user），
operator 当前 2 项（dashboard.home、plan.list）；Docker dev 保持空数组。下方历史 20/14 对象
保持不变。当前宿主机配置通过严格 checker，未来授权仍需对应有效模块。不要把旧对象恢复为活动旧变量，也不要未经模块
可用性核对就把不支持的授权复制到可运行项目配置。

宿主机开发 / 正式构建（`.env`）历史：

```json
{
  "supervisor": [
    "dashboard.home",
    "plan.list",
    "performance.list",
    "performance.split",
    "performance.print",
    "performance.quality",
    "performance.efficiency",
    "monitor.temperature",
    "monitor.energy",
    "equipment.production-parameters",
    "equipment.drive",
    "equipment.temperature",
    "auxiliary.stop",
    "auxiliary.shift",
    "auxiliary.price",
    "maintenance.log",
    "quality.list",
    "quality.control",
    "quality.spc",
    "system.user"
  ],
  "operator": [
    "dashboard.home",
    "plan.list",
    "performance.list",
    "performance.split",
    "performance.print",
    "performance.quality",
    "performance.efficiency",
    "quality.list",
    "quality.control",
    "quality.spc",
    "equipment.production-parameters",
    "equipment.drive",
    "equipment.temperature",
    "maintenance.log"
  ]
}
```

Docker 开发（`.env.docker.dev`）历史：

```json
{}
```

## 模块手册

创建模块前先阅读 [src/app/README.zh-CN.md](src/app/README.zh-CN.md)。其中说明最小 manifest、API facade、mock、locale、路由和权限/菜单边界。

## 验证

源码检查使用 Node contract matrix 与 pnpm build（含 prebuild manifest 校验）。新增/删除模块需要 dev 重启或生产重建。这些检查不启动 Docker、不连接 backend 真实数据库、不访问 PLC，也不发布版本。

已批准的 `ARCH-DOCKER-001` frontend 镜像使用固定 Node/pnpm lockfile 构建阶段，并把 dist 复制进 Nginx
runtime。runtime 不挂载源码或 `node_modules`，`/api/v1` 反向代理到 Compose 的 `backend` 服务；它只是
可丢弃的 MySQL smoke 表面，不是生产发布产物。

## 预构建 dist 部署

根 `docker-compose.prod.yml` 使用固定版本 Nginx 和本目录现有 `nginx.conf`，把 `dist` 只读挂载到 `/usr/share/nginx/html/current`。启动前使用已提交的 pnpm 锁文件构建；缺少 `dist/index.html` 会明确启动失败。生产构建使用 `/api/v1`，关闭 mock 和演示账号。前端 Dockerfile 保留为独立镜像构建配方；prod 使用宿主机构建的 dist。详见[部署准备](../INITIALIZATION.zh-CN.md#单机部署)。
