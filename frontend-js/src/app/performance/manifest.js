/**
 * 文件路径: /frontend-next-js/src/app/performance/manifest.js
 * 功能描述: 实绩模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露可见实绩列表、分卷、打印、质检和效率页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const performanceModule = {
  name: 'performance',
  enabled: true,
  navigation: { titleKey: 'performance.title', icon: 'DataLine' },
  order: 30,
  routes: [
    {
      path: 'performance/list',
      name: 'PerformanceList',
      component: () => import('./views/list/index.vue'),
      meta: {
        titleKey: 'performance.list',
        pageId: 'performance.list',
        parentTitleKey: 'performance.title',
        navigation: { visible: true, order: 10, icon: 'List' }
      }
    },
    {
      path: 'performance/split',
      name: 'PerformanceSplit',
      component: () => import('./views/split/index.vue'),
      meta: {
        titleKey: 'performance.split',
        pageId: 'performance.split',
        parentTitleKey: 'performance.title',
        navigation: { visible: true, order: 20, icon: 'Scissor' }
      }
    },
    {
      path: 'performance/print',
      name: 'PerformancePrint',
      component: () => import('./views/print/index.vue'),
      meta: {
        titleKey: 'performance.print',
        pageId: 'performance.print',
        parentTitleKey: 'performance.title',
        navigation: { visible: true, order: 30, icon: 'Printer' }
      }
    },
    {
      path: 'performance/quality/:id',
      name: 'PerformanceQuality',
      component: () => import('./views/quality/index.vue'),
      meta: {
        titleKey: 'performance.modules.qualityControl',
        pageId: 'performance.quality',
        parentTitleKey: 'performance.title',
        navigation: { visible: false }
      }
    },
    {
      path: 'performance/efficiency',
      name: 'PerformanceEfficiency',
      component: () => import('./views/efficiency/index.vue'),
      meta: {
        titleKey: 'performance.modules.efficiency',
        pageId: 'performance.efficiency',
        parentTitleKey: 'performance.title',
        navigation: { visible: true, order: 40, icon: 'TrendCharts' }
      }
    }
  ]
}
