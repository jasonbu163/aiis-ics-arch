/** 文件路径: /frontend-js/src/app/aiis_demo/manifest.js
 * 功能描述: 默认关闭的离线模块接入样例；不授予 pageId 权限，不执行外部 I/O。 */
export default {
  name: 'aiis_demo',
  enabled: false,
  order: 90,
  navigation: { titleKey: 'aiis_demo.navigation.title', icon: 'Menu' },
  routes: [{
    path: 'aiis_demo/example',
    name: 'AiisDemoExample',
    component: () => import('./views/example/index.vue'),
    meta: {
      titleKey: 'aiis_demo.example.title',
      parentTitleKey: 'aiis_demo.navigation.title',
      pageId: 'aiis_demo.example',
      navigation: { visible: true, order: 10, icon: 'Document' }
    }
  }]
}
