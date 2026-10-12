/**
 * 文件路径: /frontend-js/src/app/auxiliary/manifest.js
 * 功能描述: 辅助模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露停机、班组和能耗单价页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const auxiliaryModule = {
  name: 'auxiliary',
  enabled: true,
  navigation: { titleKey: 'auxiliary.title', icon: 'Tools' },
  order: 60,
  routes: [
    {
      path: 'auxiliary/stop',
      name: 'AuxiliaryStop',
      component: () => import('./views/stop/index.vue'),
      meta: {
        titleKey: 'auxiliary.stop.title',
        pageId: 'auxiliary.stop',
        parentTitleKey: 'auxiliary.title',
        navigation: { visible: true, order: 10, icon: 'VideoPause' }
      }
    },
    {
      path: 'auxiliary/shift',
      name: 'AuxiliaryShift',
      component: () => import('./views/shift/index.vue'),
      meta: {
        titleKey: 'auxiliary.shift.title',
        pageId: 'auxiliary.shift',
        parentTitleKey: 'auxiliary.title',
        navigation: { visible: true, order: 20, icon: 'Timer' }
      }
    },
    {
      path: 'auxiliary/price',
      name: 'AuxiliaryPrice',
      component: () => import('./views/price/index.vue'),
      meta: {
        titleKey: 'auxiliary.price.title',
        pageId: 'auxiliary.price',
        parentTitleKey: 'auxiliary.title',
        navigation: { visible: true, order: 30, icon: 'PriceTag' }
      }
    }
  ]
}
