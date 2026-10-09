/**
 * 文件路径: /frontend-js/scripts/check-page-access.mjs
 * 功能描述: 按 Vite mode/local/进程覆盖读取并校验角色配置；裸调用仅帮助。
 */
import { loadEnv } from 'vite'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadRegistry } from './check-module-manifests.mjs'
import { parseRolePageAccess } from '../src/config/pageAccess.js'

export async function checkPageAccess(root, mode) {
  const env = loadEnv(mode, root, 'VITE_')
  const registry = await loadRegistry(root)
  const grants = parseRolePageAccess(env, registry)
  return { env, registry, grants }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2)
  if (args.length === 0 || args.includes('--help')) {
    console.log('Usage: node scripts/check-page-access.mjs --check --mode development|production\nChecks effective Vite env and local manifests; no external service I/O.')
  } else if (args.length !== 3 || args[0] !== '--check' || args[1] !== '--mode' || !args[2] || args[2].startsWith('-')) {
    console.error('Unknown arguments; use --help.')
    process.exitCode = 2
  } else {
    try {
      const { grants } = await checkPageAccess(fileURLToPath(new URL('../', import.meta.url)), args[2])
      console.log(`Page access passed: supervisor=${grants.supervisor.length}, operator=${grants.operator.length}, mode=${args[2]}`)
    } catch (error) {
      console.error(error.message)
      process.exitCode = 1
    }
  }
}
