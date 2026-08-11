# 前端模块手册

English version: [README.md](README.md)

每个项目模块放在 src/app/<module>/：

~~~text
<module>/
├── api/index.js
├── api/mock.js                 # 可选
├── components/                 # 可选
├── locales/en-US.json
├── locales/zh-CN.json
├── views/<page>/index.vue
└── manifest.js
~~~

最小 manifest：

~~~js
export default {
  name: 'example',
  order: 100,
  routes: [{
    path: 'example/list',
    name: 'ExampleList',
    component: () => import('./views/list/index.vue'),
    meta: {
      titleKey: 'example.list.title',
      pageId: 'example.list'
    }
  }]
}
~~~

router 会自动发现 manifest.js，locale 组合根会自动发现模块 locale。manifest 只声明路由 metadata，不调用 API、不创建 timer、不连接设备。

页面只导入本模块 API facade，不能直接导入 mock。模块 mock 只用于诊断，必须使用明显虚构的数据。根 src/api/ 只保留 request/auth/mock-mode 等共享基础设施。

本基线不会根据每个 manifest 自动生成侧栏。模块可以先拥有路由，菜单加入规则待独立获批的菜单组装工作流定义。页面可见性和后端 API 权限仍是两套独立检查。

模块验证命令：

~~~bash
pnpm build
~~~
