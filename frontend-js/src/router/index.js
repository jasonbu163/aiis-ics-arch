/**
 * 文件路径: /frontend-js/src/router/index.js
 * 功能描述: Vue Router 路由配置，定义应用所有路由规则
 * 主要功能:
 *   - 路由懒加载配置
 *   - 路由元信息定义（标题、权限、父级菜单）
 *   - 路由守卫（认证检查、权限验证）
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const moduleManifestFiles = import.meta.glob('../app/*/manifest.js', { eager: true })

const toModuleExportName = (moduleName) => {
  const pascalName = moduleName
    .split('-')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('')

  return `${pascalName.charAt(0).toLowerCase()}${pascalName.slice(1)}Module`
}

const getModuleNameFromPath = (path) => {
  const match = path.match(/\/app\/([^/]+)\/manifest\.js$/)
  return match?.[1]
}

const resolveModuleManifest = (path, manifestModule) => {
  const moduleName = getModuleNameFromPath(path)
  const namedExport = moduleName ? manifestModule[toModuleExportName(moduleName)] : null
  const manifest = manifestModule.default || namedExport

  if (!manifest || !Array.isArray(manifest.routes)) {
    throw new Error(`[router] Invalid module manifest: ${path}`)
  }

  return {
    order: Number.isFinite(manifest.order) ? manifest.order : 1000,
    name: manifest.name || moduleName || path,
    routes: manifest.routes
  }
}

const moduleManifests = Object.entries(moduleManifestFiles)
  .map(([path, manifestModule]) => resolveModuleManifest(path, manifestModule))
  .sort((current, next) => current.order - next.order || current.name.localeCompare(next.name))

if (import.meta.env.DEV) {
  console.info('[router] loaded module manifests:', moduleManifests.map(module => module.name).join(', '))
}

const moduleRoutes = moduleManifests.flatMap(module => module.routes)

const toAbsolutePath = (path) => path.startsWith('/') ? path : `/${path}`

const resolveDefaultAuthenticatedPath = (userStore) => {
  const defaultRoute = moduleRoutes.find(route => (
    route.meta?.pageId &&
    !route.path.includes(':') &&
    userStore.hasPageAccess(route.meta.pageId)
  ))

  return defaultRoute ? toAbsolutePath(defaultRoute.path) : '/login'
}

const routes = [
  {
    path: '/login',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        name: 'Login',
        component: () => import('@/pages/login/index.vue'),
        meta: { titleKey: 'breadcrumb.login', requiresAuth: false }
      }
    ]
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: () => resolveDefaultAuthenticatedPath(useUserStore()),
    children: moduleRoutes
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth === false) {
    next()
    return
  }

  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    console.warn(`管理员页面访问被拒绝: ${to.path}`)
    const fallbackPath = resolveDefaultAuthenticatedPath(userStore)
    next(fallbackPath !== '/login' && fallbackPath !== to.path ? fallbackPath : '/login')
    return
  }

  if (to.meta.pageId && !userStore.hasPageAccess(to.meta.pageId)) {
    console.warn(`页面访问被拒绝: ${to.path}，需要页面 ID: ${to.meta.pageId}`)
    const fallbackPath = resolveDefaultAuthenticatedPath(userStore)
    next(fallbackPath !== '/login' && fallbackPath !== to.path ? fallbackPath : '/login')
    return
  }

  console.log('路由守卫通过:', to.path)
  next()
})

export default router
