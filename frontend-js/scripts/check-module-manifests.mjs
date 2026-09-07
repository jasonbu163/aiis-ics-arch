/**
 * 文件路径: /frontend-js/scripts/check-module-manifests.mjs
 * 功能描述: Node 内建 API 读取本地静态 manifest/JSON；复用生产 Registry 校验，裸调用仅帮助。
 * 边界: manifest 是受信任源码，必须无副作用；本工具不执行页面懒加载、不读取 .env、不连接服务。
 */
import { readdir, readFile } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { assembleGlobalMessages, createModuleRegistry } from '../src/app/moduleManifest.js'

export async function loadRegistry(root) {
  const app = join(root, 'src/app')
  const manifestFiles = {}
  const localeFiles = {}
  const globalFiles = {}
  for (const directory of await readdir(app, { withFileTypes: true })) {
    if (!directory.isDirectory()) continue
    const entries = await readdir(join(app, directory.name))
    if (!entries.includes('manifest.js')) continue
    const manifestPath = join(app, directory.name, 'manifest.js')
    manifestFiles[manifestPath] = await import(pathToFileURL(manifestPath).href)
    if (!entries.includes('locales')) continue
    for (const filename of await readdir(join(app, directory.name, 'locales'))) {
      if (!filename.endsWith('.json')) continue
      const path = join(app, directory.name, 'locales', filename)
      localeFiles[path] = JSON.parse(await readFile(path, 'utf8'))
    }
  }
  for (const locale of ['en-US', 'zh-CN']) {
    for (const filename of await readdir(join(root, 'src/locales', locale))) {
      if (!filename.endsWith('.json')) continue
      const path = join(root, 'src/locales', locale, filename)
      globalFiles[path] = JSON.parse(await readFile(path, 'utf8'))
    }
  }
  return createModuleRegistry(manifestFiles, localeFiles, assembleGlobalMessages(globalFiles))
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2)
  if (args.length === 0 || args.includes('--help')) {
    console.log('Usage: node scripts/check-module-manifests.mjs --check\nValidates trusted local manifests and bilingual messages without .env or external I/O.')
  } else if (args.length !== 1 || args[0] !== '--check') {
    console.error('Unknown arguments; use --help.')
    process.exitCode = 2
  } else {
    try {
      const registry = await loadRegistry(fileURLToPath(new URL('../', import.meta.url)))
      console.log(`Module contracts passed: active=[${registry.activeModuleNames.join(', ')}], routes=${registry.routes.length}, groups=${registry.navigation.length}`)
    } catch (error) {
      console.error(error.message)
      process.exitCode = 1
    }
  }
}
