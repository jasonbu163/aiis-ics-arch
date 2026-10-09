# AIIS ICS Architecture Frontend (JavaScript)

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This is the JavaScript Vue 3 + Vite Core frontend template. It contains login, the authenticated shell, system pages, the dashboard/plan onboarding pilot and shared infrastructure. Consuming projects add business modules under src/app/<module>/.

## Stable boundaries

- src/app/moduleRegistry.js is the single manifest/locale discovery and validated assembly entrypoint.
- src/router/index.js and src/locales/index.js consume its active routes and bilingual messages.
- src/layouts/ contains shell structure only; business page behavior stays in its module.
- src/api/ contains auth/request/mock-mode infrastructure; business API facades belong to their module.
- The sidebar uses manifest navigation and the same access provider as route/default filtering. Required system remains enabled; optional modules can opt out of all four consumers.

## Commands

~~~bash
pnpm install
pnpm dev
pnpm check:modules
pnpm test:modules
pnpm build
~~~

Use pnpm only. Vite reads .env at process start; restart the process after environment changes. VITE_* values are public browser configuration and must not contain secrets.

## Project page configuration

Host `pnpm dev` and `pnpm build` share the Git-ignored `.env`; `.env.production` is not required.
Docker dev keeps `.env.docker.dev`; copy the matching example and adjust project values. Vite reads `.env`,
`.env.local`, `.env.[mode]`, `.env.[mode].local` at startup (later files override earlier ones); existing
process variables have priority. Default modes are development for dev and production for build. Existing
mode/local files still follow this precedence.

```dotenv
VITE_SUPERVISOR_PAGE_ACCESS_JSON='["dashboard.home","plan.list"]'
VITE_OPERATOR_PAGE_ACCESS_JSON='["dashboard.home"]'
```

Arrays contain manifest `meta.pageId` values. Operator must be a subset of supervisor. `[]` grants no pages;
admin is built in and is not configured in env. Only enabled valid leaf pages can be granted. Duplicates,
unknown/disabled/admin-only pages, malformed JSON and missing arrays fail explicitly; unknown roles deny access.
These grants control menus, routes and default entry; backend API authorization is still required.
Module `enabled` controls assembly; `navigation` and leaf `visible` control menus. Module `order` sorts groups;
leaf `navigation.order` sorts entries inside a group. Dashboard is 10, plan 20, system 80; aiis_demo stays disabled.

Migrate the old `VITE_ROLE_PAGE_ACCESS_JSON` object's supervisor/operator arrays unchanged into the two new
variables, preserving membership, order and all other settings. Keep the historical JSON in the README history section; the local env files now contain only active configuration and usage comments.
An active legacy key fails with an explicit migration error. Missing legacy roles migrate to `[]`; invalid
objects, extra roles or conflicting new/old sources require review instead of silent clearing.
Preserve old grants for modules not yet migrated: dev/build reports unknown pageIds until those modules are
migrated or the Owner explicitly adjusts grants.

```bash
pnpm check:access --mode development
pnpm check:access --mode production
```

These commands share the effective-env validation used by dev/build. `pnpm check:modules` validates only
module contracts without reading env; bare invocation of either checker only shows help. Restart dev after
env changes. Rebuild dist for delivery; restarting Nginx alone cannot change compiled grants. Review API
addresses and disable mocks/demo accounts for production; fixture builds are not delivery artifacts.

## Environment variables

Both tracked examples contain public defaults. Local `.env` / `.env.docker.dev` stay Git ignored; do not
copy an entire real env file into documentation or commit it. The entries below describe current readers,
not backend credentials or API authorization. Vite values are read at startup and embedded into browser
bundles where consumed. Restart dev after changes; rebuild the production `dist` after changes to consumed
build values. Updating env or restarting Nginx cannot rewrite an existing bundle.

| Key | Purpose and scope |
| --- | --- |
| `VITE_API_BASE_URL` | Browser HTTP API base URL, read by `src/config/api.js`. Default `/api/v1` sends same-origin requests: Vite proxies them in development and the existing Nginx configuration proxies them in deployment. An absolute URL is a browser-reachable address, not a container-only hostname. |
| `VITE_PROXY_TARGET` | Destination of Vite's development `/api` proxy in `vite.config.js`. Host and Docker dev use different network contexts; configure a target reachable by the Vite process. This value does not configure the production Nginx upstream. |
| `VITE_APP_PORT` | Vite development server port; absent/unparseable values fall back to `5190`. It does not configure Nginx's listening port. |
| `VITE_REQUEST_TIMEOUT` | HTTP request timeout in milliseconds; default `10000`, read by the API configuration. |
| `VITE_FRONTEND_MOCK_ENABLED` | Exact `true` selects local frontend diagnostic API mocks; other values use the real API facade. Mock results do not verify backend behavior. Keep false for delivery. |
| `VITE_SUPERVISOR_PAGE_ACCESS_JSON` | JSON array of enabled, non-admin leaf `meta.pageId` grants for supervisor. `[]` grants no pages. The array does not change module `enabled` or backend permissions. |
| `VITE_OPERATOR_PAGE_ACCESS_JSON` | JSON array of operator pageId grants; must be a subset of supervisor. Unknown/disabled/admin-only pages and invalid arrays prevent dev/build. Admin is built in and has no env grant array. |
| `VITE_LOGIN_DEMO_ACCOUNTS_ENABLED` | Exact `true` displays the login page's demo account hints. It does not create accounts, authenticate users, enable mocks or grant pages. Keep false for delivery. |
| `VITE_OPEN_BROWSER` (optional, absent from these four files) | Exact `true` opens the browser when the Vite dev server starts; absent/other values leave it closed. This development-only setting is read by `vite.config.js`. |

