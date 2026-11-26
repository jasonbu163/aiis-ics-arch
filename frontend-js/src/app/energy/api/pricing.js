/** 登录后的单价项目、现价及分时价格接口。 */
import request from '@/utils/request'

const base = '/energy/pricing'
const quiet = { suppressErrorMessage: true }
const itemPath = key => {
  // 浏览器会规范化单独的点段，服务端以原始路径区分它与字面百分号。
  if (key === '.' || key === '..') return key.replaceAll('.', '%252e')
  if (key === '%2e' || key === '%2e%2e') return key.replaceAll('%2e', '%25%32%65')
  return encodeURIComponent(key)
}

export const pricingItems = () => request.get(base + '/items', quiet)
export const createPricingItem = data => request.post(base + '/items', data, quiet)
export const updatePricingItem = (key, data) => request.patch(base + '/items/' + itemPath(key), data, quiet)
export const currentPrices = () => request.get(base + '/current', quiet)
export const hourlyPrices = params => request.get(base + '/hours', { ...quiet, params })
export const saveHourlyPrices = data => request.post(base + '/hours', data, quiet)
