# Public UI source consumer

[中文](README.zh-CN.md)

This minimal app belongs to CU and compiles only the public UI entrypoints into its own Vite output. It imports no CU workbench, App, private locale instance, IPC, Rust or industrial configuration. Its strings and state belong to this consumer; all examples are marked **Design sample**.

## Run from this directory

```bash
pnpm install --frozen-lockfile
pnpm build                 # vue-tsc + own dist
pnpm dev                   # strict 15194, source must be accessible
pnpm preview               # strict 14194, own dist only
```

The example declares its own dependencies/lockfile/node_modules. It is not a root workspace package and does not use CU node_modules at runtime. After build, serve this directory's `dist` with any static host; stop CU's browser/native processes first to demonstrate independent operation. Copying only dist is enough for runtime. It requires no CU source or dependency directory, pnpm, Cargo or CU HTTP service on the deployed static host.

## Start from an existing Vue/Vite consumer

1. Make public `src/ui/` source available at build time, either through an explicit sibling checkout path or by copying that public directory into your consumer. Preserve internal relative imports. Do not copy CU App/main/workbench/locales/Rust. A source-path integration must pin its source version in the consumer's project governance; there is no npm package/version pipeline in this task.
2. Install the dependency versions in this example's package.json, or compatible versions already owned by the consumer. Validated: Vue 3.5.38, Element Plus 2.14.2, icons 2.3.2; Vite 5.4.21, plugin-vue 5.2.4, TypeScript 5.9.3 and vue-tsc 2.2.12. The example uses vue-i18n 9.14.5 privately; the public components do not require an i18n instance. Do not install a second Vue/i18n app just for UI.
3. Configure exact aliases and dedupe in Vite (adapt the relative paths to your checkout):

```ts
resolve: {
  alias: {
    '@aw-ui': fileURLToPath(new URL('../../src/ui/index.ts', import.meta.url)),
    '@aw-ui-styles': fileURLToPath(new URL('../../src/ui/styles/index.css', import.meta.url))
  },
  dedupe: ['vue', 'element-plus', '@element-plus/icons-vue', 'vue-i18n']
}
```

Use `fileURLToPath` and `URL` from `node:url`, as in [vite.config.ts](vite.config.ts). For dev source outside Vite root, explicitly allow that source directory with `server.fs.allow`. TypeScript's `paths` in [tsconfig.json](tsconfig.json) resolve the public entrypoint and Vue/Element Plus/icons to this consumer's own declarations. Keep the same resolved versions and a single runtime instance. No CU bootstrap imports are needed.

4. In your own bootstrap, import styles in this order and install only your own app/plugins:

```ts
import 'element-plus/dist/index.css'
import '@aw-ui-styles'
// createApp(YourApp).use(yourI18n).mount('#app')
```

5. Compose exported components in your page, as in [App.vue](src/App.vue):

```vue
<AgentLayout :theme="theme">
  <template #sidebar>
    <AgentSidebar :items="items" active-id="sample" :brand="t('brand')" />
  </template>
  <template #topbar>
    <AgentTopbar :title="t('title')" :sidebar-label="t('sidebar')">
      <template #actions><!-- consumer-owned actions --></template>
    </AgentTopbar>
  </template>
  <ConsoleCard :title="t('sample')">
    <StatusCapsule :label="t('sample')" tone="warning" />
  </ConsoleCard>
</AgentLayout>
```

Import these names from `@aw-ui`. `AgentLayout` accepts `theme: 'light' | 'dark'` and `sidebarHidden`; it exposes sidebar/topbar/default slots. `AgentSidebar` receives translated `{id,label,icon?}` items and emits `select(id)`. `AgentTopbar` receives title/subtitle/sidebarLabel and emits `toggle-sidebar`. `ConsoleCard` supports actions/tools/default/footer slots and compact mode. `ConsoleActionButton` accepts translated label/title or slot, tone, small/large size and emits click. `StatusCapsule` accepts label plus neutral/success/warning/danger display tone. These tones are presentation values, not device statuses.

