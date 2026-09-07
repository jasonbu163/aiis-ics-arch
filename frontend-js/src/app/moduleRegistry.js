/**
 * 文件路径: /frontend-js/src/app/moduleRegistry.js
 * 功能描述: 唯一 Vite 模块发现入口，路由、菜单和文案共同消费同一规范化 Registry。
 */
import { assembleGlobalMessages, createModuleRegistry } from './moduleManifest.js'

const manifests = import.meta.glob('./*/manifest.js', { eager: true })
const locales = import.meta.glob('./*/locales/*.json', { eager: true, import: 'default' })
const globals = import.meta.glob('../locales/*/*.json', { eager: true, import: 'default' })
const appPaths = files => Object.fromEntries(Object.entries(files).map(([path, value]) => [`/app/${path.slice(2)}`, value]))

export const moduleRegistry = createModuleRegistry(appPaths(manifests), appPaths(locales), assembleGlobalMessages(globals))
export const { activeModules, activeModuleNames, routes: moduleRoutes, messages } = moduleRegistry
