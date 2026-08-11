/**
 * 文件路径: /frontend-js/src/config/permissions.js
 * 功能描述: 前端角色页面可访问性与登录演示账号显示配置
 * 主要功能:
 *   - 解析 Vite 注入的 role -> leaf page id JSON 映射
 *   - 配置损坏时默认拒绝页面访问
 *   - 提供 system 叶子页面与演示账号显示开关
 */

export const SYSTEM_PAGE_IDS = [
  'system.user',
  'system.projection-mapping'
]

const PAGE_ID_PATTERN = /^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$/

export const parseRolePageAccess = (rawConfig) => {
  if (typeof rawConfig !== 'string' || !rawConfig.trim()) {
    return {}
  }

  try {
    const configuredPermissions = JSON.parse(rawConfig)
    if (!configuredPermissions || Array.isArray(configuredPermissions) || typeof configuredPermissions !== 'object') {
      return {}
    }

    for (const [role, pageIds] of Object.entries(configuredPermissions)) {
      if (!role.trim() || role === 'admin' || !Array.isArray(pageIds)) {
        return {}
      }
      if (pageIds.some(pageId => typeof pageId !== 'string' || !PAGE_ID_PATTERN.test(pageId))) {
        return {}
      }
      if (new Set(pageIds).size !== pageIds.length) {
        return {}
      }
    }

    return configuredPermissions
  } catch {
    return {}
  }
}

const viteEnv = import.meta.env || {}

export const ROLE_PAGE_ACCESS = parseRolePageAccess(
  viteEnv.VITE_ROLE_PAGE_ACCESS_JSON
)

export const isLoginDemoAccountsEnabled = viteEnv.VITE_LOGIN_DEMO_ACCOUNTS_ENABLED === 'true'