### Brand Logo configuration

The login page and authenticated shell share `BrandLogo.vue` and now consume these five keys through
`src/config/brand.js`. The component preserves the image's natural aspect ratio with contain sizing,
left/center/right alignment, and ResizeObserver layout updates. It uses the existing theme glow tokens;
light theme hides the glow and dark theme displays it. No global theme changes are required.

| Key | Supported values and fallback |
| --- | --- |
| `VITE_BRAND_LOGO_FILE` | A filename from bundled `src/assets/brand/*`, default `demo-organization-logo.svg`. Trim surrounding whitespace. Missing/unknown files and invalid paths/URLs fall back to the neutral demo SVG; only packaged local assets are resolved. |
| `VITE_BRAND_LOGO_ALIGN` | `left`, `center`, `right`; default `center`. Whitespace/case normalize, invalid values use the default. |
| `VITE_BRAND_GLOW_LEFT` | Left segment: `light`, `high-light`, `accent`, `none`; default `light`. |
| `VITE_BRAND_GLOW_CENTER` | Center segment: the same four modes; default `accent`. |
| `VITE_BRAND_GLOW_RIGHT` | Right segment: the same four modes; default `accent`. |

Glow values normalize whitespace/case. Historical misspelling `hight-light` is accepted as `high-light`.
`light` is a white glow, `high-light` a stronger white glow, `accent` uses the theme accent color, and `none`
is transparent. The three regions are configured independently. The image alt text comes from the current
language's `common.systemTitle`. The public fallback contains only a generic demo identity, no customer logo.

To use a project Logo, place a reviewed asset under `src/assets/brand/`, set its filename, restart dev or
rebuild dist. A name containing a path separator, traversal or URL is rejected; copying an image only into
`dist` does not register it with the source glob. Existing local brand settings are preserved; a configured
file absent from this Core checkout intentionally displays the demo. Public examples and standalone Dockerfile
ARG/ENV defaults use the neutral asset, center alignment and light/accent/accent glow. Docker dev without these
keys uses the same source defaults. Production Nginx still serves the prebuilt host dist.

### Historical role configuration

These are the Owner-provided old pageId-only JSON objects, moved from local env comments. They are historical
references and are **not read by the current application**. The active configuration still uses only the two
new arrays. For the current module test, the Owner authorized intersecting the old grants with enabled
non-admin leaf pages, preserving order: host supervisor now has 3 grants (dashboard.home, plan.list, system.user),
operator has 2 (dashboard.home, plan.list); Docker dev keeps empty arrays. The historical 20/14 objects below
are unchanged. Current host configuration passes the strict checker; future grants still require valid modules. Do not restore these objects as an active legacy variable or copy unsupported
grants into a working project configuration without reviewing module availability.

Host development / production build (`.env`) history:

```json
{
  "supervisor": [
    "dashboard.home",
    "plan.list",
    "performance.list",
    "performance.split",
    "performance.print",
    "performance.quality",
    "performance.efficiency",
    "monitor.temperature",
    "monitor.energy",
    "equipment.production-parameters",
    "equipment.drive",
    "equipment.temperature",
    "auxiliary.stop",
    "auxiliary.shift",
    "auxiliary.price",
    "maintenance.log",
    "quality.list",
    "quality.control",
    "quality.spc",
    "system.user"
  ],
  "operator": [
    "dashboard.home",
    "plan.list",
    "performance.list",
    "performance.split",
    "performance.print",
    "performance.quality",
    "performance.efficiency",
    "quality.list",
    "quality.control",
    "quality.spc",
    "equipment.production-parameters",
    "equipment.drive",
    "equipment.temperature",
    "maintenance.log"
  ]
}
```

Docker development (`.env.docker.dev`) history:

```json
{}
```

## Module handbook

Read [src/app/README.md](src/app/README.md) before creating a module. It documents the minimum manifest, API facade, mock, locale and route shape and the permission/menu boundary.

## Verification

The source-only checks use the Node contract matrix and pnpm build (including prebuild manifest validation). Adding/removing modules requires a dev restart or production rebuild. These checks do not start Docker, connect to a backend database, access PLC devices or publish a release.

The approved `ARCH-DOCKER-001` frontend image runs a fixed Node/pnpm lockfile build stage and copies its dist into
an Nginx runtime image. The runtime has no source or `node_modules` bind mount and proxies `/api/v1` to the Compose
`backend` service; it is a disposable MySQL smoke surface, not a production release artifact.

## Prebuilt dist deployment

The root `docker-compose.prod.yml` uses pinned Nginx with this directory's existing `nginx.conf` and mounts `dist` read-only at `/usr/share/nginx/html/current`. Build with the checked-in pnpm lockfile before startup; a missing `dist/index.html` fails startup explicitly. Use `/api/v1` and disable mocks/demo accounts for the production build. The frontend Dockerfile remains available as a standalone image-build recipe; prod uses host-built dist. See [deployment preparation](../INITIALIZATION.md#single-host-deployment).
