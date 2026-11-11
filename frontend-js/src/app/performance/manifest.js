/** 通用实绩模块只注册列表，退役页面不再装配。 */
export const performanceModule = {
  name: 'performance', enabled: true,
  navigation: { titleKey: 'performance.title', icon: 'DataLine' }, order: 30,
  routes: [{ path: 'performance/list', name: 'PerformanceList',
    component: () => import('./views/list/index.vue'),
    meta: { titleKey: 'performance.list', pageId: 'performance.list', parentTitleKey: 'performance.title',
      navigation: { visible: true, order: 10, icon: 'List' } } }]
}
