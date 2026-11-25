/** 能耗管理菜单、页面权限及统计和单价的兼容入口。 */
export default {
  name: 'energy',
  enabled: true,
  navigation: { titleKey: 'energy.title', icon: 'Cpu' },
  order: 55,
  routes: [
    {
      path: 'monitor/consumption',
      name: 'MonitorEnergy',
      component: () => import('./views/consumption.vue'),
      meta: {
        pageId: 'monitor.energy', titleKey: 'energy.consumption', parentTitleKey: 'energy.title',
        navigation: { visible: true, order: 10, icon: 'TrendCharts' }
      }
    },
    {
      path: 'auxiliary/price',
      name: 'AuxiliaryPrice',
      component: () => import('./views/price.vue'),
      meta: {
        pageId: 'auxiliary.price', titleKey: 'energy.price.title', parentTitleKey: 'energy.title',
        navigation: { visible: true, order: 20, icon: 'PriceTag' }
      }
    },
    {
      path: 'energy/observations/data',
      name: 'EnergyObservationData',
      component: () => import('./views/data.vue'),
      meta: {
        pageId: 'energy.observations.data', titleKey: 'energy.data', parentTitleKey: 'energy.title', requiresAdmin: true,
        navigation: { visible: true, order: 30, icon: 'List' }
      }
    },
    {
      path: 'energy/observations/admin',
      name: 'EnergyObservationAdmin',
      component: () => import('./views/admin.vue'),
      meta: {
        pageId: 'energy.observations.admin', titleKey: 'energy.configuration', parentTitleKey: 'energy.title', requiresAdmin: true,
        navigation: { visible: true, order: 40, icon: 'Setting' }
      }
    }
  ]
}
