/** 公共纯方案逻辑的 TypeScript 声明；规则只在相邻 JS 实现。 */
export type PaletteField = 'background' | 'surface' | 'surfaceMuted' | 'text' | 'textMuted' | 'border' | 'accent' | 'accentStrong' | 'onAccent'
export type NumberField = 'cardPaddingPx' | 'actionGapPx' | 'cardRadiusPx' | 'controlRadiusPx'
export interface DesignProfile {
  schemaVersion: 1
  themes: Record<'light' | 'dark', Record<PaletteField, string>>
  shared: Record<NumberField, number> & { tableDensity: 'standard' | 'compact' }
}
export const PALETTE_FIELDS: readonly PaletteField[]
export const NUMBER_FIELDS: Readonly<Record<NumberField, readonly [number, number]>>
export function normalizeProfile(input: unknown): DesignProfile
export function profileJSON(input: unknown): string
export function profileVariables(input: unknown, theme: 'light' | 'dark'): Record<string, string>
export function profileCSS(input: unknown): string
