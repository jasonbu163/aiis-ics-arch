/**
 * 文件路径: /frontend-js/src/config/permissions.js
 * 功能描述: 将 Vite 项目角色数组按活动 Registry 校验后提供给用户 store；admin 不配置。
 */
import { moduleRegistry } from '../app/moduleRegistry.js'
import { parseRolePageAccess } from './pageAccess.js'

const viteEnv = import.meta.env || {}
export const ROLE_PAGE_ACCESS = parseRolePageAccess(viteEnv, moduleRegistry)
export const isLoginDemoAccountsEnabled = viteEnv.VITE_LOGIN_DEMO_ACCOUNTS_ENABLED === 'true'