Language installation is entirely consumer-owned: create or reuse your vue-i18n instance, load your own symmetric locale resources and pass `t(...)` results. Theme installation is explicit through AgentLayout; standalone components require an `.aw-ui` wrapper with `data-aw-theme="light"` or `"dark"`. Element Plus controls should stay within that scope. Consumer CSS owns body resets and sample-specific spacing. Neither public code nor styles write storage, create an app or contact CU. This example intentionally does not persist preferences.

`ThemeToggle` accepts `theme: UiTheme` and a translated target-action `label`; `LanguageSwitch` accepts `locale: 'zh-CN' | 'en-US'`, translated `zhLabel` / `enLabel` (normally “中” / “EN”) and a translated target-action `label`. Both emit `toggle` without changing state or writing storage. The label supplies the native tooltip and accessible name; the theme button also exposes its current dark state. Import both from `@aw-ui`, keep them inside the public style scope, and let your host handle the event and update props. CU keeps its existing UI preferences; the consumer owns separate state and does not persist it. The built consumer needs no running CU.

6. Run `pnpm build`, stop CU, then `pnpm preview`. The consumer's compiled JS/CSS are local to its dist. No code splitting chunk points to CU's dist or dev port. Actual Agent integration, publishing and business configuration are separate approved work.

The [CU README](../../README.md) defines ownership and [CU PLAN](../../PLAN.md) indexes this foundation.

## Controlled navigation example

Import `NavigationItem` and `NavigationChildItem` with the components from `@aw-ui`. In the host's script, keep IDs independent of translations:

```ts
const activeId = ref('panel-a')
const items = computed<NavigationItem[]>(() => [
  { id: 'overview', label: t('navigationSample.overview') },
  { id: 'panels', label: t('navigationSample.group'), children: [
    { id: 'panel-a', label: t('navigationSample.alpha') },
    { id: 'panel-b', label: t('navigationSample.beta') }
  ] }
])
// Flat form: the same three leaves without the panels group.
```

```vue
<AgentSidebar :items="items" :active-id="activeId" :brand="t('brand')"
  @select="activeId = $event" />
```

`NavigationChildItem` is `{ id: string; label: string; icon?: Component }`; `NavigationItem` extends it with optional `children?: NavigationChildItem[]`, never recursive groups. All IDs are non-empty and globally unique. No children or empty children means a selectable top-level leaf; a non-empty group toggles only and emits no select. Empty items show the brand; unknown/group active IDs do not select a leaf or generate a fallback. Each leaf activation emits once, and the host decides whether to accept it; initialization/external updates emit nothing. The host owns translations, theme, active state, pages and any business action.

Initial child active, external active changes to a child, or an active child's move between groups opens its parent. A parent with the current child has active title text; the selected leaf and focus outline remain distinct. Manually closing the current group retains selection; multiple groups may stay open. Labels/theme do not reset open groups. Open state lives only in each Sidebar instance; hiding via AgentLayout unmounts it, and restoring reopens the active parent without restoring other groups or taking focus. There is no navigation storage, router or permission mechanism.

Tab/Shift+Tab enter/leave visible menu items. Up/Down move between visible items, Right expands/enters a group, Left returns to its parent or collapses a group, and Enter/Space select once or toggle. Collapsing a subtree containing focus returns focus to the parent; closed children are not tabbable. External updates do not move focus. Group aria-expanded, leaf aria-current, active-parent text and focus outline work in both themes. Narrow grouped menus stay inline with local scrolling; flat menus wrap.

The actual App.vue starts flat and uses a radio to switch grouping without changing leaf IDs or remounting its table/form/dialog. It shows current selection/event count and an external active button. Both modes are Design samples held only in memory. CU's Shell preview retains its four flat primary items and shows a separate grouped sample. See the [CU navigation contract](../../README.md#flat-and-grouped-navigation). Source consumption keeps the aliases, CSS order, dedupe and dependency versions above; build your own output, with no CU runtime prerequisite. For exact uncommitted bytes use the CU-008 r1 [Development source SHA manifest](../../plans/CU-008-grouped-sidebar-navigation/tasks.md) and the subsequent independent QA/Owner evidence when formed; context HEAD is not a published source version. DAA pins and verifies its own integration separately.

## Element Plus page composition

