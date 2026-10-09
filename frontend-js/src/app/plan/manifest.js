/**
 * 文件路径: /frontend-js/src/app/plan/manifest.js
 * 功能描述: 计划模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露计划模块路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const planModule = {
  name: 'plan',
  enabled: true,
  navigation: { titleKey: 'plan.title', icon: 'Calendar' },
  order: 20,
  routes: [
    {
      path: 'plan/list',
      name: 'PlanList',
      component: () => import('./views/list/index.vue'),
      meta: {
        titleKey: 'plan.list',
        pageId: 'plan.list',
        parentTitleKey: 'plan.title',
        navigation: { visible: true, order: 10, icon: 'Calendar' }
      }
    }
  ]
}
