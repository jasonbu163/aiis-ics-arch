/** 文件路径: /frontend-js/tests/module-registry/brand-options.test.mjs
 * 功能描述: 已打包 Logo 来源限制、对齐三值、光晕四值/三段及旧别名的纯合同矩阵。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { resolveBrandOptions, fallbackLogoFile } from '../../src/config/brandOptions.js'
const assets = {
  [`../assets/brand/${fallbackLogoFile}`]: '/bundled/demo.svg',
  '../assets/brand/public-test.svg': '/bundled/public-test.svg'
}

test('only bundled filenames resolve; missing, unknown and unsafe inputs fall back', () => {
  assert.equal(resolveBrandOptions({ VITE_BRAND_LOGO_FILE: ' public-test.svg ' }, assets).logoUrl, '/bundled/public-test.svg')
  for (const file of [undefined, '', 'missing.svg', '.', '..', '../public-test.svg', '/public-test.svg', 'brand/public-test.svg', 'brand\\public-test.svg', 'https://example.invalid/logo.svg', 'file:///logo.svg', 'C:\\logo.svg', '%2e%2e%2flogo.svg']) {
    const result = resolveBrandOptions({ VITE_BRAND_LOGO_FILE: file }, assets)
    assert.equal(result.logoFile, fallbackLogoFile)
    assert.equal(result.logoUrl, '/bundled/demo.svg')
  }
})

test('all alignments normalize and invalid settings use the center default', () => {
  for (const alignment of ['left', 'center', 'right']) assert.equal(resolveBrandOptions({ VITE_BRAND_LOGO_ALIGN: ` ${alignment.toUpperCase()} ` }, assets).logoAlign, alignment)
  for (const value of [undefined, '', 'start', 4]) assert.equal(resolveBrandOptions({ VITE_BRAND_LOGO_ALIGN: value }, assets).logoAlign, 'center')
})

test('three independent glow segments support every mode, legacy alias and defaults', () => {
  assert.deepEqual(resolveBrandOptions({}, assets).glowModes, { left: 'light', center: 'accent', right: 'accent' })
  for (const segment of ['left', 'center', 'right']) {
    for (const mode of ['light', 'high-light', 'accent', 'none', 'hight-light']) {
      const env = { [`VITE_BRAND_GLOW_${segment.toUpperCase()}`]: ` ${mode.toUpperCase()} ` }
      assert.equal(resolveBrandOptions(env, assets).glowModes[segment], mode === 'hight-light' ? 'high-light' : mode)
    }
    assert.equal(resolveBrandOptions({ [`VITE_BRAND_GLOW_${segment.toUpperCase()}`]: 'unknown' }, assets).glowModes[segment], segment === 'left' ? 'light' : 'accent')
  }
  assert.deepEqual(resolveBrandOptions({ VITE_BRAND_GLOW_LEFT: 'none', VITE_BRAND_GLOW_CENTER: 'HIGH-LIGHT', VITE_BRAND_GLOW_RIGHT: 'light' }, assets).glowModes, { left: 'none', center: 'high-light', right: 'light' })
})
