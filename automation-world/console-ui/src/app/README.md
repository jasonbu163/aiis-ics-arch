# Console UI source layers

[中文](README.zh-CN.md)

CU is a design workbench, not an industrial application-module host. Legacy `runtime`, `collection`, `plc` and `gates` modules were removed from this copy with their runtime adapters. No module manifest discovery, route registration, API/mock adapter or business menu assembly is active.

Public presentation belongs in `src/ui/` and is exported only through `index.ts` / `styles/index.css`. The private workbench lives in `src/workbench/`; its bilingual strings live in `src/locales/`. App.vue is only composition and main.ts owns app installation. Rust only starts the desktop window. Do not import workbench, app bootstrap, Tauri or CU locale instances from public source.

To add a bounded design sample manually: add symmetric keys to both workbench JSON locales, compose public exports inside `Workbench.vue`, and keep sample layout in `workbench.css`. For a separate sample page, create a private Vue file under `src/workbench/`, import it explicitly from Workbench and add explicit navigation; no auto-registration is implied. Copying a sample requires renaming its component and locale keys and checking both languages. All sample regions must remain marked Design sample and have no device side effects. New business/Agent modules require a separate approved task.

To add an approved shared primitive: create its Vue file under `src/ui/components/`, accept translated props/slots/events, export it from `src/ui/index.ts`, and place reusable token-based styles under the public style entrypoint. Keep dependency paths inside public UI or consumer-owned Vue/Element Plus packages. Build CU and the [consumer example](../../examples/source-consumer/README.md) to verify export consumption. Full source-path and single-instance installation steps are in that tutorial.
