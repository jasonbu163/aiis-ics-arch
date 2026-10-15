/** SMA Backend bootstrap/OpenAPI navigation; no SQL, device or fixed WS routes. */
import type { AppModuleManifest, ModulePageManifest } from "../navigation";
export const backendConnectionPage: ModulePageManifest = { id: "backendConnection", labelKey: "navBackendConnection", helpKey: "", defaultDetail: "" };
export const connectionDiagnosticPages: readonly ModulePageManifest[] = [backendConnectionPage];
export const connectionManifest: AppModuleManifest = { id: "connection", order: 10, pages: [backendConnectionPage] };
