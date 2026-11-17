/**
 * 文件路径: /frontend-next-js/src/app/equipment/manifest.js
 * 功能描述: 设备模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露生产参数、传动状态和温控状态页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const equipmentModule = {
  name: 'equipment',
  enabled: true,
  navigation: { titleKey: 'equipment.title', icon: 'Monitor' },
  order: 50,
  routes: [
    {
      path: 'equipment/production-parameters',
      name: 'EquipmentProductionParameters',
      component: () => import('./views/observations/cards.vue'),
      meta: {
        titleKey: 'equipment.productionParameters',
        pageId: 'equipment.production-parameters', observationPage: 'production',
        parentTitleKey: 'equipment.title',
        navigation: { visible: true, order: 10, icon: 'DataLine' }
      }
    },
    {
      path: 'equipment/drive',
      name: 'EquipmentDrive',
      component: () => import('./views/observations/cards.vue'),
      meta: {
        titleKey: 'equipment.drive',
        pageId: 'equipment.drive', observationPage: 'drive',
        parentTitleKey: 'equipment.title',
        navigation: { visible: true, order: 20, icon: 'Odometer' }
      }
    },
    {
      path: 'equipment/temperature',
      name: 'EquipmentTemperature',
      component: () => import('./views/observations/cards.vue'),
      meta: {
        titleKey: 'equipment.temperature',
        pageId: 'equipment.temperature', observationPage: 'temperature',
        parentTitleKey: 'equipment.title',
        navigation: { visible: true, order: 30, icon: 'Operation' }
      }
    },
    {
      path: 'equipment/cleaning', name: 'EquipmentCleaning',
      component: () => import('./views/observations/cards.vue'),
      meta: { titleKey: 'equipment.observation.cleaning', pageId: 'equipment.cleaning', observationPage: 'cleaning',
        parentTitleKey: 'equipment.title', navigation: { visible: true, order: 40, icon: 'Operation' } }
    },
    {
      path: 'equipment/observations/admin', name: 'EquipmentObservationAdmin',
      component: () => import('./views/observations/admin.vue'),
      meta: { titleKey: 'equipment.observation.configManagement', pageId: 'equipment.observations.admin', requiresAdmin: true,
        parentTitleKey: 'equipment.title', navigation: { visible: true, order: 50, icon: 'Setting' } }
    },
    {
      path: 'equipment/observations/data', name: 'EquipmentObservationData',
      component: () => import('./views/observations/data.vue'),
      meta: { titleKey: 'equipment.observation.dataManagement', pageId: 'equipment.observations.data', requiresAdmin: true,
        parentTitleKey: 'equipment.title', navigation: { visible: true, order: 60, icon: 'List' } }
    }
  ]
}
