# Frontend Module Handbook

Chinese version: [README.zh-CN.md](README.zh-CN.md)

Create each project module under src/app/<module>/:

~~~text
<module>/
├── api/index.js
├── api/mock.js                 # optional
├── components/                 # optional
├── locales/en-US.json
├── locales/zh-CN.json
├── views/<page>/index.vue
└── manifest.js
~~~

Minimal manifest:

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

The router discovers manifest.js automatically. The locale composition root discovers module locale files automatically. A manifest declares route metadata only; it does not call an API, create a timer or connect to a device.

Pages import the module API facade, never a mock file directly. Module mocks are diagnostic-only and must be obviously fake. Root src/api/ is reserved for request/auth/mock-mode helpers.

The sidebar is not inferred from every manifest in this baseline. A module may be routable without being added to a menu until the separately approved menu-assembly workstream defines that contract. Page visibility and backend API permissions remain separate checks.

Verify a module with:

~~~bash
pnpm build
~~~
