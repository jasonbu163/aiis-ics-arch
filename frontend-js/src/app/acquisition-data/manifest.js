/** 文件路径: /frontend-js/src/app/acquisition-data/manifest.js
 * 功能描述: 采集数据模块的菜单、页面标识和路由声明。 */
export const acquisitionDataModule = {
  name: 'acquisition-data',
  enabled: true,
  navigation: { titleKey: 'acquisition-data.title', icon: 'DataLine' },
  order: 100,
  routes: [
    {
      path: 'acquisition-data/realtime',
      name: 'AcquisitionDataRealtime',
      component: () => import('./views/realtime/index.vue'),
      meta: {
        titleKey: 'acquisition-data.realtime',
        pageId: 'acquisition-data.realtime',
        parentTitleKey: 'acquisition-data.title',
        navigation: { visible: true, order: 10, icon: 'Monitor' }
      }
    },
    {
      path: 'acquisition-data/history',
      name: 'AcquisitionDataHistory',
      component: () => import('./views/history/index.vue'),
      meta: {
        titleKey: 'acquisition-data.history',
        pageId: 'acquisition-data.history',
        parentTitleKey: 'acquisition-data.title',
        navigation: { visible: true, order: 20, icon: 'Clock' }
      }
    },
    {
      path: 'acquisition-data/sources',
      name: 'AcquisitionDataSources',
      component: () => import('./views/sources/index.vue'),
      meta: {
        titleKey: 'acquisition-data.sources',
        pageId: 'acquisition-data.sources',
        parentTitleKey: 'acquisition-data.title',
        requiresAdmin: true,
        navigation: { visible: true, order: 30, icon: 'Setting' }
      }
    }
  ]
}
