# AIIS AW Console UI

[中文](README.zh-CN.md)

Console UI (CU) is a lightweight Tauri design workbench and a reusable Vue / TypeScript / CSS source surface. It previews the existing Element Plus shell, cards, actions, status capsules and parameters. All data is marked **Design sample**; it is not live Agent telemetry.

## Source boundaries

- `src/ui/index.ts`: the sole public code entrypoint, exporting `AgentLayout`, `AgentSidebar`, `AgentTopbar`, `ConsoleCard`, `ConsoleActionButton`, `StatusCapsule`, `ThemeToggle`, `LanguageSwitch` and presentation types.
- `src/ui/styles/index.css`: the sole public style entrypoint, with light/dark tokens and component styles. Tokens retain the existing `--agent-*` names and visual values; `.aw-ui` scopes defaults and `[data-aw-theme="dark"]` selects dark mode.
- `src/workbench/`: private design samples and composition. The workbench imports the same public components as consumers.
- `src/workbench/useSharedDesignProfile.ts`: private local-development client; holds the submitted snapshot, result and Parameters-page state in memory across source HMR, with no new storage key.
- `scripts/shared-design-profile.js`: private fixed public JSON/CSS I/O and content revisions shared by the CLI and development plugin; importing it does not read or write files. `scripts/shared-design-profile-dev.js` registers only the local Vite development channel; its adjacent `.d.ts` declares the plugin factory.
- `src/locales/`: CU-private bilingual resources and i18n instance. Components receive translated strings through props/slots; public UI does not depend on i18n.
- `src-tauri/`: window startup only; no business command handlers or industrial configuration readers.
- [source-consumer](examples/source-consumer/README.md): independent minimal Vue/Vite application and source-consumption tutorial, owned by [CU PLAN](PLAN.md).

CU started as a CA-source copy. Its executable PLC/database/headless logic, sample YAML/env, driver features, industrial scripts and dedicated dependencies have been removed. [CA](../control-agent/README.md), DAA and SMA are independent projects; CU does not change their implementations or responsibilities. CU does not read industrial settings, collect data or save business configuration. The `cu.theme` and `cu.locale` keys persist UI preferences; the separate versioned design draft described below stores only style values; previous Agent keys are not migrated.

## Run and build

Use pnpm and Cargo; keep the lockfiles. Current validated versions: Node 22.19.0, pnpm 11.11.0, Vue 3.5.38, Element Plus 2.14.2, icons 2.3.2, vue-i18n 9.14.5, Vite 5.4.21, TypeScript 5.9.3 and vue-tsc 2.2.12. This task retains the existing dependency generation.

```bash
pnpm install --frozen-lockfile
pnpm dev                          # strict 15193
pnpm build                        # type check + own dist
pnpm preview                      # strict 14193
cargo fmt --manifest-path src-tauri/Cargo.toml --check
cargo check --manifest-path src-tauri/Cargo.toml --locked
pnpm tauri dev                    # desktop with Vite
pnpm tauri build --no-bundle       # current-platform native executable
```

