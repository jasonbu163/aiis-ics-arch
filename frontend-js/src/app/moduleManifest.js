/**
 * 文件路径: /frontend-js/src/app/moduleManifest.js
 * 功能描述: 无 I/O 的模块合同校验、规范化、排序与装配 consumer 原语。
 */
export const localeCodes = ['en-US', 'zh-CN']
const own = (value, key) => Object.hasOwn(value, key)
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value)
const text = value => typeof value === 'string' && value.trim().length > 0
const fail = message => { throw new Error(`[module-registry] ${message}`) }
const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0
const order = (value, label) => {
  if (value === undefined) return 1000
  if (!Number.isFinite(value)) fail(`Invalid order: ${label}`)
  return value
}
const unique = (set, value, label) => {
  if (set.has(value)) fail(`Duplicate ${label}: ${value}`)
  set.add(value)
}
const keys = (value, prefix = '') => Object.entries(value).flatMap(([key, child]) => {
  const path = prefix ? `${prefix}.${key}` : key
  return object(child) ? keys(child, path) : [path]
}).sort()
export const resolveMessage = (messages, key) => key.split('.').reduce(
  (value, part) => object(value) && own(value, part) ? value[part] : undefined, messages
)
export const toAbsolutePath = path => `/${path.replace(/^\/+|\/+$/g, '')}`
const childPath = (path, parent = '') => toAbsolutePath(path.startsWith('/') ? path : `${parent}/${path}`)
const validateRoutePath = path => {
  // 参数的 ?/*/+ 与自定义正则属于 Vue Router 源码语法，不是 URL query/hash。
  const staticPath = path.replace(/:[a-zA-Z0-9_]+(?:\((?:\\.|[^)])*\))?[?*+]?/g, '')
  if (/[?#]/.test(staticPath) || path.includes('//')) fail(`Invalid route path: ${path}`)
}
const hasNavigation = routes => routes.some(route => own(route?.meta || {}, 'navigation') || (Array.isArray(route?.children) && hasNavigation(route.children)))
const flattenRoutes = (routes, parent = '', parentMeta = {}) => routes.flatMap(route => {
  const path = childPath(route.path, parent)
  const meta = { ...parentMeta, ...route.meta }
  return [{ ...route, path, meta }, ...flattenRoutes(route.children || [], path, meta)]
})

// 与历史具名导出保持一致；新模块推荐 default export。
const exportName = name => {
  const pascal = name.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join('')
  return `${pascal.charAt(0).toLowerCase()}${pascal.slice(1)}Module`
}

export function assembleGlobalMessages(files) {
  const result = Object.fromEntries(localeCodes.map(locale => [locale, {}]))
  for (const [path, messages] of Object.entries(files)) {
    const match = path.match(/\/(en-US|zh-CN)\/([^/]+)\.json$/)
    if (!match || !object(messages)) fail(`Invalid global locale: ${path}`)
    const [, locale, namespace] = match
    if (own(result[locale], namespace)) fail(`Duplicate global namespace: ${namespace}`)
    result[locale][namespace] = messages
  }
  return result
}

function navigation(value, label, leaf = false) {
  if (value === undefined) return undefined
  if (!object(value)) fail(`Invalid navigation: ${label}`)
  if (leaf && own(value, 'visible') && typeof value.visible !== 'boolean') fail(`Invalid navigation visible: ${label}`)
  if (!leaf && !text(value.titleKey)) fail(`Missing navigation titleKey: ${label}`)
  if (own(value, 'icon') && !text(value.icon)) fail(`Invalid navigation icon: ${label}`)
  if (own(value, 'children')) fail(`Navigation supports group/leaf only: ${label}`)
  return { ...value, order: order(value.order, label) }
}

/** 完整 Core 装配默认要求 system；纯隔离 fixture 可显式提供 requiredModules。 */
export function createModuleRegistry(manifestFiles, localeFiles, globalMessages, { requiredModules = ['system'] } = {}) {
  const names = new Set()
  const routeNames = new Set(['Login'])
  const paths = new Map([['/', null], ['/login', null]])
  const pageIds = new Set()
  const modules = Object.entries(manifestFiles).map(([path, exports]) => {
    const directory = path.match(/\/app\/([^/]+)\/manifest\.js$/)?.[1]
    if (!directory) fail(`Invalid manifest path: ${path}`)
    const manifest = exports.default || exports[exportName(directory)]
    if (!object(manifest) || !Array.isArray(manifest.routes)) fail(`Invalid manifest: ${path}`)
    const name = manifest.name || directory
    unique(names, name, 'module name')
    if (name !== directory || !/^[a-z][a-z0-9_-]*$/.test(name)) fail(`Module name must match directory: ${path}`)
    if (own(manifest, 'enabled') && typeof manifest.enabled !== 'boolean') fail(`Invalid enabled: ${name}`)
    if (requiredModules.includes(name) && manifest.enabled !== true) fail(`Required module must declare enabled: true: ${name}`)
    const modern = own(manifest, 'enabled') || own(manifest, 'navigation') || hasNavigation(manifest.routes)
    const group = navigation(manifest.navigation, name)
    const normalizeRoutes = (records, parents = [{ path: '', ancestors: [] }]) => records.map((route, index) => {
      if (!object(route) || typeof route.path !== 'string' || (own(route, 'meta') && !object(route.meta))) fail(`Invalid route: ${name}[${index}]`)
      if (own(route, 'children') && !Array.isArray(route.children)) fail(`Invalid route children: ${name}[${index}]`)
      const meta = route.meta || {}
      const isLeaf = !route.children?.length && !route.redirect
      if (modern && isLeaf) {
        if (!text(route.name) || !text(meta.pageId) || !text(meta.titleKey)) fail(`Missing name/pageId/titleKey: ${route.path}`)
        if (typeof route.component !== 'function' && !object(route.component) && !object(route.components)) fail(`Missing route component: ${route.name}`)
      }
      validateRoutePath(route.path)
      const fullPath = childPath(route.path, parents[0].path)
      if (route.name !== undefined) {
        if (!text(route.name)) fail(`Invalid route name: ${route.path}`)
        unique(routeNames, route.name, 'route name')
      }
      if (meta.pageId !== undefined) {
        if (!text(meta.pageId)) fail(`Invalid pageId: ${route.path}`)
        unique(pageIds, meta.pageId, 'pageId')
      }
      const aliases = route.alias === undefined ? [] : Array.isArray(route.alias) ? route.alias : [route.alias]
      for (const alias of aliases) {
        if (!text(alias)) fail(`Invalid alias: ${route.path}`)
        validateRoutePath(alias)
      }
      // 展开父 alias 派生路径；只允许祖先与其唯一空默认子节点共用 URL，不豁免 sibling。
      const variants = parents.flatMap(parent => [route.path, ...aliases].map(localPath => {
        const path = childPath(localPath, parent.path)
        const key = path.toLowerCase()
        const previous = paths.get(key)
        if (paths.has(key) && previous !== route && !(localPath === '' && parent.ancestors.includes(previous))) {
          fail(`Duplicate route path: ${path}`)
        }
        paths.set(key, route)
        return { path, ancestors: [...parent.ancestors, route] }
      }))
      for (const flag of ['requiresAdmin', 'requiresAuth']) {
        if (own(meta, flag) && typeof meta[flag] !== 'boolean') fail(`Invalid ${flag}: ${route.name}`)
      }
      const leaf = navigation(meta.navigation, route.name || fullPath, true)
      if (leaf?.visible === true && (/[:*]/.test(fullPath) || !isLeaf)) fail(`Dynamic or non-leaf route cannot be visible: ${route.name}`)
      const result = { ...route, meta: { ...meta, navigation: leaf }, order: order(route.order ?? leaf?.order, route.name) }
      if (route.children) result.children = normalizeRoutes(route.children, variants)
      return result
    }).sort((a, b) => a.order - b.order)
    const routes = normalizeRoutes(manifest.routes)
    return { name, enabled: manifest.enabled !== false, modern, order: order(manifest.order, name), navigation: group, routes, routeRecords: flattenRoutes(routes) }
  }).sort((a, b) => a.order - b.order || compare(a.name, b.name))
  for (const name of requiredModules) {
    if (!names.has(name)) fail(`Missing required module: ${name}`)
  }

  const namespaceOwners = new Map()
  const allMessages = Object.fromEntries(localeCodes.map(locale => [locale, { ...globalMessages[locale] }]))
  for (const locale of localeCodes) {
    for (const namespace of Object.keys(globalMessages[locale] || {})) namespaceOwners.set(namespace, '<global>')
  }
  const localeRecords = []
  const localeNamespaces = new Set()
  for (const [path, messages] of Object.entries(localeFiles).sort(([a], [b]) => compare(a, b))) {
    const match = path.match(/\/app\/([^/]+)\/locales\/(?:(.+)\.)?(en-US|zh-CN)\.json$/)
    if (!match || !object(messages)) fail(`Invalid module locale: ${path}`)
    const [, moduleName, alias, locale] = match
    // 不含 manifest 的目录不是已注册模块，历史孤立文案不自动获得装配权。
    if (!names.has(moduleName)) continue
    const namespace = alias || moduleName
    if (namespaceOwners.has(namespace) && namespaceOwners.get(namespace) !== moduleName) fail(`Duplicate locale namespace: ${namespace}`)
    namespaceOwners.set(namespace, moduleName)
    unique(localeNamespaces, `${locale}:${namespace}`, 'locale namespace')
    allMessages[locale][namespace] = messages
    localeRecords.push({ moduleName, namespace, locale, messages })
  }
  for (const [namespace, owner] of namespaceOwners) {
    if (owner === '<global>') continue
    if (!localeCodes.every(locale => localeNamespaces.has(`${locale}:${namespace}`))) fail(`Missing bilingual locale: ${namespace}`)
    if (JSON.stringify(keys(allMessages['en-US'][namespace])) !== JSON.stringify(keys(allMessages['zh-CN'][namespace]))) fail(`Bilingual key mismatch: ${namespace}`)
  }
  for (const module of modules) {
    const titleKeys = [module.navigation?.titleKey, ...module.routeRecords.flatMap(route => [route.meta.titleKey, route.meta.parentTitleKey])].filter(key => key !== undefined)
    for (const key of titleKeys) {
      if (!text(key)) fail(`Invalid titleKey: ${module.name}`)
      const namespace = key.split('.')[0]
      if (module.modern && namespaceOwners.get(namespace) !== module.name) fail(`Title must use module namespace: ${module.name}: ${key}`)
      for (const locale of localeCodes) {
        if (!text(resolveMessage(allMessages[locale], key))) fail(`Missing ${locale} titleKey: ${module.name}: ${key}`)
      }
    }
  }

  const activeModules = modules.filter(module => module.enabled)
  const activeModuleNames = activeModules.map(module => module.name)
  const messages = Object.fromEntries(localeCodes.map(locale => [locale, { ...globalMessages[locale] }]))
  for (const record of localeRecords) {
    if (activeModuleNames.includes(record.moduleName)) messages[record.locale][record.namespace] = record.messages
  }
  for (const module of activeModules) {
    const titles = [module.navigation?.titleKey, ...module.routeRecords.flatMap(route => [route.meta.titleKey, route.meta.parentTitleKey])].filter(Boolean)
    for (const key of titles) {
      for (const locale of localeCodes) {
        if (!text(resolveMessage(messages[locale], key))) fail(`Inactive title namespace: ${module.name}: ${key}`)
      }
    }
  }
  const routes = activeModules.flatMap(module => module.routes)
  const routeRecords = activeModules.flatMap(module => module.routeRecords)
  const groups = activeModules.filter(module => module.navigation).map(module => ({
    name: module.name, ...module.navigation,
    children: module.routeRecords.filter(route => route.meta.navigation?.visible === true).map(route => ({
      name: route.name, path: toAbsolutePath(route.path), titleKey: route.meta.titleKey,
      icon: route.meta.navigation.icon, route
    }))
  }))
  return { modules, activeModules, activeModuleNames, routes, routeRecords, navigation: groups, messages }
}

/** 页面可见性仅消费调用方提供的权限；不是后端授权。未知、损坏或抛错输入拒绝访问。 */
export function canAccessRoute(route, access) {
  if (!route?.meta?.pageId || !access || access.isLoggedIn === false) return false
  if (access.isAdmin === true) return true
  if (route.meta.requiresAdmin || typeof access.hasPageAccess !== 'function') return false
  try { return access.hasPageAccess(route.meta.pageId) === true } catch { return false }
}

export const accessibleNavigation = (registry, access) => registry.navigation
  .map(group => ({ ...group, children: group.children.filter(leaf => canAccessRoute(leaf.route, access)) }))
  .filter(group => group.children.length > 0)

export function defaultAuthenticatedPath(registry, access) {
  const route = registry.routeRecords.find(route => !route.redirect && !route.children?.length && !/[:*]/.test(route.path) && canAccessRoute(route, access))
  return route ? toAbsolutePath(route.path) : '/login'
}

export const resolveNavigationIcon = (icon, components, fallback) =>
  typeof icon === 'string' && own(components, icon) ? components[icon] : fallback
