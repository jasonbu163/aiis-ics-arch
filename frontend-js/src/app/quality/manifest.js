/**
 * 文件路径: /frontend-next-js/src/app/quality/manifest.js
 * 功能描述: 质量模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露质量列表、质量控制和 SPC 页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const qualityModule = {
  name: 'quality',
  enabled: true,
  navigation: { titleKey: 'quality.title', icon: 'CircleCheck' },
  order: 70,
  routes: [
    {
      path: 'quality/list',
      name: 'QualityList',
      component: () => import('./views/list/index.vue'),
      meta: {
        titleKey: 'quality.list',
        pageId: 'quality.list',
        parentTitleKey: 'quality.title',
        navigation: { visible: true, order: 10, icon: 'List' }
      }
    },
    {
      path: 'quality/control/:id',
      name: 'QualityControl',
      component: () => import('./views/control/index.vue'),
      meta: {
        titleKey: 'quality.control.routeTitle',
        pageId: 'quality.control',
        parentTitleKey: 'quality.title',
        navigation: { visible: false }
      }
    },
    {
      path: 'quality/spc',
      name: 'QualitySPC',
      component: () => import('./views/spc/index.vue'),
      meta: {
        titleKey: 'quality.spc',
        pageId: 'quality.spc',
        parentTitleKey: 'quality.title',
        navigation: { visible: true, order: 20, icon: 'DataAnalysis' }
      }
    }
  ]
}