Native prerequisites follow [Tauri](https://tauri.app/start/prerequisites/). Product/window: `AIIS AW Console UI`; package/bin: `aiis-aw-console-ui`; lib: `aiis_aw_console_ui_lib`; identifier: `com.aiis.aw.consoleui`. Tauri embeds CU's own `dist` through `../dist`. No signing, distribution or deployment is implied. Dependencies, dist, targets and generated native artifacts stay untracked.

## Consume public source

Follow the complete [consumer tutorial](examples/source-consumer/README.md). At compile time, make the CU public source accessible, alias `@aw-ui` to `src/ui/index.ts` and `@aw-ui-styles` to `src/ui/styles/index.css`. Install consumer-owned compatible Vue, Element Plus and icons; use Vite `resolve.dedupe` for a single instance. The example also installs its own i18n, which supplies strings to public components.

```ts
import { AgentLayout, ConsoleCard, StatusCapsule, type UiTheme } from '@aw-ui'
import 'element-plus/dist/index.css'
import '@aw-ui-styles'
```

The consumer creates/mounts its own Vue app, provides the `theme` prop (`light`/`dark`) on `AgentLayout`, passes localized labels and owns all state/events. Public imports neither mount an app nor read preferences, IPC, runtime snapshots or CU private files. Standalone composition can use an `.aw-ui` wrapper with `data-aw-theme`; public components must remain inside that theme scope. Consumer CSS owns body resets and page layouts.

`ThemeToggle` accepts `theme: UiTheme` and a translated target-action `label`; `LanguageSwitch` accepts `locale: 'zh-CN' | 'en-US'`, translated `zhLabel` / `enLabel` (normally “中” / “EN”) and a translated target-action `label`. Both emit `toggle` without changing state or writing storage. The label supplies the native tooltip and accessible name; the theme button also exposes its current dark state. Import both from `@aw-ui`, keep them inside the public style scope, and let your host handle the event and update props. CU keeps its existing UI preferences; the consumer owns separate state and does not persist it. The built consumer needs no running CU.

The round language control displays only the target: `EN` in Chinese and `中` in English. For a round icon-only action, pass `round-icon`, an `icon` and a translated `label` to `ConsoleActionButton`; the label supplies its accessible name and, unless `title` is provided, its tooltip. Loading and disabled behavior are retained. Without `round-icon`, the ordinary text button is unchanged.

After source compilation, the consumer serves its **own** `dist`. Running built output needs no CU process, source checkout or CU node_modules. This first version provides source exports, not an npm publication, root workspace, online CU service or actual integration into another Agent. See [source layers](src/app/README.md) and [approved scope](plans/CU-001-workbench-foundation/spec.md).

## Flat and grouped navigation

`AgentSidebar` keeps `activeId: string`, `items: NavigationItem[]`, `brand: string`, optional `detail`, and `select(id: string)`. The public entrypoint exports these finite, non-recursive types (Vue's `Component` is the optional icon type):

```ts
interface NavigationChildItem { id: string; label: string; icon?: Component }
interface NavigationItem extends NavigationChildItem { children?: NavigationChildItem[] }
```

A top-level item without children, including `children: []`, is a selectable leaf. A non-empty group only expands/collapses; its children are selectable leaves. Supply non-empty, globally unique stable IDs for groups and leaves; translations change labels, never IDs. Nested groups and duplicate IDs are outside this contract. Empty items retain the brand region. Unknown or group `activeId` selects no leaf and emits no fallback event.

The host translates labels, owns active state and handles `select` once per activation. It may update active externally or decline a selection; final leaf highlighting and `aria-current` follow the prop. Initial active children, external active changes to a child and a child's move to another parent expand that parent without selecting or moving focus. A selected child's parent has active title text distinct from the selected leaf background. Users can collapse it while keeping the selection. Multiple groups may remain open. Label/theme changes preserve expansion; manual expansion exists only in Sidebar memory. `AgentLayout` hiding unmounts Sidebar; restoring keeps host active and expands its parent again, without restoring other manually open groups or taking focus from the toggle. No navigation storage, router, permission model or business/IPC side effect is provided.

Tab/Shift+Tab traverse visible leaves and group titles and can leave the menu. Up/Down move among visible items; Right opens a group and enters its first child; Left returns a child to its parent or collapses a focused group. Enter/Space activate a leaf once or toggle a group. Collapsing a subtree containing focus returns it to its parent. Closed children are excluded from Tab; external prop changes do not move focus. Group `aria-expanded`, leaf `aria-current`, active-parent text and focus outline remain scoped to the current light/dark theme. Narrow grouped menus expand inline and scroll locally; flat menus retain wrapping.

The workbench's **Page samples** group uses icons on both levels. Expand it and select Normal list, Loading list, Empty list or Failed list. The group title only expands or collapses the four entries. Shell preview also shows how a host can change the active child. The independent consumer switches between flat and grouped forms of the same IDs, with a host-owned external active button and event count; table/form/dialog state remains mounted. Its [App.vue](examples/source-consumer/src/App.vue) compiles through public exports. Navigation has no CU service prerequisite. Historical CU-008 evidence remains in the [Development handoff](plans/CU-008-grouped-sidebar-navigation/tasks.md).

## Element Plus page composition

A card has a header and a body. Use `#tools` for a middle toolbar when filters or other controls act on the contents. The header places the title and optional help on the left, the status area in the middle, and `#actions` followed by `#refresh` on the right. Supply `headerStatuses` in priority order. The first status appears in full. When several statuses exist, a thin divider and chevron indicate that hovering or activating the label opens the full list. Refresh, when supplied, stays at the right edge. A narrow card can wrap the right-hand group below the title within the same header. Keep actionable warnings and errors visible in the body. The separate `#status` row remains supported for existing cards.

Set `help` and `helpLabel` for the question-mark tooltip and `statusOverflowLabel` for the localized status list control name. Point `helpAppendTo` to a themed overlay container mounted before the card for both popups. Use `#footer` for pagination.

The general `size="small"` button is 30 px. Use `variant="row"` for 24 px table actions and group them with `.console-row-actions`. Use `tone="primary"` for the main action such as edit, `secondary` for details or preview, and `danger` for deletion. Opt into `.aw-ui--dense` for an 18 px page title, 15 px card titles, and 13 px default body and navigation text. Supply `icon` separately for navigation groups and their child entries.

In the [list sample](src/workbench/PageSamples.vue), search by name or category, then try the page numbers, previous/next and page-size selector below the table. Applying or resetting filters and changing page size return to page one. Add and Edit open a validated modal. Details opens a read-only view. Refresh and Retry use the local records. Data edits live in the current workbench session; reloading restores the sample records.

Drag the Name or Category header edge to resize it. The Actions column has a fixed width and narrow tables scroll horizontally. Each table keeps its own local widths across paging, filtering, refreshing, navigation and reopening. The header's **Reset widths** action shows the hint **Restore default column widths** and removes that table's preference. A consumer can import `useTableColumnWidths(appId, tableId, minimums)` from `@aw-ui`. Connect the returned `resize` to `ElTable`'s `header-dragend`, `tableVersion` to its key and `reset` to the reset action. Enable `border` and bind each resizable column's stable `prop`, `min-width` and saved `width`. Leave fixed columns out of `minimums` and set `resizable` to false. The workbench and Parameters preview use separate table IDs and the preference stays in local storage.

Import Element Plus CSS before `@aw-ui-styles`. Use `aw-data-table` on `ElTable`, `aw-sample-form` on `ElForm`, `aw-form-actions` for actions and `aw-page-state` for state content. Public CSS maps Element Plus variables to the current scoped `--agent-*` tokens; page layout belongs to each host. These classes are style conventions, not new public Vue components.

The [workbench](src/workbench/Workbench.vue) mounts a persistent `.aw-ui` overlay container in `body` before either preview mounts. The help tooltip, dialog and selects target it via `helpAppendTo` or `append-to`; the pagination size selector uses `append-size-to`. Bind the container to the host theme and preview variables, and provide the Element Plus locale via `ElConfigProvider`.

## Design profile: preview, draft and shared source

The CU Parameters page edits a finite schemaVersion 1 profile: each light/dark palette has background, surface, surfaceMuted, text, textMuted, border, accent, accentStrong and onAccent (`#RRGGBB`, normalized lowercase). Shared integers are cardPaddingPx 12–32 (default 24), actionGapPx 4–24 (12), cardRadiusPx 8–28 (20), controlRadiusPx 4–20 (14), all in px; tableDensity is standard (default, 8px vertical cell padding) or compact (4px). Compact card padding/radius and small control radius are derived. Default palette values are owned only by the public JSON. Status colors, decorative glass/shadows, layout and 44px toolbar controls stay fixed.

The Parameters page places the finite editor on the left and live design samples on the right. The preview stays visible while scrolling on desktop and stacks below the editor in a narrow window. Only the current Light/Dark palette is expanded; its explicit mode selector and the topbar share the host theme and `cu.theme` preference. Both palettes retain their values. Each color has a swatch, Element Plus picker and six-digit HEX input; valid edits apply immediately without saving, exporting or restarting. The workbench, live samples, picker popup and sample dialog share the same last valid profile and current theme. Surface affects Element Plus controls, the base table surface and overlays; decorative card glass/background/shadows stay fixed. Secondary title/tone/compact controls remain available below the editor. Valid color edits do not switch theme or locale. Invalid fields keep the last valid preview, identify the mode/field beside the input and in the persistent preview status, and block save/export until corrected. First open always uses the compiled public default. Save/restore/reset are explicit and touch only `cu.design-profile.draft.v1`; theme/locale keys and business samples are separate. Drafts are local to the current CU browser/WebView/origin, never read by consumers or other Agents. Missing/corrupt drafts fall back to the public default with feedback; storage failures are reported. Reset restores the public default and removes only this draft. JSON export is copyable text, not a native file write or source update.

[design-profile.json](src/ui/styles/design-profile.json) is the sole editable public default. [design-profile.generated.css](src/ui/styles/design-profile.generated.css) is deterministic output, not manually maintained. The pure JS validator/mapper is shared by preview and CLI; fixed theme tokens stay in theme.css. Public styles load fixed theme → generated profile → components. Consumers keep using the same public style entrypoint and component APIs.

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

In local source development (`pnpm dev` or `pnpm tauri dev`), use **Apply shared styles** after previewing valid edits. This explicit action writes the complete light/dark/shared profile to the same public JSON and generated CSS above; CU itself consumes those same sources. Invalid edits or an unavailable channel disable the action. While applying, the submitted snapshot is held and duplicate submissions are blocked. Success survives the resulting HMR and keeps Parameters open; refresh/start uses the updated public default. Applying neither saves the draft nor changes theme/language preferences. Preview and packaged CU have no source-write endpoint and show the disabled action with export/CLI guidance.

The private `/__cu/design-profile` channel accepts only actual loopback connections on the existing local 15193 Host names. Its guarded GET establishes a process session and the two-file content revision; POST requires the matching local Origin, session token and a bounded JSON body. It has no cross-origin CORS and accepts no output paths, arbitrary CSS/scripts or consumer directories. A version conflict refuses the write: first export your edits, refresh, review the public default, then retry. Do not concurrently run the CLI or manually edit the public targets while applying; process-local serialization and optimistic revision checks are not a cross-process lock. An I/O/network failure is not a confirmed application: inspect both files, restore valid JSON if needed, run `pnpm design:profile --generate` and `pnpm design:profile --check`, then refresh. Two safe file replacements are not a two-file transaction. Other Agents still consume the unchanged public style entrypoint and own source synchronization, development refresh or rebuilding/distribution of installed binaries.