CU's private **Page samples** page demonstrates a table, validated form, edit dialog and manually selected normal/loading/empty/failed states. Data and retry/submit/edit feedback exist only in memory; reload resets samples. The eight public components and their APIs stay unchanged. The independent consumer composes a smaller table/form/dialog directly from its own Element Plus dependency, with its own locale and state; it never imports PageSamples or workbench files.

Import Element Plus CSS before `@aw-ui-styles`. Use `aw-data-table` on `ElTable`, `aw-sample-form` on `ElForm`, `aw-form-actions` for actions and `aw-page-state` for state content. Public CSS maps Element Plus variables to the current scoped `--agent-*` tokens; page layout belongs to each host. These classes are style conventions, not new public Vue components.

Dialogs outside the layout need an explicit theme scope. This example uses Vue `Teleport to="body"` with a child `<div class="aw-ui aw-sample-overlays" :data-aw-theme="theme">`, and nests `ElDialog` with `:append-to-body="false"` inside it. Each `ElSelect` uses `:teleported="false"`, including inside the dialog, so its popup inherits that scope. Keep the scope bound to the host theme and provide the host's Element Plus locale through `ElConfigProvider`; do not set global html/body theme variables. Labels, validation, feedback and all state transitions are host responsibilities. This sample saves no business data, drafts or generated style plans.

## Design profile: preview, draft and shared source

The CU Parameters page edits a finite schemaVersion 1 profile: each light/dark palette has background, surface, surfaceMuted, text, textMuted, border, accent, accentStrong and onAccent (`#RRGGBB`, normalized lowercase). Shared integers are cardPaddingPx 12–32 (default 24), actionGapPx 4–24 (12), cardRadiusPx 8–28 (20), controlRadiusPx 4–20 (14), all in px; tableDensity is standard (default, 8px vertical cell padding) or compact (4px). Compact card padding/radius and small control radius are derived. Default palette values are owned only by the public JSON. Status colors, decorative glass/shadows, layout and 44px toolbar controls stay fixed.

Valid edits preview on the workbench root and explicit Page samples overlay scope; they do not change the host theme/locale. Invalid fields keep the last valid preview and block save/export. First open always uses the compiled public default. Save/restore/reset are explicit and touch only `cu.design-profile.draft.v1`; theme/locale keys and business samples are separate. Drafts are local to the current CU browser/WebView/origin, never read by consumers or other Agents. Missing/corrupt drafts fall back to the public default with feedback; storage failures are reported. Reset restores the public default and removes only this draft. JSON export is copyable text, not a native file write or source update.

[design-profile.json](../../src/ui/styles/design-profile.json) is the sole editable public default. [design-profile.generated.css](../../src/ui/styles/design-profile.generated.css) is deterministic output, not manually maintained. The pure JS validator/mapper is shared by preview and CLI; fixed theme tokens stay in theme.css. Public styles load fixed theme → generated profile → components. Consumers keep using the same public style entrypoint and component APIs.

From the CU directory:

```bash
pnpm design:profile                         # help only, no reads/writes
pnpm design:profile --help                  # same
# Copy exported JSON into an explicit local file first:
pnpm design:profile --import /absolute/path/profile.json
pnpm design:profile --generate              # regenerate fixed CSS from public JSON
pnpm design:profile --check                 # read-only consistency check
pnpm build                                 # check first; never silently generate
```

All fields are required; unknown fields, paths, arbitrary CSS/scripts, invalid types/colors/ranges/versions are rejected before target writes. Import writes only the fixed CU public JSON/CSS using safe per-file replacement; it does not promise a two-file transaction. For stale/missing CSS, run `--generate` then `--check`. For damaged public JSON, restore a known valid backup before generating. After an I/O failure, inspect both targets, restore valid JSON if needed, then generate/check; failure returns nonzero. Back up your valid public profile before imports.

Export → explicit engineering import → generate/check → host development refresh or rebuild is the sharing path. The existing consumer source is unchanged and imports generated CSS through its normal public entrypoint; its own built dist needs no running CU and reads no CU drafts. DAA/SMA are not integrated by this task. Future hosts own synchronization and builds; installed desktop binaries require rebuilding and distribution, with no promised real-time propagation or online CU dependency.
