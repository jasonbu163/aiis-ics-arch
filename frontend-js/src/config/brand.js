/**
 * 文件路径: /frontend-js/src/config/brand.js
 * 功能描述: 解析已打包品牌资产和五项 Vite 配置，供登录页与认证壳共用。
 * 主要功能: 限制 Logo 来源为本地 glob，缺失资产回退通用 Demo，沿用旧对齐与三段光晕合同。
 */
import { resolveBrandOptions } from './brandOptions.js'

const brandAssets = import.meta.glob('../assets/brand/*', {
  eager: true,
  import: 'default',
  query: '?url'
})
const options = resolveBrandOptions(import.meta.env, brandAssets)
export const brandLogoUrl = options.logoUrl
export const brandLogoAlign = options.logoAlign
export const brandGlowModes = options.glowModes
