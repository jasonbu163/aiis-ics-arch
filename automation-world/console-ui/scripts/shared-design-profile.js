/** CU 私有 Node I/O：锚定唯一公共 JSON/CSS，共用校验、内容版本与单文件安全替换；导入无 I/O。 */
import { readFile, writeFile, rename, unlink } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { createHash, randomUUID } from 'node:crypto'
import { normalizeProfile, profileJSON, profileCSS } from '../src/ui/design-profile.js'

const jsonPath = fileURLToPath(new URL('../src/ui/styles/design-profile.json', import.meta.url))
const cssPath = fileURLToPath(new URL('../src/ui/styles/design-profile.generated.css', import.meta.url))
const revision = (json, css) => createHash('sha256').update(JSON.stringify([json, css])).digest('hex')
async function readTarget(path) {
  try { return await readFile(path, 'utf8') }
  catch (error) { if (error.code === 'ENOENT') return null; throw error }
}
async function replace(path, content) {
  const temp = `${path}.tmp-${process.pid}-${randomUUID()}`
  try { await writeFile(temp, content, { encoding: 'utf8', flag: 'wx' }); await rename(temp, path) }
  finally { await unlink(temp).catch(() => {}) }
}
export async function readSharedRevision() {
  const [json, css] = await Promise.all([readTarget(jsonPath), readTarget(cssPath)])
  return revision(json, css)
}
export async function readPublicProfile() {
  return normalizeProfile(JSON.parse(await readFile(jsonPath, 'utf8')))
}
export async function writeSharedProfile(input, expectedRevision) {
  // 所有内容先完整校验/生成，再核对版本和开始任何目标替换。
  const json = profileJSON(input)
  const css = profileCSS(input)
  if (expectedRevision !== undefined && await readSharedRevision() !== expectedRevision) {
    throw Object.assign(new Error('Shared source changed'), { code: 'conflict' })
  }
  await replace(jsonPath, json)
  await replace(cssPath, css)
  return revision(json, css)
}
export async function generateSharedCSS() {
  await replace(cssPath, profileCSS(await readPublicProfile()))
}
export async function checkSharedCSS() {
  return await readTarget(cssPath) === profileCSS(await readPublicProfile())
}
