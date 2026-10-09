/**
 * 文件路径: /frontend-js/src/config/brandOptions.js
 * 功能描述: 纯品牌文件名、对齐和三段光晕解析；不读取文件或环境、不加载外部资源。
 */
export const fallbackLogoFile = 'demo-organization-logo.svg'
const alignments = new Set(['left', 'center', 'right'])
const glowModes = new Set(['light', 'high-light', 'accent', 'none'])
const normalize = value => typeof value === 'string' ? value.trim().toLowerCase() : ''
const resolveGlow = (value, fallback) => {
  const raw = normalize(value)
  const mode = raw === 'hight-light' ? 'high-light' : raw
  return glowModes.has(mode) ? mode : fallback
}

export function resolveBrandOptions(env, assets) {
  const candidate = typeof env.VITE_BRAND_LOGO_FILE === 'string' ? env.VITE_BRAND_LOGO_FILE.trim() : ''
  const validFile = candidate && !/[/\\:?#\u0000]/.test(candidate) && !candidate.includes('..') && candidate !== '.'
  const key = `../assets/brand/${candidate}`
  const file = validFile && Object.hasOwn(assets, key) ? candidate : fallbackLogoFile
  const align = normalize(env.VITE_BRAND_LOGO_ALIGN)
  return {
    logoFile: file,
    logoUrl: assets[`../assets/brand/${file}`],
    logoAlign: alignments.has(align) ? align : 'center',
    glowModes: {
      left: resolveGlow(env.VITE_BRAND_GLOW_LEFT, 'light'),
      center: resolveGlow(env.VITE_BRAND_GLOW_CENTER, 'accent'),
      right: resolveGlow(env.VITE_BRAND_GLOW_RIGHT, 'accent')
    }
  }
}
