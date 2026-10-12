/**
 * 文件路径: /frontend-next-js/src/app/maintenance/manifest.js
 * 功能描述: 保养模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露保养日志页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const maintenanceModule = {
  name: 'maintenance',
  enabled: true,
  navigation: { titleKey: 'maintenance.title', icon: 'Notebook' },
  order: 90,
  routes: [
    {
      path: 'maintenance/log',
      name: 'MaintenanceLog',
      component: () => import('./views/log/index.vue'),
      meta: {
        titleKey: 'maintenance.log.title',
        pageId: 'maintenance.log',
        parentTitleKey: 'maintenance.title',
        navigation: { visible: true, order: 10, icon: 'Document' }
      }
    }
  ]
}
