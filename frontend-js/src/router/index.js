/**
 * 文件路径: /frontend-js/src/router/index.js
 * 功能描述: 消费统一模块 Registry，配置认证壳、默认入口及一致的页面访问 gate。
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { moduleRegistry, moduleRoutes } from '@/app/moduleRegistry'
import { canAccessRoute, defaultAuthenticatedPath } from '@/app/moduleManifest'

const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresAuth: false },
    children: [{
      path: '', name: 'Login', component: () => import('@/pages/login/index.vue'),
      meta: { titleKey: 'breadcrumb.login', requiresAuth: false }
    }]
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: () => defaultAuthenticatedPath(moduleRegistry, useUserStore()),
    children: moduleRoutes
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.name === 'Login') return next()
  const access = useUserStore()
  if (!access.isLoggedIn) return next('/login')
  // 必须匹配活动 Registry；未知/已删除 URL 和残留 pageId grant 均不能重建页面。
  const matched = to.matched.at(-1)
  const canonical = matched?.aliasOf || matched
  const route = moduleRegistry.routeRecords.find(route => route.name !== undefined
    ? route.name === canonical?.name : route.path === canonical?.path)
  if (!route || !canAccessRoute({ ...route, meta: to.meta }, access)) {
    const fallback = defaultAuthenticatedPath(moduleRegistry, access)
    return next(fallback !== to.path ? fallback : '/login')
  }
  next()
})

export default router
