/** CU 固定公共方案 CLI：显式导入/生成/只读校验；裸入口仅帮助。 */
import { readFile } from 'node:fs/promises'
import { isAbsolute } from 'node:path'
import { writeSharedProfile, generateSharedCSS, checkSharedCSS } from './shared-design-profile.js'
const args = process.argv.slice(2)
const help = 'CU design profile\n  pnpm design:profile [--help]\n  pnpm design:profile --import /absolute/path/profile.json\n  pnpm design:profile --generate\n  pnpm design:profile --check'
async function main() {
  if (!args.length || (args.length === 1 && args[0] === '--help')) { console.log(help); return }
  const importing = args.length === 2 && args[0] === '--import' && isAbsolute(args[1])
  if (!importing && !(args.length === 1 && ['--generate', '--check'].includes(args[0]))) throw new Error('Unsupported arguments. ' + help)
  if (args[0] === '--check') {
    if (!await checkSharedCSS()) throw new Error('Generated CSS missing or stale. Run pnpm design:profile --generate')
    console.log('Design profile and CSS are consistent.'); return
  }
  if (importing) await writeSharedProfile(JSON.parse(await readFile(args[1], 'utf8')))
  else await generateSharedCSS()
  console.log(importing ? 'Imported public JSON and generated CSS.' : 'Generated CSS.')
}
main().catch(error => {
  console.error(`Design profile failed: ${error.message}\nNo cross-file atomicity is promised. For I/O failure, inspect both fixed targets; restore valid public JSON from your backup if needed, then run pnpm design:profile --generate and --check.`)
  process.exitCode = 1
})
