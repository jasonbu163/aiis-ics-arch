/**
 * 文件路径: /frontend-next-js/src/app/dashboard/manifest.js
 * 功能描述: Dashboard 模块前端 manifest，集中声明工作台路由
 * 主要功能:
 *   - 暴露 dashboard 首页路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const dashboardModule = {
  name: 'dashboard',
  order: 10,
  routes: [
    {
      path: 'dashboard',
      redirect: '/dashboard/home'
    },
    {
      path: 'dashboard/home',
      name: 'Dashboard',
      component: () => import('./views/home/index.vue'),
      meta: {
        titleKey: 'breadcrumb.dashboard',
        pageId: 'dashboard.home',
        parentTitleKey: 'nav.dashboard'
      }
    }
  ]
}
