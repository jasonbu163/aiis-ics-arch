/**
 * 文件路径: /frontend-js/src/config/api.js
 * 功能描述: API 全局配置文件，定义后端接口基础设置
 * 主要功能:
 *   - API 基础 URL 配置
 *   - 请求超时时间配置
 */
// API 配置
const API_CONFIG = {
  // 后端 API 基础 URL（使用相对路径，让 Vite 代理处理）
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  // 请求超时时间（毫秒）
  TIMEOUT: parseInt(import.meta.env.VITE_REQUEST_TIMEOUT) || 10000,
}

export default API_CONFIG
