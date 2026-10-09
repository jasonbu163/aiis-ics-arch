/** 文件路径: /frontend-js/tests/module-registry/page-access.test.mjs
 * 功能描述: 角色配置正反例、三角色决策、Vite env 优先级与双语模块接入回归。 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, readFile, rm, readdir, cp } from 'node:fs/promises'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { loadEnv } from 'vite'
import { parseRolePageAccess } from '../../src/config/pageAccess.js'
import { loadRegistry } from '../../scripts/check-module-manifests.mjs'
import { checkPageAccess } from '../../scripts/check-page-access.mjs'
import { canAccessRoute, accessibleNavigation, defaultAuthenticatedPath, resolveMessage } from '../../src/app/moduleManifest.js'
const root = fileURLToPath(new URL('../../', import.meta.url))
const env = (supervisor = [], operator = []) => ({
  VITE_SUPERVISOR_PAGE_ACCESS_JSON: JSON.stringify(supervisor),
  VITE_OPERATOR_PAGE_ACCESS_JSON: JSON.stringify(operator)
})
const registry = await loadRegistry(root)

test('role arrays reject missing, broken, duplicate, forbidden and non-subset configuration', () => {
  assert.deepEqual(parseRolePageAccess(env(), registry), { supervisor: [], operator: [] })
  for (const role of ['SUPERVISOR', 'OPERATOR']) {
    const key = `VITE_${role}_PAGE_ACCESS_JSON`
    for (const raw of [undefined, '', '{broken', '{}', 'null', '[null]', '[4]', '["bad"]', '["/plan/list"]', '["plan.list","plan.list"]']) {
      assert.throws(() => parseRolePageAccess({ ...env(), [key]: raw }, registry), new RegExp(key))
    }
  }
  assert.throws(() => parseRolePageAccess({ ...env(), VITE_ROLE_PAGE_ACCESS_JSON: '{}' }, registry), /retired/)
  assert.throws(() => parseRolePageAccess(env(['missing.list']), registry), /unknown pageId missing.list/)
  assert.throws(() => parseRolePageAccess(env(['aiis_demo.example']), registry), /disabled pageId aiis_demo.example/)
  assert.throws(() => parseRolePageAccess(env(['system.projection-mapping']), registry), /admin-only/)
  assert.throws(() => parseRolePageAccess(env(['dashboard.home'], ['plan.list']), registry), /absent from VITE_SUPERVISOR/)
  assert.deepEqual(parseRolePageAccess(env(['dashboard.home', 'plan.list'], ['dashboard.home']), registry).operator, ['dashboard.home'])
})

test('admin, supervisor, operator and unknown share route/menu/default decisions', () => {
  const grants = parseRolePageAccess(env(['dashboard.home', 'plan.list'], ['dashboard.home']), registry)
  const matrix = {
    admin: { paths: ['/dashboard/home', '/plan/list', '/system/user', '/system/dict'], menus: ['dashboard', 'plan', 'system'], entry: '/dashboard/home' },
    supervisor: { paths: ['/dashboard/home', '/plan/list'], menus: ['dashboard', 'plan'], entry: '/dashboard/home' },
    operator: { paths: ['/dashboard/home'], menus: ['dashboard'], entry: '/dashboard/home' },
    unknown: { paths: [], menus: [], entry: '/login' }
  }
  for (const [role, expected] of Object.entries(matrix)) {
    const access = { isAdmin: role === 'admin', hasPageAccess: id => (grants[role] || []).includes(id) }
    assert.deepEqual(registry.routeRecords.filter(route => canAccessRoute(route, access)).map(route => route.path), expected.paths)
    assert.deepEqual(accessibleNavigation(registry, access).map(group => group.name), expected.menus)
    assert.equal(defaultAuthenticatedPath(registry, access), expected.entry)
    assert.equal(registry.routes.some(route => route.name === 'AiisDemoExample'), false)
  }
})

test('Vite shared env, local/mode and process priority feed the same checker', async () => {
  const fixture = await mkdtemp('/private/tmp/arch-fe002-env-')
  const roleKeys = ['VITE_SUPERVISOR_PAGE_ACCESS_JSON', 'VITE_OPERATOR_PAGE_ACCESS_JSON', 'VITE_ROLE_PAGE_ACCESS_JSON']
  const original = Object.fromEntries(roleKeys.map(key => [key, process.env[key]]))
  for (const key of roleKeys) delete process.env[key]
  try {
    await mkdir(join(fixture, 'src'), { recursive: true })
    await cp(join(root, 'src/app'), join(fixture, 'src/app'), { recursive: true })
    await cp(join(root, 'src/locales'), join(fixture, 'src/locales'), { recursive: true })
    await writeFile(join(fixture, 'package.json'), '{"type":"module"}')
    await writeFile(join(fixture, '.env'), "VITE_SUPERVISOR_PAGE_ACCESS_JSON='[\"dashboard.home\",\"plan.list\"]'\nVITE_OPERATOR_PAGE_ACCESS_JSON='[]'\n")
    for (const mode of ['development', 'production']) assert.deepEqual((await checkPageAccess(fixture, mode)).grants.operator, [])
    await writeFile(join(fixture, '.env.local'), "VITE_OPERATOR_PAGE_ACCESS_JSON='[\"dashboard.home\"]'\n")
    assert.deepEqual((await checkPageAccess(fixture, 'development')).grants.operator, ['dashboard.home'])
    await writeFile(join(fixture, '.env.production'), "VITE_OPERATOR_PAGE_ACCESS_JSON='[\"plan.list\"]'\n")
    assert.deepEqual((await checkPageAccess(fixture, 'production')).grants.operator, ['plan.list'])
    await writeFile(join(fixture, '.env.production.local'), "VITE_OPERATOR_PAGE_ACCESS_JSON='[\"dashboard.home\",\"plan.list\"]'\n")
    assert.equal((await checkPageAccess(fixture, 'production')).grants.operator.length, 2)
    process.env.VITE_OPERATOR_PAGE_ACCESS_JSON = '["dashboard.home"]'
    assert.deepEqual((await checkPageAccess(fixture, 'production')).grants.operator, ['dashboard.home'])
    process.env.VITE_OPERATOR_PAGE_ACCESS_JSON = '["missing.list"]'
    assert.throws(() => parseRolePageAccess(loadEnv('production', fixture, 'VITE_'), registry), /unknown pageId/)
    // 实际 Vite config 必须在启动 dev 和构建前拒绝进程覆盖的未知授权。
    await cp(join(root, 'scripts'), join(fixture, 'scripts'), { recursive: true })
    await cp(join(root, 'src/config'), join(fixture, 'src/config'), { recursive: true })
    await cp(join(root, 'vite.config.js'), join(fixture, 'vite.config.js'))
    const { symlink } = await import('node:fs/promises')
    await symlink(join(root, 'node_modules'), join(fixture, 'node_modules'))
    for (const args of [[], ['build'], ['build', '--mode', 'development']]) {
      const result = spawnSync(process.execPath, [join(root, 'node_modules/vite/bin/vite.js'), ...args], { cwd: fixture, encoding: 'utf8' })
      assert.equal(result.status, 1)
      assert.match(result.stderr, /unknown pageId missing.list/)
    }
  } finally {
    for (const key of roleKeys) {
      if (original[key] === undefined) delete process.env[key]
      else process.env[key] = original[key]
    }
    await rm(fixture, { recursive: true, force: true })
  }
})

test('pilot literal i18n keys resolve in both assembled languages', async () => {
  async function walk(directory) {
    for (const item of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, item.name)
      if (item.isDirectory()) await walk(path)
      else if (/\.(vue|js)$/.test(item.name)) {
        const source = await readFile(path, 'utf8')
        for (const match of source.matchAll(/\b(?:\$t|t)\(['"]([^'"]+)['"]/g)) {
          for (const locale of ['en-US', 'zh-CN']) assert.equal(typeof resolveMessage(registry.messages[locale], match[1]), 'string', `${path}:${locale}:${match[1]}`)
        }
      }
    }
  }
  await walk(join(root, 'src/app/dashboard'))
  await walk(join(root, 'src/app/plan'))
})
