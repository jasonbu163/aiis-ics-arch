# Frontend Module Handbook

Chinese version: [README.zh-CN.md](README.zh-CN.md)

## Ownership and assembly

```text
src/app/<module>/
├── api/index.js                 # optional API facade
├── api/mock.js                  # optional paired diagnostic implementation
├── components/                  # optional module-local components
├── locales/en-US.json
├── locales/zh-CN.json
├── views/<page>/index.vue
└── manifest.js
```

`moduleManifest.js` owns pure normalization, validation, ordering and consumer helpers.
`moduleRegistry.js` is the only Vite discovery entrypoint. Router, sidebar and i18n consume its normalized
routes, two-level navigation and active messages; none maintains a module list.

`system` is required Core: it must exist and explicitly declare `enabled: true`. Its `system` and `user`
namespaces support the shell and remain available. This does not bypass any page permission.
Optional modules with `enabled: false` leave routes, menus, default redirect candidates and module messages.
Deleting an optional module directory has the same effect. Invalid manifests, including disabled ones, fail validation.

Discovery is source assembly: restart the dev server after adding/removing modules; production requires rebuilding
and delivering `dist`. Disabled means unregistered, not excluded from bundler scanning or isolated for security.

## Create a module manually

1. Create `src/app/sample/views/list/index.vue` and both locale files. No API is needed for an offline page.
2. Put this JSON in each locale file, translating its values:

```json
{ "navigation": { "title": "Sample" }, "list": { "title": "Sample list" } }
```

3. Add a page using module-owned keys:

```vue
<template>
  <div class="page-layout"><el-card>{{ $t('sample.list.title') }}</el-card></div>
</template>
```

4. Add `manifest.js`:

```js
export default {
  name: 'sample', enabled: true, order: 90,
  navigation: { titleKey: 'sample.navigation.title', icon: 'Menu' },
  routes: [{
    path: 'sample/list', name: 'SampleList',
    component: () => import('./views/list/index.vue'),
    meta: {
      titleKey: 'sample.list.title', parentTitleKey: 'sample.navigation.title',
      pageId: 'sample.list',
      navigation: { visible: true, order: 10, icon: 'List' }
    }
  }]
}
```

5. Run `pnpm check:modules`, `pnpm test:modules`, then `pnpm build`; restart `pnpm dev` for discovery.
6. For a non-admin user, the consuming project's access provider must already grant `sample.list`.
   Creating a manifest never grants access. Use local fixtures for offline verification; do not call real services.

The optional API facade belongs in `api/index.js`; pages import that facade, never `api/mock.js` directly.
If diagnostic mocking is needed, use the existing `src/api/mockMode.js` `callApi` boundary:

```js
import request from '@/api/request'
import { callApi } from '@/api/mockMode'
import * as mock from './mock'
export const listItems = () => callApi(mock.listItems,
  () => request.get('/sample/items'), 'sample.listItems')
```

`api/mock.js` exports the same function and returns the same unwrapped data shape, with obvious diagnostic
markers such as `sourceType: 'frontend_mock'`. This is a contract illustration: define the actual API in a separate
approved integration task. Root `src/api/` remains request/auth/mock-mode infrastructure.

## Copy, disable or remove

Copy the default-disabled `aiis_demo` directory to a new name. Rename manifest `name`, route `name/path/pageId`,
all translation prefixes, and page imports inside the copied directory. Translate both locale files, run the checks,
then explicitly enable the copied module. Do not edit shared router, MainLayout, locale loader or icon registry.
To disable it, set `enabled: false`; to remove it, delete its directory and restart/rebuild.

Other modules' explicit imports, links, route pushes and API dependencies must be handled by their owners.
Orphan grants cannot recreate deleted routes/menus; the Registry never edits the project's permission policy.

## Manifest contract and compatibility

- `name` must match its directory. New templates explicitly provide boolean `enabled` and finite numeric `order`.
- Modules sort by order then name; routes sort by route order (or leaf navigation order), retaining source order
  for ties. The first accessible non-parameter route is the authenticated default, or `/login` if none exists.
- Navigation is optional; without it a module remains routable and localized but has no sidebar group.
  Only `meta.navigation.visible: true` creates a leaf. Parameter routes cannot be visible. Empty groups are hidden.
- Icons are optional Element Plus icon names; missing/unknown hints use `Menu` without editing shared registration.
- New-format module/route/parent titles must resolve in both languages in namespaces owned by the module.
  `<locale>.json` owns the module namespace; the legacy `<namespace>.<locale>.json` naming remains supported.
  Namespace collisions, including with global messages, are errors; bilingual key sets must match.
- A manifest declaring none of `enabled`, module `navigation`, or route `meta.navigation` is legacy: it remains
  enabled, gets no automatic menu, and may resolve global title keys such as `breadcrumb.*`. Historical named
  exports (for example `systemModule`) still load. Declaring any of those fields opts into owned-title validation.
  Keep existing route name/path/pageId when upgrading. Active titles cannot depend on disabled module messages.
- Duplicate module names, route names, canonical paths, pageIds and namespaces fail, as do invalid schemas,
  incomplete bilingual titles and disabling/removing required Core. Nested Vue Router records, aliases and
  redirect parents remain supported; the Registry inspects their effective leaf paths and inherited metadata.
  Navigation still has exactly module group -> route leaf, independent of router nesting.
- Manifests are trusted, static, side-effect-free source; no API calls, timers, role grants or remote loading.

## Permission provider

`canAccessRoute`, `accessibleNavigation` and `defaultAuthenticatedPath` take a consumer-supplied object:
`{ isAdmin, hasPageAccess(pageId) }` (an explicit `isLoggedIn: false` also denies access).
Only literal `true` grants access. Non-admin users need a page grant; `requiresAdmin` also requires admin.
Missing/unknown/broken providers fail closed. The user store currently adapts the existing role configuration;
projects may supply backend-derived permissions without coupling the Registry to that source.
The router separately enforces authentication and active route membership. Frontend visibility never replaces
backend API authorization.

## Checks

```bash
pnpm install --frozen-lockfile
pnpm check:modules
pnpm test:modules
pnpm build
```

The build's `prebuild` validates the same Registry before Vite. Direct `vite build` bypasses this hook; use the
project command. Bare `node scripts/check-module-manifests.mjs` prints help only. The checker imports trusted
local manifests and JSON, never invokes lazy page imports or loads `.env`. Vite itself reads build environment;
use public project-owned values or an isolated copy without real `.env` for source verification.
