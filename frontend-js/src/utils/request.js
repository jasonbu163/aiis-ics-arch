/**
 * 文件路径: /frontend-js/src/utils/request.js
 * 功能描述: Axios HTTP 请求封装，统一处理请求和响应拦截
 * 主要功能:
 *   - 请求拦截器：自动添加 Token 认证头
 *   - 保持请求/响应字段命名与后端契约一致
 *   - 响应拦截器：统一错误处理和消息提示
 *   - 401 未授权自动跳转登录页
 */
import axios from 'axios'
import API_CONFIG from '../config/api'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
})

const isLoginRequest = (config) => config?.url?.split('?')[0]?.endsWith('/auth/login')

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    const res = response.data

    if (response.config?.responseType === 'blob' || response.config?.responseType === 'arraybuffer') {
      return res
    }

    if (!res || typeof res !== 'object' || !Object.prototype.hasOwnProperty.call(res, 'code')) {
      return res
    }
    
    if (res.code !== 200) {
      const handledByLoginPage = isLoginRequest(response.config)

      if (!handledByLoginPage) {
        ElMessage.error(res.message || '请求失败')
      }
      
      if (res.code === 401 && !handledByLoginPage) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
      
      const responseError = new Error(res.message || '请求失败')
      responseError.code = res.code
      return Promise.reject(responseError)
    }
    
    return res.data
  },
  (error) => {
    console.error('HTTP 错误:', error)

    if (isLoginRequest(error.config)) {
      return Promise.reject(error)
    }
    
    let message = '网络错误，请稍后重试'
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          message = '未授权，请重新登录'
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问，权限不足'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || message
      }
    } else if (error.request) {
      message = '无法连接到服务器，请检查后端服务是否启动'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
