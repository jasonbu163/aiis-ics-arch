/** 公共方案纯逻辑：严格校验/规范化与确定性 token/CSS 映射；无 I/O 或应用副作用。 */
export const PALETTE_FIELDS = Object.freeze(['background', 'surface', 'surfaceMuted', 'text', 'textMuted', 'border', 'accent', 'accentStrong', 'onAccent'])
export const NUMBER_FIELDS = Object.freeze({ cardPaddingPx: [12, 32], actionGapPx: [4, 24], cardRadiusPx: [8, 28], controlRadiusPx: [4, 20] })
const tokens = ['bg', 'surface', 'surface-muted', 'text', 'text-muted', 'border', 'accent', 'accent-strong', 'on-accent']
function exact(value, keys, path) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== keys.length || keys.some(key => !Object.hasOwn(value, key))) throw new Error(path)
}
export function normalizeProfile(input) {
  exact(input, ['schemaVersion', 'themes', 'shared'], 'profile')
  if (input.schemaVersion !== 1) throw new Error('schemaVersion')
  exact(input.themes, ['light', 'dark'], 'themes')
  const themes = {}
  for (const theme of ['light', 'dark']) {
    exact(input.themes[theme], PALETTE_FIELDS, `themes.${theme}`)
    themes[theme] = {}
    for (const key of PALETTE_FIELDS) {
      const value = input.themes[theme][key]
      if (typeof value !== 'string' || !/^#[0-9a-fA-F]{6}$/.test(value)) throw new Error(`themes.${theme}.${key}`)
      themes[theme][key] = value.toLowerCase()
    }
  }
  exact(input.shared, [...Object.keys(NUMBER_FIELDS), 'tableDensity'], 'shared')
  const shared = {}
  for (const [key, [min, max]] of Object.entries(NUMBER_FIELDS)) {
    const value = input.shared[key]
    if (!Number.isInteger(value) || value < min || value > max) throw new Error(`shared.${key}`)
    shared[key] = value
  }
  if (!['standard', 'compact'].includes(input.shared.tableDensity)) throw new Error('shared.tableDensity')
  shared.tableDensity = input.shared.tableDensity
  return { schemaVersion: 1, themes, shared }
}
export function profileJSON(input) { return JSON.stringify(normalizeProfile(input), null, 2) + '\n' }
export function profileVariables(input, theme) {
  const profile = normalizeProfile(input)
  if (!['light', 'dark'].includes(theme)) throw new Error('theme')
  const palette = profile.themes[theme]
  const vars = {}
  PALETTE_FIELDS.forEach((key, i) => { vars[`--agent-${tokens[i]}`] = palette[key] })
  const rgb = [1, 3, 5].map(offset => parseInt(palette.accent.slice(offset, offset + 2), 16)).join(', ')
  const alphas = theme === 'light' ? [0.1, 0.16, 0.1, 0.22, 0.06] : [0.14, 0.2, 0.12, 0.24, 0.08]
  ;['accent-soft', 'accent-surface', 'sidebar-active-bg', 'card-border-hover', 'table-row-hover'].forEach((key, i) => { vars[`--agent-${key}`] = `rgba(${rgb}, ${alphas[i]})` })
  const s = profile.shared
  Object.assign(vars, {
    '--agent-card-padding': `${s.cardPaddingPx}px`,
    '--agent-card-padding-compact': `${Math.max(8, s.cardPaddingPx - 6)}px`,
    '--agent-action-gap': `${s.actionGapPx}px`,
    '--agent-card-radius': `${s.cardRadiusPx}px`,
    '--agent-card-radius-compact': `${Math.max(4, s.cardRadiusPx - 4)}px`,
    '--agent-control-radius': `${s.controlRadiusPx}px`,
    '--agent-control-radius-small': `${Math.max(2, s.controlRadiusPx - 4)}px`,
    '--agent-table-cell-padding': s.tableDensity === 'standard' ? '8px' : '4px'
  })
  return vars
}
export function profileCSS(input) {
  return '/** 自动生成自 design-profile.json；不可手改。运行 pnpm design:profile --generate。 */\n' + ['light', 'dark'].map(theme => {
    const selector = theme === 'light' ? '.aw-ui' : '.aw-ui[data-aw-theme="dark"]'
    return selector + ' {\n' + Object.entries(profileVariables(input, theme)).map(([key, value]) => `  ${key}: ${value};`).join('\n') + '\n}\n'
  }).join('')
}
