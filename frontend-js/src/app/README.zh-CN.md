# 前端模块手册

English version: [README.md](README.md)

## 归属与装配

```text
src/app/<module>/
├── api/index.js                 # 可选 API facade
├── api/mock.js                  # 可选成对诊断实现
├── components/                  # 可选模块内组件
├── locales/en-US.json
├── locales/zh-CN.json
├── views/<page>/index.vue
└── manifest.js
```

`moduleManifest.js` 负责纯规范化、校验、排序与 consumer helper；`moduleRegistry.js` 是唯一 Vite
发现入口。router、侧栏、i18n 共同消费其 routes、两级 navigation 与活动文案，不维护各自模块清单。

`system` 是必需 Core，必须存在并显式声明 `enabled: true`；其 `system`、`user` namespace 继续服务
公共壳层，但不豁免页面权限。可选模块 `enabled: false` 时同时退出路由、菜单、默认入口候选和模块
文案；删除整个可选模块目录效果相同。非法 manifest（包括已禁用模块）仍会导致校验失败。

这是源码装配：新增/删除模块后重启 dev server；生产必须重新构建和交付 `dist`。禁用仅表示不注册，
不代表 bundler 不扫描源码，也不构成安全隔离。

## 从零手工接入

1. 创建 `src/app/sample/views/list/index.vue` 与双语 locale 文件。离线页面不需要 API。
2. 每份 locale 写入相同键，并翻译对应值：

```json
{ "navigation": { "title": "示例" }, "list": { "title": "示例列表" } }
```

3. 页面使用模块内键：

```vue
<template>
  <div class="page-layout"><el-card>{{ $t('sample.list.title') }}</el-card></div>
</template>
```

4. 创建 `manifest.js`：

```js
export default {
  name: 'sample', enabled: true, order: 90,
  navigation: { titleKey: 'sample.navigation.title', icon: 'Menu' },
  routes: [{
    path: 'sample/list', name: 'SampleList',
    component: () => import('./views/list/index.vue'),
    meta: {
      titleKey: 'sample.list.title', parentTitleKey: 'sample.navigation.title',
      pageId: 'sample.list',
      navigation: { visible: true, order: 10, icon: 'List' }
    }
  }]
}
```

5. 执行 `pnpm check:modules`、`pnpm test:modules`、`pnpm build`；重启 `pnpm dev` 完成发现。
6. 非 admin 用户需要使用方 access provider 已授予 `sample.list`。创建 manifest 不会授予权限。
   离线验证使用本地 fixture，不连接真实服务。

可选 API facade 归 `api/index.js`；页面只导入 facade，不直接导入 `api/mock.js`。需要诊断 mock 时，
沿用 `src/api/mockMode.js` 的 `callApi` 边界：

```js
import request from '@/api/request'
import { callApi } from '@/api/mockMode'
import * as mock from './mock'
export const listItems = () => callApi(mock.listItems,
  () => request.get('/sample/items'), 'sample.listItems')
```

`api/mock.js` 必须同名导出、返回相同解包后数据形态，并带明显诊断标记，如
`sourceType: 'frontend_mock'`。以上仅演示合同，真实 API 由单独获批的集成任务定义；根 `src/api/`
继续只承载 request/auth/mock-mode 基础设施。

## 复制、禁用和删除

复制默认关闭的 `aiis_demo` 为新目录，修改副本内 manifest `name`、route `name/path/pageId`、全部
翻译前缀与页面 import，补齐双语，执行验证后显式启用副本。无需修改共享 router、MainLayout、locale
loader 或图标注册表。禁用时设置 `enabled: false`；删除时删除整个目录，随后重启/重建。

其他模块显式 import、链接、route push 和 API 依赖由各自 owner 处理；orphan grant 不能重建已删除
的路由/菜单。Registry 不自动修改使用方权限政策。

## Manifest 合同与兼容

- `name` 与目录一致；新模板显式提供 boolean `enabled` 与有限数值 `order`。
- 模块按 order、name 排序；路由按 route order（或 leaf navigation order）排序，同序保持源码顺序。
  默认入口是首个可访问的非参数路由，无候选时为 `/login`。
- navigation 可选：缺省仍注册 route/locale，但不生成侧栏 group。仅 `meta.navigation.visible: true`
  生成 leaf，参数路由不得可见，没有可访问 leaf 的 group 隐藏。
- icon 是可选 Element Plus 图标名；未知或缺失时使用 `Menu`，无需修改共享注册。
- 新格式 module/route/parent title 必须在模块拥有的双语 namespace 内可解析。`<locale>.json` 使用模块
  namespace，历史 `<namespace>.<locale>.json` 命名继续兼容。namespace 冲突（含全局文案）失败，双语键集合必须一致。
- 没声明 `enabled`、模块 navigation 或 route `meta.navigation` 的旧格式默认启用、不自动出菜单，
  可继续解析 `breadcrumb.*` 等全局标题。历史具名导出（如 `systemModule`）继续加载。声明任一新字段
  就采用模块标题校验；升级时保留原 route name/path/pageId。活动标题不能依赖被禁用模块的文案。
- 重复模块名、route name、规范化 path、pageId、namespace，以及非法 schema、双语标题缺失、必需
  Core 缺失/禁用会失败。Vue Router 嵌套记录、alias 与 redirect 父路由继续兼容；Registry 检查实际
  leaf path 与继承 metadata。导航层级独立于路由嵌套，仍只支持 module group -> route leaf。
- manifest 是受信任、静态、无副作用源码；不调用 API、不启动 timer、不授予角色权限、不远程加载。

## 权限提供者

`canAccessRoute`、`accessibleNavigation` 和 `defaultAuthenticatedPath` 接收使用方对象
`{ isAdmin, hasPageAccess(pageId) }`，显式 `isLoggedIn: false` 也会拒绝。仅 boolean true 授权；
非 admin 需要 page grant，`requiresAdmin` 还要求 admin。缺失、未知、损坏输入 fail closed。
当前 user store 适配原角色配置；使用方可接入 backend 返回的权限，不把 Registry 耦合到某个来源。
router 另检查登录与活动路由归属；前端可见性永远不替代 backend API 授权。

## 检查

```bash
pnpm install --frozen-lockfile
pnpm check:modules
pnpm test:modules
pnpm build
```

build 的 `prebuild` 在 Vite 前校验相同 Registry；直接 `vite build` 会绕过 hook，应使用项目命令。
裸调用 `node scripts/check-module-manifests.mjs` 仅显示帮助。checker 导入受信任本地 manifest 与
JSON，不调用页面懒加载、不读取 `.env`。Vite 自身会读取构建环境；源码验证应使用公开的项目自有
值，或使用排除真实 `.env` 的隔离副本。
