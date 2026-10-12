/**
 * 文件路径: /frontend-next-js/src/app/monitor/manifest.js
 * 功能描述: 过程监控模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露实时监控、温度监控和能耗监控页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const monitorModule = {
  name: 'monitor',
  enabled: true,
  navigation: { titleKey: 'monitor.title', icon: 'Monitor' },
  order: 40,
  routes: [
    {
      path: 'monitor/realtime',
      name: 'MonitorRealtime',
      component: () => import('./views/realtime/index.vue'),
      meta: {
        titleKey: 'monitor.realtime.menu',
        pageId: 'monitor.realtime',
        parentTitleKey: 'monitor.title',
        navigation: { visible: true, order: 10, icon: 'Monitor' }
      }
    },
    {
      path: 'monitor/temperature',
      name: 'MonitorTemperature',
      component: () => import('./views/temperature/index.vue'),
      meta: {
        titleKey: 'monitor.temperature',
        pageId: 'monitor.temperature',
        parentTitleKey: 'monitor.title',
        navigation: { visible: true, order: 20, icon: 'TrendCharts' }
      }
    },
    {
      path: 'monitor/energy',
      name: 'MonitorEnergy',
      component: () => import('./views/energy/index.vue'),
      meta: {
        titleKey: 'monitor.energy',
        pageId: 'monitor.energy',
        parentTitleKey: 'monitor.title',
        navigation: { visible: true, order: 30, icon: 'Cpu' }
      }
    }
  ]
}
