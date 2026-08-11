/**
 * 文件路径: /frontend-js/src/app/system/api/mock.js
 * 功能描述: 系统模块 mock facade，聚合用户和字典管理诊断 mock
 * 主要功能:
 *   - 暴露与系统模块 API facade 对应的 mock 实现
 *   - 让模块内 API 文件统一通过 ./mock 使用诊断数据
 */
import { createMockMutation } from '@/api/mock/_diagnostic'

export * from './mock/user'
export * from './mock/dict'

export async function resetUserPassword(id, data) {
  return {
    ...createMockMutation('user.resetUserPassword', data, id),
    requiresRelogin: false
  }
}
