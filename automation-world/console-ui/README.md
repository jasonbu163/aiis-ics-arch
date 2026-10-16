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

After source compilation, the consumer serves its **own** `dist`. Running built output needs no CU process, source checkout or CU node_modules. This first version provides source exports, not an npm publication, root workspace, online CU service or actual integration into another Agent. See [source layers](src/app/README.md) and [approved scope](plans/CU-001-workbench-foundation/spec.md).

## Element Plus page composition

CU's private **Page samples** page demonstrates a table, validated form, edit dialog and manually selected normal/loading/empty/failed states. Data and retry/submit/edit feedback exist only in memory; reload resets samples. The eight public components and their APIs stay unchanged. The independent consumer composes a smaller table/form/dialog directly from its own Element Plus dependency, with its own locale and state; it never imports PageSamples or workbench files.

Import Element Plus CSS before `@aw-ui-styles`. Use `aw-data-table` on `ElTable`, `aw-sample-form` on `ElForm`, `aw-form-actions` for actions and `aw-page-state` for state content. Public CSS maps Element Plus variables to the current scoped `--agent-*` tokens; page layout belongs to each host. These classes are style conventions, not new public Vue components.

Dialogs outside the layout need an explicit theme scope. This example uses Vue `Teleport to="body"` with a child `<div class="aw-ui aw-sample-overlays" :data-aw-theme="theme">`, and nests `ElDialog` with `:append-to-body="false"` inside it. Each `ElSelect` uses `:teleported="false"`, including inside the dialog, so its popup inherits that scope. Keep the scope bound to the host theme and provide the host's Element Plus locale through `ElConfigProvider`; do not set global html/body theme variables. Labels, validation, feedback and all state transitions are host responsibilities. Page sample business data stays in memory; the separate Parameters editor below manages style drafts.

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
