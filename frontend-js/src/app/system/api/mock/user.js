/**
 * 文件路径: /frontend-js/src/app/system/api/mock/user.js
 * 功能描述: user 前端 mock 诊断实现
 * 主要功能:
 *   - 在 VITE_FRONTEND_MOCK_ENABLED=true 时提供模块本地诊断数据
 *   - 与 /frontend-js/src/app/system/api/user.js 保持同名导出
 */
import {
  MOCK_LABEL,
  createMockMutation,
  createMockPage,
  createMockRecord
} from '@/api/mock/_diagnostic'

const makeUser = (apiName, index) => createMockRecord(apiName, index, {
  username: `frontend_mock_user_${index}`,
  name: `${MOCK_LABEL}-USER-${index}`,
  role: index === 1 ? 'supervisor' : 'operator',
  phone: `1990000000${index}`,
  email: `frontend-mock-${index}@example.invalid`,
  status: 'active'
})

export async function getUserList(params) {
  const apiName = 'user.getUserList'
  return createMockPage(apiName, params, [makeUser(apiName, 1), makeUser(apiName, 2)])
}

export async function getUserById(id) {
  return makeUser('user.getUserById', Number(id) || 1)
}

export async function createUser(data) {
  return createMockMutation('user.createUser', data)
}

export async function updateUser(id, data) {
  return createMockMutation('user.updateUser', data, id)
}

export async function deleteUser(id) {
  return createMockMutation('user.deleteUser', {}, id)
}
