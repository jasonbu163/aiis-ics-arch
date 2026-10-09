/**
 * 文件路径: /frontend-js/src/config/pageAccess.js
 * 功能描述: 无 I/O 的项目角色数组与 Registry 页面合同校验；浏览器和 Node 共用。
 */
const PAGE_ID_PATTERN = /^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$/
export const ROLE_ENV_KEYS = {
  supervisor: 'VITE_SUPERVISOR_PAGE_ACCESS_JSON',
  operator: 'VITE_OPERATOR_PAGE_ACCESS_JSON'
}
const fail = message => { throw new Error(`[page-access] ${message}`) }

export function parseRolePageAccess(env, registry) {
  if (Object.hasOwn(env, 'VITE_ROLE_PAGE_ACCESS_JSON')) {
    fail('VITE_ROLE_PAGE_ACCESS_JSON is retired; migrate to VITE_SUPERVISOR_PAGE_ACCESS_JSON and VITE_OPERATOR_PAGE_ACCESS_JSON.')
  }
  const grants = {}
  for (const [role, key] of Object.entries(ROLE_ENV_KEYS)) {
    const raw = env[key]
    if (typeof raw !== 'string' || !raw.trim()) fail(`${key}: missing JSON array; use [] for no access.`)
    let values
    try { values = JSON.parse(raw) } catch { fail(`${key}: invalid JSON.`) }
    if (!Array.isArray(values)) fail(`${key}: must be a JSON array.`)
    const seen = new Set()
    for (const pageId of values) {
      if (typeof pageId !== 'string' || !PAGE_ID_PATTERN.test(pageId)) fail(`${key}: invalid pageId ${JSON.stringify(pageId)}.`)
      if (seen.has(pageId)) fail(`${key}: duplicate pageId ${pageId}.`)
      seen.add(pageId)
      const route = registry.routeRecords.find(record => record.meta.pageId === pageId && !record.redirect && !record.children?.length)
      if (!route) {
        const disabled = registry.modules.some(module => !module.enabled && module.routeRecords.some(record => record.meta.pageId === pageId))
        fail(`${key}: ${disabled ? 'disabled' : 'unknown'} pageId ${pageId}.`)
      }
      if (route.meta.requiresAdmin) fail(`${key}: admin-only pageId ${pageId}.`)
    }
    grants[role] = values
  }
  for (const pageId of grants.operator) {
    if (!grants.supervisor.includes(pageId)) fail(`${ROLE_ENV_KEYS.operator}: pageId ${pageId} is absent from ${ROLE_ENV_KEYS.supervisor}.`)
  }
  return grants
}
