/**
 * 文件路径: /frontend-js/src/app/system/manifest.js
 * 功能描述: 系统模块前端 manifest，集中声明模块路由
 * 主要功能:
 *   - 暴露用户管理和 Projection 映射设置页面路由定义
 *   - 保持 router 实例和导航守卫仍由 src/router 统一管理
 */

export const systemModule = {
  name: 'system',
  enabled: true,
  order: 80,
  navigation: { titleKey: 'system.title', icon: 'Setting' },
  routes: [
    {
      path: 'system/user',
      name: 'SystemUser',
      component: () => import('./views/user/index.vue'),
      meta: {
        titleKey: 'system.user',
        pageId: 'system.user',
        parentTitleKey: 'system.title',
        navigation: { visible: true, order: 10, icon: 'User' }
      }
    },
    {
      path: 'system/dict',
      name: 'SystemProjectionMapping',
      component: () => import('./views/dict/index.vue'),
      meta: {
        titleKey: 'system.mapping.title',
        pageId: 'system.projection-mapping',
        requiresAdmin: true,
        parentTitleKey: 'system.title',
        navigation: { visible: true, order: 20, icon: 'Collection' }
      }
    }
  ]
}
