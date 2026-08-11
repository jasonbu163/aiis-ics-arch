# AIIS ICS Architecture Frontend (JavaScript)

Chinese version: [README.zh-CN.md](README.zh-CN.md)

This is the JavaScript Vue 3 + Vite Core frontend template. It contains login, the authenticated shell, system pages and shared infrastructure. Consuming projects add business modules under src/app/<module>/.

## Stable boundaries

- src/router/index.js is the route composition root and automatically discovers module manifest.js files.
- src/locales/index.js is the i18n composition root and automatically discovers module locale JSON files.
- src/layouts/ contains shell structure only; business page behavior stays in its module.
- src/api/ contains auth/request/mock-mode infrastructure; business API facades belong to their module.
- The sidebar currently exposes only Core system pages. Full manifest-driven menu assembly is tracked in ARCH-FE-001 and is not implemented here.

## Commands

~~~bash
pnpm install
pnpm dev
pnpm build
~~~

Use pnpm only. Vite reads .env at process start; restart the process after environment changes. VITE_* values are public browser configuration and must not contain secrets.

## Module handbook

Read [src/app/README.md](src/app/README.md) before creating a module. It documents the minimum manifest, API facade, mock, locale and route shape and the permission/menu boundary.

## Verification

The source-only baseline uses pnpm build and JavaScript syntax checks. It does not start Docker, connect to a backend database, access PLC devices or publish a release.

The approved `ARCH-DOCKER-001` frontend image runs a fixed Node/pnpm lockfile build stage and copies its dist into
an Nginx runtime image. The runtime has no source or `node_modules` bind mount and proxies `/api/v1` to the Compose
`backend` service; it is a disposable MySQL smoke surface, not a production release artifact.
