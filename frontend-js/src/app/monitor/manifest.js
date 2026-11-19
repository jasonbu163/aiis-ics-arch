/**
 * 文件路径: /frontend-next-js/src/app/monitor/manifest.js
 * 功能描述: 过程监控模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 声明过程曲线、表计能耗及管理页面
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const monitorModule = {
  name: 'monitor',
  enabled: true,
  navigation: { titleKey: 'monitor.title', icon: 'Monitor' },
  order: 40,
  routes: [
    {
      path: 'monitor/temperature',
      name: 'MonitorTemperature',
      component: () => import('./views/observations/curves.vue'),
      meta: {
        titleKey: 'monitor.temperature',
        pageId: 'monitor.temperature', observationCategory: 'temperature',
        parentTitleKey: 'monitor.title',
        navigation: { visible: true, order: 20, icon: 'TrendCharts' }
      }
    },
    {
      path: 'monitor/consumption',
      name: 'MonitorEnergy',
      component: () => import('./views/observations/energy.vue'),
      meta: {
        titleKey: 'monitor.energy',
        pageId: 'monitor.energy',
        parentTitleKey: 'monitor.title',
        navigation: { visible: true, order: 30, icon: 'Cpu' }
      }
    },
    {
      path: 'monitor/drive', name: 'MonitorDrive',
      component: () => import('./views/observations/curves.vue'),
      meta: { titleKey: 'monitor.observation.drive', pageId: 'monitor.drive', observationCategory: 'drive',
        parentTitleKey: 'monitor.title', navigation: { visible: true, order: 40, icon: 'TrendCharts' } }
    },
    {
      path: 'monitor/cleaning', name: 'MonitorCleaning',
      component: () => import('./views/observations/curves.vue'),
      meta: { titleKey: 'monitor.observation.cleaning', pageId: 'monitor.cleaning', observationCategory: 'cleaning',
        parentTitleKey: 'monitor.title', navigation: { visible: true, order: 50, icon: 'TrendCharts' } }
    },
    {
      path: 'monitor/observations/admin', name: 'MonitorObservationAdmin',
      component: () => import('./views/observations/admin.vue'),
      meta: { titleKey: 'monitor.observation.configManagement', pageId: 'monitor.observations.admin', requiresAdmin: true,
        parentTitleKey: 'monitor.title', navigation: { visible: true, order: 60, icon: 'Setting' } }
    },
    {
      path: 'monitor/observations/data', name: 'MonitorObservationData',
      component: () => import('./views/observations/data.vue'),
      meta: { titleKey: 'monitor.observation.dataManagement', pageId: 'monitor.observations.data', requiresAdmin: true,
        parentTitleKey: 'monitor.title', navigation: { visible: true, order: 70, icon: 'List' } }
    }
  ]
}
