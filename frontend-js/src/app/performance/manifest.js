/** 通用实绩列表和管理员共享字段管理入口。 */
export const performanceModule = {
  name: 'performance', enabled: true,
  navigation: { titleKey: 'performance.title', icon: 'DataLine' }, order: 30,
  routes: [{ path: 'performance/list', name: 'PerformanceList',
    component: () => import('./views/list/index.vue'),
    meta: { titleKey: 'performance.list', pageId: 'performance.list', parentTitleKey: 'performance.title',
      navigation: { visible: true, order: 10, icon: 'List' } } },
  { path: 'performance/shared-fields', name: 'PerformanceSharedFields',
    component: () => import('@/app/plan/views/shared-fields/index.vue'),
    props: { module: 'performance' },
    meta: { titleKey: 'performance.workflow.sharedFieldSettings', pageId: 'performance.shared-fields',
      parentTitleKey: 'performance.title', requiresAdmin: true,
      navigation: { visible: true, order: 20, icon: 'Setting' } } }]
}
