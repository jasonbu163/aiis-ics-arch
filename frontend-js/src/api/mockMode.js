/**
 * 文件路径: /frontend-js/src/api/mockMode.js
 * 功能描述: 前端 API mock 诊断模式开关
 * 主要功能:
 *   - 读取 VITE_FRONTEND_MOCK_ENABLED 环境变量
 *   - 在 API facade 层切换真实 HTTP 与同名 mock 实现
 *   - 保持 request 拦截器只处理真实 HTTP 请求
 */

export const isFrontendMockEnabled = () => import.meta.env.VITE_FRONTEND_MOCK_ENABLED === 'true'

export const callApi = (mockFn, realFn, apiName) => {
  if (!isFrontendMockEnabled()) {
    return realFn()
  }

  if (typeof mockFn !== 'function') {
    return Promise.reject(new Error(`[frontend-mock] Missing mock implementation for ${apiName}`))
  }

  return mockFn()
}
